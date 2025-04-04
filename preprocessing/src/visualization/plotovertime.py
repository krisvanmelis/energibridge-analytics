import json
from typing import List, Dict, Any
from models.types.measurement_type import MeasurementType
from models.group import Group


class PlotOverTime:
    """
    Class for generating time-series visualizations of measurement data.
    """
    
    @staticmethod
    def generate_panels(experiment_name: str, groups: List[Group], measurement_types: List[MeasurementType], y_pos: int = 0) -> List[Dict[str, Any]]:
        """
        Generate visualization panels for plot over time experiment type.
        
        :param experiment_name: Name of the experiment
        :param groups: List of groups to visualize
        :param measurement_types: List of measurement types to visualize
        :param y_pos: Starting vertical position for panels
        :return: List of panel configurations
        """
        panels = []
        
        for measurement_type in measurement_types:
            # Skip ALL type as it's too broad for visualization
            if measurement_type == MeasurementType.ALL:
                continue
            panels.append(PlotOverTime._create_row_panel(measurement_type.name.replace("_", " "), y_pos))
            y_pos += 1

            # For energy measurements, add stat panels with detailed statistics
            if "ENERGY" in str(measurement_type):
                for group in groups:
                    stat_panels = PlotOverTime._create_energy_stat_panels(
                        measurement_type, group.name, y_pos)
                    panels.extend(stat_panels)
                    y_pos += 4  # Stat panels are smaller
            
            # Use specialized panel generators based on measurement type
            elif measurement_type in [MeasurementType.CORE_POWER, MeasurementType.CORE_VOLTAGE]:
                for group in groups:
                    panel = PlotOverTime._create_per_core_panel(
                        measurement_type, group, y_pos)
                    if panel:
                        panels.append(panel)
                        y_pos += panel["gridPos"]["h"]
            # For regular measurements
            else:
                for group in groups:
                    panel = PlotOverTime._create_standard_panel(
                        measurement_type, group.name, y_pos)
                    panels.append(panel)
                    y_pos += panel["gridPos"]["h"]

            # spacing - 2 graphs per line
            x_pos = 0
            for panel in panels:
                # Set the x position for each panel
                panel["gridPos"]["x"] = x_pos
                x_pos += panel["gridPos"]["w"]
                if x_pos >= 24:  # Reset x position if it exceeds the grid width
                    x_pos = 0
                    y_pos += panel["gridPos"]["h"]
                    
        return panels

    @staticmethod
    def _load_template_with_placeholders(template_name: str, placeholders: Dict[str, str]) -> Dict[str, Any]:
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
    
    @staticmethod
    def _create_energy_stat_panels(measurement_type: MeasurementType, 
                                   group_name: str, y_pos: int) -> List[Dict[str, Any]]:
        """
        Generate stat panels for energy measurements, showing individual statistics.
        
        :param measurement_type: The energy measurement type
        :param group_name: Name of the group to visualize
        :param y_pos: Vertical position on the dashboard
        :return: List of stat panel configurations
        """
        panels = []
        stats = ["mean", "median", "min", "max", "LQ", "UQ", "std"]
        
        # For other energy metrics like CPU_ENERGY, create a row of panels for each statistic
        x_pos = 0
        for stat in stats:
            column_name = measurement_type.get_full_column_name(statistic=stat)
            title = f"{str(measurement_type)} {stat.upper()}"
            
            panel = PlotOverTime._load_template_with_placeholders("stat_panel_template.json", {
                "TITLE": title,
                "GROUPNAME": group_name,
                "UNIT": measurement_type.unit or "joule"
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
            
            if stat == "std":
                panel["title"] = f"{str(measurement_type)} StdDev"
            
            panels.append(panel)
            x_pos += 4  # Move to the next position in the row
        
        return panels

    @staticmethod
    def _create_per_core_panel(measurement_type: MeasurementType, 
                               group: Group, y_pos: int, x_pos: int = 0) -> Dict[str, Any]:
        """
        Generate a panel specifically for per-core measurements, showing data for all cores.
        
        :param measurement_type: The core measurement type (energy, power, voltage, etc.)
        :param group: The group whose data will be visualized
        :param y_pos: Vertical position on the dashboard
        :return: Panel configuration dictionary for Grafana
        """
        # Extract the metric name and base column pattern from the measurement type
        metric_name = str(measurement_type).replace("CORE_", "")
        
        # Get base panel from template
        panel = PlotOverTime._load_template_with_placeholders("panel_template.json", {
            "MEASUREMENTTYPE": str(measurement_type),
            "GROUPNAME": group.name
        })
        
        # Customize panel title and position - removing experiment name
        panel["title"] = f"{group.name} - Per Core {metric_name}"
        panel["gridPos"]["y"] = y_pos

        
        # Apply unit to the panel
        if measurement_type.unit:
            panel["fieldConfig"]["defaults"]["unit"] = measurement_type.unit
        
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
    
    @staticmethod
    def _create_standard_panel(measurement_type: MeasurementType, 
                              group_name: str, y_pos: int) -> Dict[str, Any]:
        """
        Generate a standard panel for non-core measurements.
        For power measurements (CPU_POWER), also includes quartile data.
        
        :param measurement_type: The measurement type
        :param group_name: Name of the group to visualize
        :param y_pos: Vertical position on the dashboard
        :return: Panel configuration dictionary for Grafana
        """
        # Get panel from template
        panel = PlotOverTime._load_template_with_placeholders("panel_template.json", {
            "MEASUREMENTTYPE": str(measurement_type),
            "GROUPNAME": group_name
        })
        
        # Set descriptive panel title and position - removing experiment name
        panel["title"] = f"{group_name} - {str(measurement_type)}"
        panel["gridPos"]["y"] = y_pos
        
        # Apply unit to the panel
        if measurement_type.unit:
            panel["fieldConfig"]["defaults"]["unit"] = measurement_type.unit
        
        # Ensure targets array exists
        if "targets" not in panel:
            panel["targets"] = [{"columns": []}]
        elif len(panel["targets"]) == 0:
            panel["targets"] = [{"columns": []}]
        
        # If this is a power measurement type, include quartiles
        if measurement_type in [MeasurementType.CPU_POWER]:
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
            
            # Add special field configurations for quartile fields with fixed overrides
            measurement_name = str(measurement_type)
            panel["fieldConfig"]["overrides"] = [
                {
                    "matcher": {
                        "id": "byName",
                        "options": f"{measurement_name} (Upper Quartile)"
                    },
                    "properties": [
                        {
                            "id": "custom.fillBelowTo",
                            "value": f"{measurement_name} (Lower Quartile)"
                        },
                        {
                            "id": "custom.lineStyle",
                            "value": {
                                "dash": [3, 3],
                                "fill": "dash"
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
                },
                {
                    "matcher": {
                        "id": "byName",
                        "options": f"{measurement_name} (Lower Quartile)"
                    },
                    "properties": [
                        {
                            "id": "custom.lineStyle",
                            "value": {
                                "dash": [3, 3],
                                "fill": "dash"
                            }
                        },
                        {
                            "id": "color",
                            "value": {
                                "fixedColor": "rgba(77, 112, 255, 0.4)",
                                "mode": "fixed"
                            }
                        },
                        {
                            "id": "custom.fillBelowTo",
                            "value": f"{measurement_name} (Lower Quartile)"
                        }
                    ]
                },
                {
                    "matcher": {
                        "id": "byName",
                        "options": f"{measurement_name} (Median)"
                    },
                    "properties": [
                        {
                            "id": "custom.fillOpacity",
                            "value": 0
                        }
                    ]
                }
            ]

        # If this is a logical processor measurement type that needs a core number
        elif measurement_type in [MeasurementType.CPU_USAGE_LOGICAL]:
            # Create a list of columns for each logical processor
            columns = []
            # Add time column with correct format
            columns.append({
                "selector": "Time",
                "text": "Time (s)",
                "type": "timestamp_epoch",
                "format": "unixtimestampms"
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
                "text": "Time (s)",
                "type": "timestamp_epoch",
                "format": "unixtimestampms"
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

    @staticmethod
    def _create_row_panel(title: str, y_pos: int, panels: list = []) -> Dict[str, Any]:
        with open("csv-data/grafana-templates/row_panel_template.json", "r") as f:
            template = json.load(f)
        template["title"] = title
        template["gridPos"]["y"] = y_pos
        template["panels"] = panels
        return template
