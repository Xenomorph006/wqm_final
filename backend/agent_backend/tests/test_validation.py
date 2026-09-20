from app.agent.water_agent import WaterQualityAgent


def test_valid_observation():
    agent = WaterQualityAgent()

    valid, errors = agent.validate_observation(
        7.2,
        15.0,
        27.0,
        6.5,
        350.0
    )

    assert valid is True
    assert errors == []


def test_invalid_ph():
    agent = WaterQualityAgent()

    valid, errors = agent.validate_observation(
        20.0,
        15.0,
        27.0,
        6.5,
        350.0
    )

    assert valid is False
    assert "pH is outside valid range" in errors


def test_negative_turbidity():
    agent = WaterQualityAgent()

    valid, errors = agent.validate_observation(
        7.2,
        -5.0,
        27.0,
        6.5,
        350.0
    )

    assert valid is False


def test_invalid_dissolved_oxygen():
    agent = WaterQualityAgent()

    valid, errors = agent.validate_observation(
        7.2,
        15.0,
        27.0,
        50.0,
        350.0
    )

    assert valid is False