from app.agent.water_agent import WaterQualityAgent


def test_process_observation_generates_dynamic_hardware_control():
    agent = WaterQualityAgent()

    result = agent.process_observation(
        ph=7.0,
        turbidity=10.0,
        temperature=25.0,
        dissolved_oxygen=2.0,
        tds=300.0,
    )

    assert result["success"] is True
    assert result["prediction_ready"] is False

    hardware = result["hardware_control"]

    assert set(hardware.keys()) == {"message", "time"}
    assert hardware["message"] == "Start Aerator"
    assert hardware["time"] == 0.1633


def test_process_observation_hardware_actions():
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
            "Start Cooling System",
        ),
        (
            {
                "ph": 7.0,
                "turbidity": 10.0,
                "temperature": 10.0,
                "dissolved_oxygen": 7.0,
                "tds": 300.0,
            },
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
            "Release Acid",
        ),
        (
            {
                "ph": 5.0,
                "turbidity": 10.0,
                "temperature": 25.0,
                "dissolved_oxygen": 7.0,
                "tds": 300.0,
            },
            "Release Base",
        ),
        (
            {
                "ph": 7.0,
                "turbidity": 100.0,
                "temperature": 25.0,
                "dissolved_oxygen": 7.0,
                "tds": 300.0,
            },
            "Start Water Pump",
        ),
    ]

    for values, expected_action in test_cases:
        result = agent.process_observation(
            **values
        )

        assert result["success"] is True

        hardware = result["hardware_control"]

        assert set(hardware.keys()) == {
            "message",
            "time",
        }

        assert hardware["message"] == expected_action
        assert 0 < hardware["time"] <= 0.25

def test_process_observation_no_action_for_normal_water():
    agent = WaterQualityAgent()

    result = agent.process_observation(
        ph=7.0,
        turbidity=10.0,
        temperature=25.0,
        dissolved_oxygen=7.0,
        tds=300.0,
    )

    assert result["success"] is True

    hardware = result["hardware_control"]

    assert hardware == {
        "message": "No Action",
        "time": 0,
    }

def test_process_observation_can_run_repeatedly():
    agent = WaterQualityAgent()

    observations = [
        {
            "ph": 7.0,
            "turbidity": 10.0,
            "temperature": 25.0,
            "dissolved_oxygen": 7.0,
            "tds": 300.0,
        },
        {
            "ph": 7.0,
            "turbidity": 10.0,
            "temperature": 25.0,
            "dissolved_oxygen": 2.0,
            "tds": 300.0,
        },
        {
            "ph": 7.0,
            "turbidity": 10.0,
            "temperature": 25.0,
            "dissolved_oxygen": 7.0,
            "tds": 300.0,
        },
    ]

    results = []

    for observation in observations:
        result = agent.process_observation(**observation)

        assert result["success"] is True
        results.append(result)

    assert len(results) == 3

    assert results[0]["hardware_control"]["message"] == "No Action"

    assert results[1]["hardware_control"]["message"] == "Start Aerator"
    assert results[1]["hardware_control"]["time"] == 0.1633

    assert results[2]["hardware_control"]["message"] == "No Action"