from __future__ import annotations

from copy import deepcopy

import numpy as np

from .replay_buffer import ReplayBuffer
from .learner import OnlineLearner


class AdaptationController:
    """
    Controls when and how the LNN performs
    online self-learning.

    The controller prevents unnecessary or
    harmful updates by checking:

    1. Enough learning samples exist
    2. Current prediction error is meaningful
    3. The update improves performance
    4. Bad updates are rejected
    """

    def __init__(
        self,
        replay_buffer: ReplayBuffer,
        learner: OnlineLearner,
        batch_size: int = 32,
        minimum_samples: int = 64,
        error_threshold: float = 0.01,
        max_allowed_loss_increase: float = 0.02,
        adaptation_interval: int = 60,
    ) -> None:

        self.replay_buffer = replay_buffer

        self.learner = learner

        self.batch_size = batch_size

        self.minimum_samples = (
            minimum_samples
        )

        self.error_threshold = (
            error_threshold
        )

        self.max_allowed_loss_increase = (
            max_allowed_loss_increase
        )

        self.adaptation_interval = (
            adaptation_interval
        )



        # ----------------------------------------------
        # Statistics
        # ----------------------------------------------

        self.accepted_updates = 0

        self.rejected_updates = 0

        self.skipped_updates = 0

        self.last_result = None

        self.last_adaptation_sample_count = 0

    # ==================================================
    # CHECK IF READY
    # ==================================================

    def is_ready(self) -> bool:
        """
        Check whether the system has enough
        new learning samples for adaptation.
        """

        current_samples = len(
        self.replay_buffer
        )

    # ------------------------------------------
    # Minimum samples required
    # ------------------------------------------

        if (
            current_samples
            < self.minimum_samples
        ):

            return False

    # ------------------------------------------
    # Require new samples since
    # previous adaptation
    # ------------------------------------------

        new_samples = (
         current_samples
            - self.last_adaptation_sample_count
        )

        return (
            new_samples
            >= self.adaptation_interval
        )

    # ==================================================
    # ADAPT
    # ==================================================

    def adapt(self) -> dict:
        """
        Attempt a controlled online learning update.
        """

    # ----------------------------------------------
    # Check samples and adaptation interval
    # ----------------------------------------------

        if not self.is_ready():

            self.skipped_updates += 1

            result = {
                "status": "skipped",
                "reason": "not_ready_for_adaptation",
                "available_samples":
                    len(self.replay_buffer),
                "minimum_samples":
                    self.minimum_samples,
                "last_adaptation_sample_count":
                    self.last_adaptation_sample_count,
                "adaptation_interval":
                    self.adaptation_interval,
            }

            self.last_result = result

            return result

        # ----------------------------------------------
        # Record current sample count
        #
        # This represents the point where an actual
        # adaptation check is happening.
        # ----------------------------------------------

        current_sample_count = len(
            self.replay_buffer
        )

        # ----------------------------------------------
        # Sample recent data
        # ----------------------------------------------

        X, y = self.replay_buffer.get_latest(
            self.batch_size
        )

        # ----------------------------------------------
        # Evaluate before update
        # ----------------------------------------------

        before = self.learner.evaluate(
            X,
            y,
        )

        before_loss = before["loss"]

        # ----------------------------------------------
        # Check if adaptation is needed
        # ----------------------------------------------

        if before_loss < self.error_threshold:

            self.skipped_updates += 1

            # Record this adaptation check
            # so it does not run again immediately.
            self.last_adaptation_sample_count = (
                current_sample_count
            )

            result = {
                "status": "skipped",
                "reason": "error_below_threshold",
                "loss": before_loss,
                "threshold": self.error_threshold,
            }

            self.last_result = result

            return result

        # ----------------------------------------------
        # Backup model
        # ----------------------------------------------

        model_backup = deepcopy(
            self.learner.model.state_dict()
        )

        # ----------------------------------------------
        # Learn
        # ----------------------------------------------

        learning_result = self.learner.learn(
            X,
            y,
        )

        # ----------------------------------------------
        # Evaluate after update
        # ----------------------------------------------

        after = self.learner.evaluate(
            X,
            y,
        )

        after_loss = after["loss"]

        # ----------------------------------------------
        # Calculate change
        # ----------------------------------------------

        loss_change = (
            after_loss
            - before_loss
        )

        # ----------------------------------------------
        # Reject bad update
        # ----------------------------------------------

        if (
            loss_change
            > self.max_allowed_loss_increase
        ):

            self.learner.model.load_state_dict(
                model_backup
            )

            self.rejected_updates += 1

            # Record adaptation attempt
            self.last_adaptation_sample_count = (
                current_sample_count
            )

            result = {
                "status": "rejected",

                "before_loss":
                    before_loss,

                "after_loss":
                    after_loss,

                "loss_change":
                    loss_change,

                "learning":
                    learning_result,
            }

            self.last_result = result

            return result

    # ----------------------------------------------
    # Accept update
    # ----------------------------------------------

        self.accepted_updates += 1

    # Record successful adaptation
        self.last_adaptation_sample_count = (
        current_sample_count
        )

        result = {
        "status": "accepted",

        "before_loss":
            before_loss,

        "after_loss":
            after_loss,

        "loss_change":
            loss_change,

        "learning":
            learning_result,
        }

        self.last_result = result

        return result

    def get_state(self) -> dict:
        """
        Return persistent adaptation state.
        """

        return {

            "accepted_updates":
                self.accepted_updates,

            "rejected_updates":
                self.rejected_updates,

            "skipped_updates":
                self.skipped_updates,

            "last_adaptation_sample_count":
                self.last_adaptation_sample_count,
        }

    def load_state(
        self,
        state: dict,
    ) -> None:
        """
        Restore adaptation state from checkpoint.
        """

        if not state:
            return

        self.accepted_updates = (
            state.get(
                "accepted_updates",
                0,
            )
        )

        self.rejected_updates = (
            state.get(
                "rejected_updates",
                0,
            )
        )

        self.skipped_updates = (
            state.get(
                "skipped_updates",
                0,
            )
        )

        self.last_adaptation_sample_count = (
            state.get(
                "last_adaptation_sample_count",
                0,
            )
        )
    
    # ==================================================
    # STATUS
    # ==================================================

    def get_status(self) -> dict:

        return {
            "buffer_samples":
                len(self.replay_buffer),

            "accepted_updates":
                self.accepted_updates,

            "rejected_updates":
                self.rejected_updates,

            "skipped_updates":
                self.skipped_updates,

            "last_result":
                self.last_result,
        }