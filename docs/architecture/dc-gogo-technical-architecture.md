# DC GoGo Fest — Technical Architecture

**Date**: 2026-11-05  
**Engine**: Unreal Engine 5 (latest stable)  
**Language**: C++ (core systems) + Blueprints (gameplay logic, rapid prototyping)

---

## System Map

```
[Player Input] 
      ↓
[Hype Mode Controller]
      ↓
[Crowd Energy Manager] ←→ [Band Reaction System]
      ↓
[Stage Effects Controller]
      ↓
[Audio Manager] ←→ [Animation Sync System]
                          ↓
                   [Band Member Characters]
                   (MetaHuman + custom clothing/instruments)
                          ↓
                   [Venue Scene] (Lincoln Theatre → others)
```

---

## Core Systems

### 1. VenueManager
- Loads/unloads venue levels (level streaming)
- Manages ambient crowd, lighting state, weather
- Exposes venue metadata (name, capacity, historical notes)
- **File**: `Source/DCGoGoFest/Venue/VenueManager.h`

### 2. BandMemberComponent
- Attached to each MetaHuman actor
- Drives instrument animation state machine
- Receives energy level events and plays matching reactions
- **File**: `Source/DCGoGoFest/Characters/BandMemberComponent.h`

### 3. AudioSyncManager
- Wraps Unreal's MetaSounds
- Parses BPM markers from audio metadata
- Fires `OnBeatWindow` events at correct intervals
- **File**: `Source/DCGoGoFest/Audio/AudioSyncManager.h`

### 4. CrowdEnergySubsystem (GameInstanceSubsystem)
- Global subsystem, persists across level loads
- Tracks energy float (0.0–100.0)
- Applies formula: `delta = (accuracy * base_gain) - (misses * penalty)`
- Broadcasts `OnEnergyChanged`, `OnEnergyThresholdCrossed`
- **File**: `Source/DCGoGoFest/Core/CrowdEnergySubsystem.h`

### 5. HypeModeController (PlayerController extension)
- Detects player input during response windows
- Scores timing (Perfect / Good / Miss)
- Sends result to CrowdEnergySubsystem
- **File**: `Source/DCGoGoFest/Gameplay/HypeModeController.h`

### 6. CameraDirector
- Manages concert camera modes: Cinematic, Free Roam, Follow Performer
- Cinematic mode runs pre-authored Sequencer camera paths
- Free Roam: standard UE5 fly camera with collision
- **File**: `Source/DCGoGoFest/Camera/CameraDirector.h`

### 7. UnlockRegistry (SaveGame)
- Persists which venues and songs are unlocked
- Tracks per-venue high scores
- **File**: `Source/DCGoGoFest/Save/UnlockRegistry.h`

---

## Character Pipeline

```
MetaHuman Creator (web)
    → Export to UE5 project
    → Add BandMemberComponent
    → Attach instrument skeletal mesh
    → Import Mixamo base animations
    → Retarget to MetaHuman skeleton (IK Retargeter)
    → Layer custom Go-Go performance animations
    → Apply custom clothing (groom + cloth sim)
```

### Instrument Rigs (Phase 1)
- Conga drum (static mesh + procedural hand IK)
- Cowbell + stick (simple attach socket)
- Microphone (held prop, lip-sync driven)
- Bass guitar (skeletal mesh, finger pose blend)

---

## Venue Pipeline — Lincoln Theatre

```
Reference Photos / Floor Plans (U Street)
    → Rough blockout in UE5 (BSP or modular kit)
    → High-detail modeling (Blender → FBX → UE5)
    → Nanite mesh import
    → Lumen lighting setup (emissive stage lights, practical fixtures)
    → Crowd placement (UE5 Mass Crowd or instanced meshes)
    → Audio reverb zones (EQ per room area)
    → Collision pass + performance optimization
```

---

## Rendering Budget (Target: 60fps, PC High Preset)

| Budget Item | Target |
|---|---|
| Total frame time | 16.67ms |
| Characters on screen | 7 band members max |
| LOD switching | Auto (Nanite) |
| Draw calls | < 800 |
| Shadow maps | Cascaded (3 levels) |
| Lumen GI | Enabled, medium quality |
| Post-process | Bloom, motion blur, color grade |

---

## Project Folder Structure (UE5)

```
DCGoGoFest/
├── Content/
│   ├── Characters/
│   │   ├── MetaHumans/        # Exported MetaHuman assets
│   │   ├── Clothing/          # Custom clothing meshes
│   │   └── Instruments/       # Instrument props
│   ├── Venues/
│   │   ├── LincolnTheatre/    # Phase 1
│   │   └── HowardTheatre/     # Phase 2
│   ├── Audio/
│   │   ├── Tracks/            # Licensed Go-Go stems
│   │   └── MetaSounds/        # Audio graph assets
│   ├── UI/                    # UMG widgets
│   └── VFX/                   # Niagara stage effects
├── Source/
│   └── DCGoGoFest/
│       ├── Audio/
│       ├── Camera/
│       ├── Characters/
│       ├── Core/
│       ├── Gameplay/
│       ├── Save/
│       └── Venue/
└── Config/
```

---

## Phase 1 Milestones

| Milestone | Deliverable | Gate |
|---|---|---|
| M0 — Setup | UE5 project created, source control wired | Repo commit |
| M1 — Venue Shell | Lincoln Theatre blockout in engine, Lumen lighting | Screenshot review |
| M2 — First Character | 1 MetaHuman band member animating in venue | Video capture |
| M3 — Audio Sync | 1 Go-Go track playing with animation locked to BPM | Playtest |
| M4 — Hype Mode | Player input + Crowd Energy meter functional | QA pass |
| M5 — Vertical Slice | Full song playable start to end, all systems connected | Playtest + video |
