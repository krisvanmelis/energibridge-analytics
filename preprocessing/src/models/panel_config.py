from models.experiment import Experiment
from models.group import Group
from models.types.measurement_type import MeasurementType
from models.types.experiment_type import ExperimentType


class PanelConfig:
    """
    Data class representing grafana panel configuration.
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
        return {'name': self.name, 'groups': [{'name': group.name} for group in self.experiment.groups]}
