# Ambient Narration Template

Use this when you want something **slow, atmospheric, and mood-driven** — more audio
poem than drama. A single voice (or two voices in loose alternation) with long pauses,
deliberate imagery, and a piece that exists to create a feeling rather than tell a
story. Good for meditation scripts, atmospheric game narration, audio art, mood pieces,
or dreamlike spoken word.

**Tips:**
- Silence does as much work as speech here. Use `(2.0)` and `(3.0)` pauses freely.
  The gaps between lines are part of the piece.
- Short lines hit harder than long ones in this format. A four-word sentence on its
  own, followed by three seconds of silence, lands very differently than prose.
- Avoid narrative urgency — no plot, no conflict, no resolution required. The piece
  can simply exist in a feeling.
- If using two voices, they don't converse — they echo, respond, or contrast. Like two
  instruments in the same key, not two characters in a scene.
- Inner thoughts `((like this))` can represent the listener's own interior voice
  emerging — very effective in meditation or introspective pieces.
- Repetition with variation works well in this format. A phrase that returns slightly
  changed carries emotional weight.

---
<!-- Everything below this line is the prompt. Select from the next line downward. -->

I need you to write an ambient narration piece — slow, atmospheric, mood-driven. This
will be synthesized by a text-to-speech voice engine. Write for the ear, not the eye.
Lines should sound natural when spoken aloud with space around them.

---

**MOOD / FEELING:**
[What emotional state or atmosphere should this create? Be specific.
Example: "The feeling of waking up alone in a house that used to be full of people.
Quiet, slightly hollow, but not sad exactly. More like... still."]

**VOICE(S):**
[One voice or two? If two, describe their relationship and contrast — not characters
in a story, but two tones or perspectives.
Example: "One voice — warm, unhurried, slightly tired but not defeated."]

**SUBJECT OR IMAGE:**
[A central image, place, or concept the piece circles around. It doesn't need to be
explained — just evoked.
Example: "An empty train station at 4am. Platform lights. No one arriving. No one leaving."]

**LENGTH:**
[Roughly how many lines, or the intended duration when spoken aloud at a slow pace.
Ambient pieces work well short — 2 to 4 minutes is often enough.]

---

**FORMAT RULES:**

Write every spoken line as:
```
VoiceID: Spoken text.
```

Use the same VoiceID consistently. No spaces, max 20 characters. If two voices,
use two distinct IDs.

- One image or thought per line. Keep lines short — 5 to 15 words is often ideal.
  Longer lines are fine occasionally but should feel deliberate.
- End every line with a period, question mark, or exclamation mark.
- Use `...` freely for trailing off or soft incompleteness.
- For pauses, write `(2.0)` on its own line. In this format, pauses are structural —
  use them generously. A `(3.0)` or `(4.0)` is not too long.
- For inner thoughts or a quiet interior voice, write `((Thought here.))` on its own
  line with no speaker ID.
- For notes, write `// Note here` on its own line. Not voiced.

**STYLE GUIDANCE:**

Avoid explanation. Don't tell the listener what to feel — give them images, sensations,
specific small details. The concrete is more evocative than the abstract here.

Avoid narrative momentum. Nothing needs to happen. Something can be noticed, and then
something else, and then a silence, and then something remembered.

Use repetition with variation. A line that comes back changed is one of the most
effective tools in this format.

**IMPORTANT — Writing for Google TTS:**

Avoid non-word vocalizations — Google TTS reads them letter by letter:
- Avoid: "hnng", "ah", "mmm", "shh"
- Use silence (explicit pause markers) instead, or real words: "oh", "well", "hush"

Ellipses `...` produce a natural soft pause. Keep punctuation intentional — every
comma and period shapes the delivery. `**bold**` adds strong emphasis in speech;
`_italic_` adds moderate emphasis. Use sparingly on key words.
