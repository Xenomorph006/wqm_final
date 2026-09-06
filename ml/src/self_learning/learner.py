from __future__ import annotations

from typing import Any

import numpy as np
import torch
import torch.nn as nn


class OnlineLearner:
    """
    Performs controlled online learning for the LNN.

    The learner receives raw water-quality samples
    from the Replay Buffer, normalizes them using
    the existing scaler, and performs small gradient
    updates on the pre-trained LNN.
    """

    def __init__(
        self,
        model: nn.Module,
        scaler: Any,
        learning_rate: float = 1e-5,
        weight_decay: float = 1e-6,
        device: str | None = None,
    ) -> None:

        # --------------------------------------------------
        # Device
        # --------------------------------------------------

        if device is None:

            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        self.device = torch.device(
            device
        )

        # --------------------------------------------------
        # Model
        # --------------------------------------------------

        self.model = model.to(
            self.device
        )

        # --------------------------------------------------
        # Scaler
        # --------------------------------------------------

        self.scaler = scaler

        # --------------------------------------------------
        # Optimizer
        # --------------------------------------------------

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
        )

        # --------------------------------------------------
        # Loss
        # --------------------------------------------------

        self.loss_function = nn.MSELoss()

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self.total_updates = 0

        self.last_loss = None

    # ======================================================
    # NORMALIZATION
    # ======================================================

    def normalize_batch(
        self,
        data: np.ndarray,
    ) -> np.ndarray:
        """
        Normalize a batch of sequences.

        Input:
            (batch, sequence, features)

        Output:
            (batch, sequence, features)
        """

        original_shape = data.shape

        flattened = data.reshape(
            -1,
            original_shape[-1],
        )

        normalized = (
            self.scaler.transform(
                flattened
            )
        )

        return normalized.reshape(
            original_shape
        )

    # ======================================================
    # LEARNING STEP
    # ======================================================

    def learn(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> dict:
        """
        Perform one controlled online learning step.

        X:
            Historical water-quality sequences

        y:
            Actual future observations
        """

        # --------------------------------------------------
        # Normalize
        # --------------------------------------------------

        X_normalized = (
            self.normalize_batch(X)
        )

        y_normalized = (
            self.normalize_batch(y)
        )

        # --------------------------------------------------
        # Convert to tensors
        # --------------------------------------------------

        X_tensor = torch.tensor(
            X_normalized,
            dtype=torch.float32,
            device=self.device,
        )

        y_tensor = torch.tensor(
            y_normalized,
            dtype=torch.float32,
            device=self.device,
        )

        # --------------------------------------------------
        # Training mode
        # --------------------------------------------------

        self.model.train()

        # --------------------------------------------------
        # Forward pass
        # --------------------------------------------------

        predictions, confidence = (
            self.model(X_tensor)
        )

        # --------------------------------------------------
        # Prediction loss
        # --------------------------------------------------

        prediction_loss = (
            self.loss_function(
                predictions,
                y_tensor,
            )
        )

        # --------------------------------------------------
        # Confidence regularization
        #
        # Prevent confidence from
        # collapsing toward zero.
        # --------------------------------------------------

        confidence_regularization = (
            torch.mean(
                (confidence - 0.7) ** 2
            )
        )

        # --------------------------------------------------
        # Total loss
        # --------------------------------------------------

        total_loss = (
            prediction_loss
            +
            0.01
            * confidence_regularization
        )

        # --------------------------------------------------
        # Backpropagation
        # --------------------------------------------------

        self.optimizer.zero_grad()

        total_loss.backward()

        # --------------------------------------------------
        # Gradient clipping
        # --------------------------------------------------

        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            max_norm=1.0,
        )

        # --------------------------------------------------
        # Update
        # --------------------------------------------------

        self.optimizer.step()

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self.total_updates += 1

        self.last_loss = float(
            total_loss.item()
        )

        return {
            "loss":
                self.last_loss,

            "prediction_loss":
                float(
                    prediction_loss.item()
                ),

            "confidence_loss":
                float(
                    confidence_regularization.item()
                ),

            "mean_confidence":
                float(
                    confidence.mean().item()
                ),

            "total_updates":
                self.total_updates,
        }

    # ======================================================
    # EVALUATE
    # ======================================================

    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> dict:
        """
        Evaluate without changing
        model parameters.
        """

        X_normalized = (
            self.normalize_batch(X)
        )

        y_normalized = (
            self.normalize_batch(y)
        )

        X_tensor = torch.tensor(
            X_normalized,
            dtype=torch.float32,
            device=self.device,
        )

        y_tensor = torch.tensor(
            y_normalized,
            dtype=torch.float32,
            device=self.device,
        )

        self.model.eval()

        with torch.no_grad():

            predictions, confidence = (
                self.model(X_tensor)
            )

            loss = self.loss_function(
                predictions,
                y_tensor,
            )

        return {
            "loss":
                float(loss.item()),

            "mean_confidence":
                float(
                    confidence.mean().item()
                ),
        }


    def get_state(self) -> dict:
        """
        Return persistent learner state.
        """

        return {

            "total_updates":
                self.total_updates,

            "last_loss":
                self.last_loss,
        }

    def load_state(
        self,
        state: dict,
    ) -> None:
        """
        Restore learner state from checkpoint.
        """

        if not state:
            return

        self.total_updates = (
            state.get(
                "total_updates",
                0,
            )
        )

        self.last_loss = (
            state.get(
                "last_loss",
                None,
            )
        )


    # ======================================================
    # MODEL INFORMATION
    # ======================================================

    def get_status(
        self,
    ) -> dict:

        return {
            "device":
                str(self.device),

            "total_updates":
                self.total_updates,

            "last_loss":
                self.last_loss,
        }