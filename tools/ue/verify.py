import unreal
from collections import Counter
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = eas.get_all_level_actors()
print("TOTAL", len(acts))
print("BY CLASS", dict(Counter(a.get_class().get_name() for a in acts).most_common(12)))
for tag in ("stage", "venue", "band_mark", "stage_light"):
    named = [a.get_actor_label() for a in acts if unreal.Name(tag) in (a.tags or [])]
    print(f"{tag}({len(named)}):", sorted(named))
