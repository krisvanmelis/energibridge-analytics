import pandas as pd
import json
import re
from typing import List, Dict, Any
from models.group import Group
from models.types.experiment_type import ExperimentType
from models.types.measurement_type import MeasurementType


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
        Generate all visualization panels for this experiment based on measurement types.
        Ensures data is preprocessed, analyzed and then creates appropriate panels.
        
        :return: List of panel configurations for Grafana dashboard.
        """
        # # Ensure data is preprocessed for each group
        # for group in self.groups:
        #     group.aggregate(self.measurement_types)
        #     group.summarize(self.measurement_types)
        
        self.analyze()
        
        # Generate panels for each measurement type
        panels = []
        y_pos = 0
        
        for measurement_type in self.measurement_types:
            # Skip ALL type as it's too broad for visualization
            if measurement_type == MeasurementType.ALL:
                continue
            
            # For energy measurements, add stat panels with detailed statistics
            if "ENERGY" in str(measurement_type):
                for group in self.groups:
                    stat_panels = self._create_energy_stat_panels(measurement_type, group.name, y_pos)
                    panels.extend(stat_panels)
                    y_pos += 4  # Stat panels are smaller
            
            # Use specialized panel generators based on measurement type
            elif measurement_type in [MeasurementType.CORE_POWER, MeasurementType.CORE_VOLTAGE, 
                                    MeasurementType.CORE_FREQUENCY, MeasurementType.CORE_PSTATE]:
                for group in self.groups:
                    panel = self._create_per_core_panel(measurement_type, group, y_pos)
                    if panel:
                        panels.append(panel)
                        y_pos += 9
            # For regular measurements
            else:
                for group in self.groups:
                    panel = self._create_standard_panel(measurement_type, group.name, y_pos)
                    panels.append(panel)
                    y_pos += 9
            
        return panels

    def _create_energy_stat_panels(self, measurement_type: MeasurementType, group_name: str, y_pos: int) -> List[Dict[str, Any]]:
        """
        Generate stat panels for energy measurements, showing individual statistics.
        
        :param measurement_type: The energy measurement type.
        :param group_name: Name of the group to visualize.
        :param y_pos: Vertical position on the dashboard.
        :return: List of stat panel configurations.
        """
        panels = []
        stats = ["mean", "median", "min", "max", "LQ", "UQ", "std"]
        
        # For core energy, create a separate row of panels for each core
        if measurement_type == MeasurementType.CORE_ENERGY:
            # We'll create a row of panels for each core statistic
            core_count = 8
            for i in range(core_count):
                x_pos = 0
                for stat in stats:
                    column_name = measurement_type.get_full_column_name(core_num=i, statistic=stat)
                    title = f"Core {i} Energy {stat.upper()}"
                    
                    panel = self._load_template_with_placeholders("stat_panel_template.json", {
                        "TITLE": title,
                        "GROUPNAME": group_name
                    })
                    
                    # Set panel position
                    panel["gridPos"]["x"] = x_pos
                    panel["gridPos"]["y"] = y_pos
                    
                    # Configure column to display
                    panel["targets"][0]["columns"] = [{
                        "selector": column_name,
                        "text": title,
                        "type": "number"
                    }]
                    
                    # Add unit configuration
                    if stat == "std":
                        panel["fieldConfig"]["defaults"]["unit"] = "joule"
                        panel["title"] = f"Core {i} Energy StdDev"
                    
                    panels.append(panel)
                    x_pos += 4  # Move to the next position in the row
                
                y_pos += 4  # Move to the next row for the next core
        else:
            # For other energy metrics like CPU_ENERGY, create a row of panels for each statistic
            x_pos = 0
            for stat in stats:
                column_name = measurement_type.get_full_column_name(statistic=stat)
                title = f"{str(measurement_type)} {stat.upper()}"
                
                panel = self._load_template_with_placeholders("stat_panel_template.json", {
                    "TITLE": title,
                    "GROUPNAME": group_name
                })
                
                # Set panel position
                panel["gridPos"]["x"] = x_pos
                panel["gridPos"]["y"] = y_pos
                
                # Configure column to display
                panel["targets"][0]["columns"] = [{
                    "selector": column_name,
                    "text": title,
                    "type": "number"
                }]
                
                # Add unit configuration
                if stat == "std":
                    panel["fieldConfig"]["defaults"]["unit"] = "joule"
                    panel["title"] = f"{str(measurement_type)} StdDev"
                
                panels.append(panel)
                x_pos += 4  # Move to the next position in the row
        
        return panels

    def _create_per_core_panel(self, measurement_type: MeasurementType, group: Group, y_pos: int) -> Dict[str, Any]:
        """
        Generate a panel specifically for per-core measurements, showing data for all cores.
        
        :param measurement_type: The core measurement type (energy, power, voltage, etc.).
        :param group: The group whose data will be visualized.
        :param y_pos: Vertical position on the dashboard.
        :return: Panel configuration dictionary for Grafana.
        """
        # Extract the metric name and base column pattern from the measurement type
        metric_name = str(measurement_type).replace("CORE_", "")
        base_column_pattern = measurement_type.get_column_name
        
        # Get base panel from template
        panel = self._load_template_with_placeholders("panel_template.json", {
            "MEASUREMENTTYPE": str(measurement_type),
            "GROUPNAME": group.name
        })
        
        # Customize panel title and position
        panel["title"] = f"{self.name}: {group.name} - Per Core {metric_name}"
        panel["gridPos"]["y"] = y_pos
        
        # Ensure targets array exists
        if "targets" not in panel:
            panel["targets"] = [{"columns": []}]
        elif len(panel["targets"]) == 0:
            panel["targets"] = [{"columns": []}]
        
        # Configure columns for visualization
        columns = []
        # Always include time column with correct format
        columns.append({
            "selector": "Time",
            "text": "Time (s)",
            "type": "timestamp_epoch",
            "format": "unixtimestampms"
        })
            
        # Add columns for each core
        core_count = 8  # Based on provided CSV header
        for i in range(core_count):
            col_name = measurement_type.get_full_column_name(core_num=i, statistic="median")
            columns.append({
                "selector": col_name,
                "text": f"Core {i}",
                "type": "number"
            })
        
        # Update the target columns in the panel and ensure URL is set
        panel["targets"][0]["columns"] = columns
        panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{group.name}/aggregate_data.csv"
        panel["targets"][0]["source"] = "url"
        panel["targets"][0]["type"] = "csv"
        
        return panel
    
    def _create_standard_panel(self, measurement_type: MeasurementType, group_name: str, y_pos: int) -> Dict[str, Any]:
        """
        Generate a standard panel for non-core measurements.
        For power measurements (CPU_POWER and SYSTEM_POWER), also includes quartile data.
        
        :param measurement_type: The measurement type.
        :param group_name: Name of the group to visualize.
        :param y_pos: Vertical position on the dashboard.
        :return: Panel configuration dictionary for Grafana.
        """
        # Get panel from template
        panel = self._load_template_with_placeholders("panel_template.json", {
            "MEASUREMENTTYPE": str(measurement_type),
            "GROUPNAME": group_name
        })
        
        # Set descriptive panel title and position
        panel["title"] = f"{self.name}: {group_name} - {str(measurement_type)}"
        panel["gridPos"]["y"] = y_pos
        
        # Ensure targets array exists
        if "targets" not in panel:
            panel["targets"] = [{"columns": []}]
        elif len(panel["targets"]) == 0:
            panel["targets"] = [{"columns": []}]
        
        # If this is a power measurement type, include quartiles
        if measurement_type in [MeasurementType.CPU_POWER, MeasurementType.SYSTEM_POWER]:
            # Create a list of columns with median, LQ and UQ for power data visualization
            columns = []
            # Add time column with correct format
            columns.append({
                "selector": "Time",
                "text": "Time (s)",
                "type": "timestamp_epoch",
                "format": "unixtimestampms"
            })

            
            # Add median value
            median_col = measurement_type.get_full_column_name(statistic="median")
            columns.append({
                "selector": median_col,
                "text": f"{str(measurement_type)} (Median)",
                "type": "number"
            })
            
            # Add lower quartile
            lq_col = measurement_type.get_full_column_name(statistic="LQ")
            columns.append({
                "selector": lq_col,
                "text": f"{str(measurement_type)} (Lower Quartile)",
                "type": "number"
            })
            
            # Add upper quartile
            uq_col = measurement_type.get_full_column_name(statistic="UQ")
            columns.append({
                "selector": uq_col,
                "text": f"{str(measurement_type)} (Upper Quartile)",
                "type": "number"
            })
            
            # Update the target columns in the panel
            panel["targets"][0]["columns"] = columns
            
            # Make sure URL is properly set
            panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{group_name}/aggregate_data.csv"
            panel["targets"][0]["source"] = "url"
            panel["targets"][0]["type"] = "csv"
                
            # Add a special tooltip to explain the quartiles
            if "options" not in panel:
                panel["options"] = {}
            if "tooltip" not in panel["options"]:
                panel["options"]["tooltip"] = {}
            
            panel["options"]["tooltip"]["mode"] = "multi"
            panel["options"]["tooltip"]["sort"] = "none"
            
            # Configure area fill between quartiles
            if "fieldConfig" not in panel:
                panel["fieldConfig"] = {"defaults": {}, "overrides": []}
            
            # Add special field configurations for quartile fields
            panel["fieldConfig"]["overrides"] = panel["fieldConfig"].get("overrides", [])
            
            # Add new override for lower quartile
            panel["fieldConfig"]["overrides"].append({
                "matcher": {
                    "id": "byName",
                    "options": f"{str(measurement_type)} (Lower Quartile)"
                },
                "properties": [
                    {
                        "id": "custom.fillBelowTo",
                        "value": f"{str(measurement_type)} (Upper Quartile)"
                    },
                    {
                        "id": "custom.lineStyle",
                        "value": {
                            "fill": "dash",
                            "dash": [3, 3]
                        }
                    },
                    {
                        "id": "color",
                        "value": {
                            "fixedColor": "rgba(77, 112, 255, 0.4)",
                            "mode": "fixed"
                        }
                    }
                ]
            })
            
            # Add override for upper quartile
            panel["fieldConfig"]["overrides"].append({
                "matcher": {
                    "id": "byName",
                    "options": f"{str(measurement_type)} (Upper Quartile)"
                },
                "properties": [
                    {
                        "id": "custom.lineStyle",
                        "value": {
                            "fill": "dash",
                            "dash": [3, 3]
                        }
                    },
                    {
                        "id": "color",
                        "value": {
                            "fixedColor": "rgba(77, 112, 255, 0.4)",
                            "mode": "fixed"
                        }
                    }
                ]
            })

        # If this is a logical processor measurement type that needs a core number
        elif measurement_type in [MeasurementType.CPU_FREQUENCY_LOGICAL, MeasurementType.CPU_USAGE_LOGICAL]:
            # Create a list of columns for each logical processor
            columns = []
            # Add time column with correct format
            columns.append({
                "selector": "Time",
                "text": "Time",
                "type": "timestamp_epoch",
                "format": "unixtimestampms"
            })
            columns.append({
                "selector": "Time (s)",
                "text": "Time (s)",
                "type": "number"
            })
            
            # Add columns for each logical processor
            processor_count = 16  # Based on typical hyperthreaded 8-core CPU
            for i in range(processor_count):
                col_name = measurement_type.get_full_column_name(core_num=i, statistic="median")
                columns.append({
                    "selector": col_name,
                    "text": f"LP {i}",
                    "type": "number"
                })
            
            # Update the target columns in the panel
            panel["targets"][0]["columns"] = columns
            panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{group_name}/aggregate_data.csv"
            panel["targets"][0]["source"] = "url"
            panel["targets"][0]["type"] = "csv"
        
        # For other standard measurement types
        else:
            # Standard columns setup with median only
            columns = []
            # Add time column with correct format
            columns.append({
                "selector": "Time",
                "text": "Time",
                "type": "timestamp_epoch",
                "format": "unixtimestampms"
            })
            columns.append({
                "selector": "Time (s)",
                "text": "Time (s)",
                "type": "number"
            })
            
            # Add median value
            median_col = measurement_type.get_full_column_name(statistic="median")
            columns.append({
                "selector": median_col,
                "text": str(measurement_type),
                "type": "number"
            })
            
            # Update the target columns in the panel
            panel["targets"][0]["columns"] = columns
            panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{group_name}/aggregate_data.csv"
            panel["targets"][0]["source"] = "url"
            panel["targets"][0]["type"] = "csv"
        
        return panel

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


