import numpy as np

from .replay_buffer import ReplayBuffer


def main():

    buffer = ReplayBuffer(
        capacity=1000,
        input_window=60,
        prediction_horizon=12,
        num_features=5,
    )

    print(
        "Adding observations..."
    )

    for _ in range(100):

        observation = np.random.rand(5)

        sample_created = (
            buffer.add_observation(
                observation
            )
        )

        if sample_created:

            print(
                "New sample created"
            )

    print()

    print(
        "Observation count:",
        buffer.observation_count()
    )

    print(
        "Learning samples:",
        len(buffer)
    )

    if buffer.is_ready(
        minimum_samples=10
    ):

        X, y = buffer.sample(
            batch_size=10
        )

        print()

        print(
            "Input batch shape:",
            X.shape
        )

        print(
            "Target batch shape:",
            y.shape
        )


if __name__ == "__main__":
    main()