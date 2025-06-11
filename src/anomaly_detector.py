import pandas as pd
from anomalib.data.utils import read_image
from anomalib.models import Padim
from anomalib.config import get_configurable_parameters
import torch


class FuelAnomalyDetector:
    def __init__(self):
        self.model = None

    def train(self, df: pd.DataFrame):
        cfg = get_configurable_parameters(model_name="padim")
        self.model = Padim(cfg.model)
        data = torch.tensor(df["diff"].values, dtype=torch.float32).unsqueeze(1)
        self.model.fit(data)

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            raise RuntimeError("Model is not trained")
        data = torch.tensor(df["diff"].values, dtype=torch.float32).unsqueeze(1)
        scores = self.model.predict(data)
        df = df.copy()
        df["anomaly_score"] = scores.numpy()
        return df[df["anomaly_score"] > 0.5]
