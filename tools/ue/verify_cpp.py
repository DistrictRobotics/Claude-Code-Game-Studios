import unreal
for n in ("CrowdEnergySubsystem", "AudioSyncManager", "PerformanceDirector"):
    print("CLASS", n, "->", "OK" if hasattr(unreal, n) else "MISSING")

d = unreal.get_default_object(unreal.CrowdEnergySubsystem)
for p in ("BaseGain", "MissPenalty", "EnergyDecayPerSecond", "Thresholds"):
    print("TUNING", p, d.get_editor_property(p))

print("HAS StartPerformance",
      hasattr(unreal.PerformanceDirector, "start_performance"))
print("HAS PlayTrack", hasattr(unreal.AudioSyncManager, "play_track"))
print("HAS RegisterHit", hasattr(unreal.CrowdEnergySubsystem, "register_hit"))
print("HitGrade values", [x.name for x in unreal.HitGrade])
