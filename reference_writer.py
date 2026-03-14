"""
reference_writer.py — Generates the session reference sheet written to the output folder.

Called by FileManager.generate_reference_sheet() after every successful generation run.
"""

from datetime import datetime

from config import (
    MERGED_AUDIO_PAUSE_DEFAULTS,
    CONTEXTUAL_MODIFIER_DEFAULTS,
    INNER_THOUGHTS_DEFAULT_PRESET,
)

# Effect abbreviations for the reference sheet
EFFECT_ABBREVS = {
    "radio":       "RAD",
    "reverb":      "RVB",
    "distortion":  "DIST",
    "telephone":   "TEL",
    "robot_voice": "ROBO",
    "cheap_mic":   "CHP",
    "underwater":  "UNDR",
    "megaphone":   "MEGA",
    "worn_tape":   "TAPE",
    "intercom":    "ICOM",
    "alien":       "ALN",
    "cave":        "CAVE",
}

# Pause keys in display order with their short labels
_PAUSE_LABELS = [
    ("period",       "."),
    ("comma",        ","),
    ("exclamation",  "!"),
    ("question",     "?"),
    ("hyphen",       "-"),
    ("ellipsis",     "..."),
    ("double_power", "!?"),
    ("triple_power", "?!?"),
]


def _effects_string(effects: dict) -> str:
    """
    Build the effects display string from a speaker or SFX effects dict.
    Returns '| NONE |' if no effects are active.

    Active means:
    - String effects: value != "off"
    - fmsu / reverse booleans: True
    - pitch_shift float: non-zero
    """
    parts = []

    for key, abbrev in EFFECT_ABBREVS.items():
        val = effects.get(key, "off")
        if val and val != "off":
            parts.append(f"{abbrev}:{val}")

    pitch = effects.get("pitch_shift", 0.0)
    try:
        pitch = float(pitch)
    except (TypeError, ValueError):
        pitch = 0.0
    if pitch != 0.0:
        sign = "+" if pitch >= 0 else ""
        parts.append(f"PS:{sign}{pitch:.1f}st")

    if effects.get("fmsu", False):
        parts.append("FMSU")
    if effects.get("reverse", False):
        parts.append("REV")

    if not parts:
        return "| NONE |"
    return "| " + " | ".join(parts) + " |"


def _format_speaker_block(speaker_id: str, sp: dict) -> list:
    """Return lines for one speaker block in the SPEAKERS section."""
    lines = []
    lines.append(speaker_id)

    voice = sp.get("voice_name", "")
    lines.append(f"  Voice     : | {voice} |")

    api_pitch = sp.get("pitch_semitones", 0.0)
    ffmpeg_pitch = 0.0
    effects = sp.get("effects", {})
    try:
        ffmpeg_pitch = float(effects.get("pitch_shift", 0.0))
    except (TypeError, ValueError):
        ffmpeg_pitch = 0.0

    speed = sp.get("speaking_rate", 1.0)
    volume = sp.get("volume", 100)
    yell = sp.get("yell_impact", 0)

    api_sign = "+" if api_pitch >= 0 else ""
    ff_sign = "+" if ffmpeg_pitch >= 0 else ""

    settings_str = (
        f"| Pitch (API) {api_sign}{api_pitch:.1f} st "
        f"| Pitch (FFMPEG) {ff_sign}{ffmpeg_pitch:.1f} st "
        f"| Speed {speed:.2f}x "
        f"| Level : {volume}% "
        f"| Yell : {yell}% |"
    )
    lines.append(f"  Settings  : {settings_str}")
    lines.append(f"  Effects   : {_effects_string(effects)}")

    return lines


def _format_parameters_section(config_manager, sfx_effects: dict) -> list:
    """Return lines for the PARAMETERS section."""
    lines = []

    # SFX Filters
    lines.append(f"SFX Filters    : {_effects_string(sfx_effects)}")

    # Punctuations — always show all, in order
    pause_parts = []
    for key, label in _PAUSE_LABELS:
        val = config_manager.get_pause(key) if config_manager else MERGED_AUDIO_PAUSE_DEFAULTS[key]
        pause_parts.append(f"{label}  {val:.1f}s")
    lines.append("Punctuations   : | " + " | ".join(pause_parts) + " |")

    # Contextuals — always show all
    def _m(key):
        return config_manager.get_modifier(key) if config_manager else CONTEXTUAL_MODIFIER_DEFAULTS[key]

    ctx_parts = [
        f"Change {_m('speaker_change_bonus'):.1f}s",
        f"Short {int(_m('short_line_threshold_chars'))}/{_m('short_line_reduction_s'):.1f}s",
        f"Long {int(_m('long_line_threshold_chars'))}/{_m('long_line_addition_s'):.1f}s",
        f"Inner {_m('inner_thought_padding_s'):.1f}s",
        f"Same {_m('same_speaker_reduction_s'):.1f}s",
        f"First {_m('first_line_padding_s'):.1f}s",
        f"Last {_m('last_line_padding_s'):.1f}s",
    ]
    lines.append("Contextuals    : | " + " | ".join(ctx_parts) + " |")

    # Inner thoughts preset
    preset = config_manager.get_inner_thoughts_preset() if config_manager else INNER_THOUGHTS_DEFAULT_PRESET
    lines.append(f"Inner thoughts : | {preset} |")

    # Silence trim mode
    trim = config_manager.get_silence_trim("mode") if config_manager else "beginning_end"
    lines.append(f"Silence trim   : | {trim} |")

    return lines


def _format_clip_list(ref_entries: list) -> list:
    """Return lines for the CLIPS section. Two-line format per clip."""
    lines = []
    for entry in ref_entries:
        filename, speaker_id, spoken_text, is_inner_thought = entry
        # Extract line number from filename (second segment, zero-padded 4 digits)
        # Filename format: project_NNNN_speaker_content.ext
        # Fall back to sequential index if parsing fails
        num_str = "????"
        parts = filename.split("_")
        for part in parts:
            if part.isdigit():
                num_str = part.zfill(4)
                break

        speaker_label = speaker_id.upper()
        if is_inner_thought:
            speaker_label += " [IT]"

        lines.append(f"{num_str}. {filename}")
        lines.append(f"      {speaker_label}: {spoken_text}")
        lines.append("")  # blank line between clips

    # Remove trailing blank line
    if lines and lines[-1] == "":
        lines.pop()

    return lines


def write_reference_sheet(
    output_path: str,
    project_name: str,
    output_format: str,
    speaker_settings: dict,
    ref_entries: list,
    config_manager,
    sfx_effects: dict,
    sound_count: int,
) -> None:
    """
    Write the full session reference sheet to output_path.

    Args:
        output_path:      Destination file path.
        project_name:     Project name string.
        output_format:    "mp3" or "ogg".
        speaker_settings: Dict of speaker_id -> settings dict.
        ref_entries:      List of (filename, speaker_id, spoken_text, is_inner_thought).
        config_manager:   ConfigManager instance (may be None).
        sfx_effects:      SFX effects settings dict.
        sound_count:      Number of unique SFX filenames in the script.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    fmt_label = output_format.upper() if output_format else "MP3"
    clip_count = len(ref_entries)
    speaker_ids = list(speaker_settings.keys())
    speaker_list = ", ".join(speaker_ids)

    out = []

    # ── Title ──────────────────────────────────────────────────────────────
    out.append("# SCRIPT TO VOICE GENERATOR - GOOGLE TTS — SESSION REFERENCE")
    out.append("")

    # ── Project line ───────────────────────────────────────────────────────
    sounds_label = f"{sound_count} Sound{'s' if sound_count != 1 else ''}"
    out.append(
        f"Project  : | {project_name} | {timestamp} | {fmt_label} "
        f"| {clip_count} Clips | {sounds_label} |"
    )
    out.append(
        f"Speakers : | {len(speaker_ids)} | {speaker_list} |"
    )

    # ── Speakers section ───────────────────────────────────────────────────
    out.append("")
    out.append("---")
    out.append("")
    out.append("## SPEAKERS")
    out.append("")

    for speaker_id, sp in speaker_settings.items():
        out.extend(_format_speaker_block(speaker_id, sp))
        out.append("")

    # ── Parameters section ─────────────────────────────────────────────────
    out.append("---")
    out.append("")
    out.append("## PARAMETERS")
    out.append("")
    out.extend(_format_parameters_section(config_manager, sfx_effects))

    # ── Clips section ──────────────────────────────────────────────────────
    out.append("")
    out.append("---")
    out.append("")
    out.append(f"## CLIPS")
    out.append("")
    out.extend(_format_clip_list(ref_entries))

    # ── Footer ─────────────────────────────────────────────────────────────
    out.append("")
    out.append("---")
    out.append("")
    out.append("EoF")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
