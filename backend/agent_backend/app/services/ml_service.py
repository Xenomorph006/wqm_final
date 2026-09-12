import sys
from pathlib import Path


class MLService:

    def __init__(self):

        self.manager = None
        self.preprocessor = None
        self.ml_loaded = False
        self.initialization_error = None

        self._initialize_ml()


    def _initialize_ml(self):

        """
        Initialize the existing ML system.

        Supports both:
            from ml.src....
            from src....
        """

        try:

            # ==========================================
            # PATHS
            # ==========================================

            current_file = Path(
                __file__
            ).resolve()

            # Project root
            project_root = (
                current_file.parents[4]
            )

            # ML root
            ml_path = (
                project_root / "ml"
            )


            # ==========================================
            # PYTHON IMPORT PATHS
            # ==========================================

            # Supports:
            # from ml.src....
            if str(project_root) not in sys.path:

                sys.path.insert(
                    0,
                    str(project_root)
                )


            # Supports:
            # from src....
            if str(ml_path) not in sys.path:

                sys.path.insert(
                    0,
                    str(ml_path)
                )


            # ==========================================
            # IMPORT ML COMPONENTS
            # ==========================================

            from ml.src.data.build_ml_dataset import (
                build_ml_dataset,
            )

            from ml.src.self_learning.manager import (
                SelfLearningManager,
            )


            # ==========================================
            # ML FILE PATHS
            # ==========================================

            dataset_path = (
                ml_path
                / "data"
                / "generated"
                / "healthy"
                / "healthy.csv"
            )

            model_path = (
                ml_path
                / "results"
                / "checkpoints"
                / "lnn_baseline_best.pt"
            )


            # ==========================================
            # VALIDATE FILES
            # ==========================================

            if not dataset_path.exists():

                raise FileNotFoundError(
                    f"Dataset not found: "
                    f"{dataset_path}"
                )


            if not model_path.exists():

                raise FileNotFoundError(
                    f"Model not found: "
                    f"{model_path}"
                )


            # ==========================================
            # BUILD PREPROCESSOR
            # ==========================================

            print()
            print(
                "Initializing ML preprocessor..."
            )


            (
                _,
                _,
                _,
                _,
                _,
                _,
                self.preprocessor,
            ) = build_ml_dataset(

                str(dataset_path),

                input_window=60,

                prediction_horizon=12,

                stride=1,

            )


            # ==========================================
            # INITIALIZE SELF-LEARNING MANAGER
            # ==========================================

            print(
                "Loading ML LNN..."
            )


            self.manager = (
                SelfLearningManager(

                    model_path=str(
                        model_path
                    ),

                    scaler=(
                        self.preprocessor.scaler
                    ),

                    input_window=60,

                    prediction_horizon=12,

                    num_features=5,

                    hidden_size=64,

                    minimum_samples=32,

                    adaptation_batch_size=32,

                )
            )


            # ==========================================
            # SUCCESS
            # ==========================================

            self.ml_loaded = True
            self.initialization_error = None

            print()
            print(
                "ML system initialized successfully"
            )

            print(
                "Pretrained LNN loaded"
            )


            if (
                self.manager.loaded_checkpoint
                is not None
            ):

                print(
                    "Adapted checkpoint restored"
                )

            else:

                print(
                    "No adapted checkpoint found"
                )


        except Exception as error:

            self.ml_loaded = False
            self.initialization_error = str(error)

            print()
            print(
                "FAILED TO INITIALIZE ML SYSTEM"
            )
            print(error)
            print()


    def process_observation(
        self,
        ph,
        turbidity,
        temperature,
        dissolved_oxygen,
        tds,
    ):

        """
        Process one sensor observation.
        """

        if not self.ml_loaded:

            return {
                "success": False,
                "error": (
                    self.initialization_error
                    or
                    "ML system not initialized"
                ),
            }


        try:

            observation = [

                float(ph),

                float(turbidity),

                float(temperature),

                float(dissolved_oxygen),

                float(tds),

            ]


            result = (
                self.manager.process_observation(
                    observation
                )
            )


            return {

                "success": True,

                "buffer": result.get(
                    "buffer"
                ),

                "prediction": result.get(
                    "prediction"
                ),

            }


        except Exception as error:

            return {

                "success": False,

                "error": str(error),

            }


    def get_status(self):

        """
        Get ML system status.
        """

        if not self.ml_loaded:

            return {

                "ml_loaded": False,

                "error":
                    self.initialization_error,

            }


        try:

            return {

                "ml_loaded": True,

                "manager":
                    self.manager.get_status(),

            }


        except Exception as error:

            return {

                "ml_loaded": True,

                "error": str(error),

            }