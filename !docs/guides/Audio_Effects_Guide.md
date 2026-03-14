# Audio Effects Guide — Script to Voice Generator

## Overview

Script to Voice Generator includes 12 audio effects, each with 4 preset levels
(Off, Mild, Medium, Strong). Effects are set per speaker in **Tab 2** and applied
during generation. They can be freely combined.

There are also 2 boolean toggles — **FMSU** and **Reverse** — which have no levels,
just on or off. And a 13th effect — **Inner Thoughts** — which applies automatically
to lines marked as internal monologue in the script. It has 3 named presets plus a
fully customisable mode. See the [Inner Thoughts section](#inner-thoughts) below.

**Note:** "Cheap Mic" is enabled at Mild by default, which gives TTS voices a
slightly more natural, less AI-perfect character out of the box.

---

## Available Effects

### 1. Radio Filter
**Description:** Walkie-talkie / comms radio effect
**Use case:** Military or tactical characters, space crews, dispatch operators

**Presets:**
- **Off:** No effect
- **Mild:** Slight frequency filtering (500–3200 Hz bandpass)
- **Medium:** Clear walkie-talkie with phaser and compression
- **Strong:** Heavy military radio with distortion and further compression

**Pairs well with:**
- Radio + Reverb = Echoing transmission from a large facility
- Radio + Distortion = Damaged or emergency radio signal

---

### 2. Reverb
**Description:** Spatial depth and presence
**Use case:** Narrators, authority figures, large environments, ethereal characters

**Presets:**
- **Off:** No effect
- **Mild:** Subtle room presence (short echo)
- **Medium:** Arena or large hall (double echo)
- **Strong:** Cathedral or otherworldly presence (long, layered echoes)

**Pairs well with:**
- Reverb + Distortion = Powerful, aggressive presence
- Reverb + Robot Voice = Massive mechanical entity

---

### 3. Distortion
**Description:** Aggressive, gritty, raw
**Use case:** Angry characters, monsters, corrupted voices, intense emotional moments

**Presets:**
- **Off:** No effect
- **Mild:** Subtle compression and grit
- **Medium:** Clear aggression with overdrive
- **Strong:** Heavy, monster-like distortion

**Pairs well with:**
- Distortion + Reverb = Powerful, dominating presence
- Distortion + Telephone = Broken or corrupted transmission
- Distortion + Robot Voice = Corrupted/damaged AI

---

### 4. Telephone
**Description:** Lo-fi, compressed, retro
**Use case:** Phone calls, intercoms, old recordings, degraded comms

**Presets:**
- **Off:** No effect
- **Mild:** Slight bandpass filtering and compression
- **Medium:** Clear telephone / intercom effect
- **Strong:** Heavily compressed, crushed audio (emergency speaker, ancient intercom)

**Pairs well with:**
- Telephone + Reverb = PA system in a large building
- Telephone + Distortion = Damaged speaker or broken comms

---

### 5. Robot Voice
**Description:** Robotic, mechanical, synthetic
**Use case:** AI characters, cyborgs, robots, synthetic entities

**Presets:**
- **Off:** No effect
- **Mild:** 80 Hz ring modulator with metallic filtering — noticeable robotic character
  while maintaining clarity
- **Medium:** 40 Hz ring modulator — classic robotic sweet spot with good intelligibility
- **Strong:** 100 Hz ring modulator + 8 kHz sample crushing + 6-bit degradation —
  extreme crunchy digital / terminator voice

**Pairs well with:**
- Robot Voice + Reverb = Massive mechanical entity
- Robot Voice + Distortion = Corrupted or damaged AI
- Robot Voice + Telephone = Synthetic comms system
- Robot Voice + Radio = Robotic military transmissions

**Technical note:** Uses ring modulation (mixing the voice with sine waves) combined with
sample rate reduction and bit crushing for the Strong preset. This creates authentic
robotic character without phasing artifacts.

---

### 6. Cheap Mic *(Default: Mild)*
**Description:** Degraded quality, poor recording
**Use case:** Adding natural character to any voice, retro recordings, worn equipment

**Presets:**
- **Off:** Clean digital quality (no processing)
- **Mild:** Subtle lo-fi character *(DEFAULT — enabled automatically)*
- **Medium:** Clear degradation with compression
- **Strong:** Heavily degraded, extreme lo-fi

**Pairs well with:**
- Cheap Mic + Radio = Old military radio transmission
- Cheap Mic + Telephone = Ancient intercom system
- Cheap Mic + Distortion = Broken or damaged speaker

**Why default Mild?** The mild preset makes TTS voices sound more natural and less
"AI-perfect" by simulating a realistic microphone recording without being obviously
degraded.

---

### 7. Underwater
**Description:** Submerged, muffled, wet — voice heard through water
**Use case:** Underwater scenes, drowning, distant sounds through liquid

**Presets:**
- **Off:** No effect
- **Mild:** Gentle lowpass + soft flanger wobble
- **Medium:** Stronger muffling with deeper flange
- **Strong:** Heavily muffled, strong wet wobble with compression

**Pairs well with:**
- Underwater + Reverb = Vast submerged space
- Underwater + Robot Voice = Machine speaking from beneath the surface

---

### 8. Megaphone
**Description:** Projected bullhorn — punchy, bandpassed, no transmission shimmer
**Use case:** Crowd control, announcements, protest scenes, military loudspeaker

**Presets:**
- **Off:** No effect
- **Mild:** Moderate bandpass with light compression
- **Medium:** Tighter bandpass, higher compression ratio
- **Strong:** Aggressive narrow band, heavy compression and saturation

**Pairs well with:**
- Megaphone + Reverb = Outdoor announcement in a large space
- Megaphone + Distortion = Damaged or overdriven loudspeaker

---

### 9. Worn Tape
**Description:** VHS/cassette degradation — wow-flutter, lo-fi, analog warble
**Use case:** Flashback recordings, found footage, old home video feel

**Presets:**
- **Off:** No effect
- **Mild:** Subtle sample rate reduction with gentle phaser warble and light bit crush
- **Medium:** Noticeable tape warble, stronger crush and compression
- **Strong:** Heavy degradation, extreme flutter and bit depth loss

**Pairs well with:**
- Worn Tape + Reverb = Distant old recording played in an empty room
- Worn Tape + Telephone = Ancient answering machine message

---

### 10. Intercom
**Description:** Hallway speaker box with static bleed — boxy, compressed, crackling
**Use case:** Building intercoms, security systems, facility announcements, walkie-talkie adjacent

**Presets:**
- **Off:** No effect
- **Mild:** Moderate frequency narrowing with subtle background static hiss
- **Medium:** Tighter frequency range, noticeable crackling noise
- **Strong:** Narrow boxy sound with prominent rough static that competes with the voice

**Note:** Unlike Telephone (which is purely a filter effect), Intercom mixes generated
static noise into the voice signal. The noise becomes progressively coarser and louder
across preset levels using bit-crushed pink noise.

**Pairs well with:**
- Intercom + Cheap Mic = Worn-out building speaker system
- Intercom + Distortion = Damaged or malfunctioning intercom

---

### 11. Alien Voice
**Description:** Inhuman, otherworldly, strange
**Use case:** Alien characters, eldritch entities, heavily altered non-human voices

**Presets:**
- **Off:** No effect
- **Mild:** Subtle ring modulation — slightly uncanny, still intelligible
- **Medium:** Stronger ring mod with filtering — clearly non-human
- **Strong:** Heavy ring modulation, extreme character

**Pairs well with:**
- Alien + Reverb = Vast presence from another dimension
- Alien + Distortion = Aggressive hostile entity

---

### 12. Cave / Tunnel
**Description:** Environmental acoustic depth — echo and space
**Use case:** Underground scenes, tunnels, cavernous spaces, enclosed stone rooms

**Presets:**
- **Off:** No effect
- **Mild:** Tunnel — tight, slightly reverberant space
- **Medium:** Cave — full cave echo with layered reflections
- **Strong:** Abyss — deep, long decay echoing into darkness

**Pairs well with:**
- Cave + Robot Voice = Massive mechanical entity in an underground facility
- Cave + Distortion = Creature lurking in the dark

---

### FMSU *(Toggle — On/Off)*
**Description:** F*** My Sh** Up — brutal digital corruption
**Use case:** Glitched voices, corrupted transmissions, damaged AI, horror distortion, extreme creative destruction

**What it does:** Applies a two-stage bit-crush and hard-clip cycle to the fully processed
audio. 2-bit quantization in both log and linear modes, with overdrive before each stage
and waveform fold-over clipping. The result is harsh, artifact-heavy, and genuinely
corrupted — speech rhythms survive but the voice is clearly destroyed.

**Note:** Applied as the very last processing stage, after normalisation and limiting,
so the damage is not corrected by the safety pipeline. A secondary limiter fires after
FMSU to prevent encoder overflow when combined with other volume-boosting effects.

**Pairs well with:**
- FMSU + Robot Voice = Catastrophically malfunctioning AI
- FMSU + Distortion = Complete signal breakdown
- FMSU + Telephone = Dying transmission on its last legs

---

### Reverse *(Toggle — On/Off)*
**Description:** Plays the fully processed clip backwards
**Use case:** Dream sequences, supernatural voices, creative sound design

**Note:** Applied absolutely last — reversal is the final state of the clip.

---

## How Effects Are Applied

### Processing Pipeline

Most effects run through a single optimised FFMPEG pass. Intercom is a special case
(see note below).

```
0. Silence Trim (leading/trailing TTS padding removed — configurable in Tab 4)
   ↓
1. Apply Effects:
   2. Frequency Effects (Radio, Telephone, Cheap Mic, Underwater, Megaphone, Worn Tape, Intercom)
   3. Ring Modulation / Pitch Effects (Robot Voice, Alien)
   4. Spatial / Echo Effects (Reverb, Cave)
   5. Distortion
   5.5. Inner Thoughts filter (if applicable)
   ↓
7. Soft Limiting (always active — prevents encoder clipping)
   ↓
8. Final Volume Adjustment (5–100%)
   ↓
8.5. FMSU (if enabled) + safety limiter
   ↓
9. Reverse (if enabled)
   ↓
Peak Normalise (separate pass — brings clip peak to 0 dBFS, preserving dynamics)
```

**Intercom static noise** is handled via a separate `filter_complex` pass when active:
the voice goes through all the above stages, then bit-crushed pink noise is generated
and mixed in at the end. Everything else uses the standard single-pass chain.

**Per-clip peak normalisation** runs after the effect pass. Each `clips_effect` file is
brought to 0 dBFS using a two-pass linear gain (measure peak, apply exact gain). This
preserves all dynamics and relative loudness within the clip — it is purely a ceiling
adjustment, not compression or loudness targeting. Effects that remove frequency content
(Radio, Telephone, Cheap Mic) will naturally sound quieter than fullband audio at the
same peak level — this is correct and realistic behaviour, not a bug.

---

## Recommended Combinations by Character Type

### Narrator / Announcer
- Reverb: Medium or Strong
- Cheap Mic: Off or Mild
- Result: Booming, authoritative presence

### Space Marine / Tactical Soldier
- Radio: Medium
- Reverb: Off or Mild
- Cheap Mic: Mild
- Result: Clear tactical comms with authority

### Gruff Veteran
- Distortion: Mild
- Cheap Mic: Mild or Medium
- Result: Gritty, experienced fighter

### Robot / AI / Cyborg
- Robot Voice: Medium or Strong
- Reverb: Off or Mild
- Result: Clear synthetic character

### Corrupted / Damaged AI
- Robot Voice: Strong
- Distortion: Mild or Medium
- Telephone: Mild
- Result: Glitchy, malfunctioning mechanical voice

### Ethereal / Supernatural Entity
- Reverb: Strong
- Telephone: Mild
- Cheap Mic: Off
- Result: Distant, otherworldly presence

### Phone / Intercom Character
- Telephone: Medium or Strong
- Cheap Mic: Mild
- Result: Clear telephone or intercom effect

### Emergency Broadcast
- Telephone: Strong
- Radio: Medium
- Distortion: Mild
- Result: Damaged emergency speaker system

---

## Yell Impact

**What it does:** Applies an extra speed reduction to single-word exclamatory lines,
making them hit harder and feel more deliberate — a shout that lands with weight rather
than rushing past.

**Range:** 0 to -80% speed reduction (default: 0, disabled)

**Trigger conditions — all three must be true:**
- The line is a single word (no spaces)
- The line ends with punctuation containing at least one `!`
- Examples that trigger: `YES!`, `NO?!`, `HELP!!!`
- Examples that do NOT trigger: `Get out!` (multi-word), `Why?` (no exclamation)

**Usage:** Set in Tab 2 per speaker. A value of -40% slows qualifying yell lines by
40%. Use it on combat characters, aggressive voices, or any speaker who delivers
short explosive reactions.

---

## Inner Thoughts

Inner Thoughts is an automatic effect applied to any line written as internal monologue
— lines enclosed in double parentheses in the script:

```
Narrator: (( I shouldn't have said that. ))
```

The effect runs as a separate processing stage after all the speaker's regular effects,
so it stacks on top of Radio, Telephone, etc. It is configured globally in **Tab 4**
and applies to all speakers equally.

### Presets

**Dissociated** *(default)*
Cold, slightly hollow, mildly narrowed frequency range with a tight single echo.
The voice is still intelligible but feels detached from the outside world — like a
thought surfacing in a noisy environment. Good default for most characters.

**Whisper**
Heavily muffled with an aggressive lowpass cut (up to ~1100 Hz). Sounds like the
voice is speaking through a wall or inside a helmet. Very occluded and private.
Works well for characters suppressing emotion or trying not to think too loudly.

**Dreamlike**
Warm, open frequency range with a dual-tap echo trail (150 ms + 280 ms). The voice
dissolves into space rather than cutting off cleanly. Good for meditation scripts,
surreal or altered-state scenes, and characters drifting in and out of consciousness.

**Custom**
Full manual control over highpass/lowpass cutoffs, echo delay, echo wet amount, and
volume. Useful if none of the presets fit your character or tone.

### Using Inner Thoughts as a Creative Effect

Because Inner Thoughts applies per-line rather than per-speaker, it can be used for
creative purposes beyond literal internal monologue:

- **Flashback / memory:** Write recalled dialogue with `(( ))` to give it a distant,
  filtered quality distinct from present-tense speech.
- **Voiceover narration:** A narrator delivering inner commentary between action lines
  can use Dreamlike for a floaty, meditative tone separate from their normal voice.
- **Dissociation / breakdown:** A character spiralling mentally can have a mix of normal
  lines and `(( ))` lines — the contrast between the two sounds tells the story.
- **Environmental filtering:** A character speaking through thick walls, helmets, or
  over a degraded channel can use the Whisper preset as a secondary layer on top of
  their regular Telephone or Radio effect.
- **Ambient narration:** In slow, atmospheric scripts (meditation, spoken word), setting
  all lines as inner thoughts with the Dreamlike preset creates a sustained dissolved
  quality throughout.

### Inner Thoughts + Regular Effects

Inner Thoughts runs after the speaker's regular effect chain, so combinations are
possible:

- Radio + Inner Thoughts (Dissociated) = Fragmented transmission with a cold, haunted
  quality
- Reverb + Inner Thoughts (Dreamlike) = Massive echoing space dissolving into the void
- Telephone + Inner Thoughts (Whisper) = Muffled signal within an already degraded
  channel — extreme lo-fi intimacy
- No effects + Inner Thoughts (Whisper) = Simple clean voice becoming suddenly
  claustrophobic and internal

---

## Tips for Best Results

1. **Start with Mild** — test effects at low levels before going stronger.
2. **Use "Test Voice"** in Tab 2 to audition before a full generation run.
3. **Don't over-combine** — using all effects at maximum usually creates mud.
4. **Choose the base voice first** — effects enhance a good voice; they can't fix a
   poor one. Pick your voice in Tab 2 before adjusting effects.
5. **Cheap Mic is already on** — remember Mild is the default. Turn it off if you
   want a clean digital sound.
6. **Volume range is 5–100%** — the default 100% is full normalized output. Reduce a
   specific speaker's level to make them quieter relative to others in the mix.
7. **The pipeline prevents clipping** — the soft limiter and per-clip peak normalisation
   handle safety. Experiment freely.

---

## Configuring Effects (`config.py`)

Effects and their FFMPEG filter chains are defined in `config.py` under `AUDIO_EFFECTS`:

```python
AUDIO_EFFECTS = {
    "effect_name": {
        "name": "Display Name",
        "description": "Effect description",
        "presets": {
            "off": "",
            "mild": "ffmpeg_filter_chain",
            "medium": "ffmpeg_filter_chain",
            "strong": "ffmpeg_filter_chain",
        }
    }
}
```

To add new effects or modify existing ones, edit the FFMPEG filter chains in `config.py`.
Do not modify working filter chains without testing — see developer notes in `CLAUDE.md`.

---

## FFMPEG Filters Reference

| Filter       | Purpose                                              |
|--------------|------------------------------------------------------|
| `loudnorm`   | Loudness normalisation (EBU R128)                   |
| `highpass`   | Removes frequencies below cutoff                     |
| `lowpass`    | Removes frequencies above cutoff                     |
| `bandpass`   | Passes only a specific frequency range               |
| `aphaser`    | Phaser effect (cyclic comb filtering / warble)       |
| `flanger`    | Flanger effect (short delay + feedback sweep)        |
| `aecho`      | Echo and reverb                                      |
| `acompressor`| Dynamic range compression                            |
| `acrusher`   | Bit crushing / sample rate reduction (lo-fi)         |
| `aresample`  | Sample rate conversion                               |
| `asoftclip`  | Soft or hard clipping for distortion / fold-over    |
| `alimiter`   | Soft limiter to prevent clipping                     |
| `anoisesrc`  | Generated noise source (white, pink, brown, etc.)   |
| `amix`       | Mixes multiple audio streams together                |
| `areverse`   | Reverses the audio clip                              |
| `volume`     | Volume multiplication                                |
| `treble`     | High-frequency boost/cut                             |
| `bass`       | Low-frequency boost/cut                              |
| `aeval`      | Mathematical audio expression (used for ring mod)   |

Full FFMPEG audio filter documentation: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters


---

## Reference Sheet (`project_reference.txt`)

Each generation run writes a session reference sheet to the output folder. It records
everything needed to reproduce or audit the session: project settings, per-speaker
voice/effects configuration, and the full clip list with spoken text.

Example (condensed):

```
# SCRIPT TO VOICE GENERATOR - GOOGLE TTS — SESSION REFERENCE

Project  : | my_scene | 2026-03-13  14:32:07 | MP3 | 7 Clips | 2 Sounds |
Speakers : | 2 | alice, bob |

---

## SPEAKERS

alice
  Voice     : | en-US-Chirp3-HD-Charon |
  Settings  : | Pitch (API) +0.0 st | Pitch (FFMPEG) +0.0 st | Speed 1.00x | Level : 100% | Yell : 0% |
  Effects   : | RAD:medium | RVB:mild |

bob
  Voice     : | en-US-Chirp3-HD-Aoede |
  Settings  : | Pitch (API) +0.0 st | Pitch (FFMPEG) +0.0 st | Speed 1.10x | Level : 80% | Yell : 0% |
  Effects   : | TEL:strong | FMSU |

---

## PARAMETERS

SFX Filters    : | NONE |
Punctuations   : | .  0.6s | ,  0.3s | !  0.5s | ?  0.5s | -  0.2s | ...  0.8s | !?  0.7s | ?!?  0.9s |
Contextuals    : | Change 0.3s | Short 20/0.1s | Long 200/0.2s | Inner 0.3s | Same 0.0s | First 0.0s | Last 0.0s |
Inner thoughts : | Dissociated |
Silence trim   : | beginning_end |

---

## CLIPS

0001. my_scene_0001_alice_hello_there.mp3
      ALICE: Hello there.

0002. my_scene_0002_bob_understood.mp3
      BOB: Understood.
```

### Effect abbreviations

Effects appear in the `Effects` line for each speaker, and in the `SFX Filters` line.
Active effects only — `| NONE |` is shown when no effects are set.

| Abbreviation | Effect | Value format |
|---|---|---|
| RAD | Radio Filter | `mild` / `medium` / `strong` |
| RVB | Reverb | `mild` / `medium` / `strong` |
| DIST | Distortion | `mild` / `medium` / `strong` |
| TEL | Telephone | `mild` / `medium` / `strong` |
| ROBO | Robot Voice | `mild` / `medium` / `strong` |
| CHP | Cheap Mic | `mild` / `medium` / `strong` |
| UNDR | Underwater | `mild` / `medium` / `strong` |
| MEGA | Megaphone | `mild` / `medium` / `strong` |
| TAPE | Worn Tape | `mild` / `medium` / `strong` |
| ICOM | Intercom | `mild` / `medium` / `strong` |
| ALN | Alien Voice | `insectoid` / `dimensional` / `warble` |
| CAVE | Cave / Tunnel | `tunnel` / `cave` / `abyss` |
| PS | Pitch Shift | semitone value e.g. `+2.0st`, `-3.5st` |
| FMSU | FMSU | (flag — no value) |
| REV | Reverse | (flag — no value) |

Inner thoughts preset is logged separately in the `## PARAMETERS` section — it is a
global setting, not a per-speaker effect, so it does not appear in the per-speaker
Effects line.

**Clip lines** show the filename on the first line and `SPEAKER: spoken text` indented
below. Inner thought lines are marked with `[IT]` after the speaker ID.

---

## Troubleshooting

**Effects sound too extreme?**
- Try a lower preset level (Mild instead of Strong).
- Reduce volume boost when combined with heavy distortion.
- Remember: Cheap Mic is already enabled at Mild by default.

**No audible difference?**
- Ensure FFMPEG is installed (`ffmpeg -version` in a terminal).
- Confirm the effect is not set to "Off".
- Try a stronger preset and use "Test Voice" to compare.

**Audio clipping or artifacts?**
- Should be rare due to the always-active soft limiter and per-clip peak normalisation.
  If it occurs, use milder effect presets.

**Audio too quiet after effects?**
- Frequency-stripping effects (Radio, Telephone, Cheap Mic, Megaphone) remove parts of
  the signal, so they naturally have less energy than a fullband voice at the same peak
  level. This is realistic — a telephone filter is supposed to sound smaller.
- The merged_loudnorm output applies broadcast-standard loudness normalisation across the
  whole file, which will bring quieter-sounding clips up to a consistent perceived level.
- If individual clips feel too distant, try a milder preset level.

**Short lines sound quieter than long lines with Radio or Telephone active?**
- This is expected behaviour caused by the phaser component in those effects.
  The phaser sweeps through a volume cycle over time. Long lines span multiple
  cycles and average out to a consistent perceived loudness. Short lines (under
  ~1 second) catch only a narrow slice of the sweep — if that slice lands in the
  quiet phase, the clip will sound subdued compared to longer lines.
- It is not a bug and cannot be fully corrected by normalisation, since the peak
  level of the clip may be accurate while the average perceived loudness is lower.
- To minimise it: use Radio or Telephone at Medium or Strong (which add compression
  that partially counteracts the phaser's volume variation), or accept it as part of
  the effect character — short clipped transmissions naturally have this quality.

**Voices sound too "AI-clean"?**
- Cheap Mic (Mild) is enabled by default for this reason. If still too clean,
  increase to Medium, or add a subtle Radio (Mild) for more character.

**Generation taking too long?**
- The full pipeline adds ~1–2 seconds per clip. A full project generation is normal.
- Disable effects for faster generation (useful for draft runs).
