from __future__ import annotations

import torch
import torch.nn as nn


class ForecastUncertaintyLoss(nn.Module):
    """
    Gaussian negative log-likelihood style loss.

    prediction:
        Model's predicted value.

    target:
        Ground-truth future value.

    confidence:
        Model confidence in [0, 1].

    Higher confidence should correspond to
    lower prediction uncertainty.
    """

    def __init__(
        self,
        confidence_weight: float = 0.1,
    ) -> None:

        super().__init__()

        self.confidence_weight = (
            confidence_weight
        )

    def forward(
        self,
        prediction: torch.Tensor,
        target: torch.Tensor,
        confidence: torch.Tensor,
    ) -> torch.Tensor:

        confidence = torch.clamp(
            confidence,
            min=1e-4,
            max=1.0 - 1e-4,
        )

        # Convert confidence to uncertainty.
        uncertainty = (
            1.0 - confidence
        )

        uncertainty = (
            uncertainty + 1e-4
        )

        squared_error = (
            prediction - target
        ) ** 2

        likelihood_loss = (
            squared_error
            / uncertainty
        )

        confidence_regularization = (
            torch.log(uncertainty)
        )

        loss = (
            likelihood_loss
            + confidence_regularization
        )

        loss = loss.mean()

        return loss


class CombinedForecastLoss(nn.Module):
    """
    Combines normal prediction error with
    uncertainty-aware loss.
    """

    def __init__(
        self,
        prediction_weight: float = 1.0,
        uncertainty_weight: float = 0.1,
    ) -> None:

        super().__init__()

        self.prediction_weight = (
            prediction_weight
        )

        self.uncertainty_weight = (
            uncertainty_weight
        )

        self.mse = nn.MSELoss()

        self.uncertainty_loss = (
            ForecastUncertaintyLoss()
        )

    def forward(
        self,
        prediction: torch.Tensor,
        target: torch.Tensor,
        confidence: torch.Tensor,
    ) -> torch.Tensor:

        prediction_loss = self.mse(
            prediction,
            target,
        )

        uncertainty_loss = (
            self.uncertainty_loss(
                prediction,
                target,
                confidence,
            )
        )

        return (
            self.prediction_weight
            * prediction_loss
            +
            self.uncertainty_weight
            * uncertainty_loss
        )