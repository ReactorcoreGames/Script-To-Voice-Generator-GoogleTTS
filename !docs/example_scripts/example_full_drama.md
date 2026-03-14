# The Haunted Apartment

// ─────────────────────────────────────────────────────────────────
// ROBUST TEST SCRIPT
// Tests all valid parser features in a realistic story context.
// ─────────────────────────────────────────────────────────────────

/*
  Cast:
    Alex       - a nervous new tenant
    Jordan     - Alex's skeptical friend
    Landlord   - gruff building manager
    Narrator   - scene-setting voice

  Sound channels:
    c1 = background ambience (looped)
    c2 = one-shot effects
*/

## Scene 1 - Moving Day

{play street_noise.mp3, c1, loop}

Narrator: It was a grey October afternoon when Alex moved into apartment 4B.

(pause 1.0s)

Alex: [muttering] Box number _twelve_. Where did I put box number twelve?
Jordan: You've been saying that for an hour. // inline comment - ignored by parser
Alex: Because I **need** box twelve!

{play door_knock.wav, c2, once}

Landlord: Door's open. You the new tenant?
Alex: That's me. Alex Mercer.
Landlord: Right. Rules are simple: no loud music after ten, no pets, no--
Alex: --subletting, yes, I read the lease.

(1.5)

Landlord: [grumbles] Smart one. Keys are on the counter.

{stop c1}

## Scene 2 - First Night

{play rain_on_window.mp3, c1, loop}

(pause 2.0s)

Narrator: By midnight the rain had started. Alex was alone.

Alex: ((This place feels wrong. I can't explain it.))
Alex: [sighs] Come on, it's just an old building.

(0.5)

Jordan: [via phone] So how's the new place?
Alex: Honestly? A bit creepy. The pipes make sounds like--
Jordan: --like every apartment ever? You're so dramatic.

{play pipe_clang.wav, c2, once}

Alex: Did you hear that??
Jordan: Hear what? My connection is fine.
Alex: Never mind. I'm going to bed.

(pause 1.5s)

Jordan: ((She's going to call me at three in the morning. I know it.))

{stop c1}

## Scene 3 - The Investigation

// The next morning. Sunlight helps.

{play morning_birds.mp3, c1, loop}

Narrator: Morning came. Alex had not, in fact, called at three in the morning.

Jordan: Okay I'll admit it... I'm impressed.
Alex: See? Nothing to worry about.
Alex: Although--

(0.3)

Alex: --the mirror in the bathroom is _definitely_ cracked.
Jordan: That's just bad luck, not a haunting.
Alex: [quietly] Seven years of it.

// Testing apostrophes and hyphens in speaker IDs below

Sarah O'Brien: [from hallway] Sorry to interrupt -- I'm in 4A. Heard voices.
Alex: Oh! Hi. I'm Alex.
Sarah O'Brien: Sarah. Fair warning: the super-heating cuts out mid-October.
Jordan: Classic old building stuff.

(2.0)

Sarah O'Brien: ((They seem nice. Maybe this floor won't be so quiet.))

{play door_close.wav, c2, once}

{stop c1}

## Scene 4 - Late Punctuation Tests

// This scene exists to exercise the ending-punctuation detection logic.

Narrator: Various lines to test punctuation tiers.

Alex: This is a plain statement.
Alex: Are you sure?
Alex: Watch out!
Alex: We have to go--
Alex: I can't believe it...
Alex: Are you _kidding_ me??
Alex: This is unacceptable!!!
Alex: I just... I don't know what to say.
Alex: **Fine.**

(pause 0.5s)

Jordan: Okay, okay, I get it.

## Scene 5 - Markdown and Bracket Cleanup

Narrator: Testing text-cleaning pipeline for TTS output.

Alex: I said _hello_ and you said **nothing**.
Jordan: [clears throat] That is _not_ what happened.
Alex: We can agree to disagree. [shrugs]
Jordan: [laughing] You're impossible, you know that?

// Inline comment stripping
Alex: Let's just move on. // this part should be stripped by parser
Jordan: Agreed. // likewise

(1.0)

Narrator: And so the haunted apartment turned out to be merely old, drafty, and full of neighbours.

(pause 1.5s)

Alex: [quietly] **Still** not convinced about that mirror though.
Jordan: ((Neither am I.))

{stop c1}
