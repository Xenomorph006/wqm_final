from __future__ import annotations

import torch
import torch.nn as nn


class LiquidCell(nn.Module):
    """
    Simplified continuous-time liquid recurrent cell.

    The hidden state evolves according to:

        dh/dt = (-h + f(Wx + Uh + b)) / tau

    where tau is a learnable time constant.

    The discretized update is:

        h(t+1) = h(t) + dt * dh/dt
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        dt: float = 1.0,
    ) -> None:

        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.dt = dt

        self.input_projection = nn.Linear(
            input_size,
            hidden_size,
        )

        self.recurrent_projection = nn.Linear(
            hidden_size,
            hidden_size,
            bias=False,
        )

        self.bias = nn.Parameter(
            torch.zeros(hidden_size)
        )

        self.log_tau = nn.Parameter(
            torch.zeros(hidden_size)
        )

    def forward(
        self,
        x: torch.Tensor,
        hidden: torch.Tensor,
    ) -> torch.Tensor:

        tau = (
            torch.exp(self.log_tau)
            + 1e-4
        )

        drive = (
            self.input_projection(x)
            + self.recurrent_projection(hidden)
            + self.bias
        )

        candidate = torch.tanh(
            drive
        )

        dh = (
            -hidden + candidate
        ) / tau

        new_hidden = (
            hidden
            + self.dt * dh
        )

        return new_hidden


class LiquidNeuralNetwork(nn.Module):
    """
    Liquid Neural Network for multi-step
    water-quality forecasting.

    Input:
        [batch, sequence_length, 5]

    Output:
        predictions:
            [batch, prediction_horizon, 5]

        confidence:
            [batch, prediction_horizon, 5]
    """

    def __init__(
        self,
        input_size: int = 5,
        hidden_size: int = 64,
        output_size: int = 5,
        prediction_horizon: int = 12,
        dt: float = 1.0,
    ) -> None:

        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.prediction_horizon = (
            prediction_horizon
        )

        # ----------------------------------------------------
        # Input projection
        # ----------------------------------------------------

        self.input_layer = nn.Linear(
            input_size,
            hidden_size,
        )

        # ----------------------------------------------------
        # Liquid recurrent layer
        # ----------------------------------------------------

        self.liquid_cell = LiquidCell(
            input_size=hidden_size,
            hidden_size=hidden_size,
            dt=dt,
        )

        # ----------------------------------------------------
        # Prediction head
        # ----------------------------------------------------

        self.prediction_head = nn.Sequential(
            nn.Linear(
                hidden_size,
                hidden_size,
            ),
            nn.Tanh(),
            nn.Linear(
                hidden_size,
                output_size,
            ),
        )

        # ----------------------------------------------------
        # Confidence head
        # ----------------------------------------------------

        self.confidence_head = nn.Sequential(
            nn.Linear(
                hidden_size,
                hidden_size,
            ),
            nn.Tanh(),
            nn.Linear(
                hidden_size,
                output_size,
            ),
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> tuple[
        torch.Tensor,
        torch.Tensor,
    ]:

        batch_size = x.size(0)

        device = x.device

        # ----------------------------------------------------
        # Initial hidden state
        # ----------------------------------------------------

        hidden = torch.zeros(
            batch_size,
            self.hidden_size,
            device=device,
        )

        # ----------------------------------------------------
        # Process historical sequence
        # ----------------------------------------------------

        sequence_length = x.size(1)

        for timestep in range(
            sequence_length
        ):

            current_input = x[
                :, timestep, :
            ]

            projected = torch.tanh(
                self.input_layer(
                    current_input
                )
            )

            hidden = self.liquid_cell(
                projected,
                hidden,
            )

        # ----------------------------------------------------
        # Multi-step prediction
        # ----------------------------------------------------

        predictions = []

        confidences = []

        current_hidden = hidden

        for _ in range(
            self.prediction_horizon
        ):

            prediction = (
                self.prediction_head(
                    current_hidden
                )
            )

            # Softplus guarantees positive
            # uncertainty.
            uncertainty = (
                torch.nn.functional.softplus(
                    self.confidence_head(
                        current_hidden
                    )
                )
                + 1e-6
            )

            # Convert uncertainty into
            # bounded confidence.
            confidence = (
                1.0
                / (1.0 + uncertainty)
            )

            predictions.append(
                prediction
            )

            confidences.append(
                confidence
            )

            # ------------------------------------------------
            # Autoregressive hidden-state update
            # ------------------------------------------------

            projected_prediction = torch.tanh(
                self.input_layer(
                    prediction
                )
            )

            current_hidden = (
                self.liquid_cell(
                    projected_prediction,
                    current_hidden,
                )
            )

        predictions = torch.stack(
            predictions,
            dim=1,
        )

        confidences = torch.stack(
            confidences,
            dim=1,
        )

        return (
            predictions,
            confidences,
        )