from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioConfig:
    """
    Configuration for a synthetic water-quality scenario.
    """

    name: str

    # Duration
    duration_seconds: int

    # Baseline water-quality values
    base_ph: float
    base_turbidity: float
    base_temperature: float
    base_do: float
    base_tds: float

    # Natural variation
    ph_noise: float = 0.01
    turbidity_noise: float = 0.5
    temperature_noise: float = 0.03
    do_noise: float = 0.03
    tds_noise: float = 1.0

    # Natural drift
    ph_drift: float = 0.0001
    turbidity_drift: float = 0.01
    temperature_drift: float = 0.001
    do_drift: float = 0.001
    tds_drift: float = 0.02


# ============================================================
# HEALTHY / STABLE WATER
# ============================================================

HEALTHY = ScenarioConfig(
    name="healthy",
    duration_seconds=24 * 60 * 60,

    base_ph=7.3,
    base_turbidity=15.0,
    base_temperature=27.0,
    base_do=6.5,
    base_tds=400.0,

    ph_noise=0.008,
    turbidity_noise=0.4,
    temperature_noise=0.025,
    do_noise=0.025,
    tds_noise=0.8,
)


# ============================================================
# TEMPERATURE INCREASE
# ============================================================

TEMPERATURE_INCREASE = ScenarioConfig(
    name="temperature_increase",
    duration_seconds=24 * 60 * 60,

    base_ph=7.3,
    base_turbidity=15.0,
    base_temperature=27.0,
    base_do=6.5,
    base_tds=400.0,

    ph_noise=0.01,
    turbidity_noise=0.5,
    temperature_noise=0.03,
    do_noise=0.03,
    tds_noise=1.0,
)


# ============================================================
# DISSOLVED OXYGEN DEPLETION
# ============================================================

DO_DEPLETION = ScenarioConfig(
    name="do_depletion",
    duration_seconds=24 * 60 * 60,

    base_ph=7.3,
    base_turbidity=15.0,
    base_temperature=27.0,
    base_do=6.5,
    base_tds=400.0,

    ph_noise=0.01,
    turbidity_noise=0.5,
    temperature_noise=0.03,
    do_noise=0.03,
    tds_noise=1.0,
)


# ============================================================
# TURBIDITY EVENT
# ============================================================

TURBIDITY_EVENT = ScenarioConfig(
    name="turbidity_event",
    duration_seconds=24 * 60 * 60,

    base_ph=7.3,
    base_turbidity=15.0,
    base_temperature=27.0,
    base_do=6.5,
    base_tds=400.0,

    ph_noise=0.01,
    turbidity_noise=0.6,
    temperature_noise=0.03,
    do_noise=0.03,
    tds_noise=1.0,
)


# ============================================================
# TDS INCREASE
# ============================================================

TDS_INCREASE = ScenarioConfig(
    name="tds_increase",
    duration_seconds=24 * 60 * 60,

    base_ph=7.3,
    base_turbidity=15.0,
    base_temperature=27.0,
    base_do=6.5,
    base_tds=400.0,

    ph_noise=0.01,
    turbidity_noise=0.5,
    temperature_noise=0.03,
    do_noise=0.03,
    tds_noise=1.2,
)


# ============================================================
# pH DRIFT
# ============================================================

PH_DRIFT = ScenarioConfig(
    name="ph_drift",
    duration_seconds=24 * 60 * 60,

    base_ph=7.3,
    base_turbidity=15.0,
    base_temperature=27.0,
    base_do=6.5,
    base_tds=400.0,

    ph_noise=0.01,
    turbidity_noise=0.5,
    temperature_noise=0.03,
    do_noise=0.03,
    tds_noise=1.0,
)


# ============================================================
# COMPOUND STRESS
# ============================================================

COMPOUND_STRESS = ScenarioConfig(
    name="compound_stress",
    duration_seconds=24 * 60 * 60,

    base_ph=7.3,
    base_turbidity=15.0,
    base_temperature=27.0,
    base_do=6.5,
    base_tds=400.0,

    ph_noise=0.012,
    turbidity_noise=0.7,
    temperature_noise=0.035,
    do_noise=0.04,
    tds_noise=1.5,
)


# ============================================================
# RECOVERY
# ============================================================

RECOVERY = ScenarioConfig(
    name="recovery",
    duration_seconds=24 * 60 * 60,

    base_ph=7.3,
    base_turbidity=15.0,
    base_temperature=27.0,
    base_do=6.5,
    base_tds=400.0,

    ph_noise=0.01,
    turbidity_noise=0.5,
    temperature_noise=0.03,
    do_noise=0.03,
    tds_noise=1.0,
)


# ============================================================
# ALL SCENARIOS
# ============================================================

SCENARIOS = {
    "healthy": HEALTHY,
    "temperature_increase": TEMPERATURE_INCREASE,
    "do_depletion": DO_DEPLETION,
    "turbidity_event": TURBIDITY_EVENT,
    "tds_increase": TDS_INCREASE,
    "ph_drift": PH_DRIFT,
    "compound_stress": COMPOUND_STRESS,
    "recovery": RECOVERY,
}