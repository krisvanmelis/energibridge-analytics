"""
Service for generating and managing Grafana dashboard configurations.
"""
import json
import os
from typing import List, Dict, Any

from models.experiment import Experiment

class GrafanaService:
    """
    Service class for managing Grafana dashboard configurations.
    """

    def __init__(self, dashboard_config_path: str = 'grafana/dashboards'):
        """
        Initialize GrafanaService with path to save dashboard configs.
        
        :param dashboard_config_path: Path where to save dashboard configuration files
        """
        self.dashboard_path = dashboard_config_path
        # Ensure the dashboards directory exists
        os.makedirs(os.path.dirname(dashboard_config_path), exist_ok=True)

    def create_dashboard_from_experiments(self, experiments: List[Experiment]) -> None:
        """
        Create a separate dashboard for each experiment.
        
        :param experiments: List of experiments to visualize
        """
        for experiment in experiments:
            self._create_single_experiment_dashboard(experiment)

    def _create_single_experiment_dashboard(self, experiment: Experiment) -> None:
        """
        Create a dashboard for a single experiment.
        
        :param experiment: Experiment to visualize
        """
        # Get panels for this experiment
        panels = experiment.create_visualization_panels()
        
        # Load dashboard template
        with open("/app/csv-data/grafana-templates/dashboard_template.json", 'r') as file:
            dashboard_template = json.load(file)
        
        # Insert panels and update dashboard title
        dashboard_template["panels"] = panels
        dashboard_template["title"] = f"Energibridge - {experiment.name}"
        
        # Generate a unique UID for the dashboard based on experiment name
        sanitized_name = experiment.name.lower().replace(' ', '_').replace('-', '_')
        dashboard_template["uid"] = f"eb_{sanitized_name}"
        
        # Save dashboard configuration
        sanitized_filename = sanitized_name.replace(' ', '_').replace('/', '_')
        save_path = os.path.join(os.path.dirname(self.dashboard_path), f"{sanitized_filename}.json")
        
        with open(save_path, 'w') as file:
            json.dump(dashboard_template, file, indent=2)
        
        print(f"Dashboard for experiment '{experiment.name}' saved to {save_path}")
