"""Lincoln Theatre blockout, 1215 U St NW, Washington DC.

SOURCED DIMENSIONS
  Stage: 38' x 40' proscenium with 37 line sets.
  Seating: 1,225. Hydraulic orchestra pit. Blue cyc. Full black. Hemp house.
  Source: DC Dept. of General Services, "Lincoln Theatre Detail VI of VI:
  Technical Capabilities" (dgs.dc.gov Lincoln_Attachment_A2.pdf), and the
  theatre's own rental page, thelincolntheatre.org.

  AMBIGUITY: the source writes "38' X 40'" without labelling which figure is
  width and which is depth. Taken here as 38 wide x 40 deep. A tech rider from
  the box office would settle it; until then treat as provisional.

UNVERIFIED (estimated, no source found - do not treat as spec)
  Grid height, balcony geometry, house width and length, ceiling height,
  proscenium opening height, wing depth. 37 line sets imply a full fly tower,
  so the grid is certainly higher than modelled here.

Units are cm. Stage centre is the origin; -Y is downstage toward the audience.
"""
import unreal

FT = 30.48

LEVEL = "/Game/Venues/LincolnTheatre/LincolnTheatre"
CUBE = unreal.load_asset("/Engine/BasicShapes/Cube")
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
    les.load_level(LEVEL)
else:
    les.new_level(LEVEL)

OURS = {"stage", "venue", "band_mark", "stage_light", "performance_rig"}
KEEP_LABELS = {"AudioSync", "PerformanceDirector"}
removed = 0
for a in eas.get_all_level_actors():
    if a.get_actor_label() in KEEP_LABELS:
        continue
    if {str(t) for t in (a.tags or [])} & OURS or \
            a.get_actor_label() in ("House_Ambient", "Venue_PostProcess"):
        eas.destroy_actor(a)
        removed += 1
print("PURGED", removed)

# Sourced stage box.
STAGE_W = 38.0 * FT   # 1158 cm
STAGE_D = 40.0 * FT   # 1219 cm
STAGE_H = 4.0 * FT    # deck height above house floor - ESTIMATED
PROSC_H = 24.0 * FT   # proscenium opening height - ESTIMATED

# Estimated house. 1,225 seats is sourced; the footprint that holds them is not.
HOUSE_W = 72.0 * FT
HOUSE_D = 95.0 * FT
CEIL_H = 46.0 * FT

def box(name, loc, scale, tags=()):
    a = eas.spawn_actor_from_object(CUBE, unreal.Vector(*loc))
    a.set_actor_label(name)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if tags:
        a.tags = [unreal.Name(t) for t in tags]
    return a

# Cube primitive is 100cm, so scale = cm / 100.
def s(cm):
    return cm / 100.0

# --- Stage (sourced footprint) ---
box("Stage_Deck", (0, 0, STAGE_H / 2),
    (s(STAGE_W), s(STAGE_D), s(STAGE_H)), ("stage",))

# Blue cyc at the upstage wall (sourced: "Blue cyc").
box("Cyc_Upstage", (0, STAGE_D / 2 + 30, PROSC_H / 2),
    (s(STAGE_W), 0.3, s(PROSC_H)), ("venue",))

# Proscenium arch framing the 38' opening.
box("Proscenium_Top", (0, -STAGE_D / 2 - 20, PROSC_H + 60),
    (s(STAGE_W + 8 * FT), 1.2, 1.8), ("venue",))
box("Proscenium_L", (-(STAGE_W / 2 + 60), -STAGE_D / 2 - 20, PROSC_H / 2),
    (1.2, 1.2, s(PROSC_H)), ("venue",))
box("Proscenium_R", (STAGE_W / 2 + 60, -STAGE_D / 2 - 20, PROSC_H / 2),
    (1.2, 1.2, s(PROSC_H)), ("venue",))

# Wings, hemp-house rail side. Depth ESTIMATED.
box("Stage_Wing_L", (-(STAGE_W / 2 + 140), 0, PROSC_H / 2),
    (2.6, s(STAGE_D * 0.7), s(PROSC_H)), ("venue",))
box("Stage_Wing_R", (STAGE_W / 2 + 140, 0, PROSC_H / 2),
    (2.6, s(STAGE_D * 0.7), s(PROSC_H)), ("venue",))

# Hydraulic orchestra pit (sourced). Footprint ESTIMATED.
PIT_D = 10.0 * FT
box("Orchestra_Pit_Floor", (0, -STAGE_D / 2 - PIT_D / 2, -2.0 * FT),
    (s(STAGE_W * 0.8), s(PIT_D), 0.2), ("venue",))

# --- House (all ESTIMATED) ---
HOUSE_MID = -STAGE_D / 2 - PIT_D - HOUSE_D / 2
box("House_Floor", (0, HOUSE_MID, -10), (s(HOUSE_W), s(HOUSE_D), 0.2), ("venue",))
box("Balcony_Deck", (0, HOUSE_MID - HOUSE_D * 0.28, 20.0 * FT),
    (s(HOUSE_W * 0.9), s(HOUSE_D * 0.34), 0.5), ("venue",))
box("House_Wall_L", (-HOUSE_W / 2, HOUSE_MID, CEIL_H / 2),
    (0.5, s(HOUSE_D), s(CEIL_H)), ("venue",))
box("House_Wall_R", (HOUSE_W / 2, HOUSE_MID, CEIL_H / 2),
    (0.5, s(HOUSE_D), s(CEIL_H)), ("venue",))
box("House_Ceiling", (0, HOUSE_MID, CEIL_H),
    (s(HOUSE_W), s(HOUSE_D), 0.5), ("venue",))

# --- Band marks on the 38x40 deck ---
# Go-Go layout: percussion upstage driving the pocket, talker downstage on the
# crowd. Deck top is STAGE_H.
MARKS = {
    "Mark_Drummer":    (0, 380),
    "Mark_Conga":      (-330, 250),
    "Mark_Cowbell":    (-520, 60),
    "Mark_Keys":       (380, 230),
    "Mark_Bass":       (300, -60),
    "Mark_Backup":     (-180, -230),
    "Mark_LeadTalker": (40, -430),
}
for name, (x, y) in MARKS.items():
    m = eas.spawn_actor_from_class(unreal.TargetPoint, unreal.Vector(x, y, STAGE_H))
    m.set_actor_label(name)
    m.tags = [unreal.Name("band_mark")]

# --- Stage lighting ---
def light(name, loc, rot, color, intensity, cone=28.0):
    a = eas.spawn_actor_from_class(unreal.SpotLight, unreal.Vector(*loc))
    a.set_actor_label(name)
    a.set_actor_rotation(unreal.Rotator(*rot), False)
    c = a.get_component_by_class(unreal.SpotLightComponent)
    c.set_intensity(intensity)
    c.set_light_color(unreal.LinearColor(*color))
    c.set_editor_property("outer_cone_angle", cone)
    c.set_editor_property("attenuation_radius", 6000.0)
    c.set_cast_shadows(True)
    a.tags = [unreal.Name("stage_light")]
    return a

FOH_Y = -STAGE_D / 2 - PIT_D - 25 * FT
light("Key_Front_L", (-520, FOH_Y, 26 * FT), (-40, 60, 0), (1.0, 0.82, 0.62), 90000)
light("Key_Front_R", (520, FOH_Y, 26 * FT), (-40, 120, 0), (1.0, 0.82, 0.62), 90000)
light("Key_Front_C", (0, FOH_Y, 27 * FT), (-42, 90, 0), (1.0, 0.88, 0.72), 75000)
light("Back_Cool_L", (-360, STAGE_D / 2 - 120, 23 * FT), (-55, -70, 0), (0.35, 0.55, 1.0), 60000)
light("Back_Cool_R", (360, STAGE_D / 2 - 120, 23 * FT), (-55, -110, 0), (0.35, 0.55, 1.0), 60000)
light("Wing_Warm_L", (-(STAGE_W / 2 + 60), 60, 13 * FT), (-12, 0, 0), (1.0, 0.55, 0.25), 28000, 45)
light("Wing_Warm_R", (STAGE_W / 2 + 60, 60, 13 * FT), (-12, 180, 0), (1.0, 0.55, 0.25), 28000, 45)

house = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, HOUSE_MID, CEIL_H * 0.7))
house.set_actor_label("House_Ambient")
hc = house.get_component_by_class(unreal.SkyLightComponent)
hc.set_intensity(0.3)
hc.set_light_color(unreal.LinearColor(0.5, 0.45, 0.55))

pp = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, HOUSE_MID, 400))
pp.set_actor_label("Venue_PostProcess")
pp.set_editor_property("unbound", True)
ppset = pp.settings
ppset.set_editor_property("override_bloom_intensity", True)
ppset.set_editor_property("bloom_intensity", 1.4)
ppset.set_editor_property("override_auto_exposure_min_brightness", True)
ppset.set_editor_property("auto_exposure_min_brightness", 0.6)
ppset.set_editor_property("override_auto_exposure_max_brightness", True)
ppset.set_editor_property("auto_exposure_max_brightness", 2.2)
pp.settings = ppset

les.save_current_level()
print(f"STAGE {STAGE_W:.0f} x {STAGE_D:.0f} cm  ({STAGE_W/FT:.0f}ft x {STAGE_D/FT:.0f}ft)")
print("ACTORS", len(eas.get_all_level_actors()))
