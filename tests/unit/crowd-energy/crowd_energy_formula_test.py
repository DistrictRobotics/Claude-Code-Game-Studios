import unreal

# Exercise the GDD formula on a real subsystem instance.
# base_gain=5.0, miss_penalty=3.0, decay=0.5/s, clamped 0..100
# The subsystem's logic has no game-instance dependency, so a standalone
# instance exercises the real formula without needing PIE.
gi = unreal.new_object(unreal.GameInstance)
es = unreal.new_object(unreal.CrowdEnergySubsystem, gi)

fails = []
def check(label, got, want, tol=0.001):
    ok = abs(got - want) < tol
    print(f"{'PASS' if ok else 'FAIL'} {label}: got {got:.3f} want {want:.3f}")
    if not ok:
        fails.append(label)

if es:
    es.reset_for_new_song()
    check("start at zero", es.get_energy(), 0.0)

    es.register_hit(unreal.HitGrade.PERFECT, 1.0)
    check("perfect hit = +5", es.get_energy(), 5.0)

    es.register_hit(unreal.HitGrade.GOOD, 0.5)
    check("half accuracy = +2.5", es.get_energy(), 7.5)

    es.register_hit(unreal.HitGrade.MISS, 0.0)
    check("miss = -3", es.get_energy(), 4.5)

    es.tick_decay(2.0)
    check("2s decay = -1.0", es.get_energy(), 3.5)

    for _ in range(10):
        es.tick_decay(10.0)
    check("clamps at zero", es.get_energy(), 0.0)

    for _ in range(40):
        es.register_hit(unreal.HitGrade.PERFECT, 1.0)
    check("clamps at 100", es.get_energy(), 100.0)
    check("peak tracked", es.get_peak_energy(), 100.0)

    es.reset_for_new_song()
    check("reset clears peak", es.get_peak_energy(), 0.0)

    print("RESULT", "ALL_PASS" if not fails else f"FAILURES: {fails}")
else:
    print("RESULT SKIPPED_NO_INSTANCE")
