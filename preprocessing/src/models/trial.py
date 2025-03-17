import pandas as pd
from typing import List
from preprocessing.src.models.types.measurement_type import MeasurementType
from preprocessing.src.models.types.visualization_type import VisualizationType
import preprocessing.src.preprocessing as pp
import os


class Trial:
    # Original file path
    raw_file_path: str

    # Preprocessed file path
    preprocessed_file_path: str

    # Preprocessed data
    preprocessed_data: pd.DataFrame

    def __init__(self, raw_file_path: str) -> None:
        if not os.path.exists(raw_file_path):
            raise FileNotFoundError(f"Import of file failed. File {raw_file_path} not found.")
        # TODO: output destination folder existence check
        self.raw_file_path = raw_file_path
        raw_data = pd.read_csv(raw_file_path)
        self.preprocessed_data = pp.preprocess(raw_data)  # preprocess upon creation
        self.preprocessed_file_path = raw_file_path.replace(".csv", "_preprocessed.csv")
        self.preprocessed_data.to_csv(self.preprocessed_file_path, index=False)

    def visualize(self, measurement_types: List[MeasurementType], visualization_type: VisualizationType) -> dict:
        """
        Returns the panel as a dictionary for grafana dashboard.
        """
        return {}


