from app.agent.water_agent import (
    WaterQualityAgent,
)


class AgentService:

    def __init__(self):

        print()
        print(
            "Initializing Agent Service..."
        )

        self.agent = WaterQualityAgent()

        print(
            "Agent Service Ready"
        )

    def process_observation(
        self,
        ph: float,
        turbidity: float,
        temperature: float,
        dissolved_oxygen: float,
        tds: float,
    ) -> dict:

        return self.agent.process_observation(
            ph=ph,
            turbidity=turbidity,
            temperature=temperature,
            dissolved_oxygen=dissolved_oxygen,
            tds=tds,
        )

    def get_status(
        self,
    ) -> dict:

        return self.agent.get_status()