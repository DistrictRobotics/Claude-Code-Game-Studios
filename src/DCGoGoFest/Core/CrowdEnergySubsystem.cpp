#include "CrowdEnergySubsystem.h"

void UCrowdEnergySubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	Thresholds.Sort();
}

void UCrowdEnergySubsystem::RegisterHit(EHitGrade Grade, float Accuracy)
{
	// GDD: energy_delta = (hit_accuracy * base_gain) - (miss_penalty * miss_count)
	const float Delta = (Grade == EHitGrade::Miss)
		? -MissPenalty
		: FMath::Clamp(Accuracy, 0.0f, 1.0f) * BaseGain;

	SetEnergy(Energy + Delta);
}

void UCrowdEnergySubsystem::TickDecay(float DeltaSeconds)
{
	if (DeltaSeconds > 0.0f && EnergyDecayPerSecond > 0.0f)
	{
		SetEnergy(Energy - EnergyDecayPerSecond * DeltaSeconds);
	}
}

void UCrowdEnergySubsystem::ResetForNewSong()
{
	PeakEnergy = 0.0f;
	SetEnergy(0.0f);
}

void UCrowdEnergySubsystem::SetEnergy(float NewEnergy)
{
	const float Previous = Energy;
	Energy = FMath::Clamp(NewEnergy, 0.0f, 100.0f);

	if (FMath::IsNearlyEqual(Previous, Energy))
	{
		return;
	}

	PeakEnergy = FMath::Max(PeakEnergy, Energy);

	for (const float Threshold : Thresholds)
	{
		const bool bWasAbove = Previous >= Threshold;
		const bool bIsAbove = Energy >= Threshold;
		if (bWasAbove != bIsAbove)
		{
			OnEnergyThresholdCrossed.Broadcast(Threshold, bIsAbove);
		}
	}

	OnEnergyChanged.Broadcast(Energy);
}
