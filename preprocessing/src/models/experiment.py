import pandas as pd
from typing import List
from group import Group
from types.experiment_type import ExperimentType
from types.measurement_type import MeasurementType

class Experiment:
    groups: List[Group]
    experiment_type: ExperimentType
    measurement_types: List[MeasurementType]

    results: pd.DataFrame

    def __init__(self, groups: List[Group], experiment_type: ExperimentType, measurement_types: List[MeasurementType]) -> None:
        self.groups = groups
        self.experiment_type = experiment_type
        self.measurement_types = measurement_types

    def analyze(self) -> None:
        """
        Analyze the data from all groups in the experiment.
        """

        # TODO: Add analysis logic here

        # Do experiment between all groups for all measurement types

 
    def visualize(self) -> dict:
        """
        Returns the panel as a dictionary for grafana dashboard.
        """

        
