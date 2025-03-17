import pandas as pd
from typing import List
from preprocessing.src.models.types.measurement_type import MeasurementType
from preprocessing.src.models.types.visualization_type import VisualizationType

class Trail:
    # Original file path
    raw_file_path: str

    # Preprocessed file path
    preprocessed_file_path: str

    # Raw csv data from energibridge
    raw_data: pd.DataFrame

    # Preprocessed data
    preprocessed_data: pd.DataFrame

    def __init__(self, raw_file_path: str) -> None:
        self.raw_file_path = raw_file_path
        # TODO: Make sure it gets saved in the right directory
        self.preprocessed_file_path = raw_file_path.replace(".csv", "_preprocessed.csv")


    def preprocess(self) -> None:
        """
        Preprocess the data.
        """
        # TODO: Add preprocessing here that is needed for every trail
        # TODO: Document overview of columns and data types of preprocessed data
        self.preprocessed_data = self.raw_data

    def visualize(self, measurement_types: List[MeasurementType], visualization_type: VisualizationType) -> dict:
        """
        Returns the panel as a dictionary for grafana dashboard.
        """

        # Make sure the data is preprocessed
        self.preprocess()



