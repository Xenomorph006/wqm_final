import torch
import joblib

from app.core.config import settings

# Import your NFLNN model
from app.ml.nflnn import NFLNN


class ModelLoader:
    def __init__(self):
        self.model = None
        self.scaler = None

    def load(self):
        """
        Load trained model and scaler into memory.
        This should be called only once during application startup.
        """

        # Load Model
        self.model = NFLNN()

        self.model.load_state_dict(
            torch.load(
                settings.MODEL_PATH,
                map_location=torch.device("cpu")
            )
        )

        self.model.eval()

        # Load Scaler
        self.scaler = joblib.load(settings.SCALER_PATH)

        print("✅ NFLNN Model Loaded Successfully")
        print("✅ Scaler Loaded Successfully")


# Singleton Instance
model_loader = ModelLoader()