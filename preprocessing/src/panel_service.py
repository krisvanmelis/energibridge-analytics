"""
Module containing service with functionality for Grafana panels.
"""
from typing import List, Optional

from models.panel_config import PanelConfig
from models.types.experiment_type import ExperimentType
from models.types.measurement_type import MeasurementType
from group_service import GroupService


class PanelService:
    """
    Class containing functionality for Grafana panels.
    """
    _group_service: GroupService
    _panel_configs: List[PanelConfig]

    def __init__(self, group_service: GroupService):
        self._group_service = group_service
        self._panel_configs = []

    def get_panels(self) -> List[PanelConfig]:
        """
        Get list of all panel configurations.

        :return: List of panel configurations.
        """
        return self._panel_configs

    def find_panel(self, panel_name: str) -> Optional[PanelConfig]:
        """
        Find panel by name.

        :param panel_name: panel name
        :return: Panel or None if not found
        """
        for config in self._panel_configs:
            if config.name.lower() == panel_name.lower():
                return config
        return None

    def add_panel(self, panel_name: str, group_names: List[str],
                  measurement_types: List[MeasurementType], experiment_type: ExperimentType):
        """
        Add a grafana panel configuration.

        :param panel_name: The name of the panel.
        :param group_names: The names of the panel groups.
        :param measurement_types: The measurement types of the panel groups.
        :param experiment_type: The experiment type of the panel groups.
        :return: New list of panels
        """
        groups = [self._group_service.find_group(name) for name in group_names]

        if self.find_panel(panel_name) is not None:
            raise ValueError(f'Panel with name "{panel_name}" already exists')

        new_config = PanelConfig(panel_name, groups, measurement_types, experiment_type)
        self._panel_configs = self._panel_configs + [new_config]
        return self._panel_configs

    def delete_panel(self, panel_name: str) -> List[PanelConfig]:
        """
        Delete a grafana panel configuration.

        :param panel_name: The name of the panel.
        :return: The new list of panel configurations.
        """
        if self.find_panel(panel_name) is None:
            raise ValueError(f'Panel with name "{panel_name}" does not exist')

        self._panel_configs = [config for config in self._panel_configs if config.name.lower() != panel_name.lower()]
        return self._panel_configs
