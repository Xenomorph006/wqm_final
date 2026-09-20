import time

from app.agent.water_agent import WaterQualityAgent


class RealtimeService:
    def __init__(self, interval_seconds: float = 5.0):
        self.agent = WaterQualityAgent()
        self.interval_seconds = interval_seconds
        self.running = False

    def process_observation(self, observation: dict) -> dict:
        return self.agent.process_observation(
            ph=observation["ph"],
            turbidity=observation["turbidity"],
            temperature=observation["temperature"],
            dissolved_oxygen=observation["dissolved_oxygen"],
            tds=observation["tds"],
        )

    def run(self, observation_source):
        self.running = True

        try:
            while self.running:

                observation = observation_source()

                if observation is None:
                    break

                result = self.process_observation(
                    observation
                )

                yield result

                time.sleep(
                    self.interval_seconds
                )

        finally:
            self.running = False

    def stop(self):
        self.running = False