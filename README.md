# Script to Voice Generator - Google TTS

Welcome to any script writing author out there!

Convert formatted script files into fully voiced audio using **Google Cloud Text-to-Speech** (Chirp 3 HD and other voice families like Neural2, WaveNet and Standard), with per-character voice settings, audio effects, and smart merged output.

Google Cloud provides 1 million free characters per month, so you can generate roughly 18 to 22 hours of audio content - for free. The exact duration depends on the average word length and the speaking rate of the voice.

**Get it here:** https://reactorcore.itch.io/script-to-voice-generator-googletts

**Made by Reactorcore** — https://linktr.ee/reactorcore

---



## What It Does

Script to Voice Generator reads a formatted `.txt` or `.md` script file and:

- Converts each dialogue line to speech using Google Cloud TTS (Chirp 3 HD and other voices).
- Saves individual clips for each line — both clean (TTS only) and effects-processed.
- Merges all clips into a single audio file, with smart pauses based on punctuation.
- Produces both a raw merge and a loudness-normalized merge.
- Generates a reference sheet listing every clip filename and its spoken text.

Multiple speakers are supported. Each speaker gets their own voice, pitch, speed,
and audio effects settings, stored in `character_profiles.json` so they're remembered
between sessions.

---

## What You Need

**Google Cloud credentials** — Required to use the TTS API.

You'll need a Google Cloud account with billing enabled, and a service account JSON key file.
The setup takes about 10 minutes — follow the step-by-step guide included with the app:

**`!docs/guides/Google_Cloud_Setup_Guide.md`**

That guide covers account creation, enabling the API, creating a service account, and downloading
the `.json` key file. It also calls out the confusing dead ends in Google's console so you don't
waste time on them.

On first launch the app will prompt you for the credentials file automatically.
You can also set it at any time in **Tab 4 (Settings) → Credentials**.

**FFMPEG** — Required for audio effects and merging.

- Automatic installer (recommended): https://reactorcore.itch.io/ffmpeg-to-path-installer
- Manual install: https://ffmpeg.org/download.html — add to system PATH after installing.

**Python 3.x** — Required to run from source (not needed if using the compiled .exe).
Use `build_exe.bat` to build to a single .exe in one click.

---

## Quick Start

### 1. Write or prepare a script file

Scripts are `.txt` or `.md` files. Each spoken line uses the format:

```
SpeakerID: Dialogue text goes here.
```

Example:

```
# My Short Film

Alex: Hey, are you okay?
Jordan: Yeah, I'm fine. [sighs] Just tired.
(1.0s)
Alex: You sure? You look pale.
Jordan: I said I'm fine.
```

See **Script Format** below for full syntax details.

### 2. Load the script (Tab 1)

1. Launch the program and click **Open Script File**.
2. The parser checks for formatting errors and lists them in the log.
3. Fix any errors in your text editor and click **Reload Script**.
4. When the parse log shows no errors, click **Continue →**.

### 3. Configure voices (Tab 2)

Each detected speaker gets a panel with:

- **Voice** — Choose from Google Cloud TTS voices (Chirp 3 HD, Neural2, WaveNet, Standard).
  Chirp 3 HD is recommended for highest quality. Use the filter checkbox to show only English voices.
- **Pitch** — Semitone slider (-10.0 to +10.0). Note: API pitch is silently ignored
  for Chirp 3 HD — use the **Pitch Shift** FFMPEG effect instead.
- **Speed** — Speaking rate from 0.25× to 2.0× (full Google API range).
- **Level** — 5–100% relative volume. 100% = full normalized output (default). Reduce to make a speaker quieter in the mix.
- **Yell Impact** — Slows down single-word exclamatory lines (e.g. WOW!). Makes such lines sound more emphasized and impactful.
- **Audio Effects** — Radio, Reverb, Distortion, Telephone, Robot Voice, Cheap Mic,
  Underwater, Megaphone, Worn Tape, Intercom, Alien Voice, Cave, and **Pitch Shift**.
  Most effects have Off / Mild / Medium / Strong levels.

Use **Test Voice** to generate a quick preview clip and hear the settings immediately.

Settings auto-save to `character_profiles.json` on every change, so known speakers
are recalled automatically next session.

### 4. Generate (Tab 3)

1. Enter a **Project Name** (used as a filename prefix, 20 chars max).
2. Choose an **Output Folder**.
3. Click **Generate All** and confirm.

The generation log shows progress. When done, all files appear in the output folder:

```
output_folder/
├── clips_clean/          ← Raw TTS clips (no FFMPEG effects)
│   └── project_0001_Speaker_line-text.mp3 (or .ogg)
├── clips_effect/         ← Effects-processed clips
│   └── project_0001_Speaker_line-text.mp3 (or .ogg)
├── !project_merged_pure.mp3        ← Merged audio, no normalization (or .ogg)
├── !project_merged_loudnorm.mp3    ← Merged audio, loudness-normalized (or .ogg)
└── project_reference.txt           ← Line-by-line reference sheet
```

---

## Script Format

### Dialogue lines

```
SpeakerID: Spoken text goes here.
```

- SpeakerID must be 20 characters or fewer. Allowed: letters, numbers, spaces, hyphens, underscores.
- All text after the first colon is spoken. Additional colons in the line are fine.
- Lines over 500 characters throw a parse error.

### Headings

```
# Scene title
## Sub-scene
```

Treated as metadata. Sets the script title. Not voiced.

### Comments

```
// This is a comment
/* Multi-line
   comment */
```

Not voiced. Useful for stage directions, notes, or commented-out listener responses.

### Pauses

```
(1.5s)
(pause 2.0)
(0.8)
```

Any line that is only parentheses containing a number inserts a silent pause in the
merged audio. The number is in seconds.

### Sound effects

```
{play filename.mp3, c1, loop}
{stop c1}
{stop all}
{play explosion.wav, once}
```

Sound effect events are placed in the merge timeline at the correct position.
Sound effect files must exist in the SFX folder specified in Tab 2.

**Note:** If a sound effect is the very last item in your script, it needs a pause after it to actually be heard in the merged audio.
Add a `(pause)` line equal to or longer than the sound effect's duration immediately after the `{play}` line. Without it, the base audio ends at the same moment the SFX starts, and the SFX gets cut off.

Like this:

```
Rei: Signing off.
{play cloth.wav, c1, once}
(2.0s)
```

**Supported formats** — Any audio format FFMPEG can read: `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`, `.m4a`, and others.
The filename in your script must match the actual file exactly (including extension).

**File size and length** — No enforced limit. FFMPEG loads each SFX file into the mix at its playback position.
Very large or very long SFX files will increase merge time and output file size, but will not cause errors on their own.
Loop-mode SFX (`loop`) are automatically trimmed at the matching `{stop}` event, so file length only matters for `once` mode plays.

### Inline notation

- [brackets] on a dialogue line are stripped before TTS — use for performance notes,
  sound effect cues, or character direction for human voice actors.
- **bold** text becomes `<emphasis level="strong">` in SSML — Google TTS applies stronger stress.
- _italic_ text becomes `<emphasis level="moderate">` in SSML — Google TTS applies moderate stress.
- ~~strikethrough~~ is stripped before TTS.
- // after dialogue text starts an inline comment; everything after it is stripped.

---

## Settings Tab (Tab 4)

**Google API** — Set credentials path and monitor monthly character usage.
Google provides 1,000,000 free characters/month for Chirp 3 HD and other premium voices.
The usage counter is tracked locally by this app — Google does not expose a characters-used figure
anywhere in the Cloud Console. If you hit the free quota, generation will fail with a quota error
in the generation log. To cross-check indirectly: Google Cloud → Billing → Reports, group by SKU,
filter by Text-to-Speech API — character totals may appear there after a ~24 hour lag.
Note: new Google Cloud accounts start on a Free Trial and are not charged for overages until
you manually upgrade to a paid account.

**Output Format** — Choose between MP3 (default) and OGG Opus. Both are ~32 kbps and use the
same free tier quota (Google charges by character count, not format). OGG offers slightly better
perceptual quality at the same file size. Use MP3 if you need broad compatibility (some game engines
or video editors don't support OGG); use OGG if your target software supports it (Unity, Godot,
Audacity, VLC, etc.). Takes effect on the next generation or Test Voice.

**Silence Trim** — Controls how leading/trailing silence is removed from each TTS clip.
Default: trim beginning and end. Options: Off, Beginning only, End only, Beginning + End, All silence.

**Merged Audio Pauses** — Adjust the pause duration added after each punctuation type
(period, comma, exclamation, question, hyphen, ellipsis, etc.).

**Contextual Modifiers** — Fine-tune how pause lengths are modified by context:
speaker changes, short lines, long lines, inner thought padding, etc.

**Inner Thoughts Effect** — Choose from Whisper, Dreamlike, Dissociated presets
or configure custom highpass/lowpass/echo parameters for the inner thought audio filter.

---

## Audio Effects Reference

| Effect | Description |
|--------|-------------|
| Radio Filter | Walkie-talkie / comms radio effect. Bandpass + phaser + compression. |
| Reverb | Spatial depth. Configurable echo chains. |
| Distortion | Aggressive, gritty clipping and bit crushing. |
| Telephone | Lo-fi compressed sound. Narrow bandpass + bit crushing. |
| Robot Voice | Ring modulator for mechanical / robotic character. |
| Cheap Mic | Degraded quality, poor recording simulation. |
| Underwater | Muffled, wet, submerged sound. Lowpass + flanger. |
| Megaphone | Projected bullhorn. Treble-boosted, punchy, bandpassed. |
| Worn Tape | VHS/cassette degradation. Wow-flutter, lo-fi analog warble. |
| Intercom | Hallway speaker box. Flat, compressed, confined. Adds crackling static noise. |
| Alien Voice | Non-human vocal quality. Three variants: Insectoid, Dimensional, Warble. |
| Cave | Physical stone space reverb. Three variants: Tunnel, Cave, Abyss. |
| Pitch Shift | FFMPEG-based pitch shifting. Works for all voice families including Chirp 3 HD. |

Most effects have Off / Mild / Medium / Strong presets. Alien, Cave, and Pitch Shift use named variants instead. Effects are combinable.

---

## Tips

- **Chirp 3 HD voices** produce the highest quality output. Look for voices with `Chirp3-HD`
  in the name (e.g. `en-US-Chirp3-HD-Charon`).

- **Pitch for Chirp 3 HD**: The API pitch slider has no effect on Chirp 3 HD voices
  (Google silently ignores it). Use the **Pitch Shift** effect instead — it works
  for all voice families via FFMPEG.

- **Bold and italic** in your script text become SSML emphasis tags, which can make
  Google TTS stress key words more naturally.

- **Test each voice** before generating everything. The Test Voice button in Tab 2
  saves a preview clip and opens it immediately.

- **Cheap Mic** at Mild is a subtle effect that adds a hint of realism to otherwise
  very clean TTS voices. Worth trying as a default.

- **Prompt templates** — The `!docs/prompt_templates/` folder has templates for using AI
  chatbots to write scripts or generate voice line banks. Open them in any text editor.

---

## Included Docs (`!docs/`)

### Guides

| File | Contents |
|------|----------|
| `!docs/guides/Script_Writing_Guide.md` | Writing for TTS, pacing with punctuation and pauses, using effects as character design, AI-assisted workflow |
| `!docs/guides/Audio_Effects_Guide.md` | Full reference for all effects, preset levels, FFMPEG pipeline, Yell Impact, troubleshooting |

### Example Scripts

Ready-to-load `.md` script files — open any of them in Tab 1 to see the format in action.

| File | What it demonstrates |
|------|----------------------|
| `example_tiny.md` | Minimal 2-line script |
| `example_small.md` | Short 2-character scene with SFX, pause, and comments |
| `example_full_drama.md` | Full multi-character drama with SFX channels, inner thoughts, and scene structure |
| `example_monologue.md` | Single narrator, no character interaction |
| `example_meditation.md` | Atmospheric piece with long pauses and inner thought lines |
| `example_oneliners.md` | Voice bank format — one character, many independent lines by category |
| `example_game_scenes.md` | Multi-scene game dialogue with tactical characters, SFX, and inner thoughts |

### Prompt Templates

Fill-in-the-blank prompts for generating scripts with an AI chatbot. Copy, fill in characters/scenario, paste to a chatbot, save the output as a `.md` file, load in Tab 1.

| File | Use case |
|------|----------|
| `cohesive_script.md` | Continuous scene — characters talk to each other |
| `separate_voice_lines.md` | Voice bank — independent lines per category |
| `game_scene_pack.md` | Single game scene with character roles, SFX, and inner thoughts |
| `narrator_monologue.md` | Single narrator — story, documentary, speech, essay |
| `podcast_interview.md` | Two-person host/guest conversation |
| `ambient_narration.md` | Slow, atmospheric, mood-driven spoken word |

---

## Troubleshooting

**Credentials not set** — On first launch, use the credentials popup to browse to your
Google service account JSON key file. Or set it in Tab 4 (Settings) at any time.

**FFMPEG not found** — Install FFMPEG and make sure it is in your system PATH.
Use the automatic installer at https://reactorcore.itch.io/ffmpeg-to-path-installer
then restart the program.

**Parse errors on load** — The parse log in Tab 1 lists every error with line numbers.
Fix them in your text editor and click Reload Script.

**Voice too quiet** — The post-effects normalization pass ensures consistent loudness.
If a speaker still sounds quiet relative to others, their Level slider may be below 100%.

**Missing voice lines in output** — Check the generation log in Tab 3 for per-line
errors. A missing voice assignment or an FFMPEG issue on a specific line will be noted.

**Test Voice not opening** — The file is saved to `output_test/` in the program folder.
Open it manually if the auto-open fails.

**Pitch slider has no effect (Chirp 3 HD)** — This is expected. Google's API ignores
the pitch parameter for Chirp 3 HD voices. Use the Pitch Shift FFMPEG effect in Tab 2 instead.

---

## Credits

- **Google Cloud Text-to-Speech** — TTS engine (Chirp 3 HD and other voice families)
- **ttkbootstrap** — Modern themed tkinter UI
- **FFMPEG** — Audio processing and merging
- **Script to Voice Generator** — By Reactorcore

---

## Links

Check out everything else I do:
https://linktr.ee/reactorcore
