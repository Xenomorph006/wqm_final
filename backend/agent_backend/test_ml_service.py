from app.services.ml_service import (
    MLService,
)


def main():

    print()

    print("=" * 60)

    print(
        "TESTING AGENT ML INTEGRATION"
    )

    print("=" * 60)

    print()


    # ==========================================
    # INITIALIZE ML SERVICE
    # ==========================================

    ml_service = MLService()


    # ==========================================
    # ML STATUS
    # ==========================================

    print()

    print(
        "ML STATUS"
    )

    print(
        ml_service.get_status()
    )


    # ==========================================
    # TEST OBSERVATION
    # ==========================================

    print()

    print(
        "SENDING TEST OBSERVATION"
    )


    result = (
        ml_service.process_observation(

            ph=7.29,

            turbidity=15.3,

            temperature=26.9,

            dissolved_oxygen=6.56,

            tds=399.5,

        )
    )


    # ==========================================
    # RESULT
    # ==========================================

    print()

    print(
        "RESULT"
    )

    print(
        result
    )


if __name__ == "__main__":

    main()