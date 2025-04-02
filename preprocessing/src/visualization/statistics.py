import os
import json
from typing import List, Dict, Any
from models.types.measurement_type import MeasurementType
from models.group import Group


class Statistics:
    """
    Class for generating significance test visualizations and statistical comparisons.
    """

    @staticmethod
    def generate_panels(experiment_name: str, groups: List[Group], measurement_types: List[MeasurementType],
                        y_pos: int = 0) -> List[Dict[str, Any]]:
        """
        Displays statistics of energy and power based on measurement types.
        For CPU_STATS, shows CPU-level panels.
        For CORE_STATS, shows per-core panels.

        :param experiment_name: Name of the experiment (used in dashboard title)
        :param groups: List of groups to visualize
        :param measurement_types: List of measurement types to visualize
        :param y_pos: Starting vertical position for panels
        :return: List of panel configurations
        """
        panels = []

        for measurement_type in measurement_types:
            if measurement_type == MeasurementType.CPU_STATS:
                for group in groups:
                    x_pos = 0

                    # Energy Panel
                    energy_col = "CPU_Total_Energy (J)"
                    energy_panel = Statistics._create_combined_stat_panel(
                        group.name, x_pos, y_pos, energy_col, "Energy")
                    y_pos += energy_panel["gridPos"]["h"]

                    # Energy Test Panel
                    energy_test_panel = Statistics._create_test_stat_panel(
                        group.name, x_pos, y_pos, energy_col, "Energy")
                    y_pos += energy_test_panel["gridPos"]["h"]

                    # Energy Image
                    energy_image_panel = Statistics._create_image_panel(
                        group.name, x_pos, y_pos, "CPU_Total_Energy_(J)_violin.png", "Energy")
                    y_pos += energy_image_panel["gridPos"]["h"]

                    # Power Panel
                    power_col = "CPU_Peak_Power (W)"
                    power_panel = Statistics._create_combined_stat_panel(
                        group.name, x_pos, y_pos, power_col, "Peak Power")
                    y_pos += power_panel["gridPos"]["h"]

                    # Power Test Panel
                    power_test_panel = Statistics._create_test_stat_panel(
                        group.name, x_pos, y_pos, power_col, "Peak Power")
                    y_pos += power_test_panel["gridPos"]["h"]

                    # Power Image
                    power_image_panel = Statistics._create_image_panel(
                        group.name, x_pos, y_pos, "CPU_Peak_Power_(W)_violin.png", "Peak Power")
                    y_pos += power_image_panel["gridPos"]["h"]

                    panels.extend([
                        energy_panel, energy_test_panel, energy_image_panel,
                        power_panel, power_test_panel, power_image_panel
                    ])

            elif measurement_type == MeasurementType.CORE_STATS:
                for group in groups:
                    for core_num in range(8):  # assuming 8 cores
                        x_pos = 0
                        core_label = f"CORE {core_num}"

                        # Energy
                        energy_col = f"CORE{core_num}_Total_Energy (J)"
                        energy_img = f"CORE{core_num}_Total_Energy_(J)_violin.png"

                        energy_panel = Statistics._create_combined_stat_panel(
                            group.name, x_pos, y_pos, energy_col, f"{core_label} Energy")
                        y_pos += energy_panel["gridPos"]["h"]

                        energy_test_panel = Statistics._create_test_stat_panel(
                            group.name, x_pos, y_pos, energy_col, f"{core_label} Energy")
                        y_pos += energy_test_panel["gridPos"]["h"]

                        energy_image_panel = Statistics._create_image_panel(
                            group.name, x_pos, y_pos, energy_img, f"{core_label} Energy")
                        y_pos += energy_image_panel["gridPos"]["h"]

                        # Peak Power
                        power_col = f"CORE{core_num}_Peak_Power (W)"
                        power_img = f"CORE{core_num}_Peak_Power_(W)_violin.png"

                        power_panel = Statistics._create_combined_stat_panel(
                            group.name, x_pos, y_pos, power_col, f"{core_label} Peak Power")
                        y_pos += power_panel["gridPos"]["h"]

                        power_test_panel = Statistics._create_test_stat_panel(
                            group.name, x_pos, y_pos, power_col, f"{core_label} Peak Power")
                        y_pos += power_test_panel["gridPos"]["h"]

                        power_image_panel = Statistics._create_image_panel(
                            group.name, x_pos, y_pos, power_img, f"{core_label} Peak Power")
                        y_pos += power_image_panel["gridPos"]["h"]

                        panels.extend([
                            energy_panel, energy_test_panel, energy_image_panel,
                            power_panel, power_test_panel, power_image_panel
                        ])

            else:
                continue

        return panels

    @staticmethod
    def _load_template_with_placeholders(template_name: str, placeholders: Dict[str, str]) -> Dict[str, Any]:
        with open("csv-data/grafana-templates/" + template_name, 'r') as file:
            template = file.read()
            for key, value in placeholders.items():
                template = template.replace("PLACEHOLDER_" + key, value)
            return json.loads(template)

    @staticmethod
    def _create_combined_stat_panel(group_name: str, x_pos: int, y_pos: int,
                                     base_column: str, title_suffix: str) -> Dict[str, Any]:
        """
        Creates a single Grafana stat panel showing all statistics for a given base column (e.g., energy or power).
        """
        panel = Statistics._load_template_with_placeholders("stat_panel_template.json", {
            "TITLE": f"{group_name} - CPU {title_suffix}",
            "GROUPNAME": group_name,
            "UNIT": "joule" if "Energy" in title_suffix else "watt"
        })

        panel["gridPos"]["x"] = x_pos
        panel["gridPos"]["y"] = y_pos
        panel["gridPos"]["w"] = 6
        panel["gridPos"]["h"] = 4

        stats = ["mean", "std", "median", "min", "max", "LQ", "UQ"]
        columns = [{
            "selector": f"{base_column}_{stat}",
            "text": stat.upper(),
            "type": "number"
        } for stat in stats]


        panel["targets"][0]["columns"] = columns
        panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{group_name}/group_summary.csv"
        panel["targets"][0]["source"] = "url"
        panel["targets"][0]["type"] = "csv"
        panel["transformations"] = []

        return panel

    @staticmethod
    def _create_test_stat_panel(group_name: str, x_pos: int, y_pos: int,
                                base_column: str, title_suffix: str) -> Dict[str, Any]:
        panel = Statistics._load_template_with_placeholders("stat_panel_template.json", {
            "TITLE": f"{group_name} - {title_suffix} p-value",
            "GROUPNAME": group_name,
            "UNIT": ""  # No unit at all
        })

        panel["gridPos"]["x"] = x_pos
        panel["gridPos"]["y"] = y_pos
        panel["gridPos"]["w"] = 6
        panel["gridPos"]["h"] = 4

        columns = [
            {
                "selector": f"{base_column}_p_value",
                "text": "P-VALUE",
                "type": "number"
            },
            {
                "selector": f"{base_column}_normally_distributed",
                "text": "normally distributed?",
                "type": "number"
            }
        ]

        panel["targets"][0]["columns"] = columns
        panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{group_name}/group_summary.csv"
        panel["targets"][0]["source"] = "url"
        panel["targets"][0]["type"] = "csv"
        panel["transformations"] = []

        return panel

    @staticmethod
    def _create_image_panel(group_name: str, x_pos: int, y_pos: int, image_filename: str, title_suffix: str) -> Dict[
        str, Any]:
        """
        Loads and customizes an image panel from the image_panel_template.json file.
        """
        with open("csv-data/grafana-templates/image_panel_template.json", "r") as f:
            template = json.load(f)

        # Replace title and positioning
        template["title"] = f"{group_name} - CPU {title_suffix} Image"
        template["gridPos"]["x"] = x_pos
        template["gridPos"]["y"] = y_pos

        # Replace placeholders in URLs
        for element in template["options"].get("elements", []):
            if "url" in element:
                element["url"] = element["url"].replace("PLACEHOLDER_GROUPNAME", group_name).replace(
                    "PLACEHOLDER_IMAGEFILENAME", image_filename)

        root_image = template["options"]["root"]["background"]["image"]
        root_image["fixed"] = root_image["fixed"].replace("PLACEHOLDER_GROUPNAME", group_name).replace(
            "PLACEHOLDER_IMAGEFILENAME", image_filename)

        return template