# The Last Broadcast

/*
  A single narrator delivers a final transmission from an abandoned research station.
  Demonstrates: single speaker, inner thoughts, varied punctuation for pacing,
  explicit pauses, SFX layering, and the full emotional range of a monologue.

  Suggested voice settings:
    Narrator - deep male voice, Reverb: Mild, Cheap Mic: Mild
    Pitch: Deep preset or slightly below normal
    Speed: -5% (slightly slower, more deliberate)

  Sound channels:
    c1 = low ambient hum / static (loop)
    c2 = one-shot punctuation sounds
*/

{play static_hum.mp3, c1, loop}

(2.0)

Narrator: Station log. Final entry.

(1.5)

Narrator: I've been trying to figure out what to say for three days now. Every time I sit down, I get as far as the date and then... nothing.

(1.0)

Narrator: So I'm not going to do the date. You'll know when this was. You'll know everything, eventually.

(2.0)

Narrator: ((They always said I talked too much. Funny how that works out.))

(1.0)

Narrator: The equipment is still running. Most of it, anyway. The east array went dark on Tuesday -- or what I'm calling Tuesday -- and I haven't had the heart to go check why.

(0.8)

Narrator: I know why.

(2.0)

{play wind_outside.wav, c2, once}

(0.5)

Narrator: The wind picked up again tonight. It comes in under the door no matter how much I pack it. Cold doesn't bother me the way it used to. That's... probably not a good sign.

(1.5)

Narrator: I keep thinking about the last real conversation I had. Petrov, arguing about whether instant coffee counted as coffee. I said no. He said I was being a snob. I said I had standards. He laughed.

(1.0)

Narrator: ((I'd give anything for that argument right now.))

(2.0)

Narrator: If you're listening to this, it means the signal got through. Which means the relay is still up. Which means at least one thing I built is still doing its job.

(0.8)

Narrator: I'll take it.

(1.5)

Narrator: There are things I should probably report. Coordinates. Observations. I have notebooks full of them. They're in the cabinet by the east window, the one with the blue tape on the handle. Take them. They matter more than anything I'm going to say here.

(1.0)

Narrator: What I'm going to say here is...

(2.5)

Narrator: Don't wait.

(1.0)

Narrator: Whatever you're waiting for. The right moment, the right words, the right conditions. They don't come. You just... go. You do the thing before you're ready. You say the words before you know how they'll land.

(0.8)

Narrator: That's all I've got after all of this. Don't wait.

(2.0)

{play static_hum.wav, c2, once}

(1.0)

Narrator: ((Not exactly groundbreaking. But it's true.))

(1.5)

Narrator: Station log. End of entry.

(1.0)

Narrator: Signing off.

(3.0)

{stop c1}
