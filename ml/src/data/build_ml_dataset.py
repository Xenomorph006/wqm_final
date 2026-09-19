from __future__ import annotations

from pathlib import Path

import numpy as np

from .preprocessor import (
    WaterQualityPreprocessor,
)
from .sequence_builder import (
    SequenceConfig,
    TimeSeriesSequenceBuilder,
)


def build_ml_dataset(
    csv_path: str | Path,
    input_window: int = 60,
    prediction_horizon: int = 12,
    stride: int = 1,
):
    """
    Build normalized LNN-ready datasets.

    Returns
    -------
    tuple
        X_train, y_train,
        X_validation, y_validation,
        X_test, y_test,
        preprocessor
    """

    preprocessor = (
        WaterQualityPreprocessor()
    )

    dataframe = (
        preprocessor.load_csv(
            csv_path
        )
    )

    (
        train,
        validation,
        test,
    ) = preprocessor.prepare(
        dataframe
    )

    sequence_config = SequenceConfig(
        input_window=input_window,
        prediction_horizon=prediction_horizon,
        stride=stride,
    )

    builder = TimeSeriesSequenceBuilder(
        sequence_config
    )

    X_train, y_train = (
        builder.build(train)
    )

    X_validation, y_validation = (
        builder.build(validation)
    )

    X_test, y_test = (
        builder.build(test)
    )

    return (
        X_train,
        y_train,
        X_validation,
        y_validation,
        X_test,
        y_test,
        preprocessor,
    )


if __name__ == "__main__":

    (
        X_train,
        y_train,
        X_validation,
        y_validation,
        X_test,
        y_test,
        preprocessor,
    ) = build_ml_dataset(
        "data/generated/healthy/healthy.csv"
    )

    print("ML Dataset")
    print("-" * 40)

    print(
        "X_train:",
        X_train.shape,
    )

    print(
        "y_train:",
        y_train.shape,
    )

    print(
        "X_validation:",
        X_validation.shape,
    )

    print(
        "y_validation:",
        y_validation.shape,
    )

    print(
        "X_test:",
        X_test.shape,
    )

    print(
        "y_test:",
        y_test.shape,
    )