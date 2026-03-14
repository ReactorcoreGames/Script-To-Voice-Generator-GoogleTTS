"""
Data models for Script to Voice Generator
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParseError:
    """Represents a parsing error found in the script"""
    line_number: int
    message: str
    line_content: str = ""


@dataclass
class PlayCommand:
    """Represents a {play} or {stop} audio command in the script"""
    command: str  # "play" or "stop"
    filename: str = ""  # e.g. "explosion.mp3"
    channel: str = "c1"  # e.g. "c1", "c2", "all"
    mode: str = "once"  # "once" or "loop"
    line_number: int = 0


@dataclass
class SoundEffectEvent:
    """Tracks a sound effect file referenced in the script"""
    filename: str
    line_numbers: list = field(default_factory=list)
    found: bool = False
    found_path: str = ""
    apply_effects: bool = True


@dataclass
class ParsedLine:
    """Represents a single parsed line from the script"""
    line_number: int
    line_type: str  # "dialogue", "pause", "comment", "play_command", "heading", "blank"
    speaker_id: str = ""
    spoken_text: str = ""  # Text sent to TTS (brackets stripped, etc.)
    raw_text: str = ""  # Original text after colon
    is_inner_thought: bool = False
    pause_duration: float = 0.0  # For pause lines
    play_command: Optional[PlayCommand] = None
    original_line: str = ""  # The entire original line from the file


@dataclass
class SpeakerProfile:
    """Voice and effect settings for a single speaker"""
    display_name: str
    last_seen: str = ""

    # Google TTS settings
    voice: str = "en-US-Chirp3-HD-Charon"
    pitch_semitones: float = 0.0
    speaking_rate: float = 1.0
    yell_impact_percent: int = 0
    volume_percent: int = 100

    # FFMPEG pitch shift (continuous, all voice families)
    pitch_shift_semitones: float = 0.0

    # Audio effects
    radio: str = "off"
    reverb: str = "off"
    distortion: str = "off"
    telephone: str = "off"
    robot_voice: str = "off"
    cheap_mic: str = "mild"
    underwater: str = "off"
    megaphone: str = "off"
    worn_tape: str = "off"
    intercom: str = "off"
    alien: str = "off"
    cave: str = "off"

    # Flags
    fmsu: bool = False
    reverse: bool = False

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "display_name": self.display_name,
            "last_seen": self.last_seen,
            "tts": {
                "voice": self.voice,
                "pitch_semitones": self.pitch_semitones,
                "speaking_rate": self.speaking_rate,
                "yell_impact_percent": self.yell_impact_percent,
                "volume_percent": self.volume_percent,
            },
            "audio_effects": {
                "pitch_shift_semitones": self.pitch_shift_semitones,
                "radio": self.radio,
                "reverb": self.reverb,
                "distortion": self.distortion,
                "telephone": self.telephone,
                "robot_voice": self.robot_voice,
                "cheap_mic": self.cheap_mic,
                "underwater": self.underwater,
                "megaphone": self.megaphone,
                "worn_tape": self.worn_tape,
                "intercom": self.intercom,
                "alien": self.alien,
                "cave": self.cave,
            },
            "flags": {
                "fmsu": self.fmsu,
                "reverse": self.reverse,
            },
        }

    @classmethod
    def from_dict(cls, data):
        """Create SpeakerProfile from dictionary (loaded from JSON)"""
        tts = data.get("tts", {})
        effects = data.get("audio_effects", {})
        flags = data.get("flags", {})

        return cls(
            display_name=data.get("display_name", ""),
            last_seen=data.get("last_seen", ""),
            voice=tts.get("voice", "en-US-Chirp3-HD-Charon"),
            pitch_semitones=float(tts.get("pitch_semitones", 0.0)),
            speaking_rate=float(tts.get("speaking_rate", 1.0)),
            yell_impact_percent=tts.get("yell_impact_percent", 0),
            volume_percent=tts.get("volume_percent") or 100,
            pitch_shift_semitones=float(effects.get("pitch_shift_semitones", 0.0)),
            radio=effects.get("radio", "off"),
            reverb=effects.get("reverb", "off"),
            distortion=effects.get("distortion", "off"),
            telephone=effects.get("telephone", "off"),
            robot_voice=effects.get("robot_voice", "off"),
            cheap_mic=effects.get("cheap_mic", "mild"),
            underwater=effects.get("underwater", "off"),
            megaphone=effects.get("megaphone", "off"),
            worn_tape=effects.get("worn_tape", "off"),
            intercom=effects.get("intercom", "off"),
            alien=effects.get("alien", "off"),
            cave=effects.get("cave", "off"),
            fmsu=flags.get("fmsu", False),
            reverse=flags.get("reverse", False),
        )


@dataclass
class ParseResult:
    """Complete result from parsing a script file"""
    lines: list = field(default_factory=list)  # List[ParsedLine]
    errors: list = field(default_factory=list)  # List[ParseError]
    speakers: list = field(default_factory=list)  # List[str] - unique speaker IDs in order
    sound_effects: list = field(default_factory=list)  # List[SoundEffectEvent]
    total_dialogue_lines: int = 0
    title: str = ""
