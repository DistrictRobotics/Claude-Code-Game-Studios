import unreal

LEVEL = "/Game/Venues/LincolnTheatre/LincolnTheatre"
CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
    les.load_level(LEVEL)
else:
    les.new_level(LEVEL)

# Idempotent: remove everything a previous run of this script created.
OURS = {"stage", "venue", "band_mark", "stage_light"}
removed = 0
for a in eas.get_all_level_actors():
    tags = {str(t) for t in (a.tags or [])}
    if tags & OURS or a.get_actor_label() in ("House_Ambient", "Venue_PostProcess"):
        eas.destroy_actor(a)
        removed += 1
print("PURGED", removed)

def box(name, loc, scale, tags=()):
    a = eas.spawn_actor_from_object(CUBE, unreal.Vector(*loc))
    a.set_actor_label(name)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if tags:
        a.tags = [unreal.Name(t) for t in tags]
    return a

# Lincoln Theatre, 1215 U St NW. Historic hall, ~1200 capacity.
# Blockout scale in cm. Stage is 1200 wide x 800 deep, 120 high.
box("Stage_Deck",      (0, 0, 60),        (12.0, 8.0, 1.2),  ("stage",))
box("Stage_Back_Wall", (0, 450, 500),     (12.0, 0.5, 10.0), ("venue",))
box("Stage_Wing_L",    (-650, 100, 400),  (1.0, 7.0, 8.0),   ("venue",))
box("Stage_Wing_R",    (650, 100, 400),   (1.0, 7.0, 8.0),   ("venue",))
box("House_Floor",     (0, -1400, -10),   (24.0, 20.0, 0.2), ("venue",))
box("Balcony_Deck",    (0, -1500, 420),   (22.0, 8.0, 0.4),  ("venue",))
box("House_Wall_L",    (-1250, -900, 450),(0.5, 28.0, 9.0),  ("venue",))
box("House_Wall_R",    (1250, -900, 450), (0.5, 28.0, 9.0),  ("venue",))
box("House_Ceiling",   (0, -900, 900),    (25.0, 28.0, 0.4), ("venue",))
box("Proscenium_Top",  (0, 420, 820),     (13.0, 1.0, 1.6),  ("venue",))

# Band marks on the stage deck (deck top is z=120).
# 7-piece from the GDD; the user's 5 for now, extras kept for later.
MARKS = {
    "Mark_LeadTalker": (0, -180),
    "Mark_Drummer":    (0, 300),
    "Mark_Conga":      (-380, 140),
    "Mark_Keys":       (420, 140),
    "Mark_Backup":     (-180, -40),
    "Mark_Bass":       (280, -40),
    "Mark_Cowbell":    (-520, -40),
}
for name, (x, y) in MARKS.items():
    m = eas.spawn_actor_from_class(unreal.TargetPoint, unreal.Vector(x, y, 120))
    m.set_actor_label(name)
    m.tags = [unreal.Name("band_mark")]

# Stage lighting. Warm wash from front, cool backlight, practicals in the wings.
def light(name, loc, rot, color, intensity, cone=28.0):
    a = eas.spawn_actor_from_class(unreal.SpotLight, unreal.Vector(*loc))
    a.set_actor_label(name)
    a.set_actor_rotation(unreal.Rotator(*rot), False)
    c = a.get_component_by_class(unreal.SpotLightComponent)
    c.set_intensity(intensity)
    c.set_light_color(unreal.LinearColor(*color))
    c.set_editor_property("outer_cone_angle", cone)
    c.set_editor_property("attenuation_radius", 4000.0)
    c.set_cast_shadows(True)
    a.tags = [unreal.Name("stage_light")]
    return a

light("Key_Front_L",  (-500, -900, 780), (-42, 55, 0),  (1.0, 0.82, 0.62), 60000)
light("Key_Front_R",  (500, -900, 780),  (-42, 125, 0), (1.0, 0.82, 0.62), 60000)
light("Key_Front_C",  (0, -1000, 800),   (-45, 90, 0),  (1.0, 0.88, 0.72), 50000)
light("Back_Cool_L",  (-350, 400, 760),  (-55, -70, 0), (0.35, 0.55, 1.0), 45000)
light("Back_Cool_R",  (350, 400, 760),   (-55, -110, 0),(0.35, 0.55, 1.0), 45000)
light("Wing_Warm_L",  (-620, 80, 420),   (-10, 0, 0),   (1.0, 0.55, 0.25), 20000, 45)
light("Wing_Warm_R",  (620, 80, 420),    (-10, 180, 0), (1.0, 0.55, 0.25), 20000, 45)

house = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, -600, 600))
house.set_actor_label("House_Ambient")
hc = house.get_component_by_class(unreal.SkyLightComponent)
hc.set_intensity(0.35)
hc.set_light_color(unreal.LinearColor(0.5, 0.45, 0.55))

pp = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, -600, 400))
pp.set_actor_label("Venue_PostProcess")
pp.set_editor_property("unbound", True)
s = pp.settings
s.set_editor_property("override_bloom_intensity", True)
s.set_editor_property("bloom_intensity", 1.4)
s.set_editor_property("override_auto_exposure_min_brightness", True)
s.set_editor_property("auto_exposure_min_brightness", 0.6)
s.set_editor_property("override_auto_exposure_max_brightness", True)
s.set_editor_property("auto_exposure_max_brightness", 2.2)
pp.settings = s

les.save_current_level()
print("ACTORS", len(eas.get_all_level_actors()))
print("LEVEL", unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name())
