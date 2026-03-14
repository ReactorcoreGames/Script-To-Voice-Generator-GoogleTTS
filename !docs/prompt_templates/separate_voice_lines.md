# Separate Voice Lines Template

Use this when you want a **batch of individual clips** for one character — each line
plays independently and doesn't connect to the others.

**Tips:**
- Be specific about tone per category: "short and punchy" vs "full sentence" vs
  "melodramatic" gives the AI clear rhythm guidance.
- A 50/50 mix of short and longer lines in a category adds variety that sounds more
  natural when clips play back-to-back repeatedly.
- After generating, paste the lines into a `.md` file as `SpeakerID: Line text.`
  and load into Tab 1. Check the parse log in Tab 1 for formatting errors.
- Test the voice in Tab 2 with "Test Voice" before running full generation.
- If a line reads awkwardly when spoken, ask the AI to rewrite that specific line —
  what looks fine as text can sound flat when synthesized.

---
<!-- Everything below this line is the prompt. Select from the next line downward. -->

I need you to generate individual voice lines for a character. Each line will be a
standalone audio clip — they do not connect to each other.

---

**MY CHARACTER:**
[Describe who the character is, how they speak, their personality, accent, tone, and
any specific quirks. A few sentences is enough. The more specific you are, the better
the lines will fit the character.]

---

**VOICE LINES NEEDED:**

[Define your categories here. Customize names, descriptions, and counts to match your
use case. The examples below are for a game NPC voice pack — replace them with your own.]

1. Idle comments (5 lines) — Things the character mutters while waiting or on patrol.
   Short, 1–6 words. Conversational, slightly distracted.

2. Alert lines (4 lines) — Short reaction when the character spots something suspicious.
   1–5 words each, punchy. e.g. "Hey!", "What's that?", "Who goes there!"

3. Combat taunts (6 lines) — Aggressive lines directed at an opponent during a fight.
   Mix short punchy lines (2–4 words) with 1–2 longer sentences.

4. Victory lines (5 lines) — Said after winning a fight or completing an objective.
   Confident, in-character. Vary length — some short, some medium.

5. Death/defeat lines (3 lines) — Said when the character is defeated or killed.
   Humorous, dramatic, or bitter — whichever fits the character.

*(Other ideas: jump, dodge, pain, interact, item picked up, access denied, success, etc.)*

[Replace the examples above with your actual categories and counts.]

**TOTAL LINES:** [Sum of all category counts]

---

**FORMAT RULES:**

Output ONLY the voice lines, one per line, in the exact order listed above.
Do not include numbering, category names, headers, or any extra text.
I will paste your output directly into the voice generator.

Write exactly [total] lines of text in the exact order listed, one per line,
no numbering, no category headers, no extra text.

**IMPORTANT — Writing for Google TTS:**

Google TTS reads non-word vocalizations letter by letter ("grr" becomes "gee arr arr").
Use real words instead:
- Avoid: "ugh", "hnng", "grr", "tsk", "pfft", "hmph", "argh"
- Use real words that carry the same feeling:
  - Pain/frustration: "ow", "ouch", "nope", "gah", "oh", "not great"
  - Anger/menace: "bah", "yeah right", "pathetic", "get wrecked"
  - Surprise: "whoa", "huh", "oh no", "wait what"

Single-word lines work great for short interjections. Keep punchy lines punchy.
