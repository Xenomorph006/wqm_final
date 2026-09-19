import numpy as np

from app.agent.water_agent import (
    WaterQualityAgent,
)


def main():

    print()

    print("=" * 60)
    print("TESTING AGENT SENSOR STREAM")
    print("=" * 60)

    agent = WaterQualityAgent()

    # Healthy baseline values
    base = np.array(
        [
            7.29,
            15.3,
            26.9,
            6.56,
            399.5,
        ]
    )

    # Send enough observations
    # to fill the 60-step window
    for index in range(65):

        # Small realistic variation
        variation = np.random.normal(
            0,
            [
                0.01,
                0.2,
                0.05,
                0.05,
                0.5,
            ],
        )

        observation = (
            base + variation
        )

        result = agent.process_observation(

            ph=observation[0],

            turbidity=observation[1],

            temperature=observation[2],

            dissolved_oxygen=observation[3],

            tds=observation[4],

        )

        print()

        print(
            f"Observation {index + 1}"
        )

        if result.get("prediction_ready"):

            print(
                "PREDICTION READY!"
            )

            print()

            print("=" * 60)
            print("FULL AGENT RESPONSE")
            print("=" * 60)

            print()

            print(
                result
            )

            break


if __name__ == "__main__":

    main()