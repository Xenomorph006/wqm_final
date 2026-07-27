"""
=========================================================
Neuro-Fuzzy Module
---------------------------------------------------------
This module implements:

1. Gaussian Membership Layer
2. Fuzzy Rule Layer
=========================================================
"""

import torch
import torch.nn as nn


class GaussianMembership(nn.Module):
    """
    Learnable Gaussian Membership Functions

    Each input feature has multiple fuzzy memberships.

    Example

    pH
      ↓
    Low
    Normal
    High

    Temperature
      ↓
    Cold
    Normal
    Hot
    """

    def __init__(self,
                 input_dim: int,
                 num_memberships: int):

        super().__init__()

        self.input_dim = input_dim
        self.num_memberships = num_memberships

        # Learnable Gaussian centers
        self.centers = nn.Parameter(
            torch.randn(input_dim, num_memberships)
        )

        # Learnable Gaussian widths
        self.sigmas = nn.Parameter(
            torch.ones(input_dim, num_memberships)
        )

    def forward(self, x):

        """
        x

        Shape:
        (Batch, Features)

        Returns

        Shape:
        (Batch, Features, Memberships)
        """

        x = x.unsqueeze(-1)

        memberships = torch.exp(

            -((x - self.centers) ** 2)

            /

            (2 * (self.sigmas ** 2) + 1e-8)

        )

        return memberships


class FuzzyRuleLayer(nn.Module):
    """
    Trainable Neuro-Fuzzy Rule Layer

    Converts fuzzy memberships
    into trainable hidden rules.
    """

    def __init__(self,
                 input_dim: int,
                 num_memberships: int,
                 hidden_dim: int):

        super().__init__()

        self.flatten = nn.Flatten()

        self.rule_generator = nn.Sequential(

            nn.Linear(

                input_dim * num_memberships,

                hidden_dim

            ),

            nn.ReLU(),

            nn.Linear(

                hidden_dim,

                hidden_dim

            ),

            nn.ReLU()

        )

    def forward(self, memberships):

        memberships = self.flatten(memberships)

        rules = self.rule_generator(

            memberships

        )

        return rules