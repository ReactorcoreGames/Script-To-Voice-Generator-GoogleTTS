"""
Audio generation using Google Cloud TTS and FFMPEG conversion utilities.
"""

import html
import os
import re
import subprocess
import sys
from pathlib import Path


# ── Voice family detection ────────────────────────────────────────────────────

def get_voice_family(voice_name: str) -> str:
    """
    Return the family string for a Google TTS voice name.
    Check order matters — "Chirp3-HD" must precede "Chirp-HD" (substring collision).
    """
    if "Chirp3-HD" in voice_name:
        return "chirp3_hd"
    if "Chirp-HD" in voice_name:
        return "chirp_hd"
    if "Neural2" in voice_name:
        return "neural2"
    if "Wavenet" in voice_name:
        return "wavenet"
    if "Studio" in voice_name:
        return "studio"
    return "standard"


# ── SSML helpers ──────────────────────────────────────────────────────────────

def _apply_emphasis(text: str) -> str:
    """Convert markdown bold/italic markers to SSML <emphasis> tags."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<emphasis level="strong">\1</emphasis>', text)
    text = re.sub(r'_(.+?)_', r'<emphasis level="moderate">\1</emphasis>', text)
    return text


def build_ssml(text: str) -> str:
    """
    Convert spoken text to a SSML string for the Google TTS API.

    Pipeline:
      1. XML-escape the raw text (&, <, > — preserves ' and " as-is)
      2. Convert **bold** to <emphasis level="strong"> and _italic_ to <emphasis level="moderate">
      3. Wrap in <speak>
    """
    escaped = html.escape(text, quote=False)
    with_emphasis = _apply_emphasis(escaped)
    return f"<speak>{with_emphasis}</speak>"


# ── Yell impact helper ────────────────────────────────────────────────────────

def is_yell_line(spoken_text):
    """
    Check if a spoken text line qualifies for the Yell Impact speed adjustment.

    Qualifies when:
    - The entire text is a single word (no spaces) before trailing punctuation
    - The trailing punctuation characters contain at least one !
    - Patterns like AAARGH!, YES!!, NO?!, HELP?!?, REALLY!!! all qualify
    - Lines ending with ? only, or multi-word lines, do NOT qualify

    Examples that qualify:  AAARGH!  YES!!  NO?!  HELP?!?  REALLY!!!
    Examples that don't:    Why?    Get out!    Help me!!
    """
    text = spoken_text.strip()
    if not text:
        return False

    match = re.match(r'^([^?!\s]+)([?!]+)$', text)
    if not match:
        return False

    punct_part = match.group(2)
    return '!' in punct_part


# ── Silence filter builder ────────────────────────────────────────────────────

def _build_silence_filter(mode: str) -> str:
    """
    Build the FFMPEG filter string(s) for Stage 0 silence trimming.
    Returns empty string when mode is "off" (caller skips the filter entirely).

    mode values: "off" / "beginning" / "end" / "beginning_end" / "all"

    Both start and end trim use a fixed -40 dB threshold. Chirp 3 HD and
    Neural2 encoder padding contains low-level breathiness/pre-phonation noise
    measured up to -39 dB in practice, so -35 dB is needed to catch it.
    Real speech onset sits above -20 dB even for quiet voices, leaving a
    comfortable margin. start_silence=0.02 (20ms minimum duration) is a light
    guard against false triggers; the areverse sandwich for end trim makes this
    robust without needing a larger duration.

    End trim uses an areverse sandwich (reverse → silenceremove start → reverse)
    rather than silenceremove stop_periods. The stop_periods approach is a
    streaming filter that can prematurely terminate on any natural amplitude dip
    (falling intonation, trailing fricatives, breathy tails). The areverse
    approach trims only the true tail and is immune to mid-clip dips.
    """
    if mode == "off":
        return ""

    trim_start = mode in ("beginning", "beginning_end", "all")
    trim_end   = mode in ("end", "beginning_end")
    trim_all   = mode == "all"

    START_FILTER = (
        "silenceremove="
        "start_periods=1:"
        "start_silence=0.02:"
        "start_threshold=-35dB:"
        "stop_periods=0"
    )
    # End trim: reverse, strip leading silence (= original trailing silence), reverse back.
    END_FILTER = (
        "areverse,"
        "silenceremove="
        "start_periods=1:"
        "start_silence=0.02:"
        "start_threshold=-35dB:"
        "stop_periods=0,"
        "areverse"
    )
    # "all" mode: strip mid-clip silence via stop_periods=-1 after start trim.
    ALL_MID_FILTER = (
        "silenceremove="
        "start_periods=0:"
        "stop_periods=-1:"
        "stop_silence=0.1:"
        "stop_threshold=-80dB"
    )

    filters = []
    if trim_start:
        filters.append(START_FILTER)
    if trim_end:
        filters.append(END_FILTER)
    elif trim_all:
        filters.append(ALL_MID_FILTER)
        filters.append(END_FILTER)

    return ",".join(filters)


# ── AudioGenerator class ──────────────────────────────────────────────────────

class AudioGenerator:
    """Handles audio generation and conversion."""

    def __init__(self, credentials_path=None):
        self.available_voices = []
        self._client = None
        if credentials_path:
            self._init_client(credentials_path)

    def _init_client(self, path: str):
        """Load service account credentials and create a TextToSpeechClient."""
        try:
            from google.cloud import texttospeech
            from google.oauth2 import service_account

            creds = service_account.Credentials.from_service_account_file(
                path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            self._client = texttospeech.TextToSpeechClient(credentials=creds)
        except Exception as e:
            print(f"Google TTS: failed to init client from '{path}': {e}")
            self._client = None

    def _get_subprocess_startupinfo(self):
        """Get subprocess startup info to hide console windows on Windows."""
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            return startupinfo
        return None

    def load_voices(self, credentials_path=None) -> list:
        """
        Load available Google TTS voices synchronously.

        Format: "en-US-Chirp3-HD-Charon | Charon (Chirp 3 HD) - en-US | Male"
        The first segment (before " | ") is the short name used by the API.

        Returns [] on credential failure.
        """
        if credentials_path:
            self._init_client(credentials_path)

        if self._client is None:
            return []

        try:
            from google.cloud import texttospeech

            response = self._client.list_voices()
            formatted_voices = []

            for voice in response.voices:
                short_name = voice.name
                family = get_voice_family(short_name)

                # Skip obsolete/expensive families: chirp_hd (Preview, superseded by Chirp 3 HD)
                # and studio (premium pricing, not worth the accidental cost risk)
                if family in ("chirp_hd", "studio"):
                    continue

                family_labels = {
                    "chirp3_hd": "Chirp 3 HD",
                    "neural2": "Neural2",
                    "wavenet": "WaveNet",
                    "standard": "Standard",
                }
                family_label = family_labels.get(family, family)

                # Extract the tail identifier from the short name
                # e.g. "en-US-Chirp3-HD-Charon" → "Charon", "en-US-Neural2-A" → "A"
                name_parts = short_name.split("-")
                display_part = name_parts[-1] if name_parts else short_name

                # Gender
                gender_map = {
                    texttospeech.SsmlVoiceGender.MALE: "Male",
                    texttospeech.SsmlVoiceGender.FEMALE: "Female",
                    texttospeech.SsmlVoiceGender.NEUTRAL: "Neutral",
                }
                gender = gender_map.get(voice.ssml_gender, "Unknown")

                lang_codes = list(voice.language_codes)
                lang_display = lang_codes[0] if lang_codes else ""

                display = (
                    f"{short_name} | "
                    f"{display_part} ({family_label}) - {lang_display} | "
                    f"{gender}"
                )
                formatted_voices.append(display)

            self.available_voices = formatted_voices
            return formatted_voices

        except Exception as e:
            raise RuntimeError(str(e)) from e

    def generate_audio(self, text: str, output_path: str, voice_name: str,
                       speaking_rate: float = 1.0, pitch_semitones: float = 0.0,
                       config_manager=None, output_format: str = "mp3"):
        """
        Generate audio using Google Cloud TTS and save to output_path.

        For Chirp 3 HD, pitch_semitones is stored in the profile but pitch=0.0
        is passed to the API (Chirp 3 HD ignores API pitch silently).
        FFMPEG pitch_shift effect is the real pitch control for all families.

        Calls config_manager.increment_char_usage(len(ssml)) on success.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if self._client is None:
            return False, ("Google TTS client not initialised. "
                           "Set your credentials path in Tab 4.")

        try:
            from google.cloud import texttospeech
            from config import GOOGLE_TTS_NO_API_PITCH_FAMILIES

            ssml_text = build_ssml(text)

            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

            family = get_voice_family(voice_name)
            api_pitch = 0.0 if family in GOOGLE_TTS_NO_API_PITCH_FAMILIES else float(pitch_semitones)

            safe_rate = max(0.25, min(2.0, float(speaking_rate)))

            voice_params = texttospeech.VoiceSelectionParams(
                name=voice_name,
                language_code="-".join(voice_name.split("-")[:2]),
            )
            encoding = (texttospeech.AudioEncoding.OGG_OPUS
                        if output_format == "ogg"
                        else texttospeech.AudioEncoding.MP3)
            audio_config = texttospeech.AudioConfig(
                audio_encoding=encoding,
                speaking_rate=safe_rate,
                pitch=api_pitch,
            )

            response = self._client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config,
            )

            with open(output_path, "wb") as f:
                f.write(response.audio_content)

            if config_manager is not None:
                config_manager.increment_char_usage(len(ssml_text))

            return True, None

        except Exception as e:
            return False, f"Google TTS error: {e}"

    def apply_volume_adjustment(self, input_path, output_path, volume_percent):
        """
        Apply volume adjustment to an audio file using FFMPEG.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            volume_multiplier = volume_percent / 100.0
            subprocess.run([
                "ffmpeg", "-i", str(input_path),
                "-af", f"volume={volume_multiplier}",
                "-y", str(output_path)
            ], check=True, capture_output=True,
                startupinfo=self._get_subprocess_startupinfo())
            return True, None
        except subprocess.CalledProcessError as e:
            return False, f"Failed to adjust volume: {str(e)}"
        except FileNotFoundError:
            return False, ("FFMPEG not found in PATH. Please install FFMPEG.\n\n"
                           "You can use: https://reactorcore.itch.io/ffmpeg-to-path-installer")

    def apply_audio_effects(self, input_path, output_path, effect_settings,
                            volume_percent=100, is_inner_thought=False,
                            config_manager=None, is_sfx=False,
                            silence_trim_mode="beginning_end",
                            silence_start_db=-65, silence_stop_db=-65,  # threshold params kept for call-site compat, ignored
                            output_format="mp3"):
        """
        Apply audio effects and volume adjustment to an audio file using FFMPEG.

        Pipeline (voice clips):
        0. Silence removal (configurable — default "beginning_end" for Chirp 3 HD)
        2. Frequency-based effects (radio, telephone, cheap_mic, underwater, megaphone, worn_tape, intercom)
        3. Ring modulation / pitch-based effects (robot_voice, alien)
        3.5. FFMPEG pitch shift (pitch_shift effect for all families)
        4. Spatial/echo effects (reverb, cave)
        5. Distortion
        5.5. Inner thoughts filter
        7. Soft limiting
        8. Final volume adjustment (capped at 100%)
        8.5. FMSU (optional destructive pass)
        9. Reverse (optional)

        Per-clip peak normalization is applied separately after this call.

        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file
            effect_settings: dict mapping effect names to preset levels
            volume_percent: Volume percentage (internally capped at 100%)
            is_inner_thought: If True, applies inner thoughts filter
            is_sfx: If True, skips silence removal stage
            silence_trim_mode: "off" / "beginning" / "end" / "beginning_end" / "all"

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        from config import AUDIO_EFFECTS, INNER_THOUGHTS_FILTER, FMSU_FILTER

        if config_manager is not None:
            inner_thoughts_filter = config_manager.get_inner_thoughts_filter()
        else:
            inner_thoughts_filter = INNER_THOUGHTS_FILTER

        try:
            filters = []

            if not is_sfx:
                # STAGE 0: Silence removal (configurable)
                silence_filter = _build_silence_filter(silence_trim_mode)
                if silence_filter:
                    filters.append(silence_filter)

            # STAGE 2: Frequency-based effects
            for effect_name in ["radio", "telephone", "cheap_mic",
                                 "underwater", "megaphone", "worn_tape", "intercom"]:
                if effect_name in effect_settings and effect_settings[effect_name] != "off":
                    level = effect_settings[effect_name]
                    if effect_name in AUDIO_EFFECTS:
                        effect_filter = AUDIO_EFFECTS[effect_name]["presets"].get(level, "")
                        if effect_filter:
                            filters.append(effect_filter)

            # STAGE 3: Ring modulation / pitch-based character effects
            for effect_name in ["robot_voice", "alien"]:
                if effect_name in effect_settings and effect_settings[effect_name] != "off":
                    level = effect_settings[effect_name]
                    if effect_name in AUDIO_EFFECTS:
                        effect_filter = AUDIO_EFFECTS[effect_name]["presets"].get(level, "")
                        if effect_filter:
                            filters.append(effect_filter)

            # STAGE 3.5: Pitch shift via rubberband (true pitch/tempo independence)
            # Per-speaker: float semitones from slider. SFX panel: string preset key.
            ps_val = effect_settings.get("pitch_shift", 0.0)
            try:
                ps_semitones = float(ps_val)
                if ps_semitones != 0.0:
                    filters.append(f"rubberband=pitch={2 ** (ps_semitones / 12.0):.6f}")
            except (TypeError, ValueError):
                # String preset from SFX panel
                if ps_val and ps_val != "off":
                    preset_filter = AUDIO_EFFECTS.get("pitch_shift", {}).get("presets", {}).get(ps_val, "")
                    if preset_filter:
                        filters.append(preset_filter)

            # STAGE 4: Spatial/echo effects
            for effect_name in ["reverb", "cave"]:
                if effect_name in effect_settings and effect_settings[effect_name] != "off":
                    level = effect_settings[effect_name]
                    if effect_name in AUDIO_EFFECTS:
                        effect_filter = AUDIO_EFFECTS[effect_name]["presets"].get(level, "")
                        if effect_filter:
                            filters.append(effect_filter)

            # STAGE 5: Distortion (needs loud signal to clip properly)
            if "distortion" in effect_settings and effect_settings["distortion"] != "off":
                level = effect_settings["distortion"]
                if "distortion" in AUDIO_EFFECTS:
                    effect_filter = AUDIO_EFFECTS["distortion"]["presets"].get(level, "")
                    if effect_filter:
                        filters.append(effect_filter)

            # STAGE 5.5: Inner thoughts filter
            if is_inner_thought:
                filters.append(inner_thoughts_filter)

            # STAGE 7: Soft limiting + final volume adjustment
            safe_volume_percent = min(volume_percent, 100)
            filters.append("alimiter=level=1:attack=1:release=100")

            # STAGE 8: Final volume adjustment
            final_volume = safe_volume_percent / 100.0
            filters.append(f"volume={final_volume}")

            # STAGE 8.5: FMSU — destructive corruption pass
            if effect_settings.get("fmsu", False):
                filters.append(FMSU_FILTER)
                filters.append("alimiter=level=1:attack=7:release=100")

            # STAGE 9: Reverse
            if effect_settings.get("reverse", False):
                filters.append("areverse")

            filter_chain = ",".join(filters)

            # Intercom static noise: uses filter_complex to mix noise into voice
            intercom_level = effect_settings.get("intercom", "off")
            intercom_noise_params = {
                "mild":   (0.08, "anoisesrc=amplitude=0.10:color=brown,highpass=f=300,lowpass=f=3500,acrusher=bits=6:mode=log:aa=0"),
                "medium": (0.20, "anoisesrc=amplitude=0.22:color=brown,highpass=f=200,lowpass=f=3000,acrusher=bits=4:mode=log:aa=0"),
                "strong": (0.28, "anoisesrc=amplitude=0.28:color=brown,highpass=f=150,lowpass=f=2800,acrusher=bits=3:mode=log:aa=0"),
            }.get(intercom_level)

            # OGG: Google TTS can return clips at 44100 or 48000 Hz depending on
            # the voice. The concat demuxer fails on mixed sample rates for OGG Vorbis.
            # Force 48000 Hz here so all processed clips are uniform before merging.
            ar_args = ["-ar", "48000"] if output_format == "ogg" else []

            if intercom_noise_params is not None:
                _, noise_filter = intercom_noise_params
                complex_graph = (
                    f"[0:a]{filter_chain},alimiter=level=1:attack=1:release=100[voice];"
                    f"{noise_filter}[noise];"
                    f"[voice][noise]amix=inputs=2:weights=1 1:normalize=0:duration=shortest"
                )
                subprocess.run([
                    "ffmpeg", "-i", str(input_path),
                    "-filter_complex", complex_graph,
                    *ar_args,
                    "-y", str(output_path)
                ], check=True, capture_output=True, text=True,
                    startupinfo=self._get_subprocess_startupinfo())
            else:
                subprocess.run([
                    "ffmpeg", "-i", str(input_path),
                    "-af", filter_chain,
                    *ar_args,
                    "-y", str(output_path)
                ], check=True, capture_output=True, text=True,
                    startupinfo=self._get_subprocess_startupinfo())

            return True, None

        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr if e.stderr else str(e)
            error_msg = (f"Failed to apply audio effects.\n\n"
                         f"FFMPEG Error:\n{stderr_output}\n\n"
                         f"This should not happen with the safety pipeline.\n"
                         f"Please report this error with your effect settings.")
            return False, error_msg
        except FileNotFoundError:
            return False, ("FFMPEG not found in PATH. Please install FFMPEG.\n\n"
                           "You can use: https://reactorcore.itch.io/ffmpeg-to-path-installer")

    def apply_peak_normalize(self, input_path, output_path):
        """
        Peak-normalize an audio file (input → output).

        Two-pass: measure peak via volumedetect, then apply linear gain so the
        loudest sample reaches exactly 0 dBFS. Dynamics are fully preserved.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        import re as _re
        import tempfile
        startupinfo = self._get_subprocess_startupinfo()
        try:
            result = subprocess.run([
                "ffmpeg", "-i", str(input_path),
                "-af", "volumedetect",
                "-f", "null", "-"
            ], capture_output=True, text=True, startupinfo=startupinfo)

            match = _re.search(r"max_volume:\s*([-\d.]+)\s*dB", result.stderr)
            if not match:
                return False, "Peak normalize failed: could not read max_volume from ffmpeg output."

            max_volume_db = float(match.group(1))
            if max_volume_db >= 0.0:
                import shutil
                if str(input_path) != str(output_path):
                    shutil.copy2(str(input_path), str(output_path))
                return True, None

            gain_db = -max_volume_db

            in_place = str(input_path) == str(output_path)
            if in_place:
                suffix = Path(str(output_path)).suffix or ".mp3"
                fd, tmp_path = tempfile.mkstemp(suffix=suffix)
                os.close(fd)
                actual_output = tmp_path
            else:
                actual_output = str(output_path)

            try:
                subprocess.run([
                    "ffmpeg", "-i", str(input_path),
                    "-af", f"volume={gain_db}dB",
                    "-y", actual_output
                ], check=True, capture_output=True, text=True, startupinfo=startupinfo)

                if in_place:
                    os.replace(tmp_path, str(output_path))
            except subprocess.CalledProcessError:
                if in_place:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
                raise

            return True, None

        except subprocess.CalledProcessError as e:
            return False, f"Peak normalize failed: {e.stderr}"
        except FileNotFoundError:
            return False, ("FFMPEG not found in PATH. Please install FFMPEG.\n\n"
                           "You can use: https://reactorcore.itch.io/ffmpeg-to-path-installer")
