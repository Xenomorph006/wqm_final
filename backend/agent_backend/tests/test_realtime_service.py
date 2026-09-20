from app.services.realtime_service import RealtimeService


def test_realtime_service_processes_multiple_observations():
    service = RealtimeService(
        interval_seconds=0
    )

    observations = iter([
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
    ])

    def observation_source():
        try:
            return next(observations)
        except StopIteration:
            return None

    results = list(
        service.run(observation_source)
    )

    assert len(results) == 2

    assert (
        results[0]["hardware_control"]["message"]
        == "No Action"
    )

    assert (
        results[1]["hardware_control"]["message"]
        == "Start Aerator"
    )


def test_realtime_service_can_stop():
    service = RealtimeService(
        interval_seconds=0
    )

    service.running = True

    service.stop()

    assert service.running is False


def test_realtime_service_uses_continuous_observation_source():
    service = RealtimeService(
        interval_seconds=0
    )

    observations = iter([
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
    ])

    def observation_source():
        try:
            return next(observations)
        except StopIteration:
            return None

    results = list(
        service.run(observation_source)
    )

    assert len(results) == 2

    assert (
        results[0]["hardware_control"]["message"]
        == "No Action"
    )

    assert (
        results[1]["hardware_control"]["message"]
        == "Start Aerator"
    )