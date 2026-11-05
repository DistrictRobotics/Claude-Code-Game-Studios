#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioSyncManager.generated.h"

class UAudioComponent;
class USoundBase;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnBeat, int32, BeatIndex, int32, BarIndex);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnResponseWindow, bool, bOpen);

/**
 * Plays a track and derives beat timing from its BPM, so animation and gameplay
 * can key off OnBeat instead of polling playback position.
 */
UCLASS(Blueprintable)
class DCGOGOFEST_API AAudioSyncManager : public AActor
{
	GENERATED_BODY()

public:
	AAudioSyncManager();

	virtual void Tick(float DeltaSeconds) override;

	/** Starts a track. BPM must be supplied because Linux has no reliable metadata probe. */
	UFUNCTION(BlueprintCallable, Category = "Audio Sync")
	void PlayTrack(USoundBase* Track, float InBeatsPerMinute, int32 InBeatsPerBar = 4);

	UFUNCTION(BlueprintCallable, Category = "Audio Sync")
	void StopTrack();

	/** Seconds since playback started, or 0 when stopped. */
	UFUNCTION(BlueprintPure, Category = "Audio Sync")
	float GetPlaybackSeconds() const { return bPlaying ? ElapsedSeconds : 0.0f; }

	UFUNCTION(BlueprintPure, Category = "Audio Sync")
	int32 GetCurrentBeat() const { return LastBeatIndex; }

	UFUNCTION(BlueprintPure, Category = "Audio Sync")
	bool IsPlaying() const { return bPlaying; }

	/** Fires once per beat while a track plays. */
	UPROPERTY(BlueprintAssignable, Category = "Audio Sync")
	FOnBeat OnBeat;

	/** Opens and closes the call-and-response input window around each downbeat. */
	UPROPERTY(BlueprintAssignable, Category = "Audio Sync")
	FOnResponseWindow OnResponseWindow;

	/** How wide the input window is on each side of a downbeat, in seconds. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tuning")
	float ResponseWindowHalfWidth = 0.18f;

	/** Open a response window every Nth bar. 1 means every bar. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tuning")
	int32 ResponseWindowEveryNBars = 2;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio Sync")
	TObjectPtr<UAudioComponent> AudioComponent;

private:
	void UpdateResponseWindow();

	float BeatsPerMinute = 0.0f;
	int32 BeatsPerBar = 4;
	float SecondsPerBeat = 0.0f;
	float ElapsedSeconds = 0.0f;
	int32 LastBeatIndex = -1;
	bool bPlaying = false;
	bool bWindowOpen = false;
};
