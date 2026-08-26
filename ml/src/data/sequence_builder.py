from __future__ import annotations

from dataclasses import dataclass

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
class SequenceConfig:
    """
    Configuration for converting time-series data
    into supervised learning sequences.
    """

    input_window: int = 60
    prediction_horizon: int = 12
    stride: int = 1


class TimeSeriesSequenceBuilder:
    """
    Converts water-quality time-series data into
    input/output sequences for the LNN.
    """

    def __init__(
        self,
        config: SequenceConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else SequenceConfig()
        )

    def build(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[np.ndarray, np.ndarray]:

        self._validate_dataframe(
            dataframe
        )

        values = dataframe[
            FEATURE_COLUMNS
        ].to_numpy(
            dtype=np.float32
        )

        input_window = (
            self.config.input_window
        )

        prediction_horizon = (
            self.config.prediction_horizon
        )

        stride = self.config.stride

        total_required = (
            input_window
            + prediction_horizon
        )

        if len(values) < total_required:

            raise ValueError(
                "Dataset does not contain enough "
                "samples for the requested sequence "
                "configuration."
            )

        X = []
        y = []

        max_start = (
            len(values)
            - total_required
            + 1
        )

        for start in range(
            0,
            max_start,
            stride,
        ):

            input_end = (
                start
                + input_window
            )

            target_end = (
                input_end
                + prediction_horizon
            )

            input_sequence = values[
                start:input_end
            ]

            target_sequence = values[
                input_end:target_end
            ]

            X.append(
                input_sequence
            )

            y.append(
                target_sequence
            )

        return (
            np.asarray(X, dtype=np.float32),
            np.asarray(y, dtype=np.float32),
        )

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

        if dataframe[FEATURE_COLUMNS].isna().any().any():

            raise ValueError(
                "Input dataframe contains "
                "missing feature values."
            )


def load_and_build_sequences(
    csv_path: str,
    input_window: int = 60,
    prediction_horizon: int = 12,
    stride: int = 1,
) -> tuple[np.ndarray, np.ndarray]:

    dataframe = pd.read_csv(
        csv_path,
        parse_dates=["timestamp"],
    )

    config = SequenceConfig(
        input_window=input_window,
        prediction_horizon=prediction_horizon,
        stride=stride,
    )

    builder = TimeSeriesSequenceBuilder(
        config
    )

    return builder.build(
        dataframe
    )