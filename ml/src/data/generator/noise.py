import numpy as np


def gaussian_noise(
    rng: np.random.Generator,
    scale: float,
    size: int,
) -> np.ndarray:
    """
    Generate independent Gaussian sensor noise.

    Parameters
    ----------
    rng:
        NumPy random number generator.
    scale:
        Standard deviation of the noise.
    size:
        Number of values to generate.

    Returns
    -------
    np.ndarray
        Generated noise values.
    """

    return rng.normal(
        loc=0.0,
        scale=scale,
        size=size,
    )


def random_walk(
    rng: np.random.Generator,
    length: int,
    scale: float = 0.01,
    initial: float = 0.0,
) -> np.ndarray:
    """
    Generate smooth random drift.

    Unlike independent noise, random-walk noise introduces
    temporal dependency between consecutive observations.
    """

    if length <= 0:
        return np.array([], dtype=float)

    steps = rng.normal(
        loc=0.0,
        scale=scale,
        size=length,
    )

    values = np.empty(length, dtype=float)
    values[0] = initial

    if length > 1:
        values[1:] = initial + np.cumsum(steps[1:])

    return values


def smooth_noise(
    rng: np.random.Generator,
    length: int,
    scale: float = 0.01,
    smoothing: int = 10,
) -> np.ndarray:
    """
    Generate temporally smooth noise.

    This approximates gradual environmental variation rather
    than completely independent sensor measurements.
    """

    if length <= 0:
        return np.array([], dtype=float)

    if smoothing <= 1:
        return gaussian_noise(rng, scale, length)

    raw = gaussian_noise(
        rng,
        scale,
        length,
    )

    kernel = np.ones(smoothing) / smoothing

    smoothed = np.convolve(
        raw,
        kernel,
        mode="same",
    )

    return smoothed


def event_curve(
    length: int,
    start: int,
    peak: int,
    end: int,
    magnitude: float,
) -> np.ndarray:
    """
    Generate a smooth disturbance event.

    The event:
        baseline → rise → peak → fall → baseline

    Parameters
    ----------
    length:
        Total number of observations.
    start:
        Event start index.
    peak:
        Index where the event reaches maximum magnitude.
    end:
        Event end index.
    magnitude:
        Maximum event magnitude.
    """

    curve = np.zeros(length, dtype=float)

    start = max(0, start)
    peak = max(start + 1, peak)
    end = min(length - 1, end)

    if start >= length or start >= end:
        return curve

    # Rising section
    rise_length = peak - start

    if rise_length > 0:
        curve[start:peak] = np.linspace(
            0.0,
            magnitude,
            rise_length,
            endpoint=False,
        )

    # Peak
    if peak < length:
        curve[peak] = magnitude

    # Falling section
    fall_length = end - peak

    if fall_length > 0:
        curve[peak + 1:end + 1] = np.linspace(
            magnitude,
            0.0,
            fall_length,
            endpoint=True,
        )

    return curve