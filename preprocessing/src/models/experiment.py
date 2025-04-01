import pandas as pd
import json
import re
from typing import List, Dict, Any
from models.group import Group
from models.types.experiment_type import ExperimentType
from models.types.measurement_type import MeasurementType
from visualization.plotovertime import PlotOverTime
from visualization.significance import SignificanceTest
from visualization.statistics import Statistics


def _format_list(array: List[str]) -> str:
    """
    Format a list of strings as a comma-separated single string.
    
    :param array: List of strings to format.
    :return: Formatted string with commas between elements.
    """
    if not array:
        return ""
    return array[0] + "".join(f", {s}" for s in array[1:])


class Experiment:
    name: str
    groups: List[Group]
    experiment_type: ExperimentType
    measurement_types: List[MeasurementType]
    results: pd.DataFrame

    def __init__(self, name: str, groups: List[Group], experiment_type: ExperimentType, measurement_types: List[MeasurementType]) -> None:
        """
        Initialize an experiment with groups, experiment type and measurement types.
        
        :param name: Name of the experiment.
        :param groups: Groups to include in this experiment.
        :param experiment_type: Type of the experiment.
        :param measurement_types: Types of measurements to analyze.
        """
        self.name = name
        self.groups = groups
        print(f'Experiment {name} has {len(groups)} groups.')
        self.experiment_type = experiment_type
        self.measurement_types = measurement_types

    def analyze(self) -> None:
        """
        Analyze the data from all groups in the experiment.
        Performs statistical analysis based on the experiment type.
        """
        # TODO: Add analysis logic here
        # Do experiment between all groups for all measurement types

    def _load_template_with_placeholders(self, template_name: str, placeholders: Dict[str, str]) -> Dict[str, Any]:
        """
        Load a JSON template file and replace placeholders with actual values.
        
        :param template_name: Name of the template file to load.
        :param placeholders: Dictionary mapping placeholder names to their values.
        :return: Parsed JSON dictionary with placeholders replaced.
        """
        with open("csv-data/grafana-templates/" + template_name, 'r') as file:
            template = file.read()
            for key, value in placeholders.items():
                template = template.replace("PLACEHOLDER_" + key, value)
            return json.loads(template)

    def create_visualization_panels(self) -> List[Dict[str, Any]]:
        """
        Generate visualization panels for this experiment based on the experiment type.
        Routes to appropriate visualization plugin based on experiment type.
        
        :return: List of panel configurations for Grafana dashboard.
        """
        # Ensure data is analyzed
        self.analyze()
        
        # Use different visualization strategies based on experiment type
        if self.experiment_type == ExperimentType.PLOT_OVER_TIME:
            return PlotOverTime.generate_panels(
                self.name, self.groups, self.measurement_types)
        
        elif self.experiment_type == ExperimentType.SIGNIFICANCE_TEST:
            return SignificanceTest.generate_panels(
                self.name, self.groups, self.measurement_types)

        elif self.experiment_type == ExperimentType.STATISTICS:
            return Statistics.generate_panels(
                self.name, self.groups, self.measurement_types)
        
        else:
            # Throw error if experiment type is not recognized
            raise ValueError(f'Unknown experiment type: {self.experiment_type}')

    def to_dict(self) -> dict:
        """
        Convert experiment to a dictionary for frontend representation.
        Formats lists as comma-separated strings for easy display.

        :return: Dictionary representation of the experiment.
        """
        return {
            'name': self.name,
            'experiment_type': str(self.experiment_type),
            'measurement_types': _format_list([str(measurement_type) for measurement_type in self.measurement_types]),
            'group_names': _format_list([group.name for group in self.groups])
        }


