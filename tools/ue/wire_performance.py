import unreal

LEVEL = "/Game/Venues/LincolnTheatre/LincolnTheatre"
TABLE_PKG = "/Game/Audio/DT_GoGoSongs"

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level(LEVEL)

# Song set list as a DataTable, so songs are data and need no recompile.
if not unreal.EditorAssetLibrary.does_asset_exist(TABLE_PKG):
    f = unreal.DataTableFactory()
    f.set_editor_property("struct", unreal.ScriptStruct.cast(
        unreal.load_object(None, "/Script/DCGoGoFest.GoGoSongRow")))
    unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "DT_GoGoSongs", "/Game/Audio", unreal.DataTable, f)
    print("TABLE created")
else:
    print("TABLE exists")

# Idempotent: drop any previous rig actors before respawning.
for a in eas.get_all_level_actors():
    if a.get_actor_label() in ("AudioSync", "PerformanceDirector"):
        eas.destroy_actor(a)

sync = eas.spawn_actor_from_class(unreal.AudioSyncManager, unreal.Vector(0, 200, 140))
sync.set_actor_label("AudioSync")
sync.tags = [unreal.Name("performance_rig")]

director = eas.spawn_actor_from_class(unreal.PerformanceDirector, unreal.Vector(0, 200, 200))
director.set_actor_label("PerformanceDirector")
director.tags = [unreal.Name("performance_rig")]
director.set_editor_property("audio_sync", sync)
director.set_editor_property("song_table", unreal.load_asset(TABLE_PKG))

les.save_current_level()

print("SYNC", sync.get_actor_label())
print("DIRECTOR", director.get_actor_label())
print("DIRECTOR.audio_sync ->",
      director.get_editor_property("audio_sync").get_actor_label())
print("DIRECTOR.song_table ->",
      director.get_editor_property("song_table").get_name())
print("SONGS", list(director.get_available_songs()))
print("TOTAL ACTORS", len(eas.get_all_level_actors()))
