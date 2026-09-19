from app.agent.water_agent import (
    WaterQualityAgent,
)


def main():

    print()

    print("=" * 60)
    print("TESTING WATER QUALITY AGENT")
    print("=" * 60)

    # ==========================================
    # INITIALIZE AGENT
    # ==========================================

    agent = WaterQualityAgent()

    # ==========================================
    # AGENT STATUS
    # ==========================================

    print()

    print("AGENT STATUS")

    print(
        agent.get_status()
    )

    # ==========================================
    # TEST SENSOR DATA
    # ==========================================

    print()

    print("SENDING WATER OBSERVATION")

    result = agent.evaluate(

        ph=7.29,

        turbidity=15.3,

        temperature=26.9,

        dissolved_oxygen=6.56,

        tds=399.5,

    )

    # ==========================================
    # RESULT
    # ==========================================

    print()

    print("=" * 60)
    print("AGENT RESULT")
    print("=" * 60)

    print()

    print(result)


if __name__ == "__main__":

    main()