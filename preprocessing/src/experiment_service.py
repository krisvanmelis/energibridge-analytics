"""
Module containing service with functionality for experiments.
"""
from typing import List, Optional

from models.experiment import Experiment
from models.types.experiment_type import ExperimentType
from models.types.measurement_type import MeasurementType
from group_service import GroupService


class ExperimentService:
    """
    Class containing functionality for experiments.
    """
    _group_service: GroupService
    _experiments: List[Experiment]

    def __init__(self, group_service: GroupService):
        self._group_service = group_service
        self._experiments = []

    def get_experiments(self) -> List[Experiment]:
        """
        Get list of all experiments.

        :return: List of experiments.
        """
        return self._experiments

    def find_experiment(self, experiment_name: str) -> Optional[Experiment]:
        """
        Find experiment by name.

        :param experiment_name: experiment name
        :return: Experiment or None if not found
        """
        for experiment in self._experiments:
            if experiment.name.lower() == experiment_name.lower():
                return experiment
        return None

    def add_experiment(self, experiment_name: str, group_names: List[str],
                  measurement_types: List[MeasurementType], experiment_type: ExperimentType):
        """
        Add an experiment configuration.

        :param experiment_name: The name of the experiment.
        :param group_names: The names of the groups in the experiment.
        :param measurement_types: The measurement types to analyze.
        :param experiment_type: The experiment type.
        :return: New list of experiments
        """
        groups = [self._group_service.find_group(name) for name in group_names]

        if self.find_experiment(experiment_name) is not None:
            raise ValueError(f'Experiment with name "{experiment_name}" already exists')

        new_experiment = Experiment(experiment_name, groups, experiment_type, measurement_types)
        self._experiments = self._experiments + [new_experiment]
        return self._experiments

    def delete_experiment(self, experiment_name: str) -> List[Experiment]:
        """
        Delete an experiment configuration.

        :param experiment_name: The name of the experiment.
        :return: The new list of experiment configurations.
        """
        if self.find_experiment(experiment_name) is None:
            raise ValueError(f'Experiment with name "{experiment_name}" does not exist')

        self._experiments = [exp for exp in self._experiments if exp.name.lower() != experiment_name.lower()]
        return self._experiments
