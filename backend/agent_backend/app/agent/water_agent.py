import numpy as np

from app.services.ml_service import (
    MLService,
)


class WaterQualityAgent:
    """
    Main Water Quality Agent.

    Responsibilities:

    1. Receive live sensor observations
    2. Evaluate current water quality
    3. Send observations to ML system
    4. Analyze future predictions
    5. Generate recommendations
    6. Generate direct hardware control commands
    """

    # ==================================================
    # HARDWARE CONTROL TIME
    # ==================================================

    # Hardware calculates:
    #
    # time * 60000
    #
    # Therefore:
    #
    # 0.0833 minutes ≈ 5 seconds

    CONTROL_TIME = 0.0833

    # ==================================================
    # INITIALIZATION
    # ==================================================

    def __init__(
        self,
    ) -> None:

        print()

        print(
            "Initializing Water Quality Agent..."
        )

        self.ml_service = MLService()

        print(
            "Water Quality Agent ready"
        )

    # ==================================================
    # STATUS
    # ==================================================

    def get_status(
        self,
    ) -> dict:

        return {

            "agent_ready":
                True,

            "ml":
                self.ml_service.get_status(),

        }

    # ==================================================
    # CURRENT WATER QUALITY
    # ==================================================

    def evaluate_current_water_quality(
        self,
        observation,
    ) -> dict:
        """
        Evaluate the current sensor values.

        Expected order:

        [
            pH,
            turbidity,
            temperature,
            dissolved_oxygen,
            TDS
        ]
        """

        values = np.asarray(
            observation,
            dtype=float,
        )

        ph = float(
            values[0]
        )

        turbidity = float(
            values[1]
        )

        temperature = float(
            values[2]
        )

        dissolved_oxygen = float(
            values[3]
        )

        tds = float(
            values[4]
        )

        issues = []

        # ==============================================
        # pH
        # ==============================================

        if ph < 6.5:

            issues.append(
                "Low pH"
            )

        elif ph > 8.5:

            issues.append(
                "High pH"
            )

        # ==============================================
        # TURBIDITY
        # ==============================================

        if turbidity > 25:

            issues.append(
                "High Turbidity"
            )

        # ==============================================
        # TEMPERATURE
        # ==============================================

        if temperature < 20:

            issues.append(
                "Low Temperature"
            )

        elif temperature > 32:

            issues.append(
                "High Temperature"
            )

        # ==============================================
        # DISSOLVED OXYGEN
        # ==============================================

        if dissolved_oxygen < 5:

            issues.append(
                "Low Dissolved Oxygen"
            )

        # ==============================================
        # TDS
        # ==============================================

        if tds > 500:

            issues.append(
                "High TDS"
            )

        # ==============================================
        # RISK LEVEL
        # ==============================================

        if len(
            issues
        ) == 0:

            status = "healthy"

            risk_level = "LOW"

        elif len(
            issues
        ) == 1:

            status = "warning"

            risk_level = "MEDIUM"

        else:

            status = "critical"

            risk_level = "HIGH"

        return {

            "status":
                status,

            "risk_level":
                risk_level,

            "issues":
                issues,

        }

    # ==================================================
    # FUTURE WATER QUALITY
    # ==================================================

    def evaluate_future_water_quality(
        self,
        prediction_result: dict,
    ) -> dict:
        """
        Evaluate predicted future water quality.

        Uses the average predicted value
        across the prediction horizon.
        """

        prediction = np.asarray(
            prediction_result[
                "prediction"
            ],
            dtype=float,
        )

        confidence = np.asarray(
            prediction_result[
                "confidence"
            ],
            dtype=float,
        )

        # ==============================================
        # MEAN FUTURE VALUES
        # ==============================================

        mean_prediction = np.mean(
            prediction,
            axis=0,
        )

        mean_confidence = np.mean(
            confidence,
            axis=0,
        )

        # ==============================================
        # VALUES
        # ==============================================

        ph = float(
            mean_prediction[0]
        )

        turbidity = float(
            mean_prediction[1]
        )

        temperature = float(
            mean_prediction[2]
        )

        dissolved_oxygen = float(
            mean_prediction[3]
        )

        tds = float(
            mean_prediction[4]
        )

        # ==============================================
        # CONFIDENCE
        # ==============================================

        ph_confidence = float(
            mean_confidence[0]
        )

        turbidity_confidence = float(
            mean_confidence[1]
        )

        temperature_confidence = float(
            mean_confidence[2]
        )

        dissolved_oxygen_confidence = float(
            mean_confidence[3]
        )

        tds_confidence = float(
            mean_confidence[4]
        )

        overall_confidence = float(
            np.mean(
                mean_confidence
            )
        )

        issues = []

        # ==============================================
        # FUTURE pH
        # ==============================================

        if ph < 6.5:

            issues.append(
                "Predicted Low pH"
            )

        elif ph > 8.5:

            issues.append(
                "Predicted High pH"
            )

        # ==============================================
        # FUTURE TURBIDITY
        # ==============================================

        if turbidity > 25:

            issues.append(
                "Predicted High Turbidity"
            )

        # ==============================================
        # FUTURE TEMPERATURE
        # ==============================================

        if temperature < 20:

            issues.append(
                "Predicted Low Temperature"
            )

        elif temperature > 32:

            issues.append(
                "Predicted High Temperature"
            )

        # ==============================================
        # FUTURE DO
        # ==============================================

        if dissolved_oxygen < 5:

            issues.append(
                "Predicted Low Dissolved Oxygen"
            )

        # ==============================================
        # FUTURE TDS
        # ==============================================

        if tds > 500:

            issues.append(
                "Predicted High TDS"
            )

        # ==============================================
        # FUTURE RISK
        # ==============================================

        if len(
            issues
        ) == 0:

            risk_level = "LOW"

        elif len(
            issues
        ) == 1:

            risk_level = "MEDIUM"

        else:

            risk_level = "HIGH"

        return {

            "risk_level":
                risk_level,

            "issues":
                issues,

            "overall_confidence":
                overall_confidence,

            "parameters": {

                "pH": {

                    "predicted_value":
                        ph,

                    "confidence":
                        ph_confidence,

                },

                "turbidity": {

                    "predicted_value":
                        turbidity,

                    "confidence":
                        turbidity_confidence,

                },

                "temperature": {

                    "predicted_value":
                        temperature,

                    "confidence":
                        temperature_confidence,

                },

                "dissolved_oxygen": {

                    "predicted_value":
                        dissolved_oxygen,

                    "confidence":
                        dissolved_oxygen_confidence,

                },

                "TDS": {

                    "predicted_value":
                        tds,

                    "confidence":
                        tds_confidence,

                },

            },

        }

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================

    def generate_recommendations(
        self,
        current_evaluation: dict,
        future_evaluation: dict,
    ) -> list:
        """
        Generate human-readable recommendations.
        """

        recommendations = []

        all_issues = (

            current_evaluation.get(
                "issues",
                [],
            )

            +

            future_evaluation.get(
                "issues",
                [],
            )

        )

        issues_lower = [

            str(
                issue
            ).lower()

            for issue in all_issues

        ]

        # ==============================================
        # pH
        # ==============================================

        if any(
            "high ph" in issue
            for issue in issues_lower
        ):

            recommendations.append(
                "pH is above the recommended range. "
                "Reduce pH carefully."
            )

        if any(
            "low ph" in issue
            for issue in issues_lower
        ):

            recommendations.append(
                "pH is below the recommended range. "
                "Increase pH carefully."
            )

        # ==============================================
        # TURBIDITY
        # ==============================================

        if any(
            "turbidity" in issue
            for issue in issues_lower
        ):

            recommendations.append(
                "Turbidity is elevated. "
                "Improve filtration or water circulation."
            )

        # ==============================================
        # TEMPERATURE
        # ==============================================

        if any(
            "temperature" in issue
            for issue in issues_lower
        ):

            recommendations.append(
                "Water temperature requires monitoring."
            )

        # ==============================================
        # DISSOLVED OXYGEN
        # ==============================================

        if any(
            "oxygen" in issue
            for issue in issues_lower
        ):

            recommendations.append(
                "Dissolved oxygen is low. "
                "Increase aeration."
            )

        # ==============================================
        # TDS
        # ==============================================

        if any(
            "tds" in issue
            for issue in issues_lower
        ):

            recommendations.append(
                "TDS is elevated. "
                "Consider partial water replacement."
            )

        # ==============================================
        # STABLE
        # ==============================================

        if not recommendations:

            recommendations.append(
                "Water quality is currently stable "
                "and predicted to remain stable."
            )

        return recommendations

    # ==================================================
    # HARDWARE CONTROL
    # ==================================================

    def generate_hardware_control(
        self,
        current_evaluation: dict,
        future_evaluation: dict,
    ) -> dict:
        """
        Generate direct hardware control command.

        Hardware expects:

        {
            "message": "...",
            "time": ...
        }

        IMPORTANT:

        Hardware interprets time in minutes.

        0.0833 minutes ≈ 5 seconds.
        """

        current_issues = current_evaluation.get(
            "issues",
            [],
        )

        future_issues = future_evaluation.get(
            "issues",
            [],
        )

        all_issues = (

            current_issues

            +

            future_issues

        )

        issues_lower = [

            str(
                issue
            ).lower()

            for issue in all_issues

        ]

        # ==============================================
        # PRIORITY 1
        # LOW DISSOLVED OXYGEN
        # ==============================================

        if any(
            "oxygen" in issue
            for issue in issues_lower
        ):

            return {

                "message":
                    "Start Aerator",

                "time":
                    self.CONTROL_TIME,

            }

        # ==============================================
        # PRIORITY 2
        # HIGH pH
        # ==============================================

        if any(
            "high ph" in issue
            for issue in issues_lower
        ):

            return {

                "message":
                    "Release Acid",

                "time":
                    self.CONTROL_TIME,

            }

        # ==============================================
        # PRIORITY 3
        # LOW pH
        # ==============================================

        if any(
            "low ph" in issue
            for issue in issues_lower
        ):

            return {

                "message":
                    "Release Base",

                "time":
                    self.CONTROL_TIME,

            }

        # ==============================================
        # PRIORITY 4
        # HIGH TURBIDITY
        # ==============================================

        if any(
            "turbidity" in issue
            for issue in issues_lower
        ):

            return {

                "message":
                    "Start Water Pump",

                "time":
                    self.CONTROL_TIME,

            }

        # ==============================================
        # NO ACTION
        # ==============================================

        return {

            "message":
                "No Action",

            "time":
                0,

        }

    # ==================================================
    # MAIN PROCESS
    # ==================================================

    def process_observation(
        self,
            ph: float,
            turbidity: float,
            temperature: float,
            dissolved_oxygen: float,
            tds: float,
        ) -> dict:
        """
        Main Agent entry point.

        Flow:

        Sensor Observation
                ↓
        Current Water Evaluation
                ↓
        ML Processing
                ↓
        Future Prediction
                ↓
        Future Evaluation
                ↓
        Recommendations
                ↓
        Hardware Control
        """

        observation = [
            ph,
            turbidity,
            temperature,
            dissolved_oxygen,
            tds,
        ]

        # ==============================================
        # CURRENT WATER QUALITY
        # ==============================================

        current_evaluation = (
            self.evaluate_current_water_quality(
                observation
            )
        )

        # ==============================================
        # ML PROCESSING
        # ==============================================

        ml_result = (
            self.ml_service.process_observation(
                ph=ph,
                turbidity=turbidity,
                temperature=temperature,
                dissolved_oxygen=dissolved_oxygen,
                tds=tds,
            )
        )

        # ==============================================
        # ML FAILURE
        # ==============================================

        if not ml_result.get(
            "success",
            False,
        ):

            return {

                "success":
                    False,

                "error":
                    ml_result.get(
                        "error",
                        "ML processing failed",
                    ),

                "current_water_quality":
                    current_evaluation,

            }

        prediction_result = (
            ml_result.get(
                "prediction"
            )
        )

        # ==============================================
        # PREDICTION NOT READY
        # ==============================================

        if prediction_result is None:

            return {

                "success":
                    True,

                "prediction_ready":
                    False,

                "current_water_quality":
                    current_evaluation,

                "hardware_control": {

                    "message":
                        "No Action",

                    "time":
                        0,

                },

                "ml": {

                    "buffer":
                        ml_result.get(
                            "buffer"
                        ),

                    "prediction":
                        None,

                },

            }

        # ==============================================
        # FUTURE WATER QUALITY
        # ==============================================

        future_evaluation = (
            self.evaluate_future_water_quality(
                prediction_result
            )
        )

        # ==============================================
        # RECOMMENDATIONS
        # ==============================================

        recommendations = (
            self.generate_recommendations(
                current_evaluation,
                future_evaluation,
            )
        )

        # ==============================================
        # HARDWARE CONTROL
        # ==============================================

        hardware_control = (
            self.generate_hardware_control(
                current_evaluation,
                future_evaluation,
            )
        )

        # ==============================================
        # JSON SAFE ML DATA
        # ==============================================

        prediction_data = np.asarray(
            prediction_result[
                "prediction"
            ]
        ).tolist()

        confidence_data = np.asarray(
            prediction_result[
                "confidence"
            ]
        ).tolist()

        # ==============================================
        # FINAL RESPONSE
        # ==============================================

        return {

            "success":
                True,

            "prediction_ready":
                True,

            "current_water_quality":
                current_evaluation,

            "future_water_quality":
                future_evaluation,

            "recommendations":
                recommendations,

            "hardware_control":
                hardware_control,

            "ml": {

                "buffer":
                    ml_result.get(
                        "buffer"
                    ),

                "prediction": {

                    "prediction":
                        prediction_data,

                    "confidence":
                        confidence_data,

                },

            },

        }