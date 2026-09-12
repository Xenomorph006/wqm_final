from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch

from src.model.lnn import (
    LiquidNeuralNetwork,
)

from .replay_buffer import (
    ReplayBuffer,
)

from .learner import (
    OnlineLearner,
)

from .adaptation import (
    AdaptationController,
)

from .model_store import (
    ModelStore,
)


class SelfLearningManager:
    """
    Main interface for the LNN self-learning system.

    Responsibilities:

    1. Load the pre-trained LNN
    2. Receive real sensor observations
    3. Store observations in the replay buffer
    4. Trigger controlled adaptation
    5. Generate future predictions
    6. Return prediction confidence
    """

    def __init__(
        self,
        model_path: str,
        scaler: Any,
        input_window: int = 60,
        prediction_horizon: int = 12,
        num_features: int = 5,
        hidden_size: int = 64,
        buffer_capacity: int = 10000,
        learning_rate: float = 1e-5,
        adaptation_batch_size: int = 32,
        minimum_samples: int = 32,
        adaptation_interval: int = 10,
    ) -> None:

        # ==================================================
        # BASIC CONFIGURATION
        # ==================================================

        self.input_window = input_window

        self.prediction_horizon = (
            prediction_horizon
        )

        self.num_features = num_features

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        # ==================================================
        # PROJECT ROOT
        #
        # manager.py:
        #
        # ML/src/self-learning/manager.py
        #
        # parents[0] = self-learning
        # parents[1] = src
        # parents[2] = ML
        # ==================================================

        self.project_root = (
            Path(__file__).resolve().parents[2]
        )

        # ==================================================
        # MODEL
        # ==================================================

        self.model = LiquidNeuralNetwork(
            input_size=num_features,
            hidden_size=hidden_size,
            output_size=num_features,
            prediction_horizon=prediction_horizon,
        )

        self._load_model(
            model_path
        )

        # ==================================================
        # MODEL STORE PATH
        # ==================================================

        adapted_model_directory = (
            self.project_root
            / "models"
            / "adapted"
        )

        # ==================================================
        # MODEL STORE
        # ==================================================

        self.model_store = ModelStore(
            directory=str(
                adapted_model_directory
            ),
            filename="lnn_latest.pt",
        )

        # ==================================================
        # LOAD SELF-LEARNING CHECKPOINT
        # ==================================================

        self.loaded_checkpoint = (
            self.model_store.load(
                model=self.model,
                device=str(self.device),
            )
        )

        self.adapted_model_metadata = None

        # ==================================================
        # REPLAY BUFFER
        # ==================================================

        self.replay_buffer = ReplayBuffer(
            capacity=buffer_capacity,
            input_window=input_window,
            prediction_horizon=prediction_horizon,
            num_features=num_features,
        )

        # ==================================================
        # ONLINE LEARNER
        # ==================================================

        self.learner = OnlineLearner(
            model=self.model,
            scaler=scaler,
            learning_rate=learning_rate,
            device=str(self.device),
        )

        # ==================================================
        # ADAPTATION CONTROLLER
        # ==================================================

        self.controller = AdaptationController(
            replay_buffer=self.replay_buffer,
            learner=self.learner,
            batch_size=adaptation_batch_size,
            minimum_samples=minimum_samples,
            adaptation_interval=adaptation_interval,
        )

        # ==================================================
        # RESTORE SELF-LEARNING STATE
        # ==================================================

        if self.loaded_checkpoint is not None:

            # ----------------------------------------------
            # Restore learner state
            # ----------------------------------------------

            self.learner.load_state(
                self.loaded_checkpoint.get(
                    "learner_state",
                    {},
                )
            )

            # ----------------------------------------------
            # Restore controller statistics
            # ----------------------------------------------

            self.controller.load_state(
                self.loaded_checkpoint.get(
                    "adaptation_state",
                    {},
                )
            )

            # ----------------------------------------------
            # IMPORTANT
            #
            # Replay buffer is NOT persistent.
            #
            # After restart:
            #
            # Buffer = 0
            #
            # Therefore adaptation sample counter
            # must also restart from 0.
            # ----------------------------------------------

            self.controller.last_adaptation_sample_count = 0

            # ----------------------------------------------
            # Restore metadata
            # ----------------------------------------------

            self.adapted_model_metadata = (
                self.loaded_checkpoint.get(
                    "metadata",
                    {},
                )
            )

        else:

            self.adapted_model_metadata = None

    # ======================================================
    # LOAD MODEL
    # ======================================================

    def _load_model(
        self,
        model_path: str,
    ) -> None:

        path = Path(
            model_path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Model not found: {path}"
            )

        checkpoint = torch.load(
            path,
            map_location=self.device,
            weights_only=False,
        )

        # Support checkpoint dictionaries
        # and direct state dictionaries.

        if (
            isinstance(
                checkpoint,
                dict,
            )
            and "model_state_dict"
            in checkpoint
        ):

            state_dict = (
                checkpoint[
                    "model_state_dict"
                ]
            )

        else:

            state_dict = checkpoint

        self.model.load_state_dict(
            state_dict
        )

        self.model.to(
            self.device
        )

        self.model.eval()

    # ======================================================
    # NORMALIZE
    # ======================================================

    def _normalize(
        self,
        data: np.ndarray,
    ) -> np.ndarray:

        original_shape = data.shape

        flattened = data.reshape(
            -1,
            self.num_features,
        )

        normalized = (
            self.learner.scaler.transform(
                flattened
            )
        )

        return normalized.reshape(
            original_shape
        )

    # ======================================================
    # PREDICT
    # ======================================================

    def predict(
        self,
        history: np.ndarray,
    ) -> dict:
        """
        Predict future water-quality values.

        history shape:

            (60, 5)
        """

        history = np.asarray(
            history,
            dtype=np.float32,
        )

        expected_shape = (
            self.input_window,
            self.num_features,
        )

        if history.shape != expected_shape:

            raise ValueError(
                "Invalid history shape. "
                f"Expected {expected_shape}, "
                f"received {history.shape}"
            )

        # ----------------------------------------------
        # Normalize
        # ----------------------------------------------

        normalized = self._normalize(
            history
        )

        # ----------------------------------------------
        # Tensor
        # ----------------------------------------------

        X_tensor = torch.tensor(
            normalized,
            dtype=torch.float32,
            device=self.device,
        ).unsqueeze(0)

        # ----------------------------------------------
        # Predict
        # ----------------------------------------------

        self.model.eval()

        with torch.no_grad():

            predictions, confidence = (
                self.model(X_tensor)
            )

        predictions = (
            predictions
            .cpu()
            .numpy()[0]
        )

        confidence = (
            confidence
            .cpu()
            .numpy()[0]
        )

        # ----------------------------------------------
        # Convert prediction to real values
        # ----------------------------------------------

        predictions_original = (
            self.learner.scaler.inverse_transform(
                predictions
            )
        )

        return {
            "prediction":
                predictions_original,

            "confidence":
                confidence,
        }

    # ======================================================
    # ADD OBSERVATION
    # ======================================================

    def add_observation(
        self,
        observation,
    ) -> dict:
        """
        Add one new real sensor reading.

        Expected:

        [
            pH,
            turbidity,
            temperature,
            DO,
            TDS
        ]
        """

        observation = np.asarray(
            observation,
            dtype=np.float32,
        )

        # ----------------------------------------------
        # Add to buffer
        # ----------------------------------------------

        sample_created = (
            self.replay_buffer
            .add_observation(
                observation
            )
        )

        # ----------------------------------------------
        # Adapt if enough samples
        # ----------------------------------------------

        adaptation_result = None

        saved_model_path = None

        if self.controller.is_ready():

            adaptation_result = (
                self.controller.adapt()
            )

    # ----------------------------------------------
    # Save model only after accepted adaptation
    # ----------------------------------------------

        if (
            adaptation_result is not None and
            adaptation_result.get("status")
            == "accepted"
        ):

            saved_model_path = (
                self._save_adapted_model(
                adaptation_result
                )
            )

        return {
            "sample_created":
                sample_created,

            "observation_count":
                self.replay_buffer
                .observation_count(),

            "learning_samples":
                len(
                    self.replay_buffer
                ),

            "adaptation":
                adaptation_result,

            "saved_model_path":
                saved_model_path,
        }

    # ======================================================
    # PREDICT FROM BUFFER
    # ======================================================

    def predict_from_buffer(
        self,
    ) -> dict | None:
        """
        Predict using the latest
        real sensor observations.
        """

        observations = list(
            self.replay_buffer
            .observations
        )

        if (
            len(observations)
            < self.input_window
        ):

            return None

        history = np.asarray(
            observations[
                -self.input_window:
            ],
            dtype=np.float32,
        )

        return self.predict(
            history
        )

    # ======================================================
    # PROCESS OBSERVATION
    # ======================================================

    def process_observation(
        self,
        observation,
    ) -> dict:
        """
        Main method for the live system.

        Flow:

        New Observation
            ↓

        Store

            ↓

        Predict

            ↓

        Adapt if required
        """

        buffer_result = (
            self.add_observation(
                observation
            )
        )

        prediction_result = (
            self.predict_from_buffer()
        )

        return {
            "buffer":
                buffer_result,

            "prediction":
                prediction_result,
        }

# ======================================================
# SAVE ADAPTED MODEL
# ======================================================

    # ======================================================
# SAVE SELF-LEARNING CHECKPOINT
# ======================================================

    def _save_adapted_model(
        self,
        adaptation_result: dict,
        ) -> str:
        """
        Save the complete self-learning checkpoint
        after an accepted model update.
        """

        metadata = {

            "learning_samples":
                len(self.replay_buffer),

            "adaptation_result":
                adaptation_result,
        }

        saved_path = self.model_store.save(
            model=self.model,

            adaptation_state=(
                self.controller.get_state()
            ),

            learner_state=(
                self.learner.get_state()
            ),

            metadata=metadata,
        )

        # Store latest metadata
        self.adapted_model_metadata = (
            metadata
        )

        return saved_path

    # ======================================================
    # STATUS
    # ======================================================

    def get_status(
        self,
        ) -> dict:

        return {

    "device":
        str(self.device),

    "model_loaded":
        True,

    "checkpoint_loaded":
        self.loaded_checkpoint is not None,

    "observation_count":
        self.replay_buffer
        .observation_count(),

    "learning_samples":
        len(
            self.replay_buffer
        ),

    "adaptation":
        self.controller.get_status(),

    "learner":
        self.learner.get_status(),

    "model_store":
        self.model_store.get_info(),

    "adapted_model_metadata":
        self.adapted_model_metadata,
}