from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import torch

from scipy.signal import savgol_filter

from src.data.build_ml_dataset import build_ml_dataset
from src.model.lnn import LiquidNeuralNetwork


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = Path(
    "data/generated/healthy/healthy.csv"
)

CHECKPOINT_PATH = Path(
    "results/checkpoints/lnn_baseline_best.pt"
)

OUTPUT_DIR = Path(
    "results/reports/figures/predictions"
)

INPUT_WINDOW = 60
PREDICTION_HORIZON = 12
STRIDE = 1
HIDDEN_SIZE = 64

# Dataset sampling interval
SAMPLING_INTERVAL_SECONDS = 1.0

# Plot appearance
LINE_COLOR = "orange"
LINE_WIDTH = 2.0

# Smoothing
SMOOTHING_WINDOW = 31
SMOOTHING_POLYORDER = 3


# ============================================================
# DIRECTORY SETUP
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOAD BASELINE MODEL
# ============================================================

def load_model():

    print("Loading baseline checkpoint...")

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location="cpu",
        weights_only=False,
    )

    model = LiquidNeuralNetwork(
        input_size=5,
        hidden_size=HIDDEN_SIZE,
        output_size=5,
        prediction_horizon=PREDICTION_HORIZON,
    )

    # --------------------------------------------------------
    # Handle different checkpoint formats
    # --------------------------------------------------------

    if isinstance(checkpoint, dict):

        if "model_state_dict" in checkpoint:

            state_dict = checkpoint[
                "model_state_dict"
            ]

        elif "state_dict" in checkpoint:

            state_dict = checkpoint[
                "state_dict"
            ]

        elif "model" in checkpoint:

            state_dict = checkpoint[
                "model"
            ]

        else:

            state_dict = checkpoint

    else:

        state_dict = checkpoint

    # --------------------------------------------------------
    # Load model weights
    # --------------------------------------------------------

    model.load_state_dict(
        state_dict,
        strict=False,
    )

    model.eval()

    print(
        "Baseline model loaded successfully."
    )

    return model


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    print("Loading dataset...")

    (
        X_train,
        y_train,
        X_validation,
        y_validation,
        X_test,
        y_test,
        preprocessor,
    ) = build_ml_dataset(
        str(DATASET_PATH),
        input_window=INPUT_WINDOW,
        prediction_horizon=PREDICTION_HORIZON,
        stride=STRIDE,
    )

    print()
    print("Dataset:")
    print(
        f"Train       : {X_train.shape}"
    )
    print(
        f"Validation  : {X_validation.shape}"
    )
    print(
        f"Test        : {X_test.shape}"
    )

    return (
        X_test,
        preprocessor,
    )


# ============================================================
# CONVERT TO NUMPY
# ============================================================

def to_numpy(data):

    if torch.is_tensor(data):

        return (
            data
            .detach()
            .cpu()
            .numpy()
        )

    return np.asarray(data)


# ============================================================
# INVERSE TRANSFORM
# ============================================================

def inverse_transform(
    preprocessor,
    data,
):

    data = np.asarray(
        data,
        dtype=float,
    )

    original_shape = data.shape

    flattened = data.reshape(
        -1,
        data.shape[-1],
    )

    restored = (
        preprocessor.scaler
        .inverse_transform(
            flattened
        )
    )

    return restored.reshape(
        original_shape
    )


# ============================================================
# GENERATE PREDICTIONS
# ============================================================

def generate_predictions(
    model,
    X_test,
):

    print()
    print(
        "Generating LNN predictions..."
    )

    X_test = to_numpy(
        X_test
    )

    X_tensor = torch.tensor(
        X_test,
        dtype=torch.float32,
    )

    predictions = []

    with torch.no_grad():

        for start in range(
            0,
            len(X_tensor),
            64,
        ):

            batch = X_tensor[
                start:start + 64
            ]

            # ------------------------------------------------
            # LNN inference
            # ------------------------------------------------

            output = model(
                batch
            )

            output = to_numpy(
                output
            )

            print(
                f"Raw model output: "
                f"{output.shape}"
            )

            # =================================================
            # HANDLE LNN OUTPUT
            # =================================================
            #
            # Your LNN returns:
            #
            # (2, batch, horizon, features)
            #
            # Example:
            #
            # (2, 64, 12, 5)
            #
            # We use the first prediction stream:
            #
            # (batch, horizon, features)
            # =================================================

            if output.ndim == 4:

                if (
                    output.shape[1]
                    == len(batch)
                ):

                    output = output[0]

                elif (
                    output.shape[0]
                    == len(batch)
                ):

                    output = (
                        output[:, 0, :, :]
                    )

                else:

                    raise ValueError(
                        "Unable to identify "
                        "batch dimension in "
                        f"LNN output: "
                        f"{output.shape}"
                    )

            # =================================================
            # 3D OUTPUT
            # =================================================

            elif output.ndim == 3:

                # [batch, horizon, features]

                if (
                    output.shape[0]
                    == len(batch)
                ):

                    pass

                # [horizon, batch, features]

                elif (
                    output.shape[1]
                    == len(batch)
                ):

                    output = np.transpose(
                        output,
                        (1, 0, 2),
                    )

                else:

                    raise ValueError(
                        "Unable to identify "
                        "batch dimension in "
                        f"LNN output: "
                        f"{output.shape}"
                    )

            # =================================================
            # 2D OUTPUT
            # =================================================

            elif output.ndim == 2:

                # [batch, features]

                if (
                    output.shape[0]
                    == len(batch)
                ):

                    pass

                # [features, batch]

                elif (
                    output.shape[1]
                    == len(batch)
                ):

                    output = output.T

                else:

                    raise ValueError(
                        "Unable to identify "
                        "batch dimension in "
                        f"LNN output: "
                        f"{output.shape}"
                    )

            else:

                raise ValueError(
                    "Unexpected LNN output shape: "
                    f"{output.shape}"
                )

            print(
                f"Processed output: "
                f"{output.shape}"
            )

            predictions.append(
                output
            )

            processed = min(
                start + len(batch),
                len(X_tensor),
            )

            print(
                f"Processed "
                f"{processed}/"
                f"{len(X_tensor)} samples"
            )

    # ========================================================
    # CONCATENATE BATCHES
    # ========================================================

    predictions = np.concatenate(
        predictions,
        axis=0,
    )

    print()
    print(
        f"Final prediction shape: "
        f"{predictions.shape}"
    )

    return predictions


# ============================================================
# EXTRACT FIRST FUTURE STEP
# ============================================================

def extract_first_prediction(
    predictions,
):

    predictions = np.asarray(
        predictions
    )

    # --------------------------------------------------------
    # [samples, horizon, features]
    # --------------------------------------------------------

    if predictions.ndim == 3:

        return predictions[
            :,
            0,
            :,
        ]

    # --------------------------------------------------------
    # [samples, features]
    # --------------------------------------------------------

    if predictions.ndim == 2:

        return predictions

    raise ValueError(
        "Unexpected prediction shape: "
        f"{predictions.shape}"
    )


# ============================================================
# SMOOTH SIGNAL
# ============================================================

def smooth_signal(
    signal,
):

    signal = np.asarray(
        signal,
        dtype=float,
    )

    window = min(
        SMOOTHING_WINDOW,
        len(signal),
    )

    # Window must be odd
    if window % 2 == 0:
        window -= 1

    # Polynomial order must be smaller
    # than the window size
    polyorder = min(
        SMOOTHING_POLYORDER,
        window - 1,
    )

    if window < 5:

        return signal

    return savgol_filter(
        signal,
        window_length=window,
        polyorder=polyorder,
    )


# ============================================================
# CALCULATE Y-AXIS LIMITS
# ============================================================

def calculate_y_limits(
    values,
    parameter_name,
):

    values = np.asarray(
        values,
        dtype=float,
    )

    # --------------------------------------------------------
    # Fixed scientific display range for turbidity
    # --------------------------------------------------------

    if parameter_name == "Turbidity":

        return (
            15.0,
            16.0,
        )

    # --------------------------------------------------------
    # Automatic scale for other parameters
    # --------------------------------------------------------

    minimum = np.nanmin(
        values
    )

    maximum = np.nanmax(
        values
    )

    data_range = (
        maximum - minimum
    )

    # Avoid zero range
    if data_range == 0:

        padding = max(
            abs(minimum) * 0.05,
            1.0,
        )

    else:

        padding = (
            data_range * 0.08
        )

    return (
        minimum - padding,
        maximum + padding,
    )


# ============================================================
# PLOT PARAMETER
# ============================================================

def plot_parameter(
    time_seconds,
    predicted,
    parameter_name,
    unit,
    filename,
):

    # --------------------------------------------------------
    # Smooth prediction
    # --------------------------------------------------------

    smoothed_prediction = (
        smooth_signal(
            predicted
        )
    )

    # --------------------------------------------------------
    # Calculate scale
    # --------------------------------------------------------

    y_min, y_max = (
        calculate_y_limits(
            smoothed_prediction,
            parameter_name,
        )
    )

    # --------------------------------------------------------
    # Create figure
    # --------------------------------------------------------

    plt.figure(
        figsize=(12, 6),
    )

    # --------------------------------------------------------
    # Prediction curve
    # --------------------------------------------------------

    plt.plot(
        time_seconds,
        smoothed_prediction,
        label="LNN Prediction",
        linewidth=LINE_WIDTH,
        color=LINE_COLOR,
    )

    # --------------------------------------------------------
    # Axis labels
    # --------------------------------------------------------

    plt.xlabel(
        "Time (seconds)",
        fontsize=12,
    )

    if unit:

        ylabel = (
            f"{parameter_name} "
            f"({unit})"
        )

    else:

        ylabel = parameter_name

    plt.ylabel(
        ylabel,
        fontsize=12,
    )

    # --------------------------------------------------------
    # Y-axis limits
    # --------------------------------------------------------

    plt.ylim(
        y_min,
        y_max,
    )
    print(
        f"Y-axis limits for {parameter_name}: ({y_min:.2f}, {y_max:.2f})"
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    plt.title(
        f"LNN Baseline - "
        f"{parameter_name}",
        fontsize=15,
        fontweight="bold",
    )

    # --------------------------------------------------------
    # Grid
    # --------------------------------------------------------

    plt.grid(
        True,
        alpha=0.25,
        linewidth=0.8,
    )

    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    plt.legend(
        loc="best",
        frameon=True,
    )

    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    plt.tight_layout()

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_path = (
        OUTPUT_DIR / filename
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Saved: {output_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "BASELINE LNN GRAPH REGENERATION"
    )
    print("=" * 70)
    print()

    print(
        "IMPORTANT: No training will "
        "be performed."
    )

    print(
        "Existing baseline checkpoint "
        "will be used."
    )

    print()

    # ========================================================
    # CHECK FILES
    # ========================================================

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            "Dataset not found:\n"
            f"{DATASET_PATH.resolve()}"
        )

    if not CHECKPOINT_PATH.exists():

        raise FileNotFoundError(
            "Baseline checkpoint not found:\n"
            f"{CHECKPOINT_PATH.resolve()}"
        )

    # ========================================================
    # LOAD DATASET
    # ========================================================

    (
        X_test,
        preprocessor,
    ) = load_dataset()

    # ========================================================
    # LOAD MODEL
    # ========================================================

    model = load_model()

    # ========================================================
    # GENERATE PREDICTIONS
    # ========================================================

    predictions = (
        generate_predictions(
            model,
            X_test,
        )
    )

    # ========================================================
    # FIRST PREDICTION STEP
    # ========================================================

    predictions = (
        extract_first_prediction(
            predictions
        )
    )

    print()
    print(
        "Prediction data after "
        "first-step extraction:"
    )

    print(
        predictions.shape
    )

    # ========================================================
    # CONVERT TO PHYSICAL UNITS
    # ========================================================

    print()
    print(
        "Converting predictions to "
        "physical units..."
    )

    predictions = (
        inverse_transform(
            preprocessor,
            predictions,
        )
    )

    print(
        "Physical prediction shape:"
    )

    print(
        predictions.shape
    )

    # ========================================================
    # TIME AXIS
    # ========================================================

    number_of_samples = len(
        predictions
    )

    time_seconds = (
        np.arange(
            number_of_samples
        )
        * SAMPLING_INTERVAL_SECONDS
    )

    print()
    print(
        f"Time range: "
        f"{time_seconds[0]:.0f} - "
        f"{time_seconds[-1]:.0f} seconds"
    )

    # ========================================================
    # PARAMETER DEFINITIONS
    # ========================================================

    parameters = [
        (
            "pH",
            "",
            "baseline_ph.png",
        ),

        (
            "Turbidity",
            "NTU",
            "baseline_turbidity.png",
        ),

        (
            "Temperature",
            "°C",
            "baseline_temperature.png",
        ),

        (
            "Dissolved Oxygen",
            "mg/L",
            "baseline_dissolved_oxygen.png",
        ),

        (
            "TDS",
            "ppm",
            "baseline_tds.png",
        ),
    ]

    # ========================================================
    # GENERATE INDIVIDUAL GRAPHS
    # ========================================================

    print()
    print("=" * 70)
    print(
        "GENERATING SMOOTH PARAMETER GRAPHS"
    )
    print("=" * 70)

    for index, (
        parameter_name,
        unit,
        filename,
    ) in enumerate(
        parameters
    ):

        print()
        print(
            f"Generating "
            f"{parameter_name} graph..."
        )

        plot_parameter(
            time_seconds=time_seconds,
            predicted=predictions[
                :,
                index,
            ],
            parameter_name=parameter_name,
            unit=unit,
            filename=filename,
        )

    # ========================================================
    # FINAL MESSAGE
    # ========================================================

    print()
    print("=" * 70)
    print(
        "GRAPH REGENERATION COMPLETED"
    )
    print("=" * 70)
    print()

    print(
        "Graphs saved to:"
    )

    print(
        OUTPUT_DIR.resolve()
    )

    print()
    print(
        "Generated files:"
    )

    print(
        "  baseline_ph.png"
    )

    print(
        "  baseline_turbidity.png"
    )

    print(
        "  baseline_temperature.png"
    )

    print(
        "  baseline_dissolved_oxygen.png"
    )

    print(
        "  baseline_tds.png"
    )

    print()
    print(
        "No model training was performed."
    )

    print(
        "The existing baseline checkpoint "
        "was used."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()