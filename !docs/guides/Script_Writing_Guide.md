# Script Writing Guide — Script to Voice Generator

This document is about thinking. Not the syntax rules (see the example scripts for
those) and not the button-by-button workflow (see the app's tooltips for that) — but
how to approach writing a script that comes alive when synthesized, and how to think
about the tools available to you.

---

## What a script file actually is

A script is a plain text file with a `.md` (Markdown) extension. Each spoken line
follows the pattern `SpeakerID: Dialogue text.` — one line per speech. Everything else
is structure: pauses, comments, stage directions, sound commands.

The `.md` extension is deliberate. Open your script in **Notepad++** (or any editor
with Markdown syntax highlighting) and the file becomes far easier to read and edit at
a glance — speaker IDs, comments, and pause markers all render in distinct colours.
It's worth setting up if you plan to write longer scripts.

The parser is forgiving about whitespace, blank lines between dialogue, and scene
headers. Use them freely to visually organize your work.

---

## Building blocks at a glance

```
SpeakerID: Spoken dialogue text.           ← a voiced line
((Inner thought spoken quietly.))          ← inner thought line (special audio effect)
(1.5)                                      ← pause in seconds
// This is a comment, not voiced.          ← inline or block comment
/* Multi-line
   comment block. */
[performance note on a line]               ← silently ignored by the parser
## Scene Header                            ← ignored, just for your organization
{play music.mp3, c1, loop}                 ← start a sound on a channel
{play hit.wav, c2, once}                   ← play a one-shot sound effect
{stop c1}                                  ← stop a channel
```

Inner thoughts use `(( double parentheses ))` and are voiced with a distinct filtering
effect configured in Tab 4. They're perfect for a character's unspoken reflection in
the middle of a scene. Tab 4 offers three named presets — **Dissociated** (cold,
detached, the default), **Whisper** (muffled and claustrophobically close), and
**Dreamlike** (warm, dissolving echoes) — plus a **Custom** mode with manual
controls. See the Audio Effects Guide for the full Inner Thoughts reference.

---

## Pacing and silence

Silence is not dead air — it's part of the performance.

The merged audio output automatically inserts silence after each voiced line based on
its ending punctuation. These durations are set in Tab 4's **Merged Audio Pauses**
section and give you a starting palette:

| Ending | Feel | Starting gap |
|--------|------|--------------|
| `.` | Statement, moves on | 0.6s |
| `,` | Quick cut, mid-thought | 0.3s |
| `?` | Question hangs in the air | 1.5s |
| `!` | Exclamation, energy | 1.0s |
| `...` | Trailing off, uncertainty | 1.3s |
| `-` | Interrupted, cut off | 0.1s |
| `!!` / `?!` | Shock, urgency | 1.5s |
| `?!?` | Paralysing shock | 1.8s |

Use these intentionally. A question that gets answered immediately feels different
from one that gets answered after a beat. An interruption with `-` snaps shut.
Trailing off with `...` lingers.

Behind the scenes, the individual raw text-to-speech clips produced by the generator come with some random default silence before and after, but those are removed by the program automatically, so the actual clips the program works with start immediately and end immediately.

A side effect of this silence removal is that any interior silence within a clip — such as the natural breath between two sentences in a single line — may also be shortened or removed. This is a limitation of how the underlying audio tool handles silence trimming: it cannot distinguish between padding silence at the edges and intentional mid-clip pauses. As a result, a line like `Bob: Who does she think I am? Deaf?` may have its inter-sentence gap compressed in the effects-processed version.

**For this reason, write one sentence per line.** Instead of putting two questions on the same line, split them:

```
Bob: Who does she think I am?
Bob: Deaf?
```

This gives you full control over the pause between them via Tab 4's punctuation gaps, contextual modifiers, or an explicit `(1.0s)` pause inserted between the two lines. Splitting lines is almost always the better approach — it also gives you more meaningful clip filenames and finer control over pacing throughout the script.

Thus if every Tab 4 value were set to zero, the lines would run together with no breath
between them at all. That's why the program has this automatic pause insertion system via Tab 4.

The Tab 4's controls are designed to be your primary pacing tool — adjust the sliders freely per script rather than treating the defaults as fixed for every script.

**Adjust Tab 4 per script.** Fast action dialogue benefits from tighter punctuation
gaps across the board — try pulling periods down to 0.3s and questions to 0.55s or lower.
A slow dramatic scene or monologue often sounds better with the defaults left alone
or even slightly widened. Neither section is set-and-forget; they're tuning dials for
each piece you make. You might find one setup that works for you best and thats fine too - it's a matter of taste.

**Tab 4's Contextual Modifiers** give you further automatic adjustments on top of
the base punctuation gaps:

- **Speaker change** — adds extra silence at every speaker transition. Tune this up
  for a more theatrical, spaced feel; down for rapid-fire exchanges.
- **Same speaker reduction** — tightens the gap when the same character continues
  speaking across consecutive lines, keeping monologue runs from feeling padded.
- **Short line** — adds a small bonus after very short lines. Short punchy lines
  can otherwise feel rushed past; this gives them room to land.
- **Long line** — reduces the gap slightly after long lines, which already carry
  their own natural trailing space from the sentence structure.
- **Inner thought padding** — adds extra silence before and after inner thought
  lines, isolating them from the surrounding dialogue so they feel clearly internal.

These modifiers stack on top of the punctuation gap, not instead of it. The speaker
change and same speaker reduction values are the first dials to reach for when a
conversation feels either breathless or sluggish overall.

For pauses you want to place exactly, write `(1.5)` on its own line in the script.
Use explicit pauses for moments the automatic system can't infer from punctuation:
- A breath before someone says something difficult
- A moment of silence after a revelation
- Comedic timing — the beat before a punchline lands
- Atmosphere — dead quiet before a sound effect hits

Explicit pauses are an escape hatch for the unusual. For most scripts, getting Tab 4
dialled in is faster and more consistent than scattering manual pauses everywhere.

---

## Writing for the voice engine

Google Cloud TTS (Chirp 3 HD in particular) reads natural prose with high quality,
but there are still quirks worth knowing.

**Punctuation shapes delivery more than you'd expect.** Commas create micro-pauses
mid-sentence. Em-dashes (`--`) produce a sharp cut. Ellipses produce a soft trail.
Experiment: the same sentence with different punctuation can feel nervous, deliberate,
or hesitant.

**Non-word vocalizations are read letter by letter.** "Grr" becomes "gee arr arr".
"Hmph" becomes "aitch em pee aitch". Use real words instead:

| Avoid | Use instead |
|-------|-------------|
| ugh, hnng | oh, gah, nope, ouch |
| grr, argh | bah, "oh come on", "seriously" |
| tsk, pfft | "right", "sure", "yeah okay" |
| hmph | "fine", "whatever", "as if" |

**Bold and italic add emphasis.** `**bold**` becomes `<emphasis level="strong">` and
`_italic_` becomes `<emphasis level="moderate">` in the SSML sent to Google TTS.
This can make the engine stress a word more naturally. Use them on individual words or
short phrases for expressive delivery. Strikethrough (`~~text~~`) is stripped silently.

**Short punchy lines hit harder than long ones.** TTS voices naturally rush through
dense text. A short line — even a single word — carries weight when it's alone.

---

## Voices, pitch, speed, and volume

Every speaker in Tab 2 gets their own voice settings. Think of these as character
design tools, not just technical adjustments.

**Voice selection** is the biggest lever. Google Cloud TTS offers many voice families.
**Chirp 3 HD** (names like `en-US-Chirp3-HD-Charon`) is the highest-quality option and
the recommended default. Spend time auditioning voices with the "Test Voice" button
before committing. A voice that already has the right base character needs far less
processing than one you're trying to bend into shape.

**Voice model reference** — All voice families differ in quality, consistency, and what controls work:

| Family | Quality | Output | API Pitch |
|--------|---------|--------|-----------|
| Chirp 3 HD | Highest | Varies each generation* | Ignored — use Pitch Shift effect |
| Neural2 | Very good | Deterministic | Works |
| WaveNet | Good | Deterministic | Works |
| Standard | Basic | Deterministic | Works |

\*The variation in Chirp 3 HD output is intentional — Google designed this model to produce
slightly different prosody each call for a more natural, human feel. There is no seed parameter in
the Google TTS API. If you need exactly repeatable output, use Neural2 or WaveNet instead.

**Pitch (semitone slider)** — The slider runs from -10 to +10 semitones. For most
voice families (Neural2, WaveNet, Standard), this controls the API-level pitch. For
Chirp 3 HD, Google silently ignores the API pitch parameter —
use the **Pitch Shift** FFMPEG effect instead. It works for all voice families. A few
semitones of downward shift gives a voice weight and authority; upward shift lifts it
for younger or more energetic characters.

**Speed** (0.25× to 2.0×) affects how rushed or deliberate a character feels. 1.0 is
natural. A nervous character who speaks slightly fast (1.15×) reads very differently
from a slow, deliberate one (0.85×) — even with the same voice.

**Volume** (5–100%, default 100%) sets a speaker's output level relative to full
normalized output. Reducing a speaker below 100% makes them quieter relative to
others in the mix — useful for background characters, distant voices, or
subordinate roles.

**Yell Impact** makes single-word exclamatory lines (`YES!`, `NO?!`) slow down for a
more deliberate, punchy delivery. Set it per speaker — useful for aggressive characters
who regularly shout single words. See the Audio Effects Guide for full details.

---

## Audio effects as character identity

Effects in Tab 2 are not polish — they're character design. A few approaches:

**Match the effect to the fiction.** A character speaking over a radio should have
Radio enabled. A ghost or disembodied presence suits Reverb Strong. A robot is Robot
Voice. A phone call is Telephone. When the effect is diegetically motivated, it feels
right immediately.

**Use effects for contrast.** If everyone is dry and clean, one character with subtle
Reverb stands out as larger-than-life. If most characters have Radio, one without
sounds like they're standing right next to you.

**Stack carefully.** The pipeline applies effects in a fixed order. Two or three
moderate effects tend to work better than everything at maximum. Distortion + Reverb
gives dominating presence. Robot Voice + Distortion gives a corrupted machine. Robot
Voice + Reverb gives something massive and synthetic. See the Audio Effects Guide for
the full combinations reference.

**FMSU and Reverse** are boolean toggles (no preset levels). FMSU applies brutal
digital bit-crushing as a final destructive stage — good for glitched, corrupted, or
horror voices. Reverse flips the processed clip end-to-end. Both are in Tab 2 per
speaker alongside the levelled effects.

**Cheap Mic (Mild) is on by default** for all speakers. This is intentional — it takes
the "AI-perfect digital" edge off TTS voices and makes them feel more like a real
recording. Turn it off if you want a deliberately clean, studio-quality sound.

---

## Sound effects, music, and atmosphere

Sound channels are one of the most expressive tools in the program. The script controls
them with three commands:

```
{play filename.mp3, c1, loop}    ← start looping on channel 1
{play filename.wav, c2, once}    ← play once on channel 2
{stop c1}                        ← stop channel 1
```

Your SFX folder (set in Tab 2) is where the program looks for these files.

**How to think about channels:**
- Use `c1` for the background layer — ambient sound, music, atmosphere that runs under
  the whole scene. Loop it.
- Use `c2` (and `c3`, etc.) for punctual events — a door slam, a gunshot, a phone
  ringing. Play once.
- Stop channels at scene transitions or when the fiction changes location.

**Pauses and sound work together.** A `{play thunder.wav, c2, once}` followed by a
`(1.5)` lets the sound effect land before anyone speaks. A `{stop c1}` followed by
`(0.5)` and then dialogue creates sudden silence before a line — very effective for
tense or quiet moments.

**If a sound effect is the last item in your script, add a pause after it.** The
merged audio ends when the base dialogue ends — if a `{play}` is the very last line,
the SFX starts exactly as the base track ends, and gets cut off immediately. A pause
equal to or longer than the SFX duration fixes this:

```
Rei: Signing off.
{play cloth.wav, c1, once}
(2.0s)
```

**Supported formats** — Any format FFMPEG can read: `.mp3`, `.wav`, `.ogg`, `.flac`,
`.aac`, `.m4a`, and others. The filename in your script must match the actual file
exactly, including the extension.

**Loop mode SFX** are automatically trimmed at their matching `{stop}` event, so file
length doesn't matter for looped ambient tracks — only `once` mode files need to be
the right length.

**Music under dialogue** works well at lower volume. If your music file is too loud,
adjust it in your audio editor before using it. The program doesn't control per-channel
volume — level balancing between music and voice happens at the source file level.

---

## Using AI to write scripts

AI language models are excellent script collaborators for this program — but they work
best when you treat the output as a first draft to iterate on, not a finished product.

**The workflow:**
1. Use a template from `prompt_templates/` to write your prompt.
2. Fill in your characters and scenario with as much specificity as you can.
3. Generate, paste the output into a `.md` file, load it in Tab 1.
4. Check the parse log for formatting errors and fix them.
5. Run a test generation — listen to the actual synthesized output.
6. Identify weak lines (flat delivery, awkward phrasing, wrong rhythm) and paste them
   back to the AI asking for alternatives.
7. Repeat until the script sounds right.

**Be specific about character voice.** "A soldier" produces generic lines. "A
burned-out veteran who speaks in clipped sentences, rarely completes a thought, and
deflects everything with dark humour" produces lines with real character.

**Ask for rewrites on specific lines.** TTS reads some phrasings naturally and stumbles
over others. When a line sounds off, the issue is usually sentence rhythm or word
choice — and the AI can rephrase it faster than you can.

**Let the AI handle volume, not quality.** Generating 30 NPC idle lines by hand is
tedious. Getting the AI to produce 30 and then cutting the 10 weakest is fast. Use it
for bulk generation; use your ear for curation.

---

## What can you make with this?

A few starting points to spark ideas:

**Audio dramas and short films.** Write a full scene with multiple characters, set the
voices, add ambient sound and music, generate. The merged output is a complete audio
piece ready to share or drop into a video.

**Game dialogue and cutscenes.** Write scene-by-scene dialogue for a game character.
Generate clips, then use **Advanced Renamer** or similar to batch-rename them to
whatever filenames your game engine expects (`npc_idle_01.wav`, `boss_taunt_03.wav`,
etc.). This workflow scales to hundreds of lines.

**NPC voice packs.** Use the `separate_voice_lines.md` prompt template to generate a
batch of categorized lines (idle, alert, combat, death). Paste them into a script file,
generate, rename the clips. A complete NPC voice pack in an afternoon.

**Narration and audio books.** A single-speaker script with a strong narrating voice
and reverb can produce polished narration for presentations, videos, or listening
experiences.

**Ambient audio experiences.** Combine inner thoughts, long pauses, soft music loops,
and a single whispery voice for something closer to an audio poem or mood piece than a
conventional drama.

**Prototype dialogue for any project.** Before spending money on voice actors, use STVG
to prototype your script and hear how the pacing actually works. Revise the writing
based on what you hear, not just how it reads.

---

## Practical workflow tips

**Do a draft run without effects first.** Disable effects (or set them all to Off) and
generate a fast draft. Listen for pacing, line quality, and parse errors before
committing to a full effects run.

**Use "Test Voice" extensively.** The test button in Tab 2 lets you audition a single
line with all current settings applied. Use it before every full generation. It's much
faster to catch a bad voice setting here than after generating 50 clips.

**Use "Test + Inner Thoughts" when your script uses `(( ))` lines.** The second test
button in Tab 2 runs the same preview with the Tab 4 Inner Thoughts filter stacked on
top. Audition this separately — inner thought lines go through an extra processing
stage that can interact unexpectedly with certain effect combinations.

**Check the parse log after every load.** Tab 1 shows parsing errors immediately.
Fix them before generating — a malformed line produces silence or unexpected output.

**Syntax-highlight your scripts.** Open `.md` files in Notepad++ with Markdown
language mode, or any editor with Markdown support. Speaker IDs, comments, and
structural elements each get distinct colours, making large scripts much easier to
navigate and edit.

**Keep SpeakerIDs short and consistent.** The parser is case-sensitive. `Alex` and
`ALEX` are different speakers. Pick a convention and stick to it across the whole file.

**For large clip banks, plan your naming before you generate.** The program names clips
based on SpeakerID and line order. If you know you'll need specific filenames for a
game or project, either name the SpeakerID to match, or plan your Advanced Renamer
batch rename workflow before you start — it's faster to do once than to reorganize
hundreds of files after the fact.
