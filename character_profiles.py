"""
Character profiles JSON manager for Script to Voice Generator.
Handles loading/saving character_profiles.json.
"""

import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

from config import MAX_SPEAKER_ID_LENGTH, INVALID_FILENAME_CHARS
from data_models import SpeakerProfile

CURRENT_SCHEMA_VERSION = 1


def _get_default_profiles_path():
    """Get default path for character_profiles.json alongside script/executable."""
    import sys
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "character_profiles.json"
    return Path(__file__).parent / "character_profiles.json"


def _is_valid_speaker_id(name):
    """Check if a speaker ID is valid for filenames and JSON keys."""
    if not name or len(name) > MAX_SPEAKER_ID_LENGTH:
        return False
    for ch in name:
        if ch in INVALID_FILENAME_CHARS:
            return False
    return True


def _atomic_write(path, data):
    """Write JSON atomically."""
    dir_path = path.parent
    try:
        fd, tmp_path = tempfile.mkstemp(dir=str(dir_path), suffix=".tmp")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        if path.exists():
            path.unlink()
        os.rename(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


def _now_iso():
    """Get current time as ISO 8601 string."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


class CharacterProfilesManager:
    """Manages the character_profiles.json file."""

    def __init__(self, path=None):
        self.path = Path(path) if path else _get_default_profiles_path()
        self.profiles = {}  # dict of speaker_id -> SpeakerProfile
        self.load()

    def load(self, path=None):
        """Load profiles from disk. Creates empty file if missing/malformed."""
        if path:
            self.path = Path(path)

        if not self.path.exists():
            self.profiles = {}
            self._save()
            return

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            print(f"Warning: character_profiles.json was malformed. Starting fresh.")
            self.profiles = {}
            self._save()
            return

        # Warn if schema is newer
        file_version = data.get("schema_version", 1)
        if file_version > CURRENT_SCHEMA_VERSION:
            print(f"Warning: character_profiles.json schema_version {file_version} "
                  f"is newer than this program knows ({CURRENT_SCHEMA_VERSION}).")

        # Parse profiles, skipping malformed entries
        raw_profiles = data.get("profiles", {})
        self.profiles = {}

        for key, entry in raw_profiles.items():
            if not isinstance(entry, dict):
                continue
            display_name = entry.get("display_name", key)
            # display_name wins if key and display_name diverge
            if not _is_valid_speaker_id(display_name):
                continue
            try:
                profile = SpeakerProfile.from_dict(entry)
                # Ensure display_name is consistent
                profile.display_name = display_name
                self.profiles[display_name] = profile
            except Exception:
                continue

    def _save(self):
        """Save profiles to disk with atomic write."""
        now = _now_iso()

        # Build output dict
        profiles_dict = {}
        for speaker_id, profile in self.profiles.items():
            if not _is_valid_speaker_id(profile.display_name):
                continue
            profiles_dict[profile.display_name] = profile.to_dict()

        data = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "last_updated": now,
            "profiles": profiles_dict,
        }

        _atomic_write(self.path, data)

    def save(self):
        """Public save."""
        self._save()

    def get_profile(self, speaker_id):
        """Get profile for a speaker, or None if not found."""
        return self.profiles.get(speaker_id)

    def get_or_create_profile(self, speaker_id):
        """Get existing profile or create a new one with defaults."""
        if speaker_id in self.profiles:
            profile = self.profiles[speaker_id]
            profile.last_seen = _now_iso()
            return profile

        profile = SpeakerProfile(
            display_name=speaker_id,
            last_seen=_now_iso(),
        )
        self.profiles[speaker_id] = profile
        self._save()
        return profile

    def update_profile(self, speaker_id, profile):
        """Update a profile and save immediately."""
        profile.last_seen = _now_iso()
        self.profiles[speaker_id] = profile
        self._save()

    def ensure_speakers(self, speaker_ids):
        """
        Ensure all given speaker IDs have profiles.
        Creates new entries for unknown speakers.
        Returns dict of speaker_id -> SpeakerProfile.
        """
        result = {}
        changed = False
        for sid in speaker_ids:
            if sid in self.profiles:
                self.profiles[sid].last_seen = _now_iso()
                result[sid] = self.profiles[sid]
            else:
                profile = SpeakerProfile(
                    display_name=sid,
                    last_seen=_now_iso(),
                )
                self.profiles[sid] = profile
                result[sid] = profile
                changed = True

        if changed:
            self._save()
        return result

    def open_in_editor(self):
        """Open the profiles JSON file in the system default editor."""
        import subprocess
        import sys
        import platform

        try:
            if platform.system() == "Windows":
                os.startfile(str(self.path))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(self.path)])
            else:
                subprocess.run(["xdg-open", str(self.path)])
        except Exception as e:
            print(f"Could not open profiles file: {e}")
