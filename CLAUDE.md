# CLAUDE.md — Script to Voice Generator

A GUI desktop app that converts formatted script files into fully voiced audio using Google Cloud Text-to-Speech (Chirp 3 HD primary). Written in Python with tkinter/ttkbootstrap. Made by Reactorcore.

---

## Running the app

```
python app.py
```

Requirements: `pip install -r requirements.txt` (ttkbootstrap, google-cloud-texttospeech, google-auth). FFMPEG must be on system PATH.

Build to exe: `build_exe.bat` (uses PyInstaller).

---

## File structure

| File | Purpose |
|------|---------|
| `app.py` | Entry point — calls `gui.main()` |
| `gui.py` | `ScriptToVoiceGUI` class + `main()`. Assembles GUI from mixin classes |
| `gui_tab1.py` | Tab 1 builder — script loading, parse log |
| `gui_tab2.py` | Tab 2 builder — per-speaker voice/effect panels, SFX section |
| `gui_tab3.py` | Tab 3 builder — generation summary, project name, output folder |
| `gui_tab4.py` | Tab 4 builder — Google API settings, silence trim, pause settings, contextual modifiers, inner thoughts |
| `gui_handlers.py` | Button click handlers (open script, reload, continue, help, credentials popup, etc.) |
| `gui_generation.py` | `GenerationMixin` — background generation thread, progress, cancel |
| `gui_theme.py` | ttkbootstrap theme application helpers |
| `script_parser.py` | Parses `.txt`/`.md` script files into `ParseResult` |
| `audio_generator.py` | Google Cloud TTS calls, SSML builder, FFMPEG audio effect chains, yell impact |
| `audio_merger.py` | Merges clips into final audio with smart punctuation-based pauses |
| `file_manager.py` | Filename builders, folder creation |
| `reference_writer.py` | Writes `project_reference.txt` — speaker profiles, line list, generation summary |
| `character_profiles.py` | Load/save/update `character_profiles.json` |
| `config_manager.py` | Load/save/validate `config.json`, pause values, inner thoughts filter, usage tracking, silence trim |
| `config.py` | Constants: theme colors, effect filter chains, Google TTS constants, defaults |
| `data_models.py` | Dataclasses: `ParsedLine`, `SpeakerProfile`, `ParseResult`, etc. |

### Persistent data files (auto-created on first launch)

- `config.json` — UI state, pause durations, contextual modifiers, inner thoughts settings, Google API credentials path, character usage counter, silence trim settings
- `character_profiles.json` — Per-speaker voice/effect profiles, auto-saved on every change

### Output structure

```
output_folder/
├── clips_clean/       ← Raw TTS clips (no effects) — .mp3 or .ogg
├── clips_effect/      ← Effects-processed mp3s
├── sfx/               ← FFMPEG-processed SFX copies (mp3, only created when effects are active)
├── !project_merged_pure.mp3
├── !project_merged_loudnorm.mp3
└── project_reference.txt
```

### Other folders

- `output_test/` — Test voice preview clips (written by Test Voice button in Tab 2)
- `!dev/` — Planning documents and implementation decisions log

### `!docs/` folder

User-facing documentation and resources, organized into three subfolders:

**`!docs/guides/`** — In-depth guides shipped with the app:

| File | Contents |
|------|----------|
| `Script_Writing_Guide.md` | How to write scripts that work well with TTS: pacing with punctuation and pauses, using effects as character design, sound channels, inner thoughts, SSML emphasis, and AI-assisted script writing workflow |
| `Audio_Effects_Guide.md` | Full reference for all effects (Radio, Reverb, Distortion, Telephone, Robot Voice, Cheap Mic, Pitch Shift, and more): what each preset level sounds like, recommended character type combinations, the FFMPEG processing pipeline order, Yell Impact explained, troubleshooting |
| `Google_Cloud_Setup_Guide.md` | Step-by-step Google Cloud setup: create project, enable billing, enable Cloud TTS API, create service account, download JSON key. Includes dead-end warnings (deprecated demo page, Vertex AI API keys), free tier table, and troubleshooting. |

**`!docs/example_scripts/`** — Ready-to-load `.md` script files demonstrating different use cases. Each is a working script the user can open in Tab 1 immediately:

| File | What it demonstrates |
|------|----------------------|
| `example_tiny.md` | Minimal 2-line script — the simplest possible valid format |
| `example_small.md` | Short 2-character scene with SFX, pause, and comment usage |
| `example_full_drama.md` | Full multi-character drama with SFX channels, inner thoughts, pauses, and scene structure |
| `example_monologue.md` | Single narrator delivering a sustained piece — no character interaction |
| `example_meditation.md` | Atmospheric/ambient piece with long pauses and inner thought lines |
| `example_oneliners.md` | Voice bank format — one character, many independent lines grouped by category |
| `example_game_scenes.md` | Multi-scene game dialogue with tactical characters, SFX, and inner thoughts |

**`!docs/prompt_templates/`** — AI prompt templates for generating scripts with a language model. Each file contains a fill-in-the-blank prompt and usage tips. Copy the template, fill in characters/scenario, paste to an AI chatbot, paste the output into a `.md` file, load in Tab 1:

| File | Use case |
|------|----------|
| `cohesive_script.md` | Continuous scene — characters talk to each other, story flows start to finish |
| `separate_voice_lines.md` | Voice bank / clip batch — independent lines per category (idle, combat, etc.) |
| `game_scene_pack.md` | Single complete game scene with distinct character roles, SFX placeholders, and inner thoughts |
| `narrator_monologue.md` | Single narrator delivering narration, story, documentary voice, speech, or essay |
| `podcast_interview.md` | Two-person conversation — host/guest format, spontaneous feel |
| `ambient_narration.md` | Slow, atmospheric, mood-driven piece — audio poem, meditation, dreamlike spoken word |

---

## Architecture

`ScriptToVoiceGUI` inherits from five mixin classes:

```
ScriptToVoiceGUI(Tab1Builder, Tab2Builder, Tab2StateMixin, Tab3Builder, Tab4Builder, GUIHandlers, GenerationMixin)
```

The GUI class holds all shared state (tkinter vars, config_manager, char_profiles, parse_result, etc.).

### Tab flow

1. **Tab 1 — Load Script**: User picks a `.txt`/`.md` file → `script_parser.py` parses it → errors shown in log → `Continue →` advances to Tab 2
2. **Tab 2 — Voice Settings**: Dynamic speaker panels (one per detected speaker ID). Voice list loads synchronously in a background thread. Auto-saves to `character_profiles.json` on every change.
3. **Tab 3 — Generate**: User sets project name + output folder → clicks Generate All → background thread runs the full pipeline
4. **Tab 4 — Settings**: Google API credentials + usage tracker, silence trim, pause durations, contextual modifiers, inner thoughts effect presets

### Generation pipeline

1. `script_parser.py` → `ParseResult` (list of `ParsedLine` objects)
2. Per dialogue line: `audio_generator.py` → SSML build → Google Cloud TTS → raw mp3 → FFMPEG effects → `clips_clean/` and `clips_effect/`
3. `audio_merger.py` → stitch clips with silence segments → `merged_pure.mp3` + `merged_loudnorm.mp3`
4. `reference_writer.py` → write `reference.txt`

### Thread safety

Generation runs in `threading.Thread(daemon=True)`. All UI updates from the thread go through `root.after(0, callback)`. Generation settings are gathered into a plain dict on the main thread before the thread starts — the background thread never touches tkinter vars directly.

---

## Script format (key rules)

- Dialogue: `SpeakerID: Text` — speaker IDs max 20 chars, alphanumeric + spaces/hyphens/underscores
- Headings: `#` or `##` — not voiced, first `#` sets title
- Comments: `//` (inline or full line), `/* ... */` (multi-line)
- Pauses: `(1.5s)` or `(pause 2.0)` — any float in parens
- Sound effects: `{play filename.mp3, c1, loop}` / `{stop c1}` / `{stop all}`
- `[brackets]` in dialogue are stripped before TTS
- `//` after dialogue text starts inline comment (stripped)
- `**bold**` → SSML `<emphasis level="strong">`, `_italic_` → `<emphasis level="moderate">`
- `~~strikethrough~~` stripped before TTS

---

## Key constants (config.py)

- `MAX_SPEAKER_ID_LENGTH = 20`
- `MAX_PROJECT_NAME_LENGTH = 20`
- `MAX_LINE_CHARACTERS = 500`
- `DEFAULT_VOICE = "en-US-Chirp3-HD-Charon"`
- `DEFAULT_VOLUME_PERCENT = 100`
- `GOOGLE_TTS_SPEAKING_RATE_MIN = 0.25`, `GOOGLE_TTS_SPEAKING_RATE_MAX = 2.0`
- `GOOGLE_TTS_PITCH_SEMITONES_MIN = -10.0`, `GOOGLE_TTS_PITCH_SEMITONES_MAX = 10.0`
- `GOOGLE_TTS_NO_API_PITCH_FAMILIES = {"chirp3_hd"}` — pitch=0.0 passed for these (Chirp 3 HD ignores API pitch; use FFMPEG pitch_shift instead)
- Chirp HD and Studio voices are filtered out of the voice list in `load_voices()` — Chirp HD is an obsolete Preview family superseded by Chirp 3 HD; Studio is prohibitively expensive
- `GOOGLE_TTS_FREE_TIER_CHARS = 1_000_000` — monthly free tier limit
- `OUTPUT_FORMAT_DEFAULT = "mp3"` — default TTS output encoding; `"ogg"` selects `AudioEncoding.OGG_OPUS`
- Audio effects: `radio`, `reverb`, `distortion`, `telephone`, `robot_voice`, `cheap_mic`, `underwater`, `megaphone`, `worn_tape`, `intercom`, `alien`, `cave`, `pitch_shift` — most have `off/mild/medium/strong` presets; `pitch_shift` uses named semitone variants
- Boolean toggles: `fmsu` (brutal digital corruption), `reverse` (flip clip end-to-end) — on/off only, no levels
- Inner thoughts presets: `Whisper`, `Dreamlike`, `Dissociated`, `Custom`

---

## Key behaviors to know

- **Voice family detection**: `get_voice_family()` in `audio_generator.py`. Check order matters — `"Chirp3-HD"` before `"Chirp-HD"` (substring collision). Returns `chirp3_hd`, `chirp_hd`, `neural2`, `wavenet`, `studio`, or `standard`. Note: `chirp_hd` and `studio` are filtered out in `load_voices()` and never shown to users.
- **API pitch**: Chirp 3 HD → `pitch=0.0` passed to API (silently ignored). Users use the Pitch Shift FFMPEG effect for real pitch control.
- **SSML**: `build_ssml()` in `audio_generator.py` XML-escapes text, converts `**bold**`/`_italic_` to emphasis tags, wraps in `<speak>`. Called for every TTS request.
- **Character usage tracking**: Local counter in `config.json["usage"]`. `increment_char_usage(n)` called with `len(ssml_text)` on successful TTS. Monthly reset at midnight PT on 1st of month. Tab 3 compact display + Tab 4 full display with "Set usage" field.
- **Output format**: `config.json["output_format"]` — `"mp3"` (default) or `"ogg"`. Controlled via Tab 4 radio buttons. Affects the `AudioEncoding` sent to Google TTS, all clip file extensions (`.mp3`/`.ogg`), silence files in the merger, and the merged output filenames. Free tier cost is identical for both formats.
- **Silence trim**: Configurable per-clip trim. Default: `"beginning_end"`. Config in `config.json["silence_trim"]`. Surfaced in Tab 4 (mode radio buttons only — no threshold slider). Start trim uses `silenceremove` at fixed -80 dB. End trim uses `areverse → silenceremove → areverse` to avoid the `stop_periods` streaming bug that prematurely cuts expressive voice tails. The "all" mode additionally applies `stop_periods=-1` for mid-clip silence removal.
- **Yell Impact**: Applied only when the entire spoken text is a single word with `!` in trailing punctuation (e.g. `YES!`, `NO?!`). Formula: `yell_rate = max(0.25, min(2.0, speaking_rate * (1.0 + yell_impact/100.0)))`. Slider range 0 to -80.
- **Volume (Level slider)**: Range 5%–100%, step 5. 100% = full normalized output. Capped at 100 in the pipeline (`min(volume_percent, 100)`). Alimiter always fires before the final volume multiply.
- **Cheap Mic default**: New speakers default to `cheap_mic = "mild"` (subtle realism effect).
- **Inner thoughts**: Lines where `is_inner_thought=True` (parser-detected) get an extra FFMPEG filter stage (Stage 5.5) from `config_manager.get_inner_thoughts_filter()`.
- **Clip filenames**: `[project]_[linenum]_[speaker]_[content].mp3`, total max 70 chars.
- **Merged filenames**: `![project]_merged_[variant].mp3` (leading `!` puts them at top of folder listing).
- **Cancel**: Cooperative — sets `_gen_cancel_requested = True`, checked between clips. Current clip always completes.
- **Voice loading**: Synchronous call in a background `threading.Thread`. Speaker panels may render before voices finish loading; comboboxes are populated when voices arrive.
- **Credentials popup**: Shown on startup if `google_credentials_path` is not set or file doesn't exist. Also accessible via Tab 4. Uses `filedialog.askopenfilename` for service account JSON.

---

## Docs

- [README.md](README.md) — User-facing quick start guide
- [!docs/guides/Script_Writing_Guide.md](!docs/guides/Script_Writing_Guide.md) — Writing for TTS, pacing, AI workflow
- [!docs/guides/Audio_Effects_Guide.md](!docs/guides/Audio_Effects_Guide.md) — Effects reference, pipeline, troubleshooting
- [!docs/guides/Google_Cloud_Setup_Guide.md](!docs/guides/Google_Cloud_Setup_Guide.md) — Google Cloud project + credentials setup
- [!dev/cannibal_notes.md](!dev/cannibal_notes.md) — Implementation decisions log, organized by dev session/chunk
