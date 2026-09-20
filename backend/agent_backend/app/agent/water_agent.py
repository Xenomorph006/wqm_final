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

    def calculate_control_time(
        self,
        parameter: str,
        value: float
    ) -> float:
        """
        Calculate hardware activation time based on
        the severity of the current water-quality condition.

        The returned value is in minutes because the hardware
        interprets:

            time * 60000 = milliseconds

        Maximum hardware activation time = 15 seconds.
        """

        MIN_SECONDS = 2.0
        MAX_SECONDS = 15.0

        severity = 0.0

        if parameter == "dissolved_oxygen":
            if value < 5.0:
                severity = (5.0 - value) / 5.0

        elif parameter == "temperature_high":
            if value > 32.0:
                severity = (value - 32.0) / 32.0

        elif parameter == "temperature_low":
            if value < 20.0:
                severity = (20.0 - value) / 20.0

        elif parameter == "pH_high":
            if value > 8.5:
                severity = (value - 8.5) / 8.5

        elif parameter == "pH_low":
            if value < 6.5:
                severity = (6.5 - value) / 6.5

        elif parameter == "turbidity":
            if value > 25.0:
                severity = (value - 25.0) / 25.0

        elif parameter == "tds":
            if value > 500.0:
                severity = (value - 500.0) / 500.0

        # Keep severity safely between 0 and 1.
        severity = max(0.0, min(severity, 1.0))

        seconds = MIN_SECONDS + (
            severity * (MAX_SECONDS - MIN_SECONDS)
        )

        # Absolute safety limit: 15 seconds.
        seconds = max(
            MIN_SECONDS,
            min(seconds, MAX_SECONDS)
        )

        # Hardware expects minutes.
        hardware_time = seconds / 60.0

        return round(hardware_time, 4)

    # ==================================================
    # HARDWARE CONTROL
    # ==================================================

    def generate_hardware_control(
        self,
        current_values: dict,
        current_evaluation: dict,
        future_evaluation: dict,
    ) -> dict:

    # ==============================================
    # GET CURRENT + FUTURE ISSUES
    # ==============================================

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
            + future_issues
        )

        issues_lower = [
            str(issue).lower()
            for issue in all_issues
        ]

        # ==============================================
        # CRITICALITY DETECTION
        # ==============================================

        critical_controls = []

        # LOW DISSOLVED OXYGEN
        if any(
            "low oxygen" in issue
            or "low dissolved oxygen" in issue
            for issue in issues_lower
        ):
            critical_controls.append(
                ("Start Aerator", 1.0, "dissolved_oxygen")
            )

        # HIGH TEMPERATURE
        if any(
            "high temperature" in issue
            for issue in issues_lower
        ):
            critical_controls.append(
                ("Start Cooling System", 1.0, "temperature_high")
            )

        # LOW TEMPERATURE
        if any(
            "low temperature" in issue
            for issue in issues_lower
        ):
            critical_controls.append(
                ("Start Heater", 1.0, "temperature_low")
            )

        # HIGH pH
        if any(
            "high ph" in issue
            for issue in issues_lower
        ):
           critical_controls.append(
                ("Release Acid", 1.0, "pH_high")
            )

        # LOW pH
        if any(
            "low ph" in issue
            for issue in issues_lower
        ):
            critical_controls.append(
                ("Release Base", 1.0, "pH_low")
            )

        # HIGH TURBIDITY
        if any(
            "high turbidity" in issue
            for issue in issues_lower
        ):
            critical_controls.append(
                ("Start Water Pump", 1.0, "turbidity")
            )

        # ==============================================
        # NO CRITICAL CONDITION
        # ==============================================

        if not critical_controls:

            return {
                "message": "No Action",
                "time": 0,
            }

        # ==============================================
        # SELECT MOST CRITICAL PARAMETER
        # ==============================================

        critical_controls.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        selected_control = critical_controls[0][0]
        selected_parameter = critical_controls[0][2]

        parameter_values = {
            "dissolved_oxygen": current_values["dissolved_oxygen"],
            "temperature_high": current_values["temperature"],
            "temperature_low": current_values["temperature"],
            "pH_high": current_values["ph"],
            "pH_low": current_values["ph"],
            "turbidity": current_values["turbidity"],
        }

        selected_value = parameter_values[selected_parameter]

        control_time = self.calculate_control_time(
            selected_parameter,
            selected_value,
        )

        # ==============================================
        # FINAL HARDWARE RESPONSE
        # ==============================================

        return {
            "message": selected_control,
            "time": control_time,
        }

        # ==================================================
    # FISH RECOMMENDATION
    # ==================================================

    def generate_fish_recommendation(
        self,
        current_values: dict,
        future_evaluation: dict,
    ) -> dict:
        """
        Evaluate fish suitability using current
        and predicted future water-quality values.

        Only the highest-scoring suitable fish
        is returned in recommended_fish.
        """

        # ==============================================
        # FISH PROFILES
        # ==============================================

        fish_profiles = {

            "Tilapia": {
                "ph": (6.5, 8.5),
                "temperature": (24.0, 32.0),
                "dissolved_oxygen": 3.0,
                "turbidity": (0.0, 25.0),
                "tds": (100.0, 1000.0),
            },

            "Rohu": {
                "ph": (6.5, 8.5),
                "temperature": (22.0, 32.0),
                "dissolved_oxygen": 4.0,
                "turbidity": (0.0, 25.0),
                "tds": (100.0, 1000.0),
            },

            "Catla": {
                "ph": (6.5, 8.5),
                "temperature": (22.0, 32.0),
                "dissolved_oxygen": 4.0,
                "turbidity": (0.0, 25.0),
                "tds": (100.0, 1000.0),
            },

            "Mrigal": {
                "ph": (6.5, 8.5),
                "temperature": (22.0, 32.0),
                "dissolved_oxygen": 4.0,
                "turbidity": (0.0, 25.0),
                "tds": (100.0, 1000.0),
            },

            "Common Carp": {
                "ph": (6.5, 9.0),
                "temperature": (20.0, 30.0),
                "dissolved_oxygen": 4.0,
                "turbidity": (0.0, 25.0),
                "tds": (100.0, 1500.0),
            },

            "Pangasius": {
                "ph": (6.5, 8.5),
                "temperature": (24.0, 32.0),
                "dissolved_oxygen": 3.0,
                "turbidity": (0.0, 25.0),
                "tds": (100.0, 1000.0),
            },
        }

        # ==============================================
        # CURRENT VALUES
        # ==============================================

        current_ph = float(
            current_values["ph"]
        )

        current_turbidity = float(
            current_values["turbidity"]
        )

        current_temperature = float(
            current_values["temperature"]
        )

        current_dissolved_oxygen = float(
            current_values["dissolved_oxygen"]
        )

        current_tds = float(
            current_values["tds"]
        )

        # ==============================================
        # FUTURE VALUES
        # ==============================================

        predicted_parameters = (
            future_evaluation.get(
                "parameters",
                {}
            )
        )

        future_ph = float(
            predicted_parameters["pH"][
                "predicted_value"
            ]
        )

        future_turbidity = float(
            predicted_parameters["turbidity"][
                "predicted_value"
            ]
        )

        future_temperature = float(
            predicted_parameters["temperature"][
                "predicted_value"
            ]
        )

        future_dissolved_oxygen = float(
            predicted_parameters["dissolved_oxygen"][
                "predicted_value"
            ]
        )

        future_tds = float(
            predicted_parameters["TDS"][
                "predicted_value"
            ]
        )

        # ==============================================
        # CURRENT + FUTURE WATER QUALITY
        # ==============================================

        current_water_quality = {
            "ph": current_ph,
            "turbidity": current_turbidity,
            "temperature": current_temperature,
            "dissolved_oxygen": current_dissolved_oxygen,
            "tds": current_tds,
        }

        predicted_water_quality = {
            "ph": future_ph,
            "turbidity": future_turbidity,
            "temperature": future_temperature,
            "dissolved_oxygen": future_dissolved_oxygen,
            "tds": future_tds,
        }

        # ==============================================
        # SPECIES EVALUATION
        # ==============================================

        suitable_fish = []
        unsuitable_fish = []

        for species, profile in fish_profiles.items():

            checks = []

            # ------------------------------------------
            # CURRENT pH
            # ------------------------------------------

            checks.append(
                profile["ph"][0]
                <= current_ph
                <= profile["ph"][1]
            )

            # ------------------------------------------
            # FUTURE pH
            # ------------------------------------------

            checks.append(
                profile["ph"][0]
                <= future_ph
                <= profile["ph"][1]
            )

            # ------------------------------------------
            # CURRENT TEMPERATURE
            # ------------------------------------------

            checks.append(
                profile["temperature"][0]
                <= current_temperature
                <= profile["temperature"][1]
            )

            # ------------------------------------------
            # FUTURE TEMPERATURE
            # ------------------------------------------

            checks.append(
                profile["temperature"][0]
                <= future_temperature
                <= profile["temperature"][1]
            )

            # ------------------------------------------
            # CURRENT DO
            # ------------------------------------------

            checks.append(
                current_dissolved_oxygen
                >= profile["dissolved_oxygen"]
            )

            # ------------------------------------------
            # FUTURE DO
            # ------------------------------------------

            checks.append(
                future_dissolved_oxygen
                >= profile["dissolved_oxygen"]
            )

            # ------------------------------------------
            # CURRENT TURBIDITY
            # ------------------------------------------

            checks.append(
                profile["turbidity"][0]
                <= current_turbidity
                <= profile["turbidity"][1]
            )

            # ------------------------------------------
            # FUTURE TURBIDITY
            # ------------------------------------------

            checks.append(
                profile["turbidity"][0]
                <= future_turbidity
                <= profile["turbidity"][1]
            )

            # ------------------------------------------
            # CURRENT TDS
            # ------------------------------------------

            checks.append(
                profile["tds"][0]
                <= current_tds
                <= profile["tds"][1]
            )

            # ------------------------------------------
            # FUTURE TDS
            # ------------------------------------------

            checks.append(
                profile["tds"][0]
                <= future_tds
                <= profile["tds"][1]
            )

            # ==========================================
            # SUITABILITY SCORE
            # ==========================================

            score = (
                sum(checks)
                / len(checks)
            )

            score = round(
                score,
                2
            )

            percentage = round(
                score * 100,
                1
            )

            # ==========================================
            # SUITABILITY LEVEL
            # ==========================================

            if score >= 0.8:

                suitability = "High"

            elif score >= 0.5:

                suitability = "Medium"

            else:

                suitability = "Low"

            # ==========================================
            # REASON
            # ==========================================

            if suitability == "High":

                reason = (
                    "Current and predicted "
                    "water-quality conditions "
                    "are compatible with the "
                    "species profile."
                )

            elif suitability == "Medium":

                reason = (
                    "Some current or predicted "
                    "water-quality parameters "
                    "require attention."
                )

            else:

                reason = (
                    "Current or predicted "
                    "water-quality conditions "
                    "are outside the suitable "
                    "range for this species."
                )

            fish_result = {
                "species": species,
                "suitability": suitability,
                "score": score,
                "percentage": percentage,
                "reason": reason,
            }

            # ==========================================
            # CLASSIFY FISH
            # ==========================================

            if suitability in (
                "High",
                "Medium",
            ):

                suitable_fish.append(
                    fish_result
                )

            else:

                unsuitable_fish.append(
                    fish_result
                )

        # ==============================================
        # SELECT ONLY ONE FISH
        # ==============================================

        if suitable_fish:

            suitable_fish.sort(
                key=lambda fish: fish["score"],
                reverse=True,
            )

            recommended_fish = [
                suitable_fish[0]
            ]

        else:

            recommended_fish = []

        # ==============================================
        # OVERALL RECOMMENDATION
        # ==============================================

        if recommended_fish:

            overall_recommendation = (
                "The evaluated water conditions "
                "are suitable for freshwater "
                "fish cultivation."
            )

        else:

            overall_recommendation = (
                "The evaluated water conditions "
                "are currently not suitable for "
                "the evaluated fish species."
            )

        # ==============================================
        # FINAL FISH RESPONSE
        # ==============================================

        return {

            "current_water_quality":
                current_water_quality,

            "predicted_water_quality":
                predicted_water_quality,

            "recommended_fish":
                recommended_fish,

            "unsuitable_fish":
                unsuitable_fish,

            "overall_recommendation":
                overall_recommendation,

        }


    def validate_observation(
        self,
        ph: float,
        turbidity: float,
        temperature: float,
        dissolved_oxygen: float,
        tds: float
    ):
        """
        Validate incoming water-quality sensor data before
        sending it to the ML system.

        Returns:
            tuple[bool, list[str]]
        """

        values = {
            "pH": ph,
            "turbidity": turbidity,
            "temperature": temperature,
            "dissolved_oxygen": dissolved_oxygen,
            "TDS": tds
        }

        errors = []

        for name, value in values.items():
            if value is None:
                errors.append(f"{name} is missing")
                continue

            try:
                value = float(value)
            except (TypeError, ValueError):
                errors.append(f"{name} is not numeric")
                continue

            if not np.isfinite(value):
                errors.append(f"{name} is not finite")

        # Physical / sensor operating limits
        if ph < 0 or ph > 14:
            errors.append("pH is outside valid range")

        if turbidity < 0:
            errors.append("Turbidity cannot be negative")

        if temperature < -10 or temperature > 60:
            errors.append("Temperature is outside valid range")

        if dissolved_oxygen < 0 or dissolved_oxygen > 30:
            errors.append("Dissolved oxygen is outside valid range")

        if tds < 0:
            errors.append("TDS cannot be negative")

        return len(errors) == 0, errors


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
        Validation
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
                ↓
        Fish Recommendation
                ↓
        Final Response
        """

        # ==============================================
        # SENSOR VALIDATION
        # ==============================================

        valid, validation_errors = self.validate_observation(
            ph,
            turbidity,
            temperature,
            dissolved_oxygen,
            tds,
        )

        if not valid:
            return {
                "success": False,
                "prediction_ready": False,
                "error": "Invalid sensor observation",
                "validation_errors": validation_errors,
            }

        # ==============================================
        # CURRENT VALUES
        # ==============================================

        current_values = {
            "ph": ph,
            "turbidity": turbidity,
            "temperature": temperature,
            "dissolved_oxygen": dissolved_oxygen,
            "tds": tds,
        }

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

        current_evaluation = self.evaluate_current_water_quality(
            observation
        )

        # ==============================================
        # ML PROCESSING
        # ==============================================

        ml_result = self.ml_service.process_observation(
            ph=ph,
            turbidity=turbidity,
            temperature=temperature,
            dissolved_oxygen=dissolved_oxygen,
            tds=tds,
        )

        # ==============================================
        # ML FAILURE
        # ==============================================

        if not ml_result.get("success", False):

            return {
                "success": False,
                "error": ml_result.get(
                    "error",
                    "ML processing failed",
                ),
                "current_water_quality": current_evaluation,
            }

        prediction_result = ml_result.get("prediction")

        # ==============================================
        # PREDICTION STATUS
        # ==============================================

        prediction_ready = prediction_result is not None

        # ==============================================
        # FUTURE WATER QUALITY
        # ==============================================

        if prediction_ready:

            future_evaluation = (
                self.evaluate_future_water_quality(
                    prediction_result
                )
            )

        else:

            future_evaluation = {
                "issues": []
            }

        # ==============================================
        # RECOMMENDATIONS
        # ==============================================

        recommendations = self.generate_recommendations(
            current_evaluation,
            future_evaluation,
        )

        # ==============================================
        # HARDWARE CONTROL
        # ==============================================

        hardware_control = self.generate_hardware_control(
            current_values,
            current_evaluation,
            future_evaluation,
        )

        # ==============================================
        # FISH RECOMMENDATION
        # ==============================================

        if prediction_ready:
            fish_recommendation = (
                self.generate_fish_recommendation(
                    current_values=current_values,
                    future_evaluation=future_evaluation,
                )
            )
        else:
            fish_recommendation = {
                "current_water_quality": current_evaluation,
                "predicted_water_quality": {},
                "recommended_fish": [],
                "unsuitable_fish": [],
                "overall_recommendation": (
                    "Fish recommendation unavailable until "
                    "prediction is ready."
                ),
            }

        # ==============================================
        # PREDICTION NOT READY
        # ==============================================

        if not prediction_ready:

            return {
                "success": True,
                "prediction_ready": False,

                "current_water_quality":
                    current_evaluation,

                "future_water_quality":
                    future_evaluation,

                "recommendations":
                    recommendations,

                "hardware_control":
                    hardware_control,

                "fish_recommendation":
                    fish_recommendation,

                "ml": {
                    "buffer":
                        ml_result.get("buffer"),

                    "prediction":
                        None,
                },
            }

        # ==============================================
        # JSON SAFE ML DATA
        # ==============================================

        prediction_data = np.asarray(
            prediction_result["prediction"]
        ).tolist()

        confidence_data = np.asarray(
            prediction_result["confidence"]
        ).tolist()

        # ==============================================
        # FINAL RESPONSE
        # ==============================================

        return {
            "success": True,

            "prediction_ready": True,

            "current_water_quality":
                current_evaluation,

            "future_water_quality":
                future_evaluation,

            "recommendations":
                recommendations,

            "hardware_control":
                hardware_control,

            "fish_recommendation":
                fish_recommendation,

            "ml": {
                "buffer":
                    ml_result.get("buffer"),

                "prediction": {
                    "prediction":
                        prediction_data,

                    "confidence":
                        confidence_data,
                },
            },
        }