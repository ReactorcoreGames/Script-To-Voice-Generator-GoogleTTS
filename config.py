"""
Configuration constants for Script to Voice Generator
"""

# Application settings
APP_TITLE = "Script to Voice Generator - Google TTS"
APP_GEOMETRY = "1100x800"
ICON_FILENAME = "script_to_voice.ico"
MAX_SPEAKER_ID_LENGTH = 20
MAX_PROJECT_NAME_LENGTH = 20
MAX_LINE_CHARACTERS = 500

# Theme colors (Windows 11 dark blue)
APP_THEME = {
    "type": "dark",
    "colors": {
        # Backgrounds
        "bg":        "#1A1E2E",   # deep navy — main window background
        "inputbg":   "#1E2436",   # slightly lighter — entry fields, text widgets
        "selectbg":  "#2A3A5C",   # blue-tinted selection highlight

        # Text
        "fg":        "#E8EDF5",   # cool off-white — default text
        "selectfg":  "#FFFFFF",   # pure white — selected text
        "inputfg":   "#D8E4F8",   # slightly blue-tinted — input field text

        # Interactive / brand
        "primary":   "#0078D4",   # Windows 11 accent blue — main buttons
        "secondary": "#005A9E",   # darker blue — secondary buttons
        "success":   "#107C10",   # Windows 11 green — generate button
        "info":      "#0078D4",   # same as primary
        "warning":   "#C19A00",   # muted amber — warning states
        "danger":    "#C42B1C",   # Windows 11 red — error states

        # Decorative
        "border":    "#2D3A52",   # cool dark blue-gray — borders, separators
        "active":    "#1A8FE3",   # brighter blue — hover/active state
        "accent":    "#60CDFF",   # light sky blue — header labels, highlights
    }
}

# Default merged audio pause values (seconds, 0.0 to 9.9)
MERGED_AUDIO_PAUSE_DEFAULTS = {
    "period": 0.6,
    "comma": 0.3,
    "exclamation": 1.0,
    "question": 1.5,
    "hyphen": 0.1,
    "ellipsis": 1.3,
    "double_power": 1.5,
    "triple_power": 1.8,
}

# Contextual modifiers for merged audio
CONTEXTUAL_MODIFIER_DEFAULTS = {
    "speaker_change_bonus": 0.3,
    "short_line_threshold_chars": 20,
    "short_line_reduction_s": 0.2,
    "long_line_threshold_chars": 200,
    "long_line_addition_s": 0.3,
    "inner_thought_padding_s": 0.4,
    "same_speaker_reduction_s": 0.2,
    "first_line_padding_s": 0.5,
    "last_line_padding_s": 1.0,
}

# Default UI persistence values
UI_DEFAULTS = {
    "default_profiles_path": "",
    "last_output_folder": "",
    "last_script_folder": "",
    "last_sfx_folder": "",
    "show_all_tts_languages": False,
    "last_project_name": "",
    "show_welcome_popup": True,
    "google_credentials_path": "",
    "test_text": "",
}

# Default speaker profile values
DEFAULT_VOICE = "en-US-Chirp3-HD-Charon"
DEFAULT_VOLUME_PERCENT = 100

# Google TTS API constants
GOOGLE_TTS_SPEAKING_RATE_MIN = 0.25
GOOGLE_TTS_SPEAKING_RATE_MAX = 2.0
GOOGLE_TTS_SPEAKING_RATE_DEFAULT = 1.0
GOOGLE_TTS_SPEAKING_RATE_STEP = 0.05
GOOGLE_TTS_PITCH_SEMITONES_MIN = -10.0
GOOGLE_TTS_PITCH_SEMITONES_MAX = 10.0
GOOGLE_TTS_PITCH_SEMITONES_DEFAULT = 0.0
GOOGLE_TTS_PITCH_SEMITONES_STEP = 0.5
# Families that silently ignore API pitch — pass pitch=0.0 to the API call
GOOGLE_TTS_NO_API_PITCH_FAMILIES = {"chirp3_hd"}

# FFMPEG pitch shift slider (per-speaker, all voice families)
FFMPEG_PITCH_SEMITONES_MIN = -12.0
FFMPEG_PITCH_SEMITONES_MAX = 12.0
FFMPEG_PITCH_SEMITONES_DEFAULT = 0.0
FFMPEG_PITCH_SEMITONES_STEP = 0.5

# Monthly free tier for premium voices (Chirp 3 HD, Neural2, etc.)
GOOGLE_TTS_FREE_TIER_CHARS = 1_000_000

# Usage tracking defaults (stored in config.json under "usage" key)
USAGE_DEFAULTS = {
    "chars_sent_this_month": 0,
    "month_key": "",  # "YYYY-MM" string; empty means never set
}

# Output format for TTS audio (stored in config.json under "output_format" key)
# "mp3"  — MP3 at ~32 kbps (Google default, broadest compatibility)
# "ogg"  — OGG Opus at ~32 kbps (better perceptual quality at same bitrate)
OUTPUT_FORMAT_DEFAULT = "mp3"

# Silence trim defaults (stored in config.json under "silence_trim" key)
# Default: "beginning_end" — strips leading and trailing silence, preserves mid-clip pauses
# This is appropriate for Chirp 3 HD which embeds natural breath points.
SILENCE_TRIM_DEFAULTS = {
    "mode": "beginning_end",      # off / beginning / end / beginning_end / all
}

# Audio effect presets (FFMPEG filter chains) - ported from BDVPG
AUDIO_EFFECTS = {
    "radio": {
        "name": "Radio Filter",
        "description": "Walkie-talkie/comms radio effect",
        "presets": {
            "off": "",
            "mild": "highpass=f=700,lowpass=f=2400,aphaser=in_gain=0.9:out_gain=0.9:delay=4:decay=0.7:speed=1.2,acompressor=threshold=0.1:ratio=12:attack=100:release=600,acrusher=bits=12:mode=log:aa=1,volume=1.8",
            "medium": "highpass=f=800,lowpass=f=2200,aphaser=in_gain=0.9:out_gain=0.9:delay=5:decay=0.8:speed=1.5,acompressor=threshold=0.08:ratio=16:attack=80:release=500,acrusher=bits=10:mode=log:aa=1,volume=2.0",
            "strong": "highpass=f=900,lowpass=f=2000,aphaser=in_gain=0.9:out_gain=0.9:delay=5:decay=0.9:speed=2.0,acompressor=threshold=0.06:ratio=20:attack=60:release=400,acrusher=bits=8:mode=log:aa=1,asoftclip=type=sin,volume=2.2",
        },
    },
    "reverb": {
        "name": "Reverb",
        "description": "Spatial depth and power",
        "presets": {
            "off": "",
            "mild": "aecho=0.8:0.88:60:0.4",
            "medium": "aecho=0.8:0.88:60|100:0.4|0.3",
            "strong": "aecho=0.8:0.9:500|1000:0.2|0.1,aecho=0.8:0.88:60|90:0.3|0.25",
        },
    },
    "distortion": {
        "name": "Distortion",
        "description": "Corrupt, overdriven, artifact-heavy — signal damage territory",
        "presets": {
            "off": "",
            "mild": "volume=1.2,asoftclip=type=hard,acrusher=bits=6:mode=log:aa=0,asoftclip=type=hard,acrusher=bits=4:mode=lin:aa=0,volume=0.9",
            "medium": "volume=1.2,asoftclip=type=hard,acrusher=bits=4:mode=log:aa=0,asoftclip=type=hard,acrusher=bits=2:mode=lin:aa=0,volume=0.9",
            "strong": "volume=1.2,asoftclip=type=hard,acrusher=bits=2:mode=log:aa=0,asoftclip=type=hard,acrusher=bits=1:mode=lin:aa=0,volume=0.9",
        },
    },
    "telephone": {
        "name": "Telephone",
        "description": "Lo-fi, compressed, retro",
        "presets": {
            "off": "",
            "mild": "bandpass=f=1400:width_type=h:w=1400,acompressor=threshold=0.2:ratio=8:attack=10:release=100,acrusher=bits=13:mode=log:aa=1",
            "medium": "bandpass=f=1200:width_type=h:w=1100,acompressor=threshold=0.15:ratio=12:attack=5:release=60,acrusher=bits=11:mode=log:aa=1",
            "strong": "bandpass=f=1000:width_type=h:w=900,acompressor=threshold=0.1:ratio=18:attack=2:release=40,acrusher=bits=9:mode=log:aa=1,highpass=f=300,lowpass=f=2800",
        },
    },
    "robot_voice": {
        "name": "Robot Voice",
        "description": "Robotic, mechanical voice",
        "presets": {
            "off": "",
            "mild": "aeval=val(0)*(0.15)+val(0)*sin(2*PI*80*t)*(0.85):c=same,treble=g=4:f=3000,bass=g=-3:f=150,aphaser=in_gain=0.8:out_gain=0.95:delay=2:decay=0.4:speed=0.8",
            "medium": "aeval=val(0)*(0.2)+val(0)*sin(2*PI*40*t)*(0.8):c=same",
            "strong": "aeval=val(0)*(0.1)+val(0)*sin(2*PI*100*t)*(0.9):c=same,alimiter=level_in=1:level_out=1:attack=1:release=50,apad=pad_dur=0.15,aresample=8000,aresample=44100,acrusher=bits=6:mode=log:aa=1,treble=g=6:f=4000",
        },
    },
    "cheap_mic": {
        "name": "Cheap Mic",
        "description": "Degraded quality, poor recording",
        "presets": {
            "off": "",
            "mild": "lowpass=f=3800,aresample=8000,aresample=44100,acrusher=bits=11:mode=log:aa=1,alimiter=level=1:attack=1:release=50,highpass=f=150,lowpass=f=6000",
            "medium": "aresample=5500,aresample=44100,acrusher=bits=9:mode=log:aa=1,highpass=f=200,lowpass=f=5000,acompressor=threshold=0.3:ratio=4:attack=10:release=100",
            "strong": "highpass=f=300,lowpass=f=4000,volume=2.5,asoftclip=type=tanh,aresample=3000,aresample=44100,acrusher=bits=5:mode=log:aa=0,acompressor=threshold=0.15:ratio=12:attack=3:release=40,volume=1.6",
        },
    },
    "underwater": {
        "name": "Underwater",
        "description": "Submerged, muffled, wet — voice heard through water",
        "presets": {
            "off": "",
            "mild": "lowpass=f=1000,flanger=speed=0.3:depth=2:delay=5:width=60",
            "medium": "lowpass=f=600,flanger=speed=0.25:depth=4:delay=7:width=75,volume=0.9",
            "strong": "lowpass=f=350,flanger=speed=0.2:depth=6:delay=9:width=90,acompressor=threshold=0.4:ratio=3:attack=5:release=80,volume=0.8",
        },
    },
    "megaphone": {
        "name": "Megaphone",
        "description": "Projected bullhorn — punchy, bandpassed, no transmission shimmer",
        "presets": {
            "off": "",
            "mild": "treble=g=6:f=3000,asoftclip=type=tanh,treble=g=3:f=6000",
            "medium": "treble=g=8:f=2500,volume=2.0,asoftclip=type=atan:param=2,acrusher=bits=10:mode=log:aa=1,treble=g=4:f=5000",
            "strong": "treble=g=10:f=2000,volume=3.0,asoftclip=type=hard,acrusher=bits=6:mode=log:aa=1,asoftclip=type=tanh,treble=g=5:f=4000",
        },
    },
    "worn_tape": {
        "name": "Worn Tape",
        "description": "VHS/cassette degradation — wow-flutter, lo-fi, analog warble",
        "presets": {
            "off": "",
            "mild": "aresample=11000,aresample=44100,aphaser=in_gain=0.9:out_gain=0.95:delay=4:decay=0.2:speed=0.15,acrusher=bits=14:mode=log:aa=1",
            "medium": "aresample=8000,aresample=44100,aphaser=in_gain=0.85:out_gain=0.9:delay=5:decay=0.3:speed=0.2,acrusher=bits=11:mode=log:aa=1",
            "strong": "aresample=5500,aresample=44100,aphaser=in_gain=0.8:out_gain=0.85:delay=5:decay=0.5:speed=0.25,acrusher=bits=9:mode=log:aa=1,highpass=f=120,lowpass=f=7000",
        },
    },
    "intercom": {
        "name": "Intercom",
        "description": "Hallway speaker box — flat, compressed, confined, no transmission shimmer",
        "presets": {
            "off": "",
            "mild": "highpass=f=300,lowpass=f=3500,acompressor=threshold=0.2:ratio=8:attack=3:release=50,acrusher=bits=11:mode=log:aa=1,asoftclip=type=sin",
            "medium": "highpass=f=500,lowpass=f=3000,acompressor=threshold=0.12:ratio=14:attack=2:release=35,acrusher=bits=9:mode=log:aa=1,asoftclip=type=sin",
            "strong": "highpass=f=700,lowpass=f=2500,acompressor=threshold=0.06:ratio=20:attack=1:release=20,acrusher=bits=7:mode=log:aa=1,asoftclip=type=tanh",
        },
    },
    "alien": {
        "name": "Alien Voice",
        "description": "Non-human vocal quality. Insectoid: chittering arthropod. Dimensional: flickers in/out of existence. Warble: ayylmao alien tongue wobble.",
        "presets": {
            "off": "",
            "insectoid": "aeval=val(0)*(0.2)+val(0)*sin(2*PI*250*t)*(0.8):c=same,treble=g=6:f=5000,highpass=f=200",
            "dimensional": "tremolo=f=7:d=0.7,aphaser=in_gain=0.7:out_gain=0.7:delay=5:decay=0.7:speed=2:type=t,vibrato=f=4:d=0.3",
            "warble": "tremolo=f=6:d=0.5,aeval=val(0)*(0.4)+val(0)*sin(2*PI*20*t)*(0.6):c=same,treble=g=4:f=3500",
        },
    },
    "cave": {
        "name": "Cave",
        "description": "Physical stone spaces. Tunnel: tight single echo. Cave: multi-tap chamber. Abyss: impossibly long decay.",
        "presets": {
            "off": "",
            "tunnel": "aecho=0.8:0.85:120:0.5,highpass=f=80,lowpass=f=8000",
            "cave": "aecho=0.8:0.88:180|350:0.45|0.3,aecho=0.7:0.8:80:0.2",
            "abyss": "aecho=0.8:0.92:600|1200|2000:0.4|0.25|0.12,aecho=0.8:0.85:100|200:0.3|0.2,lowpass=f=6000",
        },
    },
    "pitch_shift": {
        "name": "Pitch Shift",
        "description": "Pitch shift via FFMPEG rubberband — true pitch/tempo independence. Works for all voice families including Chirp 3 HD (which ignores API pitch). ±12 semitones, 0.5 step.",
        # No preset strings — per-speaker pitch_shift is a float slider; filter computed dynamically.
        # SFX panel still uses this entry for radio buttons (off/mild/medium/strong handled via presets below).
        "presets": {
            "off": "",
            "mild":   "rubberband=pitch=0.8909",   # -2 st
            "medium": "rubberband=pitch=0.7937",   # -4 st
            "strong": "rubberband=pitch=1.1225",   # +2 st
        },
    },
}

# Effect preset levels
EFFECT_LEVELS = ["off", "mild", "medium", "strong"]

# Variant preset keys for effects that use named variants instead of intensity levels
ALIEN_VARIANTS = ["off", "insectoid", "dimensional", "warble"]
CAVE_VARIANTS = ["off", "tunnel", "cave", "abyss"]

# FMSU (F*** My Sh** Up) — applied as final destructive stage after all other effects
# Target: harsh digital corruption — artifact territory, waveform folding, coarse crunch.
# volume boost → acrusher at 3 bits (aa=0) for brutal quantization artifacts →
# asoftclip=hard folds the overdriven peaks back (waveform fold-over distortion).
# No resampling — keeps full frequency range so corruption is textural, not muffling.
FMSU_FILTER = "volume=4.0,acrusher=bits=2:mode=log:aa=0,asoftclip=type=hard,acrusher=bits=2:mode=lin:aa=0,asoftclip=type=hard,volume=0.7"

# Inner thoughts effect presets
# Each preset builds an FFMPEG filter string for the inner-thought sound.
# The "Dissociated" preset replaces the old hardcoded INNER_THOUGHTS_FILTER.
INNER_THOUGHTS_PRESETS = {
    "Whisper": {
        "description": "Muffled, stuffy inner voice — occluded, potato-in-mouth quality",
        "highpass": 380,
        "lowpass": 1100,
        "echo_delay_ms": 60,
        "echo_wet": 0.26,
        "reverb": False,
        "volume": 0.92,
    },
    "Dreamlike": {
        "description": "Floaty, distant, spacious — multi-tap echo trails",
        "highpass": 100,
        "lowpass": 3400,
        "echo_delay_ms": 0,        # unused — dreamlike uses custom multi-tap aecho
        "echo_wet": 0.0,
        "reverb": False,
        "dreamlike": True,         # triggers multi-tap echo branch in filter builder
        "volume": 0.90,
    },
    "Dissociated": {
        "description": "Cold, detached, slightly unreal (default)",
        "highpass": 300,
        "lowpass": 3000,
        "echo_delay_ms": 80,
        "echo_wet": 0.2,
        "reverb": False,
        "volume": 0.95,
    },
}

INNER_THOUGHTS_PRESET_NAMES = ["Whisper", "Dreamlike", "Dissociated", "Custom"]
INNER_THOUGHTS_DEFAULT_PRESET = "Dissociated"

# Fallback filter string (used only if config_manager is unavailable)
INNER_THOUGHTS_FILTER = (
    "highpass=f=300,lowpass=f=3000,"
    "aecho=0.6:0.3:80:0.2,"
    "volume=0.95"
)

# Characters invalid in filenames and JSON keys
INVALID_FILENAME_CHARS = set('<>:"/\\|?*')
# Characters allowed in speaker IDs: alphanumeric, spaces, hyphens, underscores
VALID_SPEAKER_ID_PATTERN = r'^[A-Za-z0-9 _\-]+$'
