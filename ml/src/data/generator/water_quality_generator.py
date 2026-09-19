from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .noise import event_curve, gaussian_noise, random_walk, smooth_noise
from .relationships import apply_all_relationships
from .scenarios import SCENARIOS, ScenarioConfig


# ============================================================
# CONSTANTS
# ============================================================

SAMPLING_INTERVAL_SECONDS = 5

PARAMETER_COLUMNS = [
    "pH",
    "turbidity",
    "temperature",
    "DO",
    "TDS",
]


# ============================================================
# GENERATOR
# ============================================================

class WaterQualityGenerator:
    """
    Synthetic water-quality time-series generator.

    Generates:
        pH
        turbidity
        temperature
        dissolved oxygen (DO)
        total dissolved solids (TDS)

    at a fixed 5-second sampling interval.
    """

    def __init__(
        self,
        seed: int = 42,
        sampling_interval_seconds: int = SAMPLING_INTERVAL_SECONDS,
    ) -> None:

        if sampling_interval_seconds <= 0:
            raise ValueError(
                "sampling_interval_seconds must be greater than zero."
            )

        self.seed = seed
        self.sampling_interval_seconds = sampling_interval_seconds

        self.rng = np.random.default_rng(seed)

    # ========================================================
    # PUBLIC API
    # ========================================================

    def generate(
        self,
        scenario: str | ScenarioConfig,
        start_time: str = "2026-01-01 00:00:00",
        duration_seconds: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Generate a synthetic water-quality dataset.

        Parameters
        ----------
        scenario:
            Scenario name or ScenarioConfig.

        start_time:
            Timestamp for the first observation.

        duration_seconds:
            Optional custom duration. If omitted, the duration
            from the scenario configuration is used.

        Returns
        -------
        pd.DataFrame
            Generated water-quality time series.
        """

        config = self._resolve_scenario(scenario)

        if duration_seconds is None:
            duration_seconds = config.duration_seconds

        if duration_seconds <= 0:
            raise ValueError(
                "duration_seconds must be greater than zero."
            )

        num_samples = (
            duration_seconds // self.sampling_interval_seconds
        ) + 1

        timestamps = pd.date_range(
            start=start_time,
            periods=num_samples,
            freq=f"{self.sampling_interval_seconds}s",
        )

        # ----------------------------------------------------
        # Base environmental signals
        # ----------------------------------------------------

        temperature = self._generate_temperature(
            config,
            num_samples,
        )

        ph = self._generate_ph(
            config,
            num_samples,
        )

        turbidity = self._generate_turbidity(
            config,
            num_samples,
        )

        dissolved_oxygen = self._generate_do(
            config,
            num_samples,
        )

        tds = self._generate_tds(
            config,
            num_samples,
        )

        # ----------------------------------------------------
        # Scenario-specific disturbances
        # ----------------------------------------------------

        ph, turbidity, temperature, dissolved_oxygen, tds = (
            self._apply_scenario_events(
                config=config,
                ph=ph,
                turbidity=turbidity,
                temperature=temperature,
                dissolved_oxygen=dissolved_oxygen,
                tds=tds,
            )
        )

        # ----------------------------------------------------
        # Cross-parameter relationships
        # ----------------------------------------------------

        (
            ph,
            turbidity,
            temperature,
            dissolved_oxygen,
            tds,
        ) = apply_all_relationships(
            ph=ph,
            turbidity=turbidity,
            temperature=temperature,
            do=dissolved_oxygen,
            tds=tds,
        )

        # ----------------------------------------------------
        # Physical bounds
        # ----------------------------------------------------

        ph = np.clip(ph, 4.0, 10.0)

        turbidity = np.clip(
            turbidity,
            0.0,
            None,
        )

        temperature = np.clip(
            temperature,
            10.0,
            40.0,
        )

        dissolved_oxygen = np.clip(
            dissolved_oxygen,
            0.0,
            15.0,
        )

        tds = np.clip(
            tds,
            0.0,
            None,
        )

        # ----------------------------------------------------
        # Build dataframe
        # ----------------------------------------------------

        dataframe = pd.DataFrame(
            {
                "timestamp": timestamps,
                "pH": ph,
                "turbidity": turbidity,
                "temperature": temperature,
                "DO": dissolved_oxygen,
                "TDS": tds,
            }
        )

        dataframe["scenario"] = config.name

        return dataframe

    # ========================================================
    # SCENARIO RESOLUTION
    # ========================================================

    @staticmethod
    def _resolve_scenario(
        scenario: str | ScenarioConfig,
    ) -> ScenarioConfig:

        if isinstance(scenario, ScenarioConfig):
            return scenario

        if scenario not in SCENARIOS:
            available = ", ".join(SCENARIOS.keys())

            raise ValueError(
                f"Unknown scenario '{scenario}'. "
                f"Available scenarios: {available}"
            )

        return SCENARIOS[scenario]

    # ========================================================
    # PARAMETER GENERATORS
    # ========================================================

    def _generate_temperature(
        self,
        config: ScenarioConfig,
        length: int,
    ) -> np.ndarray:

        drift = random_walk(
            rng=self.rng,
            length=length,
            scale=config.temperature_drift,
            initial=0.0,
        )

        smooth_variation = smooth_noise(
            rng=self.rng,
            length=length,
            scale=config.temperature_noise,
            smoothing=24,
        )

        sensor_noise = gaussian_noise(
            rng=self.rng,
            scale=config.temperature_noise * 0.25,
            size=length,
        )

        return (
            config.base_temperature
            + drift
            + smooth_variation
            + sensor_noise
        )

    def _generate_ph(
        self,
        config: ScenarioConfig,
        length: int,
    ) -> np.ndarray:

        drift = random_walk(
            rng=self.rng,
            length=length,
            scale=config.ph_drift,
            initial=0.0,
        )

        smooth_variation = smooth_noise(
            rng=self.rng,
            length=length,
            scale=config.ph_noise,
            smoothing=30,
        )

        sensor_noise = gaussian_noise(
            rng=self.rng,
            scale=config.ph_noise * 0.25,
            size=length,
        )

        return (
            config.base_ph
            + drift
            + smooth_variation
            + sensor_noise
        )

    def _generate_turbidity(
        self,
        config: ScenarioConfig,
        length: int,
    ) -> np.ndarray:

        drift = random_walk(
            rng=self.rng,
            length=length,
            scale=config.turbidity_drift,
            initial=0.0,
        )

        smooth_variation = smooth_noise(
            rng=self.rng,
            length=length,
            scale=config.turbidity_noise,
            smoothing=18,
        )

        sensor_noise = gaussian_noise(
            rng=self.rng,
            scale=config.turbidity_noise * 0.25,
            size=length,
        )

        return (
            config.base_turbidity
            + drift
            + smooth_variation
            + sensor_noise
        )

    def _generate_do(
        self,
        config: ScenarioConfig,
        length: int,
    ) -> np.ndarray:

        drift = random_walk(
            rng=self.rng,
            length=length,
            scale=config.do_drift,
            initial=0.0,
        )

        smooth_variation = smooth_noise(
            rng=self.rng,
            length=length,
            scale=config.do_noise,
            smoothing=24,
        )

        sensor_noise = gaussian_noise(
            rng=self.rng,
            scale=config.do_noise * 0.25,
            size=length,
        )

        return (
            config.base_do
            + drift
            + smooth_variation
            + sensor_noise
        )

    def _generate_tds(
        self,
        config: ScenarioConfig,
        length: int,
    ) -> np.ndarray:

        drift = random_walk(
            rng=self.rng,
            length=length,
            scale=config.tds_drift,
            initial=0.0,
        )

        smooth_variation = smooth_noise(
            rng=self.rng,
            length=length,
            scale=config.tds_noise,
            smoothing=20,
        )

        sensor_noise = gaussian_noise(
            rng=self.rng,
            scale=config.tds_noise * 0.25,
            size=length,
        )

        return (
            config.base_tds
            + drift
            + smooth_variation
            + sensor_noise
        )

    # ========================================================
    # SCENARIO EVENTS
    # ========================================================

    def _apply_scenario_events(
        self,
        config: ScenarioConfig,
        ph: np.ndarray,
        turbidity: np.ndarray,
        temperature: np.ndarray,
        dissolved_oxygen: np.ndarray,
        tds: np.ndarray,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:

        length = len(ph)

        if config.name == "temperature_increase":

            event = self._create_event(
                length=length,
                magnitude=4.0,
            )

            temperature = temperature + event

        elif config.name == "do_depletion":

            event = self._create_event(
                length=length,
                magnitude=-3.0,
            )

            dissolved_oxygen = dissolved_oxygen + event

        elif config.name == "turbidity_event":

            event = self._create_event(
                length=length,
                magnitude=100.0,
            )

            turbidity = turbidity + event

        elif config.name == "tds_increase":

            event = self._create_event(
                length=length,
                magnitude=250.0,
            )

            tds = tds + event

        elif config.name == "ph_drift":

            event = self._create_event(
                length=length,
                magnitude=-0.8,
            )

            ph = ph + event

        elif config.name == "compound_stress":

            temperature_event = self._create_event(
                length=length,
                magnitude=3.5,
            )

            do_event = self._create_event(
                length=length,
                magnitude=-2.5,
            )

            turbidity_event_signal = self._create_event(
                length=length,
                magnitude=80.0,
            )

            tds_event = self._create_event(
                length=length,
                magnitude=150.0,
            )

            ph_event = self._create_event(
                length=length,
                magnitude=-0.5,
            )

            temperature = (
                temperature
                + temperature_event
            )

            dissolved_oxygen = (
                dissolved_oxygen
                + do_event
            )

            turbidity = (
                turbidity
                + turbidity_event_signal
            )

            tds = (
                tds
                + tds_event
            )

            ph = ph + ph_event

        elif config.name == "recovery":

            recovery_curve = self._create_recovery_curve(
                length=length
            )

            temperature = (
                temperature
                + 3.0 * recovery_curve
            )

            dissolved_oxygen = (
                dissolved_oxygen
                - 2.5 * recovery_curve
            )

            turbidity = (
                turbidity
                + 70.0 * recovery_curve
            )

            tds = (
                tds
                + 120.0 * recovery_curve
            )

            ph = (
                ph
                - 0.5 * recovery_curve
            )

        return (
            ph,
            turbidity,
            temperature,
            dissolved_oxygen,
            tds,
        )

    # ========================================================
    # EVENT HELPERS
    # ========================================================

    def _create_event(
        self,
        length: int,
        magnitude: float,
    ) -> np.ndarray:

        if length < 20:
            return np.zeros(length)

        start = int(length * 0.35)
        peak = int(length * 0.50)
        end = int(length * 0.70)

        return event_curve(
            length=length,
            start=start,
            peak=peak,
            end=end,
            magnitude=magnitude,
        )

    @staticmethod
    def _create_recovery_curve(
        length: int,
    ) -> np.ndarray:

        if length <= 1:
            return np.zeros(length)

        curve = np.zeros(length)

        disturbance_end = int(length * 0.45)

        recovery_start = disturbance_end
        recovery_end = int(length * 0.90)

        if recovery_end <= recovery_start:
            return curve

        recovery = np.linspace(
            1.0,
            0.0,
            recovery_end - recovery_start,
        )

        curve[
            recovery_start:recovery_end
        ] = recovery

        curve[:recovery_start] = 1.0

        return curve


# ============================================================
# DATASET EXPORT
# ============================================================

def save_dataset(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Save generated dataset as CSV.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )


def save_metadata(
    dataframe: pd.DataFrame,
    output_path: str | Path,
    seed: int,
    sampling_interval_seconds: int,
) -> None:
    """
    Save metadata describing a generated dataset.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "seed": seed,
        "sampling_interval_seconds": (
            sampling_interval_seconds
        ),
        "num_samples": len(dataframe),
        "parameters": PARAMETER_COLUMNS,
        "start_time": str(
            dataframe["timestamp"].iloc[0]
        ),
        "end_time": str(
            dataframe["timestamp"].iloc[-1]
        ),
        "scenario": (
            str(dataframe["scenario"].iloc[0])
            if "scenario" in dataframe.columns
            else None
        ),
    }

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )


# ============================================================
# SIMPLE COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    generator = WaterQualityGenerator(
        seed=42,
        sampling_interval_seconds=5,
    )

    dataset = generator.generate(
        scenario="healthy",
        duration_seconds=3600,
    )

    print(dataset.head())
    print()
    print(dataset.tail())
    print()
    print(f"Samples: {len(dataset)}")