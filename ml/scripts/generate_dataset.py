from pathlib import Path

from src.data.generator.water_quality_generator import (
    WaterQualityGenerator,
    save_dataset,
    save_metadata,
)


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

SAMPLING_INTERVAL_SECONDS = 5

# Start with 24 hours per scenario.
DURATION_SECONDS = 24 * 60 * 60

START_TIME = "2026-01-01 00:00:00"

OUTPUT_ROOT = Path("data/generated")


# ============================================================
# SCENARIOS
# ============================================================

SCENARIOS = {
    "healthy": "healthy",
    "temperature_increase": "temperature_increase",
    "do_depletion": "do_depletion",
    "turbidity_event": "turbidity_event",
    "tds_increase": "tds_increase",
    "ph_drift": "ph_drift",
    "compound_stress": "compound_stress",
    "recovery": "recovery",
}


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    generator = WaterQualityGenerator(
        seed=SEED,
        sampling_interval_seconds=SAMPLING_INTERVAL_SECONDS,
    )

    print("=" * 60)
    print("Synthetic Water-Quality Dataset Generator")
    print("=" * 60)

    print(
        f"Sampling interval : "
        f"{SAMPLING_INTERVAL_SECONDS} seconds"
    )

    print(
        f"Duration/scenario : "
        f"{DURATION_SECONDS // 3600} hours"
    )

    print(f"Random seed       : {SEED}")
    print()

    for scenario_folder, scenario_name in SCENARIOS.items():

        print(
            f"Generating scenario: "
            f"{scenario_name}"
        )

        dataset = generator.generate(
            scenario=scenario_name,
            start_time=START_TIME,
            duration_seconds=DURATION_SECONDS,
        )

        scenario_directory = (
            OUTPUT_ROOT / scenario_folder
        )

        scenario_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        csv_path = (
            scenario_directory
            / f"{scenario_name}.csv"
        )

        metadata_path = (
            scenario_directory
            / f"{scenario_name}_metadata.json"
        )

        save_dataset(
            dataframe=dataset,
            output_path=csv_path,
        )

        save_metadata(
            dataframe=dataset,
            output_path=metadata_path,
            seed=SEED,
            sampling_interval_seconds=(
                SAMPLING_INTERVAL_SECONDS
            ),
        )

        print(
            f"  Samples : {len(dataset):,}"
        )

        print(
            f"  CSV     : {csv_path}"
        )

        print(
            f"  Metadata: {metadata_path}"
        )

        print()

    print("=" * 60)
    print("Dataset generation completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()