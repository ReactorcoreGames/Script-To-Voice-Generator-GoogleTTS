# Cohesive Script Template

Use this when you want a **continuous scene** — characters talk to each other, the
dialogue flows from start to finish as a story or performance.

**Tips:**
- Give each character a distinct speaking style — sentence length, vocabulary, and
  rhythm should differ between characters. Ask the AI to avoid having everyone speak
  in the same register.
- After generating, load the file into Tab 1 and check the parse log for formatting
  errors. Fix and reload if needed.
- Test individual voices in Tab 2 with "Test Voice" before running full generation.

---
<!-- Everything below this line is the prompt. Select from the next line downward. -->

I need you to write a script for an audio performance. I will describe the scenario and
characters below. Write the dialogue so it reads naturally when spoken aloud by a
text-to-speech voice.

---

**SCENARIO:**
[Describe the scene, setting, and situation. A short paragraph is enough.]

**CHARACTERS:**
[List each character:
- SpeakerID: Who they are, how they speak, their personality.]

**LENGTH:**
[Roughly how many lines or exchanges, or describe the scene length.]

---

**FORMAT RULES:**

Write every spoken line as:
```
SpeakerID: Dialogue line.
```

- `SpeakerID` must be the same short identifier every time that character speaks.
  No spaces (use underscores if needed), 20 characters maximum.
- One dialogue line per text line. Never wrap a single speech across multiple lines.
- Keep lines under 500 characters each.
- End every line with a period, question mark, or exclamation mark.
- For pauses, write `(1.5)` on its own line. The number is seconds.
- For stage directions or comments, write `// Direction here` on its own line.
  These will not be voiced.
- Text in square brackets on a dialogue line `[like this]` is a performance note —
  silently ignored by the voice generator. Use it for context or future reference.

**IMPORTANT — Writing for Google TTS:**

Google TTS reads non-word vocalizations letter by letter. Use real words instead:
- Avoid: "hnng", "grr", "tsk", "pfft", "hmph", "argh"
- Use: "huh", "nah", "gah", "bah", "oh come on", "right", "fine", "whatever"

Ellipses `...` produce a natural pause. Em-dashes and commas affect pacing naturally.
`**bold**` applies strong emphasis in speech; `_italic_` applies moderate emphasis.
Use them on individual words to stress key moments. Strikethrough is stripped silently.
