import numpy as np
import torch

from src.model.lnn import (
    LiquidNeuralNetwork,
)

from src.self_learning.learner import (
    OnlineLearner,
)

from src.data.build_ml_dataset import (
    build_ml_dataset,
)


DATASET_PATH = (
    "data/generated/healthy/healthy.csv"
)


def main():

    print("=" * 60)

    print(
        "TESTING ONLINE LEARNER"
    )

    print("=" * 60)

    # --------------------------------------------------
    # Load dataset
    # --------------------------------------------------

    (
        X_train,
        y_train,
        _,
        _,
        _,
        _,
        preprocessor,
    ) = build_ml_dataset(
        DATASET_PATH,
        input_window=60,
        prediction_horizon=12,
        stride=1,
    )

    print()

    print(
        "Dataset loaded"
    )

    # --------------------------------------------------
    # Model
    # --------------------------------------------------

    model = LiquidNeuralNetwork(
        input_size=5,
        hidden_size=64,
        output_size=5,
        prediction_horizon=12,
    )

    # --------------------------------------------------
    # Learner
    # --------------------------------------------------

    learner = OnlineLearner(
        model=model,
        scaler=preprocessor.scaler,
        learning_rate=1e-5,
    )

    # --------------------------------------------------
    # Create small test batch
    # --------------------------------------------------

    X_batch = X_train[:16]

    y_batch = y_train[:16]

    # --------------------------------------------------
    # IMPORTANT
    #
    # X_train is already normalized.
    #
    # Convert back to raw values
    # so we can test the complete
    # real-world pipeline.
    # --------------------------------------------------

    X_raw = (
        preprocessor.inverse_transform(
            X_batch.reshape(
                -1,
                5,
            )
        )
        .reshape(
            X_batch.shape
        )
    )

    y_raw = (
        preprocessor.inverse_transform(
            y_batch.reshape(
                -1,
                5,
            )
        )
        .reshape(
            y_batch.shape
        )
    )

    # --------------------------------------------------
    # Evaluate before learning
    # --------------------------------------------------

    before = learner.evaluate(
        X_raw,
        y_raw,
    )

    print()

    print(
        "Before learning:"
    )

    print(
        before
    )

    # --------------------------------------------------
    # Learn
    # --------------------------------------------------

    result = learner.learn(
        X_raw,
        y_raw,
    )

    print()

    print(
        "Learning result:"
    )

    print(
        result
    )

    # --------------------------------------------------
    # Evaluate after learning
    # --------------------------------------------------

    after = learner.evaluate(
        X_raw,
        y_raw,
    )

    print()

    print(
        "After learning:"
    )

    print(
        after
    )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    print()

    print(
        "Learner status:"
    )

    print(
        learner.get_status()
    )


if __name__ == "__main__":
    main()