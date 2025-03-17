import pandas as pd
from typing import List
from trial import Trial
from preprocessing.src.models.types.measurement_type import MeasurementType
from preprocessing.src.models.types.visualization_type import VisualizationType
import os


class Group:
    name: str
    trails: List[Trial]

    # Aggregated data from all trails (e.g. mean, median, std over time)
    aggregate_data: pd.DataFrame

    # Summary statistics for the whole group (e.g. total energy, peak power)
    statistics_summary: pd.DataFrame

    def __init__(self, name: str, trails: List[Trial] | List[str]) -> None:
        self.name = name
        if type(trails[0]) is str:
            self.trails = [Trial(trail) for trail in trails]
        else:
            self.trails = trails

    def add_trial(self, trial: Trial | str) -> None:
        """
        Add a trial to the group.
        """
        if trial is str:
            self.trails.append(Trial(trial))
        else:
            self.trails.append(trial)

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