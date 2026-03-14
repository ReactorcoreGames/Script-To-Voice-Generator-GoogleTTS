"""
File management utilities for Script to Voice Generator.
Handles output directory structure, filename generation, and reference sheets.
Flat-folder output (no PK3 packaging).
"""

import re
import sys
from pathlib import Path

MAX_FILENAME_TOTAL = 70
MAX_COMPONENT_CHARS = 20


def _get_app_dir():
    """Get the application's root directory."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


class FileManager:
    """Handles file operations for Script to Voice Generator"""

    @staticmethod
    def sanitize_filename(text):
        """
        Sanitize text for use in filenames.
        Replaces spaces with hyphens, removes invalid chars.
        """
        if not text:
            return ""
        # Replace spaces/whitespace with hyphens
        result = re.sub(r'\s+', '-', text.strip())
        # Remove invalid filename characters (including straight and curly quotes,
        # which would break ffmpeg concat demuxer single-quoted path entries)
        result = re.sub(r'[<>:"/\\|?*\'\u2018\u2019\u201C\u201D]', '', result)
        # Collapse multiple hyphens
        result = re.sub(r'-{2,}', '-', result)
        # Strip leading/trailing hyphens
        result = result.strip('-')
        return result

    @staticmethod
    def build_clip_filename(project_name, line_number, speaker_id, spoken_text, extension=".mp3"):
        """
        Build filename for an individual voice clip.
        Pattern: [project]_[linenum]_[speaker]_[content].ext
        """
        proj = FileManager.sanitize_filename(project_name)[:MAX_COMPONENT_CHARS]
        speaker = FileManager.sanitize_filename(speaker_id)[:MAX_COMPONENT_CHARS]
        content = FileManager.sanitize_filename(spoken_text.lower())[:MAX_COMPONENT_CHARS]
        linenum = f"{line_number:04d}"

        filename = f"{proj}_{linenum}_{speaker}_{content}{extension}"

        # Enforce total length limit by trimming content
        if len(filename) > MAX_FILENAME_TOTAL:
            overflow = len(filename) - MAX_FILENAME_TOTAL
            content = content[:max(1, len(content) - overflow)]
            filename = f"{proj}_{linenum}_{speaker}_{content}{extension}"

        return filename

    @staticmethod
    def build_merged_filename(project_name, variant="pure", extension=".mp3"):
        """
        Build filename for merged audio.
        Pattern: ![project]_merged_[variant].ext
        """
        proj = FileManager.sanitize_filename(project_name)[:MAX_COMPONENT_CHARS]
        return f"!{proj}_merged_{variant}{extension}"

    @staticmethod
    def get_test_output_dir():
        """Get path to output_test directory (alongside program)."""
        test_dir = _get_app_dir() / "output_test"
        test_dir.mkdir(exist_ok=True)
        return test_dir

    @staticmethod
    def generate_reference_sheet(ref_entries, output_path, project_name="",
                                  output_format="mp3", speaker_settings=None,
                                  config_manager=None, sfx_effects=None,
                                  sound_count=0):
        """
        Generate a session reference sheet .txt file.

        Args:
            ref_entries:      list of (filename, speaker_id, spoken_text, is_inner_thought)
            output_path:      Path for the .txt file
            project_name:     Project name string
            output_format:    "mp3" or "ogg"
            speaker_settings: dict of speaker_id -> settings dict
            config_manager:   ConfigManager instance
            sfx_effects:      SFX effects settings dict
            sound_count:      Number of unique SFX filenames in the script
        """
        from reference_writer import write_reference_sheet
        write_reference_sheet(
            output_path=output_path,
            project_name=project_name,
            output_format=output_format,
            speaker_settings=speaker_settings or {},
            ref_entries=ref_entries,
            config_manager=config_manager,
            sfx_effects=sfx_effects or {},
            sound_count=sound_count,
        )
        return output_path

    @staticmethod
    def scan_sfx_folder(folder_path, required_filenames, search_subfolders=True):
        """
        Scan a folder for sound effect files.

        Args:
            folder_path: Path to the SFX folder
            required_filenames: List of filenames to look for
            search_subfolders: Whether to search recursively

        Returns:
            dict: {filename: found_path_or_None}
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            return {fn: None for fn in required_filenames}

        results = {}
        for fn in required_filenames:
            found_path = None
            if search_subfolders:
                for match in folder.rglob(fn):
                    if match.is_file():
                        found_path = str(match)
                        break
            else:
                candidate = folder / fn
                if candidate.is_file():
                    found_path = str(candidate)

            results[fn] = found_path

        return results
