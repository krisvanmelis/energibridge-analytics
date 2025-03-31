from typing import List
import json

from models.group import Group
from models.panel_config import PanelConfig
from models.types.measurement_type import MeasurementType

# Loads json template and replaces placeholders with actual values
def load_json_template(name: str, placeholders: dict) -> dict:
    with open("csv-data/grafana-templates/" + name, 'r') as file:
        template = file.read()
        for key, value in placeholders.items():
            template = template.replace("PLACEHOLDER_" + key, value)

        print(template)
        return json.loads(template)

def generate_dashboard(panel_configs: List[PanelConfig]) -> dict:
    """
    Generate a Grafana dashboard configuration as a dictionary based on visualization configurations.

    :param configs: List of visualization configurations.
    :return: Grafana dashboard configuration as a dictionary.
    """
    panels = []
    for panel_config in panel_configs:
        panels.append(generate_grafana_panel(panel_config))

    return load_json_template("dashboard_template.json", {"PANELS": json.dumps(panels)})

def generate_grafana_panel(panel_config):
    return load_json_template("panel_template.json", {});