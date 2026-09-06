import numpy as np

from src.data.build_ml_dataset import (
    build_ml_dataset,
)

from src.self_learning.manager import (
    SelfLearningManager,
)


DATASET_PATH = (
    "data/generated/healthy/healthy.csv"
)

MODEL_PATH = (
    "results/checkpoints/"
    "lnn_baseline_best.pt"
)


def main():

    print("=" * 60)
    print("TESTING SELF-LEARNING MANAGER")
    print("=" * 60)

    # ==================================================
    # Load dataset and scaler
    # ==================================================

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

    # ==================================================
    # Manager
    # ==================================================

    manager = SelfLearningManager(
        model_path=MODEL_PATH,
        scaler=preprocessor.scaler,
        input_window=60,
        prediction_horizon=12,
        num_features=5,
        hidden_size=64,
        minimum_samples=32,
        adaptation_batch_size=32,
    )

    print()

    print(
        "Pre-trained model loaded"
    )

    # ==================================================
    # Convert test data to raw values
    # ==================================================

    X_raw = (
        preprocessor.inverse_transform(
            X_train.reshape(-1, 5)
        )
        .reshape(
            X_train.shape
        )
    )

    y_raw = (
        preprocessor.inverse_transform(
            y_train.reshape(-1, 5)
        )
        .reshape(
            y_train.shape
        )
    )

    # ==================================================
    # Simulate continuous sensor stream
    # ==================================================

    observations = []

    # First history window

    observations.extend(
        X_raw[0]
    )

    # First future observations

    observations.extend(
        y_raw[0]
    )

    # Continue stream

    for sequence in y_raw[1:100]:

        observations.append(
            sequence[-1]
        )

    # ==================================================
    # Process stream
    # ==================================================

    for index, observation in enumerate(
        observations
    ):

        result = (
            manager.process_observation(
                observation
            )
        )

        # Print occasionally

        if (
            (index + 1) % 25 == 0
        ):

            print()

            print(
                f"Observation "
                f"{index + 1}"
            )

            print(
                "Learning samples:",
                result["buffer"][
                    "learning_samples"
                ]
            )

            if (
                result["prediction"]
                is not None
            ):

                print(
                    "Prediction ready"
                )

    # ==================================================
    # Final status
    # ==================================================

    print()

    print("=" * 60)
    print("FINAL STATUS")
    print("=" * 60)

    status = manager.get_status()

    for key, value in status.items():

        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()