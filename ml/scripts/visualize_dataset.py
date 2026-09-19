from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_ROOT = Path("data/generated")

OUTPUT_ROOT = Path(
    "results/reports/figures/dataset"
)

OUTPUT_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


PARAMETERS = [
    "pH",
    "turbidity",
    "temperature",
    "DO",
    "TDS",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset(csv_path: Path) -> pd.DataFrame:

    dataframe = pd.read_csv(
        csv_path,
        parse_dates=["timestamp"],
    )

    dataframe = dataframe.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    return dataframe


# ============================================================
# TIME-SERIES PLOTS
# ============================================================

def plot_time_series(
    dataframe: pd.DataFrame,
    scenario: str,
) -> None:

    for parameter in PARAMETERS:

        plt.figure(figsize=(12, 5))

        plt.plot(
            dataframe["timestamp"],
            dataframe[parameter],
        )

        plt.title(
            f"{scenario.title()} - "
            f"{parameter} Over Time"
        )

        plt.xlabel("Time")
        plt.ylabel(parameter)

        plt.xticks(rotation=30)

        plt.tight_layout()

        output_path = (
            OUTPUT_ROOT
            / f"{scenario}_{parameter}_timeseries.png"
        )

        plt.savefig(
            output_path,
            dpi=200,
        )

        plt.close()


# ============================================================
# DISTRIBUTIONS
# ============================================================

def plot_distributions(
    dataframe: pd.DataFrame,
    scenario: str,
) -> None:

    for parameter in PARAMETERS:

        plt.figure(figsize=(8, 5))

        plt.hist(
            dataframe[parameter],
            bins=50,
        )

        plt.title(
            f"{scenario.title()} - "
            f"{parameter} Distribution"
        )

        plt.xlabel(parameter)
        plt.ylabel("Frequency")

        plt.tight_layout()

        output_path = (
            OUTPUT_ROOT
            / f"{scenario}_{parameter}_distribution.png"
        )

        plt.savefig(
            output_path,
            dpi=200,
        )

        plt.close()


# ============================================================
# CORRELATION MATRIX
# ============================================================

def plot_correlation_matrix(
    dataframe: pd.DataFrame,
    scenario: str,
) -> None:

    correlation = dataframe[
        PARAMETERS
    ].corr()

    plt.figure(figsize=(8, 7))

    plt.imshow(
        correlation,
        interpolation="nearest",
    )

    plt.colorbar()

    plt.xticks(
        range(len(PARAMETERS)),
        PARAMETERS,
        rotation=45,
        ha="right",
    )

    plt.yticks(
        range(len(PARAMETERS)),
        PARAMETERS,
    )

    plt.title(
        f"{scenario.title()} - "
        "Parameter Correlation Matrix"
    )

    plt.tight_layout()

    output_path = (
        OUTPUT_ROOT
        / f"{scenario}_correlation_matrix.png"
    )

    plt.savefig(
        output_path,
        dpi=200,
    )

    plt.close()


# ============================================================
# SCENARIO COMPARISON
# ============================================================

def plot_scenario_comparison(
    datasets: dict[str, pd.DataFrame],
) -> None:

    for parameter in PARAMETERS:

        plt.figure(figsize=(12, 6))

        for scenario, dataframe in datasets.items():

            plt.plot(
                dataframe["timestamp"],
                dataframe[parameter],
                label=scenario,
            )

        plt.title(
            f"Scenario Comparison - {parameter}"
        )

        plt.xlabel("Time")
        plt.ylabel(parameter)

        plt.legend()

        plt.xticks(rotation=30)

        plt.tight_layout()

        output_path = (
            OUTPUT_ROOT
            / f"scenario_comparison_{parameter}.png"
        )

        plt.savefig(
            output_path,
            dpi=200,
        )

        plt.close()


# ============================================================
# MAIN
# ============================================================

def main():

    csv_files = sorted(
        DATA_ROOT.rglob("*.csv")
    )

    if not csv_files:

        print(
            "No generated datasets found."
        )

        return

    datasets = {}

    for csv_file in csv_files:

        scenario = csv_file.parent.name

        print(
            f"Visualizing: {scenario}"
        )

        dataframe = load_dataset(
            csv_file
        )

        datasets[scenario] = dataframe

        plot_time_series(
            dataframe,
            scenario,
        )

        plot_distributions(
            dataframe,
            scenario,
        )

        plot_correlation_matrix(
            dataframe,
            scenario,
        )

    plot_scenario_comparison(
        datasets
    )

    print()
    print(
        "Dataset visualization completed."
    )

    print(
        f"Figures saved to: {OUTPUT_ROOT}"
    )


if __name__ == "__main__":
    main()