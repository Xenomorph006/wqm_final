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

        result = self.agent.process_observation(
            ph=ph,
            turbidity=turbidity,
            temperature=temperature,
            dissolved_oxygen=dissolved_oxygen,
            tds=tds,
        )

        fish_recommendation = (
            self.fish_recommender.recommend(
                ph=ph,
                turbidity=turbidity,
                temperature=temperature,
                dissolved_oxygen=dissolved_oxygen,
                tds=tds,
                prediction=result.get(
                    "prediction"
                ),
            )
        )

        result["fish_recommendation"] = (
            fish_recommendation
        )

        return result

    def get_status(
        self,
    ) -> dict:

        return self.agent.get_status()