from typing import List, Any

from models.experiment import Experiment
from models.group import Group
from models.types.measurement_type import MeasurementType
from models.types.experiment_type import ExperimentType


def _format_list(array: List[str]) -> str:
    """
    Format a list of strings as a single string.

    :param array: List of strings.
    :return: Formatted string.
    """
    return array[0] + "".join([f", {s}" for s in array[1:]])


class PanelConfig:
    """
    Class representing grafana panel configuration.
    """
    name: str
    experiment: Experiment

    def __init__(self, name: str, groups: [Group], measurement_types: [MeasurementType], experiment_type: ExperimentType):
        """
        Construct panel configuration from request body.
        """
        self.name = name
        self.experiment = Experiment(groups, experiment_type, measurement_types)

    def to_dict(self) -> dict:
        """
        Convert panel configuration to dictionary parseable by frontend.

        :return: Dictionary representation of panel configuration.
        """
        return {
            'name': self.name,
            'experiment_type': str(self.experiment.experiment_type),
            'measurement_types': _format_list([str(measurement_type) for measurement_type in self.experiment.measurement_types]),
            'group_names': _format_list([group.name for group in self.experiment.groups])
        }

