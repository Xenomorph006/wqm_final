from __future__ import annotations

import numpy as np


def mae(
    prediction: np.ndarray,
    target: np.ndarray,
) -> float:

    return float(
        np.mean(
            np.abs(
                prediction - target
            )
        )
    )


def mse(
    prediction: np.ndarray,
    target: np.ndarray,
) -> float:

    return float(
        np.mean(
            (
                prediction - target
            ) ** 2
        )
    )


def rmse(
    prediction: np.ndarray,
    target: np.ndarray,
) -> float:

    return float(
        np.sqrt(
            mse(
                prediction,
                target,
            )
        )
    )


def r2_score(
    prediction: np.ndarray,
    target: np.ndarray,
) -> float:

    target_mean = np.mean(
        target
    )

    ss_res = np.sum(
        (
            target - prediction
        ) ** 2
    )

    ss_tot = np.sum(
        (
            target - target_mean
        ) ** 2
    )

    if ss_tot == 0:

        return 0.0

    return float(
        1.0
        - (
            ss_res / ss_tot
        )
    )