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

def test_hardware_actions_match_water_quality_issue():
    agent = WaterQualityAgent()

    test_cases = [
        (
            {
                "ph": 7.0,
                "turbidity": 10.0,
                "temperature": 40.0,
                "dissolved_oxygen": 7.0,
                "tds": 300.0,
            },
            ["High Temperature"],
            "Start Cooling System",
        ),
        (
            {
                "ph": 5.0,
                "turbidity": 10.0,
                "temperature": 25.0,
                "dissolved_oxygen": 7.0,
                "tds": 300.0,
            },
            ["Low pH"],
            "Release Base",
        ),
        (
            {
                "ph": 7.0,
                "turbidity": 10.0,
                "temperature": 10.0,
                "dissolved_oxygen": 7.0,
                "tds": 300.0,
            },
            ["Low Temperature"],
            "Start Heater",
        ),
        (
            {
                "ph": 12.0,
                "turbidity": 10.0,
                "temperature": 25.0,
                "dissolved_oxygen": 7.0,
                "tds": 300.0,
            },
            ["High pH"],
            "Release Acid",
        ),
        (
            {
                "ph": 7.0,
                "turbidity": 100.0,
                "temperature": 25.0,
                "dissolved_oxygen": 7.0,
                "tds": 300.0,
            },
            ["High Turbidity"],
            "Start Water Pump",
        ),
    ]

    for current_values, issues, expected_action in test_cases:
        result = agent.generate_hardware_control(
            current_values,
            {"issues": issues},
            {"issues": []},
        )

        assert result["message"] == expected_action
        assert 0 < result["time"] <= 0.25

def test_hardware_control_response_structure():
    agent = WaterQualityAgent()

    current_values = {
        "ph": 7.0,
        "turbidity": 10.0,
        "temperature": 25.0,
        "dissolved_oxygen": 2.0,
        "tds": 300.0,
    }

    result = agent.generate_hardware_control(
        current_values,
        {"issues": ["Low Dissolved Oxygen"]},
        {"issues": []},
    )

    assert result["message"] == "Start Aerator"
    assert set(result.keys()) == {"message", "time"}
    assert result["time"] == 0.1633

def test_no_action_when_water_quality_is_normal():
    agent = WaterQualityAgent()

    current_values = {
        "ph": 7.0,
        "turbidity": 10.0,
        "temperature": 25.0,
        "dissolved_oxygen": 7.0,
        "tds": 300.0,
    }

    result = agent.generate_hardware_control(
        current_values,
        {"issues": []},
        {"issues": []},
    )

    assert result == {
        "message": "No Action",
        "time": 0,
    }