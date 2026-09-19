from __future__ import annotations

from collections import deque

import numpy as np


class ReplayBuffer:
    """
    Stores real-world water-quality observations
    and creates training samples for online learning.

    Each observation contains:

        pH
        turbidity
        temperature
        DO
        TDS

    Sensor interval:
        5 seconds
    """

    def __init__(
        self,
        capacity: int = 10000,
        input_window: int = 60,
        prediction_horizon: int = 12,
        num_features: int = 5,
    ) -> None:

        self.capacity = capacity

        self.input_window = input_window

        self.prediction_horizon = (
            prediction_horizon
        )

        self.num_features = num_features

        # ----------------------------------------------------
        # Raw sensor observations
        # ----------------------------------------------------

        self.observations = deque(
            maxlen=capacity
        )

        # ----------------------------------------------------
        # Learning samples
        #
        # Each item:
        #
        # {
        #   "input": [60, 5],
        #   "target": [12, 5]
        # }
        # ----------------------------------------------------

        self.samples = deque(
            maxlen=capacity
        )

    def add_observation(
        self,
        observation,
    ) -> bool:
        """
        Add one real sensor observation.

        Returns True when a new learning sample
        can be created.
        """

        observation = np.asarray(
            observation,
            dtype=np.float32,
        )

        # ------------------------------------------------
        # Validate feature count
        # ------------------------------------------------

        if observation.shape != (
            self.num_features,
        ):

            raise ValueError(
                "Observation must contain "
                f"{self.num_features} features. "
                f"Received shape: "
                f"{observation.shape}"
            )

        self.observations.append(
            observation
        )

        required_length = (
            self.input_window
            + self.prediction_horizon
        )

        # ------------------------------------------------
        # Need enough observations
        # ------------------------------------------------

        if (
            len(self.observations)
            < required_length
        ):

            return False

        # ------------------------------------------------
        # Create training sample
        # ------------------------------------------------

        data = np.asarray(
            self.observations
        )

        input_sequence = data[
            -required_length:
            -self.prediction_horizon
        ]

        target_sequence = data[
            -self.prediction_horizon:
        ]

        self.samples.append(
            {
                "input":
                    input_sequence.copy(),

                "target":
                    target_sequence.copy(),
            }
        )

        return True

    def sample(
        self,
        batch_size: int,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
    ]:
        """
        Randomly sample learning examples.
        """

        if (
            len(self.samples)
            < batch_size
        ):

            raise ValueError(
                "Not enough samples in "
                "replay buffer."
            )

        indices = np.random.choice(
            len(self.samples),
            size=batch_size,
            replace=False,
        )

        inputs = []

        targets = []

        for index in indices:

            sample = self.samples[index]

            inputs.append(
                sample["input"]
            )

            targets.append(
                sample["target"]
            )

        return (
            np.asarray(
                inputs,
                dtype=np.float32,
            ),
            np.asarray(
                targets,
                dtype=np.float32,
            ),
        )

    def get_latest(
        self,
        batch_size: int,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
    ]:
        """
        Get most recent learning samples.
        """

        if (
            len(self.samples)
            < batch_size
        ):

            raise ValueError(
                "Not enough samples."
            )

        latest_samples = list(
            self.samples
        )[-batch_size:]

        inputs = np.asarray(
            [
                sample["input"]
                for sample
                in latest_samples
            ],
            dtype=np.float32,
        )

        targets = np.asarray(
            [
                sample["target"]
                for sample
                in latest_samples
            ],
            dtype=np.float32,
        )

        return (
            inputs,
            targets,
        )

    def __len__(
        self,
    ) -> int:

        return len(
            self.samples
        )

    def observation_count(
        self,
    ) -> int:

        return len(
            self.observations
        )

    def is_ready(
        self,
        minimum_samples: int = 32,
    ) -> bool:

        return (
            len(self.samples)
            >= minimum_samples
        )

    def clear(self) -> None:

        self.observations.clear()

        self.samples.clear()