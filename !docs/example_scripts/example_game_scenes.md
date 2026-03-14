# Threshold — First Contact

/*
  A single scene from a sci-fi game: first contact with an alien intelligence
  speaking through a captured probe. Three characters, a tense negotiation,
  one scene. Load, configure, generate.

  Demonstrates: multi-speaker dialogue, interrupted lines, inner thoughts,
  SFX integration, scene atmosphere, varied emotional registers.

  Cast:
    Commander  - mission lead, controlled but under pressure
    Dr_Voss    - xenolinguist, excited and trying not to show it
    ARIA       - alien intelligence, speaking through a translation layer

  Suggested voice settings:
    Commander  - authoritative male voice, Radio: Mild, Cheap Mic: Mild
    Dr_Voss    - warm female voice, Cheap Mic: Mild
    ARIA       - neutral voice, Robot Voice: Medium, Reverb: Mild, Cheap Mic: Off

  Sound channels:
    c1 = deep space ambient hum (loop)
    c2 = one-shot interface sounds / signal tones
*/

{play deep_space_hum.mp3, c1, loop}

(2.0)

Commander: Status.
Dr_Voss: Signal's stable. Whatever it is, it's holding the channel open deliberately.
Commander: Deliberately.
Dr_Voss: Yes. It could have dropped us three times in the last minute. It didn't.

(1.0)

Commander: ((That's either very good or very bad.))

(0.5)

Commander: Can you open a return channel?
Dr_Voss: Already did. Twenty seconds ago.

(1.5)

{play signal_tone.wav, c2, once}

(1.0)

ARIA: You are small.

(2.0)

Commander: ...That's a translation?
Dr_Voss: [quietly] Best approximation. Don't react to the framing, react to the fact that it's speaking at all.

(1.0)

Commander: We are small. Relative to many things. What are you?
ARIA: A question shaped like a mirror. You ask what I am. You mean: what am I to you.

(1.5)

Dr_Voss: ((Oh. Oh that's extraordinary.))

(0.5)

Dr_Voss: [to Commander] It's parsing intent, not just words. The translation matrix shouldn't be able to do that.
Commander: Focus, Voss.

(0.8)

Commander: [to ARIA] Fair. Then let me ask differently. What do you want from this conversation?
ARIA: The same thing you do. To determine if the other is worth the risk of continuing.

(2.0)

Commander: ((Alright. I can work with that.))

(1.0)

Commander: And your assessment so far?
ARIA: Incomplete. You are afraid and you are hiding it. That is interesting. Most afraid things do not hide it.

(1.5)

Dr_Voss: [low] Commander...
Commander: I know.

(1.0)

Commander: You're right. We are afraid. We've never done this before.
ARIA: Neither have we.

(3.0)

{play signal_tone.wav, c2, once}

(1.0)

Dr_Voss: [almost to herself] Neither have we...
Commander: Is that -- is that uncertainty? From it?
Dr_Voss: I think so. I think it just told us it's as lost as we are.

(2.0)

Commander: [to ARIA] Then we're the same, in that way.
ARIA: In that way. Yes.

(1.5)

ARIA: We will speak again. When you are less afraid. We will be... less uncertain.

(2.0)

{play signal_tone.wav, c2, once}

(3.0)

Dr_Voss: It closed the channel.
Commander: Voluntarily?
Dr_Voss: Yes.

(2.0)

Commander: ((Well. First contact.))

(1.0)

Commander: Get me a full transcript. And Voss -- good work.
Dr_Voss: [quietly] I have no idea what just happened.
Commander: Neither do I. Write it up anyway.

(1.5)

{stop c1}
