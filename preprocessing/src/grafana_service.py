"""
Service for generating and managing Grafana dashboard configurations.
"""
import json
import os
from typing import List, Dict, Any

from models.experiment import Experiment

class GrafanaService:
    """
    Service that handles Grafana dashboard generation and configuration management.
    Collects panels from experiments and composes them into a complete dashboard.
    """
    _dashboard_config_save_path: str

    def __init__(self, dashboard_config_save_path: str):
        """
        Initialize the Grafana service with specified configuration path.

        :param dashboard_config_save_path: File path where to save the generated dashboard JSON.
        """
        self._dashboard_config_save_path = dashboard_config_save_path

    def create_dashboard_from_experiments(self, experiments: List[Experiment]) -> None:
        """
        Generate a complete dashboard from multiple experiments and save it.
        Collects all panels from experiments and arranges them in the dashboard.

        :param experiments: List of experiments to include in the dashboard.
        """
        panels = []
        
        # Collect panels from each experiment
        for experiment in experiments:
            experiment_panels = experiment.create_visualization_panels()
            if experiment_panels:
                panels.extend(experiment_panels)
                
        # Generate the dashboard with all panels
        grafana_config = self._generate_dashboard_config(panels)

        # Save the configuration to file
        self._save_dashboard_config(grafana_config)
        
    def _save_dashboard_config(self, config: Dict[str, Any]) -> None:
        """
        Save the dashboard configuration to the specified file path.
        
        :param config: The dashboard configuration as a dictionary.
        """
        with open(self._dashboard_config_save_path, 'w') as json_file:
            json.dump(config, json_file, indent=4)

        print(f'Grafana dashboard configuration saved to: {self._dashboard_config_save_path}')
    
    def _load_template_with_placeholders(self, template_name: str, placeholders: Dict[str, str]) -> Dict[str, Any]:
        """
        Load a template file and replace placeholders with actual values.
        
        :param template_name: Name of the template file to load.
        :param placeholders: Dictionary of placeholder replacements.
        :return: Parsed JSON with placeholders replaced.
        """
        with open("csv-data/grafana-templates/" + template_name, 'r') as file:
            template = file.read()
            for key, value in placeholders.items():
                template = template.replace("PLACEHOLDER_" + key, value)
            return json.loads(template)

    def _generate_dashboard_config(self, panels: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a complete Grafana dashboard configuration with the provided panels.

        :param panels: List of panel configurations to include.
        :return: Complete dashboard configuration.
        """
        return self._load_template_with_placeholders("dashboard_template.json", {"PANELS": json.dumps(panels)})
