#include "PerformanceDirector.h"

#include "AudioSyncManager.h"
#include "CrowdEnergySubsystem.h"
#include "Engine/GameInstance.h"
#include "Kismet/GameplayStatics.h"

APerformanceDirector::APerformanceDirector()
{
	PrimaryActorTick.bCanEverTick = true;
}

void APerformanceDirector::BeginPlay()
{
	Super::BeginPlay();

	if (!AudioSync)
	{
		AudioSync = Cast<AAudioSyncManager>(
			UGameplayStatics::GetActorOfClass(GetWorld(), AAudioSyncManager::StaticClass()));
	}

	if (AudioSync)
	{
		AudioSync->OnResponseWindow.AddDynamic(this, &APerformanceDirector::HandleResponseWindow);
	}
}

UCrowdEnergySubsystem* APerformanceDirector::GetEnergy() const
{
	const UGameInstance* GI = UGameplayStatics::GetGameInstance(GetWorld());
	return GI ? GI->GetSubsystem<UCrowdEnergySubsystem>() : nullptr;
}

bool APerformanceDirector::StartPerformance(FName SongRowName)
{
	if (!SongTable || !AudioSync)
	{
		UE_LOG(LogTemp, Warning,
			TEXT("PerformanceDirector: needs both SongTable and AudioSync set."));
		return false;
	}

	const FGoGoSongRow* Row =
		SongTable->FindRow<FGoGoSongRow>(SongRowName, TEXT("StartPerformance"));
	if (!Row)
	{
		UE_LOG(LogTemp, Warning,
			TEXT("PerformanceDirector: no song row '%s'."), *SongRowName.ToString());
		return false;
	}

	USoundBase* Track = Row->Track.LoadSynchronous();
	if (!Track)
	{
		UE_LOG(LogTemp, Warning,
			TEXT("PerformanceDirector: song row '%s' has no track asset."),
			*SongRowName.ToString());
		return false;
	}

	if (UCrowdEnergySubsystem* Energy = GetEnergy())
	{
		Energy->ResetForNewSong();
	}

	AudioSync->PlayTrack(Track, Row->BeatsPerMinute, Row->BeatsPerBar);
	return true;
}

void APerformanceDirector::StopPerformance()
{
	if (AudioSync)
	{
		AudioSync->StopTrack();
	}
}

TArray<FName> APerformanceDirector::GetAvailableSongs() const
{
	return SongTable ? SongTable->GetRowNames() : TArray<FName>();
}

float APerformanceDirector::GetCrowdEnergy() const
{
	const UCrowdEnergySubsystem* Energy = GetEnergy();
	return Energy ? Energy->GetEnergy() : 0.0f;
}

void APerformanceDirector::HandleResponseWindow(bool bOpen)
{
	// A window that closes without a response counts as a miss.
	if (!bOpen && bResponseWindowOpen && !bRespondedThisWindow)
	{
		if (UCrowdEnergySubsystem* Energy = GetEnergy())
		{
			Energy->RegisterHit(EHitGrade::Miss, 0.0f);
		}
	}

	bResponseWindowOpen = bOpen;
	if (bOpen)
	{
		bRespondedThisWindow = false;
	}
}

void APerformanceDirector::SubmitResponse(float Accuracy)
{
	UCrowdEnergySubsystem* Energy = GetEnergy();
	if (!Energy)
	{
		return;
	}

	if (!bResponseWindowOpen)
	{
		Energy->RegisterHit(EHitGrade::Miss, 0.0f);
		return;
	}

	bRespondedThisWindow = true;
	const EHitGrade Grade = (Accuracy >= 0.8f) ? EHitGrade::Perfect : EHitGrade::Good;
	Energy->RegisterHit(Grade, Accuracy);
}

void APerformanceDirector::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// Energy only drains while no window is open, per the GDD.
	if (!bResponseWindowOpen)
	{
		if (UCrowdEnergySubsystem* Energy = GetEnergy())
		{
			Energy->TickDecay(DeltaSeconds);
		}
	}
}
