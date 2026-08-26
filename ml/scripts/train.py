from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.data.build_ml_dataset import (
    build_ml_dataset,
)
from src.model.lnn import (
    LiquidNeuralNetwork,
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

INPUT_WINDOW = 60

PREDICTION_HORIZON = 12

STRIDE = 1

HIDDEN_SIZE = 64

BATCH_SIZE = 64

EPOCHS = 50

LEARNING_RATE = 1e-3

WEIGHT_DECAY = 1e-5

CHECKPOINT_PATH = (
    "results/checkpoints/"
    "lnn_baseline_best.pt"
)

FIGURE_PATH = (
    "results/reports/figures/training/"
    "baseline_training_loss.png"
)

METRICS_PATH = (
    "results/reports/metrics/"
    "baseline_metrics.json"
)


# ============================================================
# DIRECTORY SETUP
# ============================================================

Path(
    "results/checkpoints"
).mkdir(
    parents=True,
    exist_ok=True,
)

Path(
    "results/reports/figures/training"
).mkdir(
    parents=True,
    exist_ok=True,
)

Path(
    "results/reports/metrics"
).mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# TRAINING
# ============================================================

def main():

    print("=" * 70)
    print("LNN BASELINE TRAINING")
    print("=" * 70)

    print()
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
        DATASET_PATH,
        input_window=INPUT_WINDOW,
        prediction_horizon=PREDICTION_HORIZON,
        stride=STRIDE,
    )

    print()
    print("Dataset shapes:")
    print(
        f"  X_train       : {X_train.shape}"
    )
    print(
        f"  y_train       : {y_train.shape}"
    )
    print(
        f"  X_validation  : {X_validation.shape}"
    )
    print(
        f"  y_validation  : {y_validation.shape}"
    )
    print(
        f"  X_test        : {X_test.shape}"
    )
    print(
        f"  y_test        : {y_test.shape}"
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print()
    print("Creating LNN...")

    model = LiquidNeuralNetwork(
        input_size=5,
        hidden_size=HIDDEN_SIZE,
        output_size=5,
        prediction_horizon=PREDICTION_HORIZON,
    )

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    print(
        f"Trainable parameters: "
        f"{parameter_count:,}"
    )

    # --------------------------------------------------------
    # Trainer
    # --------------------------------------------------------

    trainer = LNNTrainer(
        model=model,
        learning_rate=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    print(
        f"Device: {trainer.device}"
    )

    # --------------------------------------------------------
    # Data loaders
    # --------------------------------------------------------

    train_loader = (
        trainer.create_loader(
            X_train,
            y_train,
            batch_size=BATCH_SIZE,
            shuffle=True,
        )
    )

    validation_loader = (
        trainer.create_loader(
            X_validation,
            y_validation,
            batch_size=BATCH_SIZE,
            shuffle=False,
        )
    )

    test_loader = (
        trainer.create_loader(
            X_test,
            y_test,
            batch_size=BATCH_SIZE,
            shuffle=False,
        )
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("STARTING TRAINING")
    print("=" * 70)

    history = trainer.fit(
        train_loader=train_loader,
        validation_loader=validation_loader,
        epochs=EPOCHS,
        checkpoint_path=CHECKPOINT_PATH,
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TEST EVALUATION")
    print("=" * 70)

    evaluation = trainer.evaluate(
        test_loader
    )

    metrics = evaluation["metrics"]

    for name, value in metrics.items():

        print(
            f"{name}: {value:.6f}"
        )

    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4,
        )

    # --------------------------------------------------------
    # Training graph
    # --------------------------------------------------------

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        history["train_loss"],
        label="Training Loss",
    )

    plt.plot(
        history["validation_loss"],
        label="Validation Loss",
    )

    plt.xlabel("Epoch")

    plt.ylabel("Loss")

    plt.title(
        "LNN Training and Validation Loss"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_PATH,
        dpi=200,
    )

    plt.close()

    # --------------------------------------------------------
    # Save scaler
    # --------------------------------------------------------

    preprocessor.scaler.save(
        "results/checkpoints/"
        "baseline_scaler.json"
    )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TRAINING COMPLETED")
    print("=" * 70)

    print()
    print(
        f"Checkpoint: {CHECKPOINT_PATH}"
    )

    print(
        f"Metrics:    {METRICS_PATH}"
    )

    print(
        f"Graph:      {FIGURE_PATH}"
    )


if __name__ == "__main__":
    main()