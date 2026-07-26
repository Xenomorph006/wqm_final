"""
=========================================================
Trainer Module
---------------------------------------------------------
Training & Evaluation Utilities
=========================================================
"""

import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score


class Trainer:

    def __init__(
        self,
        model,
        optimizer,
        criterion,
        device
    ):

        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device

    def train_epoch(self, loader):

        self.model.train()

        running_loss = 0
        predictions = []
        targets = []

        for x, y in loader:

            x = x.to(self.device)
            y = y.to(self.device).float()

            self.optimizer.zero_grad()

            output = self.model(x)


            loss = self.criterion(output, y)

            loss.backward()

            self.optimizer.step()

            running_loss += loss.item()

            preds = (output >= 0.5).float()

            predictions.extend(preds.cpu().numpy())

            targets.extend(y.cpu().numpy())

        accuracy = accuracy_score(
            targets,
            predictions
        )

        return running_loss / len(loader), accuracy

    @torch.no_grad()
    def evaluate(self, loader):

        self.model.eval()

        running_loss = 0
        predictions = []
        targets = []

        for x, y in loader:

            x = x.to(self.device)
            y = y.to(self.device).float()

            output = self.model(x)


            loss = self.criterion(output, y)

            running_loss += loss.item()

            preds = (output >= 0.5).float()

            predictions.extend(preds.cpu().numpy())

            targets.extend(y.cpu().numpy())

        accuracy = accuracy_score(
            targets,
            predictions
        )

        return running_loss / len(loader), accuracy