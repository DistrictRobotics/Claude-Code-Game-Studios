# DC Go-Go Music Festival — Game Design Document

**Project**: DC GoGo Fest  
**Version**: 0.1 (Pre-Production)  
**Date**: 2026-11-05  
**Foundation**: D.C. Go-Go Music Foundation / @dcgogofestorg  
**Engine**: Unreal Engine 5

---

## 1. Overview

DC GoGo Fest is a 3D concert experience and rhythm-based game set in authentic Washington DC venues. Players explore iconic DC locations, watch and interact with realistic digital twin band members performing live Go-Go music, and unlock new venues, songs, and performance moments. The game celebrates Go-Go as the Official Music of Washington DC and the cultural legacy behind it.

---

## 2. Player Fantasy

The player feels like they are front-row at the greatest Go-Go show ever staged — the energy of a packed U Street block party, the history of Lincoln Theatre, the bounce of a live Backyard Band set. They feel DC pride, nostalgia, and hypnotic percussion. First-time players discover Go-Go; long-time fans feel it was made for them.

---

## 3. Core Game Loop

```
Select Venue → Choose Band → Choose Song → Watch/Participate in Performance → Earn Crowd Energy → Unlock Next Stage
```

### Modes (Phase 1 scope)
- **Concert Mode** — cinematic performance, free camera roam, no fail state
- **Hype Mode** — rhythm/call-and-response interaction; player drives crowd energy meter
- **Explore Mode** — walk the venue, discover lore, historical markers about DC Go-Go

---

## 4. Venues (Rollout Order)

| Priority | Venue | Location | Type | Notes |
|---|---|---|---|---|
| 1 | Lincoln Theatre | 1215 U St NW | Indoor historic hall | First build — digital twin |
| 2 | Howard Theatre | 620 T St NW | Indoor iconic | Black music history integration |
| 3 | U Street Festival Stage | U St Corridor | Outdoor block party | Summer festival atmosphere |
| 4 | RFK Campus Stage | RFK site | Large outdoor | 2026 "Biggest Show on Earth" anchor |
| 5 | Generic Club | — | Indoor small club | Go-Go pocket venue fallback |

---

## 5. Characters — Band Members

### Pipeline
- Base mesh: MetaHuman (Unreal Engine 5 native)
- Clothing: Custom modeled, DC streetwear + performer gear
- Instruments: Custom rigged props (conga, cowbell, bucket drums, bass)
- Face/hair: Custom per-character over MetaHuman base
- Animations: Mixamo base → custom Go-Go performance layers

### Starting Roster (Phase 1)
- **Lead Talker** (front mic, hype man) — vocal energy, crowd call-and-response
- **Conga Player** — percussionist, main rhythm driver
- **Cowbell / Bucket Drum Player** — signature Go-Go percussion layer
- **Bass Guitar** — low end anchor
- **Keyboard** — melodic fill
- **Backup Vocalists (2)** — response to lead calls

### Character Goals
Each band member has:
- Unique facial design (not generic)
- DC cultural style reference in clothing
- Idle animation loops between performance moments
- Reaction animations tied to Crowd Energy meter

---

## 6. Music System

- **Audio**: Pre-recorded real Go-Go tracks (licensed or original)
- **Sync**: Animation timelines driven by BPM markers in audio metadata
- **Call-and-Response**: Lead Talker fires vocal triggers; player responds via rhythm input
- **Crowd Energy**: 0–100 meter. Rises with correct responses, falls with missed beats
- **Stage Effects**: Lighting, smoke, crowd density scale with Crowd Energy level

---

## 7. Formulas

### Crowd Energy
```
energy_delta = (hit_accuracy * base_gain) - (miss_penalty * miss_count)
base_gain = 5.0
miss_penalty = 3.0
energy_decay_per_second = 0.5  # during non-active response windows
```

### Unlock Threshold
```
venue_unlock = (songs_completed_at_venue >= 3) AND (max_crowd_energy_reached >= 75)
```

---

## 8. Visual Direction

| Element | Target | Tool |
|---|---|---|
| Characters | Realistic, high-detail band members | MetaHuman + custom clothing |
| Animation | Fluid playing + Go-Go dancing | Mixamo base + custom mocap layers |
| Venues | Accurate DC digital twins | Photogrammetry reference + manual UE5 modeling |
| Rendering | Cinematic lighting | UE5 Lumen + Nanite |
| Atmosphere | Premium sports-game feel | Crowd systems, stage FX, post-processing |

---

## 9. Edge Cases

- **Song ends mid-response window**: Complete the response, then fade to end-of-song screen
- **Player idles in Hype Mode**: Energy drains; band reacts with crowd taunts at 20% energy
- **Venue not yet unlocked**: Shows locked state with teaser image and unlock requirement
- **No audio device**: Visual-only mode with on-screen beat indicators replacing audio cues

---

## 10. Dependencies

- UE5 MetaHuman Creator (character pipeline)
- Licensed or original Go-Go audio tracks
- Reference photography/photogrammetry of Lincoln Theatre (U Street)
- Mixamo animation library access
- UE5 Crowd Simulation plugin (for audience)

---

## 11. Tuning Knobs

| Parameter | Default | Range | Notes |
|---|---|---|---|
| `base_gain` | 5.0 | 2.0–10.0 | Crowd energy per correct hit |
| `miss_penalty` | 3.0 | 1.0–6.0 | Penalty per missed beat |
| `energy_decay_per_second` | 0.5 | 0.0–2.0 | Passive drain between windows |
| `venue_unlock_threshold` | 75 | 50–100 | Min crowd energy for unlock |
| `songs_required_per_venue` | 3 | 1–5 | Songs to complete before next venue |

---

## 12. Acceptance Criteria

- [ ] Lincoln Theatre scene loads in UE5 with working Lumen lighting
- [ ] At least 1 MetaHuman band member animates in sync with a Go-Go track
- [ ] Crowd Energy meter rises and falls correctly per formula
- [ ] Player can complete one full song in Hype Mode from start to end-screen
- [ ] At least 2 camera modes functional (cinematic + free roam)
- [ ] 60fps sustained in Concert Mode on target hardware (PC high preset)
