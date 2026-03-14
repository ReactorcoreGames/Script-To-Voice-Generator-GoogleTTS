# Narrator Monologue Template

Use this when you want a **single speaker delivering a continuous piece** — narration,
a story read-aloud, an introduction, a documentary-style voice, an essay, a speech.
No character interaction. The speaker's voice carries the whole piece.

**Tips:**
- The more distinctive the narrator's personality and speaking style, the more
  interesting the output. A dry, understated narrator reads very differently from a
  warm, intimate one.
- Monologues benefit from varied sentence rhythm — mix short punchy statements with
  longer flowing ones. Ask the AI to do this intentionally.
- Explicit pauses `(1.5)` are useful in monologues — place them at emotional beats,
  transitions, or moments of reflection. You can add them after generating.
- Inner thoughts `((like this))` work well in monologues for a character who is partly
  narrating and partly thinking aloud — two registers in one voice.
- Keep the piece focused. A single strong idea or emotional arc works better than
  trying to cover too much ground.

---
<!-- Everything below this line is the prompt. Select from the next line downward. -->

I need you to write a monologue for a single narrator. This will be synthesized
by a text-to-speech voice, so it must read naturally when spoken aloud.

---

**MY NARRATOR:**
[Describe who is speaking: their identity, personality, speaking style, emotional
state, and any relevant context. The more specific, the better.
Example: "A retired astronaut, late 60s, speaking plainly and without sentimentality.
Occasionally dry humour. Doesn't dramatize things — lets facts carry the weight."]

**SUBJECT / THEME:**
[What is the narrator talking about? What is the emotional arc or point of the piece?
Example: "The night they almost didn't make it back. Told from a distance of 30 years.
Starts matter-of-fact, ends with something the narrator has never said out loud before."]

**LENGTH:**
[Roughly how many lines or words, or describe the intended duration when spoken aloud.
A typical speaking pace is 120–150 words per minute.]

---

**FORMAT RULES:**

Write every spoken line as:
```
NarratorID: Spoken text.
```

Use the same NarratorID consistently throughout. No spaces in the ID (use underscores
if needed), 20 characters maximum.

- One spoken thought per line. Do not wrap a single continuous speech across multiple
  lines unless it is genuinely a new thought or beat.
- Keep individual lines under 500 characters.
- End every line with a period, question mark, or exclamation mark.
- Use `...` for trailing off or uncertainty. Use `--` for a sharp self-interruption.
- For pauses, write `(1.5)` on its own line. The number is seconds. Use them at
  transitions, emotional beats, or moments of silence.
- For inner thoughts (a second, quieter mental register), write:
  `((Thought text in double parentheses.))` on its own line — no speaker ID needed.
- For comments or notes to yourself, write `// Note here` on its own line.
  These are not voiced.

**IMPORTANT — Writing for Google TTS:**

Avoid non-word vocalizations — Google TTS reads them letter by letter:
- Avoid: "hnng", "ugh", "pfft", "tsk", "hmph"
- Use: "huh", "well", "right", "gah", "oh", real words that carry the same feeling

Ellipses `...` produce a natural soft pause in speech. Use them for hesitation or
trailing thought. `**bold**` adds strong spoken emphasis; `_italic_` adds moderate
emphasis. Use on individual words to stress key moments in the narration.
