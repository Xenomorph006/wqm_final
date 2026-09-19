from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch

from src.data.build_ml_dataset import (
    build_ml_dataset,
)
from src.model.lnn import (
    LiquidNeuralNetwork,
)
from src.training.metrics import (
    mae,
    rmse,
    r2_score,
)
from src.training.trainer import (
    LNNTrainer,
)


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = (
    "data/generated/healthy/healthy.csv"
)

CHECKPOINT_PATH = (
    "results/checkpoints/"
    "lnn_baseline_best.pt"
)

INPUT_WINDOW = 60

PREDICTION_HORIZON = 12

STRIDE = 1

BATCH_SIZE = 64

OUTPUT_ROOT = Path(
    "results/reports/figures/evaluation"
)

METRICS_ROOT = Path(
    "results/reports/metrics"
)

PARAMETERS = [
    "pH",
    "turbidity",
    "temperature",
    "DO",
    "TDS",
]


# ============================================================
# DIRECTORIES
# ============================================================

OUTPUT_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

METRICS_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model(
    device: torch.device,
) -> LiquidNeuralNetwork:

    model = LiquidNeuralNetwork(
        input_size=5,
        hidden_size=64,
        output_size=5,
        prediction_horizon=PREDICTION_HORIZON,
    )

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=device,
        weights_only=False,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)

    model.eval()

    return model


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LNN BASELINE EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    (
        _,
        _,
        _,
        _,
        X_test,
        y_test,
        preprocessor,
    ) = build_ml_dataset(
        DATASET_PATH,
        input_window=INPUT_WINDOW,
        prediction_horizon=PREDICTION_HORIZON,
        stride=STRIDE,
    )

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"Device: {device}"
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = load_model(
        device
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    X_tensor = torch.from_numpy(
        X_test
    ).float().to(device)

    with torch.no_grad():

        predictions, confidence = (
            model(X_tensor)
        )

    predictions = (
        predictions
        .cpu()
        .numpy()
    )

    confidence = (
        confidence
        .cpu()
        .numpy()
    )

    # --------------------------------------------------------
    # Convert back to physical units
    # --------------------------------------------------------

    predictions_original = (
        preprocessor.inverse_transform(
            predictions.reshape(-1, 5)
        )
        .reshape(
            predictions.shape
        )
    )

    targets_original = (
        preprocessor.inverse_transform(
            y_test.reshape(-1, 5)
        )
        .reshape(
            y_test.shape
        )
    )

    # ========================================================
    # Overall metrics
    # ========================================================

    overall_metrics = {}

    print()
    print("Overall metrics:")
    print()

    for index, parameter in enumerate(
        PARAMETERS
    ):

        parameter_prediction = (
            predictions_original[:, :, index]
        )

        parameter_target = (
            targets_original[:, :, index]
        )

        parameter_metrics = {
            "MAE": mae(
                parameter_prediction,
                parameter_target,
            ),
            "RMSE": rmse(
                parameter_prediction,
                parameter_target,
            ),
            "R2": r2_score(
                parameter_prediction,
                parameter_target,
            ),
            "Mean Confidence": float(
                np.mean(
                    confidence[:, :, index]
                )
            ),
        }

        overall_metrics[
            parameter
        ] = parameter_metrics

        print(
            f"{parameter}:"
        )

        print(
            f"  MAE        : "
            f"{parameter_metrics['MAE']:.6f}"
        )

        print(
            f"  RMSE       : "
            f"{parameter_metrics['RMSE']:.6f}"
        )

        print(
            f"  R²         : "
            f"{parameter_metrics['R2']:.6f}"
        )

        print(
            f"  Confidence : "
            f"{parameter_metrics['Mean Confidence']:.6f}"
        )

    # ========================================================
    # Horizon metrics
    # ========================================================

    horizon_metrics = {}

    for step in range(
        PREDICTION_HORIZON
    ):

        horizon = (
            (step + 1) * 5
        )

        step_metrics = {}

        for index, parameter in enumerate(
            PARAMETERS
        ):

            pred = (
                predictions_original[
                    :, step, index
                ]
            )

            target = (
                targets_original[
                    :, step, index
                ]
            )

            step_metrics[
                parameter
            ] = {
                "MAE": mae(
                    pred,
                    target,
                ),
                "RMSE": rmse(
                    pred,
                    target,
                ),
                "R2": r2_score(
                    pred,
                    target,
                ),
            }

        horizon_metrics[
            f"{horizon}s"
        ] = step_metrics

    # ========================================================
    # Save metrics
    # ========================================================

    metrics = {
        "overall": overall_metrics,
        "horizon": horizon_metrics,
    }

    metrics_path = (
        METRICS_ROOT
        / "baseline_evaluation.json"
    )

    with open(
        metrics_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4,
        )

    # ========================================================
    # Prediction vs Actual
    # ========================================================

    # Use the first test sequence as an example.
    example_index = 0

    for index, parameter in enumerate(
        PARAMETERS
    ):

        plt.figure(
            figsize=(10, 6)
        )

        future_seconds = np.arange(
            1,
            PREDICTION_HORIZON + 1,
        ) * 5

        plt.plot(
            future_seconds,
            targets_original[
                example_index,
                :,
                index,
            ],
            marker="o",
            label="Actual",
        )

        plt.plot(
            future_seconds,
            predictions_original[
                example_index,
                :,
                index,
            ],
            marker="x",
            label="LNN Prediction",
        )

        plt.xlabel(
            "Future Time (seconds)"
        )

        plt.ylabel(
            parameter
        )

        plt.title(
            f"LNN Forecast vs Actual - "
            f"{parameter}"
        )

        plt.legend()

        plt.grid(
            True,
            alpha=0.3,
        )

        plt.tight_layout()

        output_path = (
            OUTPUT_ROOT
            / f"prediction_vs_actual_{parameter}.png"
        )

        plt.savefig(
            output_path,
            dpi=200,
        )

        plt.close()

    # ========================================================
    # Horizon Error Graph
    # ========================================================

    for index, parameter in enumerate(
        PARAMETERS
    ):

        horizon_values = []

        for step in range(
            PREDICTION_HORIZON
        ):

            pred = (
                predictions_original[
                    :, step, index
                ]
            )

            target = (
                targets_original[
                    :, step, index
                ]
            )

            horizon_values.append(
                mae(
                    pred,
                    target,
                )
            )

        future_seconds = np.arange(
            1,
            PREDICTION_HORIZON + 1,
        ) * 5

        plt.figure(
            figsize=(10, 6)
        )

        plt.plot(
            future_seconds,
            horizon_values,
            marker="o",
        )

        plt.xlabel(
            "Prediction Horizon (seconds)"
        )

        plt.ylabel(
            "MAE"
        )

        plt.title(
            f"Forecast Error vs Horizon - "
            f"{parameter}"
        )

        plt.grid(
            True,
            alpha=0.3,
        )

        plt.tight_layout()

        output_path = (
            OUTPUT_ROOT
            / f"horizon_error_{parameter}.png"
        )

        plt.savefig(
            output_path,
            dpi=200,
        )

        plt.close()

    # ========================================================
    # Confidence vs Error
    # ========================================================

    for index, parameter in enumerate(
        PARAMETERS
    ):

        errors = np.abs(
            predictions_original[
                :, :, index
            ]
            -
            targets_original[
                :, :, index
            ]
        )

        confidence_values = (
            confidence[
                :, :, index
            ]
        )

        plt.figure(
            figsize=(10, 6)
        )

        plt.scatter(
            confidence_values.flatten(),
            errors.flatten(),
            alpha=0.15,
        )

        plt.xlabel(
            "Model Confidence"
        )

        plt.ylabel(
            "Absolute Prediction Error"
        )

        plt.title(
            f"Confidence vs Prediction Error - "
            f"{parameter}"
        )

        plt.grid(
            True,
            alpha=0.3,
        )

        plt.tight_layout()

        output_path = (
            OUTPUT_ROOT
            / f"confidence_vs_error_{parameter}.png"
        )

        plt.savefig(
            output_path,
            dpi=200,
        )

        plt.close()

    print()
    print("=" * 70)
    print("EVALUATION COMPLETED")
    print("=" * 70)

    print(
        f"Metrics saved to: "
        f"{metrics_path}"
    )

    print(
        f"Figures saved to: "
        f"{OUTPUT_ROOT}"
    )


if __name__ == "__main__":
    main()