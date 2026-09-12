import numpy as np

from app.services.ml_service import (
    MLService,
)


class WaterQualityAgent:

    """
    Intelligent Water Quality Agent.

    Responsibilities:

    1. Evaluate current water quality
    2. Process live observations using ML
    3. Evaluate future ML predictions
    4. Analyze prediction confidence
    5. Detect future risks
    6. Generate recommendations
    7. Generate hardware control decisions
    """

    def __init__(self):

        print()

        print(
            "Initializing Water Quality Agent..."
        )

        self.ml_service = MLService()

        self.parameter_names = [

            "pH",

            "turbidity",

            "temperature",

            "dissolved_oxygen",

            "TDS",

        ]

        print(
            "Water Quality Agent ready"
        )


    # ==================================================
    # CURRENT WATER QUALITY
    # ==================================================

    def evaluate_current_water_quality(

        self,

        ph,

        turbidity,

        temperature,

        dissolved_oxygen,

        tds,

    ):

        """
        Evaluate current sensor readings.
        """

        issues = []


        # ==============================================
        # pH
        # ==============================================

        if ph < 6.5 or ph > 8.5:

            issues.append(
                "pH is outside the recommended range"
            )


        # ==============================================
        # TURBIDITY
        # ==============================================

        if turbidity > 25:

            issues.append(
                "Turbidity is elevated"
            )


        # ==============================================
        # TEMPERATURE
        # ==============================================

        if (

            temperature < 20

            or

            temperature > 32

        ):

            issues.append(
                "Temperature is outside the recommended range"
            )


        # ==============================================
        # DISSOLVED OXYGEN
        # ==============================================

        if dissolved_oxygen < 5:

            issues.append(
                "Dissolved oxygen is low"
            )


        # ==============================================
        # TDS
        # ==============================================

        if tds > 1000:

            issues.append(
                "TDS is elevated"
            )


        # ==============================================
        # RISK
        # ==============================================

        risk_level = "LOW"

        if len(issues) >= 3:

            risk_level = "HIGH"

        elif len(issues) >= 1:

            risk_level = "MEDIUM"


        return {

            "status":

                "healthy"
                if not issues
                else "warning",

            "risk_level":
                risk_level,

            "issues":
                issues,

        }


    # ==================================================
    # FUTURE PREDICTION ANALYSIS
    # ==================================================

    def evaluate_future_predictions(

        self,

        prediction,

        confidence,

    ):

        """
        Evaluate predicted future water quality.
        """

        issues = []

        parameter_analysis = {}


        prediction = np.array(
            prediction
        )

        confidence = np.array(
            confidence
        )


        # ==============================================
        # MEAN PREDICTIONS
        # ==============================================

        mean_values = np.mean(
            prediction,
            axis=0,
        )


        mean_confidence = np.mean(
            confidence,
            axis=0,
        )


        # ==============================================
        # PARAMETER ANALYSIS
        # ==============================================

        for index, parameter in enumerate(

            self.parameter_names

        ):

            value = float(
                mean_values[index]
            )

            confidence_value = float(
                mean_confidence[index]
            )


            parameter_analysis[
                parameter
            ] = {

                "predicted_value":
                    value,

                "confidence":
                    confidence_value,

            }


        # ==============================================
        # FUTURE pH
        # ==============================================

        if (

            mean_values[0] < 6.5

            or

            mean_values[0] > 8.5

        ):

            issues.append(
                "Future pH may move outside the safe range"
            )


        # ==============================================
        # FUTURE TURBIDITY
        # ==============================================

        if mean_values[1] > 25:

            issues.append(
                "Future turbidity may become elevated"
            )


        # ==============================================
        # FUTURE TEMPERATURE
        # ==============================================

        if (

            mean_values[2] < 20

            or

            mean_values[2] > 32

        ):

            issues.append(
                "Future temperature may become unsafe"
            )


        # ==============================================
        # FUTURE DISSOLVED OXYGEN
        # ==============================================

        if mean_values[3] < 5:

            issues.append(
                "Future dissolved oxygen may become low"
            )


        # ==============================================
        # FUTURE TDS
        # ==============================================

        if mean_values[4] > 1000:

            issues.append(
                "Future TDS may become elevated"
            )


        # ==============================================
        # OVERALL CONFIDENCE
        # ==============================================

        overall_confidence = float(

            np.mean(
                mean_confidence
            )

        )


        # ==============================================
        # RISK LEVEL
        # ==============================================

        risk_level = "LOW"

        if len(issues) >= 3:

            risk_level = "HIGH"

        elif len(issues) >= 1:

            risk_level = "MEDIUM"


        return {

            "risk_level":
                risk_level,

            "issues":
                issues,

            "overall_confidence":
                overall_confidence,

            "parameters":
                parameter_analysis,

        }


    # ==================================================
    # GENERATE RECOMMENDATIONS
    # ==================================================

    def generate_recommendations(

        self,

        current,

        future,

    ):

        """
        Generate recommendations using
        current and predicted water quality.
        """

        recommendations = []


        # ==============================================
        # CURRENT ISSUES
        # ==============================================

        for issue in current["issues"]:

            recommendations.append(
                f"Current condition: {issue}"
            )


        # ==============================================
        # FUTURE ISSUES
        # ==============================================

        for issue in future["issues"]:

            recommendations.append(
                f"Predicted condition: {issue}"
            )


        # ==============================================
        # LOW CONFIDENCE
        # ==============================================

        if (

            future[
                "overall_confidence"
            ]

            < 0.6

        ):

            recommendations.append(

                "Prediction confidence is low. "
                "Continue monitoring before taking "
                "major corrective action."

            )


        # ==============================================
        # HEALTHY
        # ==============================================

        if not recommendations:

            recommendations.append(

                "Water quality is currently stable "
                "and predicted to remain stable."

            )


        return recommendations


    # ==================================================
    # HARDWARE CONTROL DECISION
    # ==================================================

    def generate_control_decision(

        self,

        current,

        future,

    ):

        """
        Generate hardware control commands.

        This JSON will later be sent
        to the control system.
        """

        controls = {

            "aerator":

                {
                    "action":
                        "OFF",

                    "reason":
                        "Dissolved oxygen is sufficient",

                },


            "water_pump":

                {
                    "action":
                        "OFF",

                    "reason":
                        "Water quality is stable",

                },

        }


        # ==============================================
        # CURRENT DO
        # ==============================================

        if (

            current["risk_level"]
            in ["MEDIUM", "HIGH"]

        ):

            controls[
                "water_pump"
            ] = {

                "action":
                    "MONITOR",

                "reason":
                    "Water quality requires monitoring",

            }


        # ==============================================
        # FUTURE DO
        # ==============================================

        predicted_do = (

            future["parameters"]
            ["dissolved_oxygen"]
            ["predicted_value"]

        )


        if predicted_do < 5:

            controls[
                "aerator"
            ] = {

                "action":
                    "ON",

                "reason":
                    "Predicted dissolved oxygen may become low",

            }


        return controls


    # ==================================================
    # MAIN AGENT WORKFLOW
    # ==================================================

    def evaluate(

        self,

        ph,

        turbidity,

        temperature,

        dissolved_oxygen,

        tds,

    ):

        """
        Main Agent workflow.
        """


        # ==============================================
        # CURRENT EVALUATION
        # ==============================================

        current_evaluation = (

            self.evaluate_current_water_quality(

                ph=ph,

                turbidity=turbidity,

                temperature=temperature,

                dissolved_oxygen=
                    dissolved_oxygen,

                tds=tds,

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

                dissolved_oxygen=
                    dissolved_oxygen,

                tds=tds,

            )

        )


        # ==============================================
        # NO ML PREDICTION YET
        # ==============================================

        if (

            not ml_result["success"]

        ):

            return {

                "success":
                    False,

                "error":
                    ml_result["error"],

            }


        prediction_result = (

            ml_result["prediction"]

        )


        if prediction_result is None:

            return {

                "success":
                    True,

                "current_water_quality":
                    current_evaluation,

                "prediction_ready":
                    False,

                "message":

                    "Collecting sensor history "
                    "for ML prediction.",

                "ml":
                    ml_result,

            }


        # ==============================================
        # FUTURE ANALYSIS
        # ==============================================

        future_evaluation = (

            self.evaluate_future_predictions(

                prediction=
                    prediction_result[
                        "prediction"
                    ],

                confidence=
                    prediction_result[
                        "confidence"
                    ],

            )

        )


        # ==============================================
        # RECOMMENDATIONS
        # ==============================================

        recommendations = (

            self.generate_recommendations(

                current=
                    current_evaluation,

                future=
                    future_evaluation,

            )

        )


        # ==============================================
        # CONTROL DECISION
        # ==============================================

        controls = (

            self.generate_control_decision(

                current=
                    current_evaluation,

                future=
                    future_evaluation,

            )

        )


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

            "controls":
                controls,

            "ml":
                ml_result,

        }


    # ==================================================
    # AGENT STATUS
    # ==================================================

    def get_status(self):

        return {

            "agent_ready":
                True,

            "ml":

                self.ml_service.get_status(),

        }