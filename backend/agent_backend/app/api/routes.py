from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.water import (
    WaterObservation,
    WaterObservationBatch,
)

from app.services.agent_service import (
    AgentService,
)


router = APIRouter()


agent_service = None


def get_agent_service():

    global agent_service

    if agent_service is None:

        agent_service = AgentService()

    return agent_service


@router.get(
    "/health"
)
def health():

    try:

        service = (
            get_agent_service()
        )

        return {

            "status": "healthy",

            "agent_ready": True,

            "agent_status":
                service.get_status(),
        }

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error),

        )


@router.post(
    "/process"
)
def process_water_observation(
    observation: WaterObservation,
):

    try:

        service = (
            get_agent_service()
        )

        result = (
            service.process_observation(

                ph=observation.ph,

                turbidity=(
                    observation.turbidity
                ),

                temperature=(
                    observation.temperature
                ),

                dissolved_oxygen=(
                    observation.dissolved_oxygen
                ),

                tds=observation.tds,

            )
        )

        return result

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error),

        )


@router.post(
    "/process-batch"
)
def process_water_batch(
    batch: WaterObservationBatch,
):

    try:

        service = (
            get_agent_service()
        )

        results = []

        ml_updates = []

        # ==============================================
        # PROCESS OBSERVATIONS
        # ==============================================

        for index, observation in enumerate(
            batch.observations
        ):

            result = (
                service.process_observation(

                    ph=observation.ph,

                    turbidity=(
                        observation.turbidity
                    ),

                    temperature=(
                        observation.temperature
                    ),

                    dissolved_oxygen=(
                        observation.dissolved_oxygen
                    ),

                    tds=observation.tds,

                )
            )

            results.append(
                result
            )

            # ==========================================
            # EXTRACT ML INFORMATION
            # ==========================================

            ml_data = result.get(
                "ml",
                {}
            )

            buffer_data = ml_data.get(
                "buffer",
                {}
            )

            adaptation = buffer_data.get(
                "adaptation"
            )

            saved_model_path = buffer_data.get(
                "saved_model_path"
            )

            # ==========================================
            # STORE IMPORTANT LEARNING EVENTS
            # ==========================================

            if adaptation is not None:

                ml_updates.append(
                    {
                        "observation_index":
                            index + 1,

                        "adaptation":
                            adaptation,

                        "saved_model_path":
                            saved_model_path,
                    }
                )

        # ==============================================
        # GET FINAL ML STATUS
        # ==============================================

        ml_status = (
            service.get_status()
        )

        # ==============================================
        # RESPONSE
        # ==============================================

        return {

            "success": True,

            # ------------------------------------------
            # BATCH INFORMATION
            # ------------------------------------------

            "observations_processed":
                len(batch.observations),

            # ------------------------------------------
            # FINAL SYSTEM RESULT
            # ------------------------------------------

            "final_result":
                results[-1]
                if results
                else None,

            # ------------------------------------------
            # SELF LEARNING EVENTS
            # ------------------------------------------

            "ml_updates":
                ml_updates,

            # ------------------------------------------
            # FINAL ML STATUS
            # ------------------------------------------

            "ml_status":
                ml_status,

            # ------------------------------------------
            # SUMMARY
            # ------------------------------------------

            "learning_summary": {

                "total_ml_events":
                    len(ml_updates),

                "accepted_updates":
                    ml_status
                    .get(
                        "ml",
                        {}
                    )
                    .get(
                        "manager",
                        {}
                    )
                    .get(
                        "adaptation",
                        {}
                    )
                    .get(
                        "accepted_updates",
                        0
                    ),

                "rejected_updates":
                    ml_status
                    .get(
                        "ml",
                        {}
                    )
                    .get(
                        "manager",
                        {}
                    )
                    .get(
                        "adaptation",
                        {}
                    )
                    .get(
                        "rejected_updates",
                        0
                    ),

                "skipped_updates":
                    ml_status
                    .get(
                        "ml",
                        {}
                    )
                    .get(
                        "manager",
                        {}
                    )
                    .get(
                        "adaptation",
                        {}
                    )
                    .get(
                        "skipped_updates",
                        0
                    ),

                "total_learning_updates":
                    ml_status
                    .get(
                        "ml",
                        {}
                    )
                    .get(
                        "manager",
                        {}
                    )
                    .get(
                        "learner",
                        {}
                    )
                    .get(
                        "total_updates",
                        0
                    ),

                "last_loss":
                    ml_status
                    .get(
                        "ml",
                        {}
                    )
                    .get(
                        "manager",
                        {}
                    )
                    .get(
                        "learner",
                        {}
                    )
                    .get(
                        "last_loss"
                    ),
            },
        }

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error),

        )

@router.get(
    "/ml/status"
)
def get_ml_status():

    try:

        service = (
            get_agent_service()
        )

        return service.get_status()

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error),

        )