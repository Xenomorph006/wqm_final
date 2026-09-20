from app.agent.water_agent import WaterQualityAgent


def test_control_time_never_exceeds_15_seconds():
    agent = WaterQualityAgent()

    test_cases = [
        ("dissolved_oxygen", 0.0),
        ("dissolved_oxygen", 2.0),
        ("dissolved_oxygen", 4.9),
        ("temperature_high", 60.0),
        ("temperature_low", -10.0),
        ("pH_high", 14.0),
        ("pH_low", 0.0),
        ("turbidity", 500.0),
        ("tds", 5000.0),
    ]

    for parameter, value in test_cases:
        hardware_time = agent.calculate_control_time(
            parameter,
            value
        )

        assert hardware_time <= 0.25
        assert hardware_time > 0


def test_severe_problem_gets_longer_action():
    agent = WaterQualityAgent()

    mild = agent.calculate_control_time(
        "dissolved_oxygen",
        4.8
    )

    severe = agent.calculate_control_time(
        "dissolved_oxygen",
        1.0
    )

    assert severe > mild


def test_extreme_problem_is_limited_to_15_seconds():
    agent = WaterQualityAgent()

    result = agent.calculate_control_time(
        "dissolved_oxygen",
        0.0
    )

    assert result == 0.25