from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "pH",
    "turbidity",
    "temperature",
    "DO",
    "TDS",
]


@dataclass(frozen=True)
class SplitConfig:
    """
    Chronological dataset split configuration.
    """

    train_ratio: float = 0.70
    validation_ratio: float = 0.15
    test_ratio: float = 0.15

    def __post_init__(self) -> None:

        total = (
            self.train_ratio
            + self.validation_ratio
            + self.test_ratio
        )

        if not np.isclose(total, 1.0):
            raise ValueError(
                "Train, validation and test ratios "
                "must sum to 1.0."
            )


class StandardScaler:
    """
    Simple NumPy-based standard scaler.

    The scaler stores mean and standard deviation
    calculated ONLY from the training dataset.
    """

    def __init__(self) -> None:

        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None

    def fit(
        self,
        data: np.ndarray,
    ) -> "StandardScaler":

        if data.ndim != 2:
            raise ValueError(
                "Scaler expects a 2D array."
            )

        self.mean_ = np.mean(
            data,
            axis=0,
        )

        self.std_ = np.std(
            data,
            axis=0,
        )

        # Prevent division by zero.
        self.std_ = np.where(
            self.std_ < 1e-8,
            1.0,
            self.std_,
        )

        return self

    def transform(
        self,
        data: np.ndarray,
    ) -> np.ndarray:

        self._check_fitted()

        return (
            data - self.mean_
        ) / self.std_

    def inverse_transform(
        self,
        data: np.ndarray,
    ) -> np.ndarray:

        self._check_fitted()

        return (
            data * self.std_
        ) + self.mean_

    def save(
        self,
        path: str | Path,
    ) -> None:

        self._check_fitted()

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "mean": self.mean_.tolist(),
            "std": self.std_.tolist(),
            "features": FEATURE_COLUMNS,
        }

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                payload,
                file,
                indent=4,
            )

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> "StandardScaler":

        path = Path(path)

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            payload = json.load(file)

        scaler = cls()

        scaler.mean_ = np.asarray(
            payload["mean"],
            dtype=np.float32,
        )

        scaler.std_ = np.asarray(
            payload["std"],
            dtype=np.float32,
        )

        return scaler

    def _check_fitted(self) -> None:

        if (
            self.mean_ is None
            or self.std_ is None
        ):

            raise RuntimeError(
                "Scaler has not been fitted yet."
            )


class WaterQualityPreprocessor:
    """
    Handles chronological splitting and normalization
    of water-quality data.
    """

    def __init__(
        self,
        split_config: SplitConfig | None = None,
    ) -> None:

        self.split_config = (
            split_config
            if split_config is not None
            else SplitConfig()
        )

        self.scaler = StandardScaler()

    # ========================================================
    # LOAD
    # ========================================================

    @staticmethod
    def load_csv(
        csv_path: str | Path,
    ) -> pd.DataFrame:

        dataframe = pd.read_csv(
            csv_path,
            parse_dates=["timestamp"],
        )

        dataframe = dataframe.sort_values(
            "timestamp"
        ).reset_index(drop=True)

        return dataframe

    # ========================================================
    # SPLIT
    # ========================================================

    def split(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
    ]:

        self._validate_dataframe(
            dataframe
        )

        total_samples = len(dataframe)

        train_end = int(
            total_samples
            * self.split_config.train_ratio
        )

        validation_end = (
            train_end
            + int(
                total_samples
                * self.split_config.validation_ratio
            )
        )

        train = dataframe.iloc[
            :train_end
        ].copy()

        validation = dataframe.iloc[
            train_end:validation_end
        ].copy()

        test = dataframe.iloc[
            validation_end:
        ].copy()

        return (
            train,
            validation,
            test,
        )

    # ========================================================
    # FIT
    # ========================================================

    def fit(
        self,
        train_dataframe: pd.DataFrame,
    ) -> None:

        values = train_dataframe[
            FEATURE_COLUMNS
        ].to_numpy(
            dtype=np.float32
        )

        self.scaler.fit(
            values
        )

    # ========================================================
    # TRANSFORM
    # ========================================================

    def transform(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        values = dataframe[
            FEATURE_COLUMNS
        ].to_numpy(
            dtype=np.float32
        )

        scaled_values = (
            self.scaler.transform(
                values
            )
        )

        result = dataframe.copy()

        result[
            FEATURE_COLUMNS
        ] = scaled_values

        return result

    # ========================================================
    # INVERSE TRANSFORM
    # ========================================================

    def inverse_transform(
        self,
        values: np.ndarray,
    ) -> np.ndarray:

        return self.scaler.inverse_transform(
            values
        )

    # ========================================================
    # COMPLETE PIPELINE
    # ========================================================

    def prepare(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
    ]:

        train, validation, test = (
            self.split(dataframe)
        )

        # IMPORTANT:
        # Fit ONLY on training data.
        self.fit(train)

        train_scaled = self.transform(
            train
        )

        validation_scaled = self.transform(
            validation
        )

        test_scaled = self.transform(
            test
        )

        return (
            train_scaled,
            validation_scaled,
            test_scaled,
        )

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def _validate_dataframe(
        dataframe: pd.DataFrame,
    ) -> None:

        missing_columns = [
            column
            for column in FEATURE_COLUMNS
            if column not in dataframe.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing feature columns: "
                f"{missing_columns}"
            )

        if dataframe[
            FEATURE_COLUMNS
        ].isna().any().any():

            raise ValueError(
                "Dataset contains missing "
                "feature values."
            )

        if not dataframe[
            "timestamp"
        ].is_monotonic_increasing:

            raise ValueError(
                "Timestamps must be in "
                "chronological order."
            )