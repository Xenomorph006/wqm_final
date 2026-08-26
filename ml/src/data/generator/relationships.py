import numpy as np


def temperature_do_effect(
    temperature: np.ndarray,
    reference_temperature: float = 27.0,
    sensitivity: float = 0.08,
) -> np.ndarray:
    """
    Approximate the effect of temperature on dissolved oxygen.

    As temperature rises above the reference temperature,
    the resulting DO adjustment becomes negative.

    This is a simplified simulation relationship, not a
    physical dissolved-oxygen solubility equation.
    """

    return -sensitivity * (
        temperature - reference_temperature
    )


def turbidity_do_effect(
    turbidity: np.ndarray,
    reference_turbidity: float = 15.0,
    sensitivity: float = 0.002,
) -> np.ndarray:
    """
    Approximate the effect of elevated turbidity on DO.

    Higher turbidity produces a small downward DO adjustment.
    """

    excess_turbidity = np.maximum(
        turbidity - reference_turbidity,
        0.0,
    )

    return -sensitivity * excess_turbidity


def tds_ph_effect(
    tds: np.ndarray,
    reference_tds: float = 400.0,
    sensitivity: float = 0.00005,
) -> np.ndarray:
    """
    Approximate a weak relationship between elevated TDS
    and pH.

    This is intentionally kept small because the relationship
    is highly environment-dependent.
    """

    excess_tds = tds - reference_tds

    return sensitivity * excess_tds


def apply_temperature_do_relationship(
    temperature: np.ndarray,
    do: np.ndarray,
) -> np.ndarray:
    """
    Apply temperature → DO relationship.
    """

    adjustment = temperature_do_effect(
        temperature
    )

    return do + adjustment


def apply_turbidity_do_relationship(
    turbidity: np.ndarray,
    do: np.ndarray,
) -> np.ndarray:
    """
    Apply turbidity → DO relationship.
    """

    adjustment = turbidity_do_effect(
        turbidity
    )

    return do + adjustment


def apply_tds_ph_relationship(
    tds: np.ndarray,
    ph: np.ndarray,
) -> np.ndarray:
    """
    Apply TDS → pH relationship.
    """

    adjustment = tds_ph_effect(
        tds
    )

    return ph + adjustment


def apply_all_relationships(
    ph: np.ndarray,
    turbidity: np.ndarray,
    temperature: np.ndarray,
    do: np.ndarray,
    tds: np.ndarray,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    """
    Apply all currently implemented cross-parameter
    relationships.

    Returns
    -------
    tuple
        Updated:
        pH, turbidity, temperature, DO, TDS
    """

    updated_do = apply_temperature_do_relationship(
        temperature,
        do,
    )

    updated_do = apply_turbidity_do_relationship(
        turbidity,
        updated_do,
    )

    updated_ph = apply_tds_ph_relationship(
        tds,
        ph,
    )

    return (
        updated_ph,
        turbidity,
        temperature,
        updated_do,
        tds,
    )