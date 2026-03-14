"""
Config file manager for Script to Voice Generator.
Handles loading/saving config.json with atomic writes and validation.
"""

import json
import os
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from config import (
    MERGED_AUDIO_PAUSE_DEFAULTS,
    CONTEXTUAL_MODIFIER_DEFAULTS,
    UI_DEFAULTS,
    INNER_THOUGHTS_PRESETS,
    INNER_THOUGHTS_DEFAULT_PRESET,
    USAGE_DEFAULTS,
    SILENCE_TRIM_DEFAULTS,
    OUTPUT_FORMAT_DEFAULT,
)

CURRENT_SCHEMA_VERSION = 1


def _get_config_path():
    """Get path to config.json alongside the script/executable."""
    import sys
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "config.json"
    return Path(__file__).parent / "config.json"


def _build_inner_thoughts_defaults():
    """Build default inner_thoughts config section."""
    return {
        "preset": INNER_THOUGHTS_DEFAULT_PRESET,
        "custom": {
            "highpass": 300,
            "lowpass": 3000,
            "echo_delay_ms": 80,
            "echo_wet": 0.2,
            "volume": 0.95,
        },
    }


def _build_defaults():
    """Build a complete default config dictionary."""
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "merged_audio_pauses": dict(MERGED_AUDIO_PAUSE_DEFAULTS),
        "contextual_modifiers": dict(CONTEXTUAL_MODIFIER_DEFAULTS),
        "ui": dict(UI_DEFAULTS),
        "inner_thoughts": _build_inner_thoughts_defaults(),
        "usage": dict(USAGE_DEFAULTS),
        "silence_trim": dict(SILENCE_TRIM_DEFAULTS),
        "output_format": OUTPUT_FORMAT_DEFAULT,
    }


def _clamp_pause(value, low=0.0, high=9.9):
    """Clamp a pause value to valid range."""
    try:
        v = float(value)
        return max(low, min(high, round(v, 1)))
    except (TypeError, ValueError):
        return low


def _validate_and_fill(config):
    """
    Validate a loaded config dict.
    Fill missing keys with defaults, clamp out-of-range values.
    Returns the corrected config.
    """
    defaults = _build_defaults()

    # Ensure output_format is valid
    if config.get("output_format") not in ("mp3", "ogg"):
        config["output_format"] = OUTPUT_FORMAT_DEFAULT

    # Ensure top-level keys exist
    for section in ("merged_audio_pauses", "contextual_modifiers", "ui", "usage", "silence_trim"):
        if section not in config or not isinstance(config[section], dict):
            config[section] = dict(defaults[section])
        else:
            # Fill missing keys within each section
            for key, default_val in defaults[section].items():
                if key not in config[section]:
                    config[section][key] = default_val

    # Clamp pause values
    for key in MERGED_AUDIO_PAUSE_DEFAULTS:
        config["merged_audio_pauses"][key] = _clamp_pause(
            config["merged_audio_pauses"].get(key, MERGED_AUDIO_PAUSE_DEFAULTS[key])
        )

    # Clamp contextual modifier time values (the ones ending in _s or bonus)
    for key, default_val in CONTEXTUAL_MODIFIER_DEFAULTS.items():
        val = config["contextual_modifiers"].get(key, default_val)
        if isinstance(default_val, float):
            try:
                val = float(val)
                val = max(0.0, min(9.9, round(val, 1)))
            except (TypeError, ValueError):
                val = default_val
        elif isinstance(default_val, int):
            try:
                val = int(val)
                val = max(0, min(9999, val))
            except (TypeError, ValueError):
                val = default_val
        config["contextual_modifiers"][key] = val

    # Validate inner_thoughts section
    it_defaults = _build_inner_thoughts_defaults()
    if "inner_thoughts" not in config or not isinstance(config["inner_thoughts"], dict):
        config["inner_thoughts"] = it_defaults
    else:
        it = config["inner_thoughts"]
        # Ensure preset key is valid
        from config import INNER_THOUGHTS_PRESET_NAMES
        if it.get("preset") not in INNER_THOUGHTS_PRESET_NAMES:
            it["preset"] = INNER_THOUGHTS_DEFAULT_PRESET
        # Ensure custom sub-dict exists and has all keys
        if "custom" not in it or not isinstance(it["custom"], dict):
            it["custom"] = dict(it_defaults["custom"])
        else:
            cust_defaults = it_defaults["custom"]
            for k, v in cust_defaults.items():
                if k not in it["custom"]:
                    it["custom"][k] = v

    # Ensure schema_version
    config.setdefault("schema_version", CURRENT_SCHEMA_VERSION)

    return config


def _atomic_write(path, data):
    """Write JSON atomically: write to temp file then rename."""
    dir_path = path.parent
    try:
        fd, tmp_path = tempfile.mkstemp(dir=str(dir_path), suffix=".tmp")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # On Windows, need to remove target first
        if path.exists():
            path.unlink()
        os.rename(tmp_path, str(path))
    except Exception:
        # Clean up temp file if rename failed
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


class ConfigManager:
    """Manages the config.json file."""

    def __init__(self):
        self.path = _get_config_path()
        self.config = self.load()

    def load(self):
        """Load config from disk. Creates default if missing/malformed."""
        if not self.path.exists():
            config = _build_defaults()
            self._save(config)
            return config

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            config = _build_defaults()
            self._save(config)
            return config

        # Warn if schema is newer than we know
        file_version = config.get("schema_version", 1)
        if file_version > CURRENT_SCHEMA_VERSION:
            print(f"Warning: config.json schema_version {file_version} "
                  f"is newer than this program knows ({CURRENT_SCHEMA_VERSION}).")

        config = _validate_and_fill(config)
        self._save(config)
        return config

    def _save(self, config=None):
        """Save config to disk with atomic write."""
        if config is None:
            config = self.config
        _atomic_write(self.path, config)

    def save(self):
        """Public save - writes current config to disk."""
        self._save(self.config)

    def get_pause(self, key):
        """Get a merged audio pause value."""
        return self.config["merged_audio_pauses"].get(
            key, MERGED_AUDIO_PAUSE_DEFAULTS.get(key, 0.6)
        )

    def set_pause(self, key, value):
        """Set a merged audio pause value and save."""
        self.config["merged_audio_pauses"][key] = _clamp_pause(value)
        self.save()

    def get_modifier(self, key):
        """Get a contextual modifier value."""
        return self.config["contextual_modifiers"].get(
            key, CONTEXTUAL_MODIFIER_DEFAULTS.get(key, 0.0)
        )

    def set_modifier(self, key, value):
        """Set a contextual modifier value and save."""
        self.config["contextual_modifiers"][key] = value
        self.save()

    def get_ui(self, key):
        """Get a UI persistence value."""
        return self.config["ui"].get(key, UI_DEFAULTS.get(key, ""))

    def set_ui(self, key, value):
        """Set a UI persistence value and save."""
        self.config["ui"][key] = value
        self.save()

    def reset_pauses_to_defaults(self):
        """Reset merged_audio_pauses and contextual_modifiers to defaults. Preserves ui."""
        self.config["merged_audio_pauses"] = dict(MERGED_AUDIO_PAUSE_DEFAULTS)
        self.config["contextual_modifiers"] = dict(CONTEXTUAL_MODIFIER_DEFAULTS)
        self.save()

    # ── Inner thoughts ────────────────────────────────────────

    def get_inner_thoughts_preset(self):
        """Get the selected inner thoughts preset name."""
        return self.config.get("inner_thoughts", {}).get(
            "preset", INNER_THOUGHTS_DEFAULT_PRESET
        )

    def set_inner_thoughts_preset(self, preset_name):
        """Set the inner thoughts preset and save."""
        self.config.setdefault("inner_thoughts", _build_inner_thoughts_defaults())
        self.config["inner_thoughts"]["preset"] = preset_name
        self.save()

    def get_inner_thoughts_custom(self):
        """Get the custom inner thoughts parameters dict."""
        it = self.config.get("inner_thoughts", {})
        return dict(it.get("custom", _build_inner_thoughts_defaults()["custom"]))

    def set_inner_thoughts_custom(self, key, value):
        """Set a single custom inner thoughts parameter and save."""
        self.config.setdefault("inner_thoughts", _build_inner_thoughts_defaults())
        self.config["inner_thoughts"].setdefault(
            "custom", dict(_build_inner_thoughts_defaults()["custom"])
        )
        self.config["inner_thoughts"]["custom"][key] = value
        self.save()

    def reset_inner_thoughts_to_defaults(self):
        """Reset inner_thoughts section to defaults."""
        self.config["inner_thoughts"] = _build_inner_thoughts_defaults()
        self.save()

    def get_inner_thoughts_filter(self):
        """
        Build and return the active FFMPEG filter string for inner thoughts.

        Reads the current preset from config. If preset is "Custom", builds
        the filter from the stored custom parameters. Otherwise uses the
        preset definition from INNER_THOUGHTS_PRESETS.
        """
        it = self.config.get("inner_thoughts", {})
        preset_name = it.get("preset", INNER_THOUGHTS_DEFAULT_PRESET)

        if preset_name == "Custom":
            params = dict(it.get("custom", _build_inner_thoughts_defaults()["custom"]))
        elif preset_name in INNER_THOUGHTS_PRESETS:
            p = INNER_THOUGHTS_PRESETS[preset_name]
            params = {
                "highpass": p["highpass"],
                "lowpass": p["lowpass"],
                "echo_delay_ms": p["echo_delay_ms"],
                "echo_wet": p["echo_wet"],
                "volume": p["volume"],
                # "reverb" field only exists on Whisper preset
                "_reverb": p.get("reverb", False),
                # "dreamlike" field only exists on Dreamlike preset
                "_dreamlike": p.get("dreamlike", False),
            }
        else:
            # Fallback to Dissociated
            p = INNER_THOUGHTS_PRESETS["Dissociated"]
            params = {
                "highpass": p["highpass"],
                "lowpass": p["lowpass"],
                "echo_delay_ms": p["echo_delay_ms"],
                "echo_wet": p["echo_wet"],
                "volume": p["volume"],
                "_reverb": False,
            }

        return _build_inner_thoughts_filter(params)

    # ── Usage tracking ────────────────────────────────────────

    def _current_pt_month_key(self) -> str:
        """Return the current month as 'YYYY-MM' in Pacific Time."""
        # Pacific Standard Time is UTC-8; Pacific Daylight Time is UTC-7.
        # We approximate with a fixed UTC-8 offset — close enough for a monthly reset.
        pt_offset = timezone(timedelta(hours=-8))
        now_pt = datetime.now(tz=pt_offset)
        return now_pt.strftime("%Y-%m")

    def _check_month_rollover(self):
        """Reset usage counter if the calendar month has changed (Pacific Time)."""
        current_key = self._current_pt_month_key()
        stored_key = self.config.get("usage", {}).get("month_key", "")
        if stored_key != current_key:
            self.config.setdefault("usage", dict(USAGE_DEFAULTS))
            self.config["usage"]["chars_sent_this_month"] = 0
            self.config["usage"]["month_key"] = current_key
            self.save()

    def get_char_usage(self) -> int:
        """Return characters sent this month, resetting counter if month rolled over."""
        self._check_month_rollover()
        return int(self.config.get("usage", {}).get("chars_sent_this_month", 0))

    def increment_char_usage(self, n: int):
        """Add n to the monthly usage counter, checking for month rollover first."""
        self._check_month_rollover()
        self.config.setdefault("usage", dict(USAGE_DEFAULTS))
        self.config["usage"]["chars_sent_this_month"] = (
            int(self.config["usage"].get("chars_sent_this_month", 0)) + max(0, n)
        )
        self.save()

    def set_char_usage(self, n: int):
        """Explicitly set the usage counter (e.g. to restore from Google Dashboard)."""
        self._check_month_rollover()
        self.config.setdefault("usage", dict(USAGE_DEFAULTS))
        self.config["usage"]["chars_sent_this_month"] = max(0, int(n))
        self.save()

    def get_quota_reset_countdown(self) -> str:
        """
        Return a human-readable string for time until midnight PT on the 1st of next month.
        Example: "18 days, 4 hours, 22 minutes"
        """
        pt_offset = timezone(timedelta(hours=-8))
        now_pt = datetime.now(tz=pt_offset)
        # First day of next month at midnight PT
        if now_pt.month == 12:
            reset_pt = datetime(now_pt.year + 1, 1, 1, tzinfo=pt_offset)
        else:
            reset_pt = datetime(now_pt.year, now_pt.month + 1, 1, tzinfo=pt_offset)
        delta = reset_pt - now_pt
        total_seconds = max(0, int(delta.total_seconds()))
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{days} days, {hours} hours, {minutes} minutes"

    # ── Silence trimming ──────────────────────────────────────

    def get_silence_trim(self, key: str):
        """Get a silence_trim config value."""
        return self.config.get("silence_trim", {}).get(
            key, SILENCE_TRIM_DEFAULTS.get(key)
        )

    def set_silence_trim(self, key: str, value):
        """Set a silence_trim config value and save."""
        self.config.setdefault("silence_trim", dict(SILENCE_TRIM_DEFAULTS))
        self.config["silence_trim"][key] = value
        self.save()

    def reset_silence_trim_to_defaults(self):
        """Reset silence_trim section to defaults."""
        self.config["silence_trim"] = dict(SILENCE_TRIM_DEFAULTS)
        self.save()

    # ── Output format ─────────────────────────────────────────

    def get_output_format(self) -> str:
        """Get the audio output format: 'mp3' or 'ogg'."""
        val = self.config.get("output_format", OUTPUT_FORMAT_DEFAULT)
        return val if val in ("mp3", "ogg") else OUTPUT_FORMAT_DEFAULT

    def set_output_format(self, value: str):
        """Set the audio output format ('mp3' or 'ogg') and save."""
        if value not in ("mp3", "ogg"):
            value = OUTPUT_FORMAT_DEFAULT
        self.config["output_format"] = value
        self.save()


def _build_inner_thoughts_filter(params):
    """
    Build an FFMPEG filter string from inner thoughts parameters.

    params keys:
        highpass (int Hz), lowpass (int Hz), echo_delay_ms (int, 0=off),
        echo_wet (float 0-1), volume (float), _reverb (bool, optional),
        _dreamlike (bool, optional)
    """
    filters = []
    filters.append(f"highpass=f={int(params['highpass'])}")
    filters.append(f"lowpass=f={int(params['lowpass'])}")

    delay_ms = int(params.get("echo_delay_ms", 0))
    reverb = params.get("_reverb", False)
    dreamlike = params.get("_dreamlike", False)

    if dreamlike:
        # Dreamlike preset: multi-tap echo — two trails that dissolve into distance
        filters.append("aecho=0.85:0.7:150|280:0.35|0.2")
    elif reverb:
        # Whisper preset: gentle reverb-style aecho instead of echo
        filters.append("aecho=0.8:0.88:45:0.28")
    elif delay_ms > 0:
        wet = float(params.get("echo_wet", 0.2))
        wet = max(0.0, min(1.0, wet))
        filters.append(f"aecho=0.6:0.3:{delay_ms}:{wet:.2f}")

    vol = float(params.get("volume", 0.75))
    vol = max(0.1, min(2.0, vol))
    filters.append(f"volume={vol:.2f}")

    return ",".join(filters)
