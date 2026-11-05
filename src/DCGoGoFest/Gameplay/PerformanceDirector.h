#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "GameFramework/Actor.h"
#include "PerformanceDirector.generated.h"

class AAudioSyncManager;
class UCrowdEnergySubsystem;
class USoundBase;

/** One playable song. Authored in a DataTable so adding songs needs no recompile. */
USTRUCT(BlueprintType)
struct FGoGoSongRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Song")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Song")
	TSoftObjectPtr<USoundBase> Track;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Song")
	float BeatsPerMinute = 100.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Song")
	int32 BeatsPerBar = 4;
};

/**
 * Entry point for driving a performance. Exposed to Blueprint, Python and the
 * Remote Control API so a song can be triggered without a packaged build.
 */
UCLASS(Blueprintable)
class DCGOGOFEST_API APerformanceDirector : public AActor
{
	GENERATED_BODY()

public:
	APerformanceDirector();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	/** Starts the song with this DataTable row name. Returns false if it is missing. */
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Performance")
	bool StartPerformance(FName SongRowName);

	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Performance")
	void StopPerformance();

	/** Row names available in SongTable, for API callers listing the set list. */
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Performance")
	TArray<FName> GetAvailableSongs() const;

	UFUNCTION(BlueprintPure, Category = "Performance")
	float GetCrowdEnergy() const;

	/** Scores an input against the open response window. Accuracy is 0..1. */
	UFUNCTION(BlueprintCallable, Category = "Performance")
	void SubmitResponse(float Accuracy);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance")
	TObjectPtr<UDataTable> SongTable;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Performance")
	TObjectPtr<AAudioSyncManager> AudioSync;

protected:
	UFUNCTION()
	void HandleResponseWindow(bool bOpen);

private:
	UCrowdEnergySubsystem* GetEnergy() const;

	bool bResponseWindowOpen = false;
	bool bRespondedThisWindow = false;
};
