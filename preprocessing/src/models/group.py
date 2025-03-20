import pandas as pd
from typing import List
from models.trial import Trial
from models.types.measurement_type import MeasurementType
from models.types.visualization_type import VisualizationType
import os


class Group:
    name: str
    trials: List[Trial]

    # Aggregated data from all trails (e.g. mean, median, std over time)
    aggregate_data: pd.DataFrame

    # Summary statistics for the whole group (e.g. total energy, peak power)
    statistics_summary: pd.DataFrame

    def __init__(self, name: str, folder_path: str) -> None:
        self.name = name

        # Construct trials by loading csv files in folder
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f'Folder does not exist: "{folder_path}"')

        self.trials = [Trial(os.path.join(folder_path, file_name)) for file_name in os.listdir(folder_path) if file_name.endswith(".csv")]
        if len(self.trials) == 0:
            raise FileNotFoundError(f'No trials found in folder: "{folder_path}"')

    def add_trial(self, trial: Trial | str) -> None:
        """
        Add a trial to the group.
        """
        if trial is str:
            self.trials.append(Trial(trial))
        else:
            self.trials.append(trial)

    def aggregate(self, measurement_types: List[MeasurementType]) -> None:
        """
        Aggregate the data from all trails in the group for the specified columns.
        """

        # TODO: Add aggregation over time logic here for the specified columns

    def summarize(self, measurement_types: List[MeasurementType]) -> None:
        """
        Generate summary statistics for the group.
        """
        # TODO: Add summary statistics logic here for all trails as whole

    def visualize(self, measurement_types: List[MeasurementType], visualization_type: VisualizationType) -> dict:
        """
        Returns the panel as a dictionary for grafana dashboard.
        """

        # Aggregate data
        self.aggregate(measurement_types)

        # Summarize data
        self.summarize(measurement_types)

        # TODO: Add logic to visualize the group data to a panel

    def to_dict(self) -> dict:
        """
        Convert group to dictionary parseable by frontend.
        """
        return {'name': self.name, 'trial_count': str(len(self.trials))}
