import pandas as pd
from typing import List
import re

# from preprocessing.src.models.types.measurement_type import MeasurementType
# from preprocessing.src.models.types.visualization_type import VisualizationType
# import preprocessing.src.preprocessing as pp

from models.types.measurement_type import MeasurementType
from models.types.visualization_type import VisualizationType
import preprocessing as pp
import os


class Trial:
    # Original file path
    raw_file_path: str
    filename: str

    # Preprocessed file path
    preprocessed_file_path: str

    # Preprocessed data
    preprocessed_data: pd.DataFrame

    def __init__(self, unprocessed_path: str = '', preprocessed_path: str = '') -> None:
        if unprocessed_path != '' and not preprocessed_path.endswith("_preprocessed.csv"):
            if not os.path.exists(unprocessed_path):
                raise FileNotFoundError(f"Import of file failed. File {unprocessed_path} not found.")
            # If unprocessed file is provided, preprocess it then save
            self.raw_file_path = unprocessed_path
            self.filename = os.path.splitext(os.path.split(unprocessed_path)[1])[0]
            raw_data = pd.read_csv(unprocessed_path)
            self.preprocessed_data = pp.preprocess(raw_data)  # preprocess upon creation
            self.preprocessed_file_path = preprocessed_path.replace(".csv", "_preprocessed.csv")
            self.preprocessed_data.to_csv(self.preprocessed_file_path, index=False)
        else:
            # For loading already existing files
            if not os.path.exists(preprocessed_path):
                raise FileNotFoundError(f"Import of file failed. File {preprocessed_path} not found.")
            self.raw_file_path = ''
            self.filename = ''
            self.preprocessed_file_path = preprocessed_path
            self.preprocessed_data = pd.read_csv(preprocessed_path)

    def no_cores(self) -> int:
        return len(re.findall(r'CORE\d+_POWER \(W\)', ', '.join(self.preprocessed_data.columns)))

    def no_logical(self) -> int:
        return len(re.findall(r'CPU_USAGE_\d+', ', '.join(self.preprocessed_data.columns)))

    def visualize(self, measurement_types: List[MeasurementType], visualization_type: VisualizationType) -> dict:
        """
        Returns the panel as a dictionary for grafana dashboard.
        """
        return {}
