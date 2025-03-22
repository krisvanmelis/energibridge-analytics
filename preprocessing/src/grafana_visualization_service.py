"""
Module containing a service with functionality for grafana visualizations.
"""
import json
import os
from typing import List

from dashboards import generate_dashboard
from models.panel_config import PanelConfig


class GrafanaVisualizationService:
    """
    Service which allows to configure grafana visualizations.
    """
    _dashboard_config_save_path: str  # Grafana configuration json file will be saved here

    def __init__(self, dashboard_config_save_path: str):
        """
        Constructor for visualization service.

        :param dashboard_config_save_path: Path where grafana dashboard configuration file will be saved.
        """
        self._dashboard_config_save_path = dashboard_config_save_path

    def configure(self, panel_configs: List[PanelConfig]) -> None:
        """
        Configure grafana dashboard by generating dashboard config json and saving to specified path.

        :param panel_configs: List of grafana panel configurations.
        """
        grafana_config = generate_dashboard(panel_configs)
        dir_name = os.path.dirname(self._dashboard_config_save_path)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(self._dashboard_config_save_path, 'w') as json_file:
            json.dump(grafana_config, json_file, indent=4)
