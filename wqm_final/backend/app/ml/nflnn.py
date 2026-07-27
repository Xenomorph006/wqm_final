"""
=========================================================
Neuro-Fuzzy Liquid Neural Network
---------------------------------------------------------
Complete Model Architecture

Input
 ↓
Gaussian Membership
 ↓
Fuzzy Rule Layer
 ↓
Liquid Cell
 ↓
Classifier
 ↓
Good / Bad

=========================================================
"""

import torch
import torch.nn as nn

from .fuzzy import GaussianMembership
from .fuzzy import FuzzyRuleLayer

from .liquid import LiquidCell


class NFLNN(nn.Module):

    def __init__(
        self,
        input_dim=4,
        num_memberships=3,
        rule_dim=32,
        hidden_dim=32
    ):

        super().__init__()

        # -------------------------
        # Fuzzy Layer
        # -------------------------

        self.membership = GaussianMembership(
            input_dim,
            num_memberships
        )

        self.rules = FuzzyRuleLayer(
            input_dim,
            num_memberships,
            rule_dim
        )

        # -------------------------
        # Liquid Layer
        # -------------------------

        self.liquid = LiquidCell(
            input_dim=rule_dim,
            hidden_dim=hidden_dim
        )

        # -------------------------
        # Classifier
        # -------------------------

        self.classifier = nn.Sequential(

            nn.Linear(
                hidden_dim,
                16
            ),

            nn.ReLU(),

            nn.Dropout(0.30),

            nn.Linear(
                16,
                1
            ),

            nn.Sigmoid()

        )

    def forward(self, x):

        batch_size = x.size(0)

        h = torch.zeros(
            batch_size,
            self.liquid.hidden_dim,
            device=x.device 
        )

        sequence_length = x.size(1)

        for t in range(sequence_length):

            xt = x[:, t, :]

            memberships = self.membership(xt)

            rules = self.rules(memberships)

            h = self.liquid(
                rules,
                h)

        output = self.classifier(h)

        return output