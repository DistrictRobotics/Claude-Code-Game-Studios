#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "CrowdEnergySubsystem.generated.h"

UENUM(BlueprintType)
enum class EHitGrade : uint8
{
	Miss    UMETA(DisplayName = "Miss"),
	Good    UMETA(DisplayName = "Good"),
	Perfect UMETA(DisplayName = "Perfect")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnEnergyChanged, float, NewEnergy);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnEnergyThresholdCrossed, float, Threshold, bool, bRising);

/**
 * Tracks crowd energy for the current performance and persists it across level loads.
 * Tuning values are config-backed so balance changes need no recompile.
 */
UCLASS(Config = Game)
class DCGOGOFEST_API UCrowdEnergySubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	/** Applies one scored input. Accuracy is 0..1 and ignored for a Miss. */
	UFUNCTION(BlueprintCallable, Category = "Crowd Energy")
	void RegisterHit(EHitGrade Grade, float Accuracy);

	/** Passive drain, called once per frame while no response window is open. */
	UFUNCTION(BlueprintCallable, Category = "Crowd Energy")
	void TickDecay(float DeltaSeconds);

	UFUNCTION(BlueprintCallable, Category = "Crowd Energy")
	void ResetForNewSong();

	UFUNCTION(BlueprintPure, Category = "Crowd Energy")
	float GetEnergy() const { return Energy; }

	UFUNCTION(BlueprintPure, Category = "Crowd Energy")
	float GetPeakEnergy() const { return PeakEnergy; }

	UPROPERTY(BlueprintAssignable, Category = "Crowd Energy")
	FOnEnergyChanged OnEnergyChanged;

	UPROPERTY(BlueprintAssignable, Category = "Crowd Energy")
	FOnEnergyThresholdCrossed OnEnergyThresholdCrossed;

	/** Crowd energy granted for a perfectly timed hit. GDD default 5.0, range 2..10. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category = "Tuning")
	float BaseGain = 5.0f;

	/** Energy lost per missed response. GDD default 3.0, range 1..6. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category = "Tuning")
	float MissPenalty = 3.0f;

	/** Passive drain per second between response windows. GDD default 0.5, range 0..2. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category = "Tuning")
	float EnergyDecayPerSecond = 0.5f;

	/** Thresholds that fire OnEnergyThresholdCrossed. 20 drives band taunts, 75 gates unlocks. */
	UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category = "Tuning")
	TArray<float> Thresholds = {20.0f, 50.0f, 75.0f};

private:
	void SetEnergy(float NewEnergy);

	UPROPERTY(Transient)
	float Energy = 0.0f;

	UPROPERTY(Transient)
	float PeakEnergy = 0.0f;
};
