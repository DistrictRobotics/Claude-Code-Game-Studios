#include "AudioSyncManager.h"

#include "Components/AudioComponent.h"
#include "Sound/SoundBase.h"

AAudioSyncManager::AAudioSyncManager()
{
	PrimaryActorTick.bCanEverTick = true;
	AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("AudioComponent"));
	SetRootComponent(AudioComponent);
	AudioComponent->bAutoActivate = false;
}

void AAudioSyncManager::PlayTrack(USoundBase* Track, float InBeatsPerMinute, int32 InBeatsPerBar)
{
	if (!Track || InBeatsPerMinute <= 0.0f)
	{
		UE_LOG(LogTemp, Warning,
			TEXT("AudioSyncManager: PlayTrack needs a track and a positive BPM."));
		return;
	}

	BeatsPerMinute = InBeatsPerMinute;
	BeatsPerBar = FMath::Max(1, InBeatsPerBar);
	SecondsPerBeat = 60.0f / BeatsPerMinute;
	ElapsedSeconds = 0.0f;
	LastBeatIndex = -1;
	bPlaying = true;

	AudioComponent->SetSound(Track);
	AudioComponent->Play();
}

void AAudioSyncManager::StopTrack()
{
	if (bWindowOpen)
	{
		bWindowOpen = false;
		OnResponseWindow.Broadcast(false);
	}

	bPlaying = false;
	AudioComponent->Stop();
}

void AAudioSyncManager::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!bPlaying)
	{
		return;
	}

	ElapsedSeconds += DeltaSeconds;

	const int32 BeatIndex = FMath::FloorToInt(ElapsedSeconds / SecondsPerBeat);
	if (BeatIndex > LastBeatIndex)
	{
		LastBeatIndex = BeatIndex;
		OnBeat.Broadcast(BeatIndex, BeatIndex / BeatsPerBar);
	}

	UpdateResponseWindow();
}

void AAudioSyncManager::UpdateResponseWindow()
{
	// Distance to the nearest downbeat, so the window straddles the beat
	// rather than opening after it has already passed.
	const float BeatPhase = FMath::Fmod(ElapsedSeconds, SecondsPerBeat);
	const float ToNearestBeat = FMath::Min(BeatPhase, SecondsPerBeat - BeatPhase);

	const int32 NearestBeat = FMath::RoundToInt(ElapsedSeconds / SecondsPerBeat);
	const bool bIsDownbeat = (NearestBeat % BeatsPerBar) == 0;
	const int32 Bar = NearestBeat / BeatsPerBar;
	const bool bScheduledBar =
		ResponseWindowEveryNBars <= 1 || (Bar % ResponseWindowEveryNBars) == 0;

	const bool bShouldBeOpen =
		bIsDownbeat && bScheduledBar && ToNearestBeat <= ResponseWindowHalfWidth;

	if (bShouldBeOpen != bWindowOpen)
	{
		bWindowOpen = bShouldBeOpen;
		OnResponseWindow.Broadcast(bWindowOpen);
	}
}
