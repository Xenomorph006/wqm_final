from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import torch


class ModelStore:
    """
    Persistent checkpoint storage for
    the self-learning LNN system.

    Stores:

    - Model weights
    - Adaptation controller state
    - Online learner state
    - Learning metadata
    """

    def __init__(
        self,
        directory: str = "models/adapted",
        filename: str = "lnn_latest.pt",
    ) -> None:

        self.directory = Path(directory)

        self.filename = filename

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.model_path = (
            self.directory
            / self.filename
        )

    # ==================================================
    # CHECKPOINT EXISTS
    # ==================================================

    def exists(self) -> bool:

        return self.model_path.exists()

    # ==================================================
    # SAVE CHECKPOINT
    # ==================================================

    def save(
        self,
        model,
        adaptation_state: dict,
        learner_state: dict,
        metadata: dict | None = None,
    ) -> str:
        """
        Save complete self-learning checkpoint.
        """

        checkpoint = {

            # ------------------------------------------
            # MODEL
            # ------------------------------------------

            "model_state_dict":
                model.state_dict(),

            # ------------------------------------------
            # ADAPTATION
            # ------------------------------------------

            "adaptation_state":
                adaptation_state,

            # ------------------------------------------
            # LEARNER
            # ------------------------------------------

            "learner_state":
                learner_state,

            # ------------------------------------------
            # METADATA
            # ------------------------------------------

            "metadata":
                metadata or {},

            # ------------------------------------------
            # TIMESTAMP
            # ------------------------------------------

            "saved_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }

        torch.save(
            checkpoint,
            self.model_path,
        )

        return str(
            self.model_path
        )

    # ==================================================
    # LOAD CHECKPOINT
    # ==================================================

    def load(
        self,
        model,
        device: str = "cpu",
    ) -> dict | None:
        """
        Load complete self-learning checkpoint.

        Returns checkpoint state.
        """

        if not self.exists():

            return None

        checkpoint = torch.load(
            self.model_path,
            map_location=device,
            weights_only=False,
        )

        model.load_state_dict(
            checkpoint[
                "model_state_dict"
            ]
        )

        return {

            "adaptation_state":
                checkpoint.get(
                    "adaptation_state",
                    {},
                ),

            "learner_state":
                checkpoint.get(
                    "learner_state",
                    {},
                ),

            "metadata":
                checkpoint.get(
                    "metadata",
                    {},
                ),

            "saved_at":
                checkpoint.get(
                    "saved_at",
                    None,
                ),
        }

    # ==================================================
    # GET INFO
    # ==================================================

    def get_info(self) -> dict:

        return {

            "path":
                str(self.model_path),

            "exists":
                self.exists(),

            "size_bytes":
                (
                    self.model_path.stat().st_size
                    if self.exists()
                    else 0
                ),
        }