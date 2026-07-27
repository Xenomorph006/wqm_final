"""
=========================================================
Liquid Neural Module
---------------------------------------------------------
This module implements a custom Liquid Neural Cell.

=========================================================
"""

import torch
import torch.nn as nn


class LiquidCell(nn.Module):
    """
    Custom Liquid Time-Constant Cell

    h(t+1) = h(t) + dt * (-h(t) + f(x,h))/tau

    tau is learnable.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        dt: float = 1.0
    ):

        super().__init__()

        self.hidden_dim = hidden_dim
        self.dt = dt

        # Input transformation
        self.input_layer = nn.Linear(
            input_dim,
            hidden_dim
        )

        # Hidden transformation
        self.hidden_layer = nn.Linear(
            hidden_dim,
            hidden_dim
        )

        # Learnable time constant
        self.tau_layer = nn.Linear(
            input_dim,
            hidden_dim
        )

        self.activation = nn.Tanh()

    def forward(self, x, h):

        """
        x : (batch,input_dim)

        h : (batch,hidden_dim)
        """

        # Candidate state
        candidate = self.activation(

            self.input_layer(x)

            +

            self.hidden_layer(h)

        )

        # Adaptive time constant

        tau = torch.sigmoid(

            self.tau_layer(x)

        ) + 0.1

        # Liquid update equation

        h_new = h + self.dt * (

            -h + candidate

        ) / tau

        return h_new