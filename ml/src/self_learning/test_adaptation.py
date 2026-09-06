import numpy as np

from src.data.build_ml_dataset import (
    build_ml_dataset,
)

from src.model.lnn import (
    LiquidNeuralNetwork,
)

from src.self_learning.replay_buffer import (
    ReplayBuffer,
)

from src.self_learning.learner import (
    OnlineLearner,
)

from src.self_learning.adaptation import (
    AdaptationController,
)


DATASET_PATH = (
    "data/generated/healthy/healthy.csv"
)


def main():

    print("=" * 60)
    print("TESTING ADAPTATION CONTROLLER")
    print("=" * 60)

    # ----------------------------------------------
    # Load dataset
    # ----------------------------------------------

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

    # ----------------------------------------------
    # Create Replay Buffer
    # ----------------------------------------------

    buffer = ReplayBuffer(
        capacity=2000,
        input_window=60,
        prediction_horizon=12,
        num_features=5,
    )

    # ----------------------------------------------
    # Convert normalized dataset back to raw values
    #
    # We reconstruct a continuous sensor stream:
    #
    # 60 historical readings
    # +
    # many future readings
    # ----------------------------------------------

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

    # ----------------------------------------------
    # Build continuous observation stream
    #
    # Start with first input sequence
    # Then append future target
    # Then continue with new readings
    # ----------------------------------------------

    observations = []

    # First 60 readings
    for observation in X_raw[0]:
        observations.append(observation)

    # Next 12 actual readings
    for observation in y_raw[0]:
        observations.append(observation)

    # Add more continuous readings
    for sequence in y_raw[1:100]:

        observations.append(
            sequence[-1]
        )

    # ----------------------------------------------
    # Fill Replay Buffer
    # ----------------------------------------------

    for observation in observations:

        buffer.add_observation(
            observation
        )

    print()

    print(
        "Observation count:",
        buffer.observation_count()
    )

    print(
        "Buffer samples:",
        len(buffer)
    )
     # ----------------------------------------------
    # Model
    # ----------------------------------------------

    model = LiquidNeuralNetwork(
        input_size=5,
        hidden_size=64,
        output_size=5,
        prediction_horizon=12,
    )

    # ----------------------------------------------
    # Learner
    # ----------------------------------------------

    learner = OnlineLearner(
        model=model,
        scaler=preprocessor.scaler,
        learning_rate=1e-5,
    )

    # ----------------------------------------------
    # Controller
    # ----------------------------------------------

    controller = (
        AdaptationController(
            replay_buffer=buffer,
            learner=learner,
            batch_size=32,
            minimum_samples=32,
            error_threshold=0.01,
        )
    )

    # ----------------------------------------------
    # Adapt
    # ----------------------------------------------

    result = controller.adapt()

    print()

    print(
        "Adaptation Result:"
    )

    print(
        result
    )

    print()

    print(
        "Controller Status:"
    )

    print(
        controller.get_status()
    )


if __name__ == "__main__":
    main()