# Podcast / Interview Template

Use this when you want **two speakers in natural conversation** — one asking, one
responding, both with distinct voices and viewpoints. The feel should be spontaneous
and human, not scripted. Good for mock interviews, documentary dialogue, talk-show
style exchanges, or any two-person conversation piece.

**Tips:**
- The guest/subject should do most of the talking. The host's job is to ask, react,
  and occasionally push back — not to deliver equal amounts of content.
- Real conversations interrupt, trail off, and self-correct. Ask the AI to include
  these — `--` interruptions, `...` hesitations, mid-sentence corrections.
- Give the host and guest genuinely different registers. A formal interviewer and a
  casual subject creates useful contrast. Two people who speak identically is boring.
- Inner thoughts `((like this))` work well for a documentary style — a character's
  internal reaction that the other person doesn't hear.
- Keep it to one topic or angle per scene. A focused conversation is more interesting
  than a broad one.

---
<!-- Everything below this line is the prompt. Select from the next line downward. -->

I need you to write a two-person conversation in a podcast or interview style. The
output will be synthesized by a text-to-speech voice engine, so all dialogue must
read naturally when spoken aloud.

---

**THE HOST:**
[Who is conducting the interview or leading the conversation? Their name, personality,
interview style, and relationship to the subject.]

**THE GUEST / SUBJECT:**
[Who is being interviewed or in conversation? Their name, background, speaking style,
and what they bring to this conversation.]

**TOPIC:**
[What is the conversation about? What angle or specific question is being explored?]

**LENGTH:**
[Roughly how many exchanges, or describe the pacing — quick back-and-forth, longer
thoughtful answers, a mix of both.]

**TONE:**
[Warm and curious, formal and probing, confrontational, playful, reverential, etc.]

---

**FORMAT RULES:**

Write every spoken line as:
```
SpeakerID: Dialogue text.
```

Use the same SpeakerID consistently for each speaker. No spaces, max 20 characters.

- One thought per line. Don't wrap a single continuous speech across multiple lines
  unless it's a genuine new beat or sentence.
- Keep lines under 500 characters each. Break long answers into natural separate lines.
- End every line with a period, question mark, or exclamation mark.
- Use `...` for hesitation or trailing off. Use `--` for self-interruption or a line
  cut off by the other speaker.
- For the other speaker cutting in: end one line with `--` and start the next with `--`
- For pauses, write `(1.0)` on its own line. The number is seconds.
- For inner thoughts (unspoken reactions), write `((Thought text here.))` on its own
  line with no speaker ID. Use sparingly for key emotional moments.
- For notes or stage directions, write `// Note here` on its own line. Not voiced.

**STYLE GUIDANCE:**

Write the host's questions and reactions as a real interviewer would — following up on
what was actually just said, not asking pre-planned questions regardless of the answer.
The conversation should feel like it's going somewhere, not like two monologues taking
turns.

The guest's answers should have natural rhythm: an initial response, then elaboration,
then perhaps a qualification or a moment of reflection. Not everything lands perfectly.

**IMPORTANT — Writing for Google TTS:**

Avoid non-word vocalizations — Google TTS reads them letter by letter:
- Avoid: "hnng", "ugh", "pfft", "tsk", "hmph"
- Use: "well", "huh", "right", "oh", "yeah", "I mean", real conversational fillers

Ellipses `...` produce a natural soft pause. Commas and em-dashes affect pacing.
`**bold**` adds strong spoken emphasis; `_italic_` adds moderate emphasis. Use on
key words to make the engine stress them naturally.
