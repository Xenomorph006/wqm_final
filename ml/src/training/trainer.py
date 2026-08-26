from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from .losses import CombinedForecastLoss
from .metrics import (
    mae,
    rmse,
    r2_score,
)


class LNNTrainer:

    def __init__(
        self,
        model,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-5,
        device: str | None = None,
    ) -> None:

        self.model = model

        if device is None:

            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        self.device = torch.device(
            device
        )

        self.model.to(
            self.device
        )

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
        )

        self.loss_function = (
            CombinedForecastLoss()
        )

        self.history = {
            "train_loss": [],
            "validation_loss": [],
        }

    def create_loader(
        self,
        X: np.ndarray,
        y: np.ndarray,
        batch_size: int = 64,
        shuffle: bool = False,
    ) -> DataLoader:

        X_tensor = torch.from_numpy(
            X
        ).float()

        y_tensor = torch.from_numpy(
            y
        ).float()

        dataset = TensorDataset(
            X_tensor,
            y_tensor,
        )

        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
        )

    def train_epoch(
        self,
        loader: DataLoader,
    ) -> float:

        self.model.train()

        total_loss = 0.0

        total_samples = 0

        for X_batch, y_batch in loader:

            X_batch = X_batch.to(
                self.device
            )

            y_batch = y_batch.to(
                self.device
            )

            self.optimizer.zero_grad()

            predictions, confidence = (
                self.model(
                    X_batch
                )
            )

            loss = (
                self.loss_function(
                    predictions,
                    y_batch,
                    confidence,
                )
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                max_norm=1.0,
            )

            self.optimizer.step()

            batch_size = (
                X_batch.size(0)
            )

            total_loss += (
                loss.item()
                * batch_size
            )

            total_samples += (
                batch_size
            )

        return (
            total_loss
            / total_samples
        )

    @torch.no_grad()
    def validate(
        self,
        loader: DataLoader,
    ) -> float:

        self.model.eval()

        total_loss = 0.0

        total_samples = 0

        for X_batch, y_batch in loader:

            X_batch = X_batch.to(
                self.device
            )

            y_batch = y_batch.to(
                self.device
            )

            predictions, confidence = (
                self.model(
                    X_batch
                )
            )

            loss = (
                self.loss_function(
                    predictions,
                    y_batch,
                    confidence,
                )
            )

            batch_size = (
                X_batch.size(0)
            )

            total_loss += (
                loss.item()
                * batch_size
            )

            total_samples += (
                batch_size
            )

        return (
            total_loss
            / total_samples
        )

    def fit(
        self,
        train_loader: DataLoader,
        validation_loader: DataLoader,
        epochs: int = 50,
        checkpoint_path: str | Path | None = None,
    ) -> dict:

        best_validation_loss = float(
            "inf"
        )

        for epoch in range(
            1,
            epochs + 1,
        ):

            train_loss = (
                self.train_epoch(
                    train_loader
                )
            )

            validation_loss = (
                self.validate(
                    validation_loader
                )
            )

            self.history[
                "train_loss"
            ].append(
                train_loss
            )

            self.history[
                "validation_loss"
            ].append(
                validation_loss
            )

            print(
                f"Epoch "
                f"{epoch:03d}/{epochs:03d} | "
                f"Train Loss: "
                f"{train_loss:.6f} | "
                f"Val Loss: "
                f"{validation_loss:.6f}"
            )

            if (
                validation_loss
                < best_validation_loss
            ):

                best_validation_loss = (
                    validation_loss
                )

                if checkpoint_path is not None:

                    self.save_checkpoint(
                        checkpoint_path
                    )

        return self.history

    def evaluate(
        self,
        loader: DataLoader,
    ) -> dict:

        self.model.eval()

        predictions = []
        targets = []
        confidences = []

        with torch.no_grad():

            for X_batch, y_batch in loader:

                X_batch = X_batch.to(
                    self.device
                )

                pred, conf = self.model(
                    X_batch
                )

                predictions.append(
                    pred.cpu().numpy()
                )

                targets.append(
                    y_batch.numpy()
                )

                confidences.append(
                    conf.cpu().numpy()
                )

        predictions = np.concatenate(
            predictions,
            axis=0,
        )

        targets = np.concatenate(
            targets,
            axis=0,
        )

        confidences = np.concatenate(
            confidences,
            axis=0,
        )

        metrics = {
            "MAE": mae(
                predictions,
                targets,
            ),
            "RMSE": rmse(
                predictions,
                targets,
            ),
            "R2": r2_score(
                predictions,
                targets,
            ),
            "mean_confidence": float(
                np.mean(
                    confidences
                )
            ),
        }

        return {
            "metrics": metrics,
            "predictions": predictions,
            "targets": targets,
            "confidence": confidences,
        }

    def save_checkpoint(
        self,
        path: str | Path,
    ) -> None:

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        torch.save(
            {
                "model_state_dict":
                    self.model.state_dict(),

                "optimizer_state_dict":
                    self.optimizer.state_dict(),

                "history":
                    self.history,
            },
            path,
        )