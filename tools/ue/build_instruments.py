"""Go-Go instrument blockouts, built from primitives as original geometry.

Go-Go's identity is its percussion section: congas and timbales carrying the
pocket, multiple cowbells, rototoms, plus a trap kit. These are generic
physical objects, so the geometry here is original and carries no third-party
rights. Proportions follow standard instrument sizes, not any specific band's
gear.

Placement snaps to the Mark_* TargetPoints the venue script creates.
"""
import unreal

CYL = unreal.load_asset("/Engine/BasicShapes/Cylinder")
CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level("/Game/Venues/LincolnTheatre/LincolnTheatre")

marks = {a.get_actor_label(): a.get_actor_location()
         for a in eas.get_all_level_actors()
         if unreal.Name("band_mark") in (a.tags or [])}
print("MARKS", sorted(marks))

removed = 0
for a in eas.get_all_level_actors():
    if unreal.Name("instrument") in (a.tags or []):
        eas.destroy_actor(a)
        removed += 1
print("PURGED", removed)

def part(name, mesh, loc, scale, rot=(0, 0, 0)):
    a = eas.spawn_actor_from_object(mesh, unreal.Vector(*loc))
    a.set_actor_label(name)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if rot != (0, 0, 0):
        a.set_actor_rotation(unreal.Rotator(*rot), False)
    a.tags = [unreal.Name("instrument")]
    return a

def at(mark, dx=0, dy=0, dz=0):
    b = marks[mark]
    return (b.x + dx, b.y + dy, b.z + dz)

made = []

# --- Congas: two drums on a stand. Quinto ~29cm head, conga ~30cm, 75cm tall.
if "Mark_Conga" in marks:
    for i, (dx, h, d) in enumerate([(-22, 75, 29), (22, 78, 30)]):
        made.append(part(f"Conga_{i+1}_Shell", CYL, at("Mark_Conga", dx, 0, h / 2),
                         (d / 100.0, d / 100.0, h / 100.0)))
    # Timbales alongside, standard in a Go-Go percussion rack.
    for i, dx in enumerate((-70, -44)):
        made.append(part(f"Timbale_{i+1}", CYL, at("Mark_Conga", dx, 35, 90),
                         (0.33, 0.33, 0.18)))

# --- Cowbells on a rack. Go-Go runs several at different pitches.
if "Mark_Cowbell" in marks:
    made.append(part("Cowbell_Rack_Post", CYL, at("Mark_Cowbell", 0, 0, 50),
                     (0.06, 0.06, 1.0)))
    for i, dx in enumerate((-24, -8, 8, 24)):
        made.append(part(f"Cowbell_{i+1}", CUBE, at("Mark_Cowbell", dx, 10, 95),
                         (0.09, 0.14, 0.2)))

# --- Trap kit: kick, snare, two toms, floor tom, hats, two cymbals.
if "Mark_Drummer" in marks:
    made.append(part("Kick_Drum", CYL, at("Mark_Drummer", 0, -40, 28),
                     (0.56, 0.56, 0.45), (0, 90, 0)))
    made.append(part("Snare", CYL, at("Mark_Drummer", -38, -8, 58),
                     (0.35, 0.35, 0.14)))
    for i, (dx, dz, dia) in enumerate([(-18, 88, 0.28), (16, 90, 0.31)]):
        made.append(part(f"Tom_{i+1}", CYL, at("Mark_Drummer", dx, 18, dz),
                         (dia, dia, 0.2), (12, 0, 0)))
    made.append(part("Floor_Tom", CYL, at("Mark_Drummer", 52, -4, 42),
                     (0.4, 0.4, 0.36)))
    made.append(part("HiHat", CYL, at("Mark_Drummer", -58, -14, 78),
                     (0.35, 0.35, 0.02)))
    for i, (dx, dy, dz, dia) in enumerate([(-46, 40, 112, 0.42), (46, 36, 108, 0.48)]):
        made.append(part(f"Cymbal_{i+1}", CYL, at("Mark_Drummer", dx, dy, dz),
                         (dia, dia, 0.015), (14, 0, 0)))
    # Rototoms - a Go-Go staple on top of the kit.
    for i, dx in enumerate((-4, 22)):
        made.append(part(f"Rototom_{i+1}", CYL, at("Mark_Drummer", dx, 52, 104),
                         (0.22, 0.22, 0.1)))

# --- Keys: two tiers on an X-stand.
if "Mark_Keys" in marks:
    made.append(part("Keys_Lower", CUBE, at("Mark_Keys", 0, 0, 72),
                     (1.3, 0.34, 0.1)))
    made.append(part("Keys_Upper", CUBE, at("Mark_Keys", 0, 22, 100),
                     (1.25, 0.32, 0.09)))

# --- Bass guitar on a stand.
if "Mark_Bass" in marks:
    made.append(part("Bass_Body", CUBE, at("Mark_Bass", 0, 0, 95),
                     (0.34, 0.12, 0.46), (0, 0, 12)))
    made.append(part("Bass_Neck", CUBE, at("Mark_Bass", 44, 6, 118),
                     (0.86, 0.07, 0.07), (0, 0, 12)))

# --- Mic stands for the talker and backup.
for mark, label in (("Mark_LeadTalker", "Lead"), ("Mark_Backup", "Backup")):
    if mark in marks:
        made.append(part(f"MicStand_{label}_Post", CYL, at(mark, 0, 0, 70),
                         (0.05, 0.05, 1.4)))
        made.append(part(f"Mic_{label}", CYL, at(mark, 0, 8, 143),
                         (0.08, 0.08, 0.14), (70, 0, 0)))

les.save_current_level()
print("INSTRUMENT PARTS", len(made))
print("TOTAL ACTORS", len(eas.get_all_level_actors()))
