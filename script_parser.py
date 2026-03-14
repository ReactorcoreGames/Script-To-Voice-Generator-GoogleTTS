"""
Script file parser for Script to Voice Generator.
Parses .md/.txt script files per the formatting rules in the plan doc.
Returns parsed lines, errors, detected speakers, and sound effect events.
"""

import re
from data_models import ParsedLine, ParseError, PlayCommand, SoundEffectEvent, ParseResult
from config import MAX_SPEAKER_ID_LENGTH, MAX_LINE_CHARACTERS, INVALID_FILENAME_CHARS


def _is_valid_speaker_id(name):
    """Check if speaker ID is valid for filenames and JSON keys."""
    if not name or len(name) > MAX_SPEAKER_ID_LENGTH:
        return False
    for ch in name:
        if ch in INVALID_FILENAME_CHARS:
            return False
    return True


def _check_balanced_brackets(text, line_number):
    """
    Check that (), (()), [], {}, <> are all balanced and properly paired.
    Returns list of ParseError if issues found.
    """
    errors = []
    pairs = {'(': ')', '[': ']', '{': '}', '<': '>'}
    openers = set(pairs.keys())
    closers = set(pairs.values())
    closer_to_opener = {v: k for k, v in pairs.items()}
    stack = []

    for i, ch in enumerate(text):
        if ch in openers:
            stack.append((ch, i))
        elif ch in closers:
            expected_opener = closer_to_opener[ch]
            if not stack:
                errors.append(ParseError(
                    line_number,
                    f"Unmatched closing '{ch}' at position {i + 1}.",
                    text
                ))
            elif stack[-1][0] != expected_opener:
                errors.append(ParseError(
                    line_number,
                    f"Mismatched bracket: expected closing for '{stack[-1][0]}' "
                    f"but found '{ch}' at position {i + 1}.",
                    text
                ))
                stack.pop()
            else:
                stack.pop()

    for opener, pos in stack:
        errors.append(ParseError(
            line_number,
            f"Unmatched opening '{opener}' at position {pos + 1}.",
            text
        ))

    return errors


def _parse_pause_line(text, line_number):
    """
    Try to parse a standalone pause line like (pause 1.0s), (1.5), (2.0s), etc.
    Returns (duration_float, error) or (None, None) if not a pause line.
    """
    stripped = text.strip()
    # Must be entirely wrapped in parentheses
    if not stripped.startswith('(') or not stripped.endswith(')'):
        return None, None

    inner = stripped[1:-1].strip()
    if not inner:
        return None, None

    # Extract all float-like numbers from the inner content
    float_pattern = r'\d+\.?\d*'
    numbers = re.findall(float_pattern, inner)

    if len(numbers) == 0:
        return None, None
    if len(numbers) > 1:
        return None, ParseError(
            line_number,
            f"Pause has multiple numeric values: {stripped}. Use only one number.",
            text
        )

    try:
        duration = float(numbers[0])
    except ValueError:
        return None, ParseError(
            line_number,
            f"Invalid pause value in: {stripped}",
            text
        )

    if duration > 9999:
        return None, ParseError(
            line_number,
            f"Pause duration {duration}s exceeds maximum of 9999 seconds.",
            text
        )

    return duration, None


def _parse_play_command(text, line_number):
    """
    Parse a {play ...} or {stop ...} command line.
    Returns (PlayCommand, error) or (None, None) if not a command.
    """
    stripped = text.strip()
    if not stripped.startswith('{') or not stripped.endswith('}'):
        return None, None

    inner = stripped[1:-1].strip()
    if not inner:
        return None, None

    lower = inner.lower()

    # {stop ...}
    if lower.startswith('stop'):
        rest = inner[4:].strip()
        channel = "all"
        if rest:
            # e.g. "c1", "all"
            channel = rest.lower()
        return PlayCommand(
            command="stop",
            channel=channel,
            line_number=line_number,
        ), None

    # {play filename.ext, c1, once/loop}
    if lower.startswith('play'):
        rest = inner[4:].strip()
        if not rest:
            return None, ParseError(
                line_number,
                "Empty {play} command - specify a filename.",
                text
            )

        parts = [p.strip() for p in rest.split(',')]
        filename = parts[0]
        channel = "c1"
        mode = "once"

        for part in parts[1:]:
            p = part.lower()
            if p.startswith('c') and p[1:].isdigit():
                channel = p
            elif p in ("once", "loop"):
                mode = p

        return PlayCommand(
            command="play",
            filename=filename,
            channel=channel,
            mode=mode,
            line_number=line_number,
        ), None

    return None, None


def _strip_brackets(text):
    """Remove [bracketed] content from text (for TTS). Returns cleaned text."""
    return re.sub(r'\[.*?\]', '', text).strip()


def _strip_markdown(text):
    """Remove markdown bold/italic markers for TTS."""
    text = text.replace('**', '')
    text = text.replace('_', '')
    return text


def _strip_inline_comments(text):
    """
    Strip inline comments from after dialogue text.
    Handles // and /* ... */ that appear after spoken content.

    // is only treated as a comment marker when preceded by whitespace,
    so embedded // (e.g. in URLs like https://example.com) are preserved.
    """
    # Single-line comment after dialogue
    # Require whitespace before // so URLs are not stripped
    m = re.search(r'\s//', text)
    if m:
        text = text[:m.start()].strip()

    return text


def _check_inner_thought_mixing(raw_dialogue, line_number, original_line):
    """
    Check if a line improperly mixes inner thoughts ((...)) with regular dialogue.
    Returns ParseError if mixing detected, None otherwise.
    """
    stripped = raw_dialogue.strip()
    if '((' not in stripped:
        return None

    # Check if the ENTIRE dialogue is wrapped in (( ))
    if stripped.startswith('((') and stripped.endswith('))'):
        # Count nesting to make sure the whole thing is one (()) block
        depth = 0
        is_whole = True
        for i, ch in enumerate(stripped):
            if stripped[i:i+2] == '((':
                depth += 1
            elif stripped[i:i+2] == '))':
                depth -= 1
                if depth == 0 and i + 2 < len(stripped):
                    is_whole = False
                    break
        if is_whole:
            return None  # Valid: entire line is inner thought

    # Has (( but not entirely wrapped - mixing detected
    return ParseError(
        line_number,
        "Cannot mix inner thoughts (( )) with regular dialogue on the same line. "
        "Put inner thoughts on a separate line.",
        original_line
    )


def parse_script(filepath):
    """
    Parse a script file and return a ParseResult.

    Args:
        filepath: Path to the .md or .txt script file.

    Returns:
        ParseResult with parsed lines, errors, speakers, sound effects, etc.
    """
    result = ParseResult()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()
    except OSError as e:
        result.errors.append(ParseError(0, f"Could not read file: {e}"))
        return result

    in_multiline_comment = False
    speakers_seen = []  # Ordered unique list
    speakers_set = set()
    sound_effects = {}  # filename -> SoundEffectEvent
    dialogue_count = 0

    for line_idx, raw_line in enumerate(raw_lines, start=1):
        original = raw_line.rstrip('\n\r')
        stripped = original.strip()

        # --- Blank lines ---
        if not stripped:
            result.lines.append(ParsedLine(
                line_number=line_idx,
                line_type="blank",
                original_line=original,
            ))
            continue

        # --- Multiline comment tracking ---
        if in_multiline_comment:
            if '*/' in stripped:
                in_multiline_comment = False
            result.lines.append(ParsedLine(
                line_number=line_idx,
                line_type="comment",
                original_line=original,
            ))
            continue

        if stripped.startswith('/*'):
            in_multiline_comment = True
            if '*/' in stripped[2:]:
                in_multiline_comment = False
            result.lines.append(ParsedLine(
                line_number=line_idx,
                line_type="comment",
                original_line=original,
            ))
            continue

        # --- Single-line comments ---
        if stripped.startswith('//') or stripped.startswith('#'):
            # Headings (# or ##) are treated as comments but we extract title
            if stripped.startswith('#') and not stripped.startswith('##'):
                title_text = stripped.lstrip('#').strip()
                if not result.title and title_text:
                    result.title = title_text
            result.lines.append(ParsedLine(
                line_number=line_idx,
                line_type="comment" if stripped.startswith('//') else "heading",
                original_line=original,
            ))
            continue

        # --- Standalone pause lines ---
        pause_duration, pause_error = _parse_pause_line(stripped, line_idx)
        if pause_error:
            result.errors.append(pause_error)
            continue
        if pause_duration is not None:
            result.lines.append(ParsedLine(
                line_number=line_idx,
                line_type="pause",
                pause_duration=pause_duration,
                original_line=original,
            ))
            continue

        # --- Play/stop commands ---
        play_cmd, play_error = _parse_play_command(stripped, line_idx)
        if play_error:
            result.errors.append(play_error)
            continue
        if play_cmd is not None:
            result.lines.append(ParsedLine(
                line_number=line_idx,
                line_type="play_command",
                play_command=play_cmd,
                original_line=original,
            ))
            # Track sound effect files
            if play_cmd.command == "play" and play_cmd.filename:
                fn = play_cmd.filename
                if fn not in sound_effects:
                    sound_effects[fn] = SoundEffectEvent(filename=fn)
                sound_effects[fn].line_numbers.append(line_idx)
            continue

        # --- Heading lines (## sub scene) ---
        if stripped.startswith('##'):
            result.lines.append(ParsedLine(
                line_number=line_idx,
                line_type="heading",
                original_line=original,
            ))
            continue

        # --- Dialogue lines (must have a colon) ---
        colon_pos = stripped.find(':')
        if colon_pos == -1:
            result.errors.append(ParseError(
                line_idx,
                "Line has text but no colon (:). Every non-blank, non-comment, "
                "non-pause, non-command line must be in 'SpeakerID: dialogue' format.",
                original
            ))
            continue

        speaker_id = stripped[:colon_pos].strip()
        raw_dialogue = stripped[colon_pos + 1:]

        # Validate speaker ID
        if not speaker_id:
            result.errors.append(ParseError(
                line_idx,
                "Empty speaker ID before the colon.",
                original
            ))
            continue

        if len(speaker_id) > MAX_SPEAKER_ID_LENGTH:
            result.errors.append(ParseError(
                line_idx,
                f"Speaker ID '{speaker_id}' exceeds {MAX_SPEAKER_ID_LENGTH} character limit "
                f"({len(speaker_id)} chars).",
                original
            ))
            continue

        if not _is_valid_speaker_id(speaker_id):
            bad_chars = [ch for ch in speaker_id if ch in INVALID_FILENAME_CHARS]
            result.errors.append(ParseError(
                line_idx,
                f"Speaker ID '{speaker_id}' contains invalid characters: "
                f"{', '.join(repr(c) for c in bad_chars)}. "
                f"Use only letters, numbers, spaces, hyphens, and underscores.",
                original
            ))
            continue

        # Track unique speakers in order
        if speaker_id not in speakers_set:
            speakers_set.add(speaker_id)
            speakers_seen.append(speaker_id)

        # Strip inline comments from dialogue
        dialogue_text = _strip_inline_comments(raw_dialogue)

        # Check bracket balance on the dialogue portion
        bracket_errors = _check_balanced_brackets(dialogue_text, line_idx)
        if bracket_errors:
            result.errors.extend(bracket_errors)
            continue

        # Check for inner thought mixing
        mix_error = _check_inner_thought_mixing(dialogue_text, line_idx, original)
        if mix_error:
            result.errors.append(mix_error)
            continue

        # Detect inner thought
        is_inner_thought = False
        tts_text = dialogue_text.strip()
        if tts_text.startswith('((') and tts_text.endswith('))'):
            is_inner_thought = True
            tts_text = tts_text[2:-2].strip()

        # Strip [brackets] (sound effect / performance notes)
        tts_text = _strip_brackets(tts_text)

        # Note: **bold** and _italic_ markdown markers are intentionally preserved here.
        # build_ssml() in audio_generator.py converts them to SSML <emphasis> tags.

        # Clean up whitespace
        tts_text = ' '.join(tts_text.split())

        # Check line length (spoken content)
        if len(tts_text) > MAX_LINE_CHARACTERS:
            result.errors.append(ParseError(
                line_idx,
                f"Spoken line is {len(tts_text)} characters, exceeding the "
                f"{MAX_LINE_CHARACTERS} character limit. Split into multiple lines.",
                original
            ))
            continue

        # Check for parentheses in dialogue that aren't inner thoughts
        # (single parens in dialogue need a valid float for pause, or they're an error)
        if not is_inner_thought:
            # Find single-paren groups in the dialogue
            single_paren_matches = re.finditer(r'\(([^()]*)\)', dialogue_text)
            for m in single_paren_matches:
                inner = m.group(1).strip()
                # Check if it looks like an inline pause
                numbers = re.findall(r'\d+\.?\d*', inner)
                if numbers:
                    # Has numbers - could be inline pause notation
                    # For now just warn; inline pauses in dialogue aren't supported
                    pass  # Allow it - might be regular text with numbers in parens

        dialogue_count += 1
        result.lines.append(ParsedLine(
            line_number=line_idx,
            line_type="dialogue",
            speaker_id=speaker_id,
            spoken_text=tts_text,
            raw_text=raw_dialogue.strip(),
            is_inner_thought=is_inner_thought,
            original_line=original,
        ))

    # Check if we ended inside a multiline comment
    if in_multiline_comment:
        result.errors.append(ParseError(
            len(raw_lines),
            "File ends inside an unclosed /* multiline comment */.",
            ""
        ))

    result.speakers = speakers_seen
    result.sound_effects = list(sound_effects.values())
    result.total_dialogue_lines = dialogue_count

    return result
