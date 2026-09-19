from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_ROOT = Path("data/generated")

EXPECTED_INTERVAL_SECONDS = 5

REQUIRED_COLUMNS = [
    "timestamp",
    "pH",
    "turbidity",
    "temperature",
    "DO",
    "TDS",
    "scenario",
]


# ============================================================
# VALIDATION
# ============================================================

def validate_file(csv_path: Path) -> bool:

    print("=" * 70)
    print(f"Checking: {csv_path}")
    print("=" * 70)

    dataframe = pd.read_csv(csv_path)

    passed = True

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        print(
            f"[FAIL] Missing columns: "
            f"{missing_columns}"
        )
        passed = False
    else:
        print("[PASS] Required columns present.")

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_values = dataframe.isna().sum()

    if missing_values.sum() > 0:

        print("[FAIL] Missing values detected:")

        print(
            missing_values[
                missing_values > 0
            ]
        )

        passed = False

    else:
        print("[PASS] No missing values.")

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    duplicate_rows = dataframe.duplicated().sum()

    if duplicate_rows > 0:

        print(
            f"[FAIL] Duplicate rows: "
            f"{duplicate_rows}"
        )

        passed = False

    else:
        print("[PASS] No duplicate rows.")

    # --------------------------------------------------------
    # Timestamp validation
    # --------------------------------------------------------

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"]
    )

    duplicate_timestamps = (
        dataframe["timestamp"]
        .duplicated()
        .sum()
    )

    if duplicate_timestamps > 0:

        print(
            f"[FAIL] Duplicate timestamps: "
            f"{duplicate_timestamps}"
        )

        passed = False

    else:
        print("[PASS] No duplicate timestamps.")

    # --------------------------------------------------------
    # 5-second interval validation
    # --------------------------------------------------------

    timestamp_difference = (
        dataframe["timestamp"]
        .diff()
        .dt.total_seconds()
        .dropna()
    )

    invalid_intervals = (
        timestamp_difference
        != EXPECTED_INTERVAL_SECONDS
    ).sum()

    if invalid_intervals > 0:

        print(
            f"[FAIL] Invalid sampling intervals: "
            f"{invalid_intervals}"
        )

        print(
            "Observed intervals:"
        )

        print(
            timestamp_difference
            .value_counts()
            .head(10)
        )

        passed = False

    else:

        print(
            "[PASS] All sampling intervals "
            "are exactly 5 seconds."
        )

    # --------------------------------------------------------
    # Numeric validation
    # --------------------------------------------------------

    numeric_columns = [
        "pH",
        "turbidity",
        "temperature",
        "DO",
        "TDS",
    ]

    for column in numeric_columns:

        if not pd.api.types.is_numeric_dtype(
            dataframe[column]
        ):

            print(
                f"[FAIL] {column} is not numeric."
            )

            passed = False

    # --------------------------------------------------------
    # Range validation
    # --------------------------------------------------------

    ranges = {
        "pH": (4.0, 10.0),
        "turbidity": (0.0, float("inf")),
        "temperature": (10.0, 40.0),
        "DO": (0.0, 15.0),
        "TDS": (0.0, float("inf")),
    }

    for column, (
        minimum,
        maximum,
    ) in ranges.items():

        below_minimum = (
            dataframe[column] < minimum
        ).sum()

        above_maximum = (
            dataframe[column] > maximum
        ).sum()

        if (
            below_minimum > 0
            or above_maximum > 0
        ):

            print(
                f"[FAIL] {column} outside "
                f"simulation bounds."
            )

            passed = False

        else:

            print(
                f"[PASS] {column} within "
                f"simulation bounds."
            )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print()
    print("Statistics:")
    print()

    print(
        dataframe[
            numeric_columns
        ].describe().round(3)
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print()

    if passed:

        print(
            f"[PASS] Dataset is valid: "
            f"{csv_path.name}"
        )

    else:

        print(
            f"[FAIL] Dataset requires attention: "
            f"{csv_path.name}"
        )

    print()

    return passed


# ============================================================
# MAIN
# ============================================================

def main():

    csv_files = sorted(
        DATA_ROOT.rglob("*.csv")
    )

    if not csv_files:

        print(
            "No CSV datasets found in "
            f"{DATA_ROOT}"
        )

        return

    overall_passed = True

    for csv_file in csv_files:

        result = validate_file(
            csv_file
        )

        if not result:
            overall_passed = False

    print("=" * 70)

    if overall_passed:

        print(
            "ALL DATASETS PASSED VALIDATION."
        )

    else:

        print(
            "ONE OR MORE DATASETS FAILED "
            "VALIDATION."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()