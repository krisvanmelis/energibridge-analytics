"""
Module containing functionality for Grafana dashboards.
"""
from typing import List

from models.panel_config import PanelConfig
from models.types.measurement_type import MeasurementType
from models.group import Group


def measurement_type_to_columns(measurement_type: MeasurementType) -> dict | [dict]:
    """
    Convert a measurement type enum to a grafana dashboard column defined as:
    # TODO: annotated enums need to be altered to get the right no. cores
    {
        "selector": str,
        "text": str,
        "type": str,
    }

    :param measurement_type: MeasurementType enum
    :return: Column description as dictionary
    """
    predefined_columns = {
        MeasurementType.SYSTEM_POWER: [{
            "selector": "SYSTEM_POWER (W)_median",
            "text": "SYSTEM_POWER (W)",
            "type": "number",
        }, {
            "selector": "SYSTEM_POWER (W)_LQ",
            "text": "SYSTEM_POWER_LQ (W)",
            "type": "number",
        }, {
            "selector": "SYSTEM_POWER (W)_UQ",
            "text": "SYSTEM_POWER_UQ (W)",
            "type": "number",
        }],
        MeasurementType.SYSTEM_ENERGY: [{
            "selector": "DIFF_SYSTEM_ENERGY (J)_median",
            "text": "SYSTEM_ENERGY (J)",
            "type": "number",
        }],
        MeasurementType.CPU_ENERGY: [{
            "selector": "DIFF_CPU_ENERGY (J)_median",
            "text": "CPU_ENERGY (J)",
            "type": "number",
        }],
        MeasurementType.CPU_POWER: [{
            "selector": "CPU_POWER (W)_median",
            "text": "CPU_POWER (W)",
            "type": "number",
        }, {
            "selector": "CPU_POWER (W)_LQ",
            "text": "CPU_POWER_LQ (W)",
            "type": "number",
        }, {
            "selector": "CPU_POWER (W)_UQ",
            "text": "CPU_POWER_UQ (W)",
            "type": "number",
        }],
        MeasurementType.POWER_PER_CORE: [{  # TODO: make this generate the right columns (varies per setup)
            "selector": "CORE0_POWER (W)_median",
            "text": "CORE0_POWER (W)",
            "type": "number",
        }],
        MeasurementType.ENERGY_PER_CORE: [{  # TODO: make this generate the right columns (varies per setup)
            "selector": "CORE0_ENERGY (J)_median",
            "text": "CORE0_ENERGY (J)",
            "type": "number",
        }],
        MeasurementType.VOLTAGE_PER_CORE: [{  # TODO: make this generate the right columns (varies per setup)
            "selector": "CORE0_VOLT (V)_median",
            "text": "CORE0_VOLT (V)",
            "type": "number",
        }],
        MeasurementType.FREQUENCIES: [{  # TODO: make this generate the right columns (varies per setup)
            "selector": "CPU_FREQUENCY_0_median",
            "text": "CPU_FREQUENCY_0",
            "type": "number",
        }, {  # TODO: make this generate the right columns (varies per setup)
            "selector": "CORE0_FREQUENCY_median",
            "text": "CORE0_FREQUENCY",
            "type": "number",
        }],
        MeasurementType.USAGES_PER_LOGICAL_PROCESSOR: [{  # TODO: make this generate the right columns (varies per setup)
            "selector": "CPU_USAGE_0_median",
            "text": "CPU_USAGE_0",
            "type": "number",
        }],
        MeasurementType.MEMORY: [{
            "selector": "TOTAL_MEMORY_median",
            "text": "TOTAL_MEMORY",
            "type": "number",
        }, {
            "selector": "TOTAL_SWAP_median",
            "text": "TOTAL_SWAP",
            "type": "number",
        }, {
            "selector": "USED_MEMORY_median",
            "text": "USED_MEMORY",
            "type": "number",
        }, {
            "selector": "USED_SWAP_median",
            "text": "USED_SWAP",
            "type": "number",
        }],
        MeasurementType.TEMPERATURE: [{  # TODO: make this generate the right columns (varies per setup)
            "selector": "CPU_TEMP_0_median",
            "text": "CPU_TEMP_0",
            "type": "number",
        }],
        MeasurementType.GPU_METRICS: [{  # TODO: make this generate the right columns (varies per setup)
            "selector": "GPU0_median",
            "text": "GPU0",
            "type": "number",
        }],
    }
    return predefined_columns[measurement_type]


def generate_target_from_group(group: Group, columns: List[dict]) -> dict:
    """
    Generate a target configuration from experiment group and columns.

    :param group: Target group
    :param columns: List of columns to include
    :return: Target configuration as dictionary
    """
    return {
        "columns": columns,
        "datasource": {
            "type": "yesoreyeram-infinity-datasource",
            "uid": "PEB6B42F54C42D283"
        },
        "filters": [],
        "format": "table",
        "global_query_id": "",
        "parser": "backend",
        "refId": group.name,
        "root_selector": "",
        "source": "url",
        "type": "csv",
        "url": f"http://nginx/{group.aggregate_data_path}",
        # TODO Single CSV containing aggregated group results
        "url_options": {
            "data": "",
            "method": "GET"
        }
    }


def generate_panel_from_config(config: PanelConfig) -> dict:
    """
    Generate a dashboard panel configuration based on visualization config.

    :param config: VisualizationConfig describing experiment and how it should be visualized.
    :return: Dashboard panel configuration as a dictionary.
    """
    columns = [
        {
            "selector": "Time",
            "text": "Time",
            "type": "timestamp_epoch",
        },
    ]
    columns = columns + [c for c in [measurement_type_to_columns(measurement_type)
                         for measurement_type in config.experiment.measurement_types]]
    targets = [generate_target_from_group(group, columns) for group in config.experiment.groups]

    return {
        "datasource": {
            "type": "yesoreyeram-infinity-datasource",
            "uid": "PEB6B42F54C42D283"
        },
        "fieldConfig": {
            "defaults": {
                "color": {
                    "mode": "palette-classic"
                },
                "custom": {
                    "axisBorderShow": False,
                    "axisCenteredZero": False,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                        "legend": False,
                        "tooltip": False,
                        "viz": False
                    },
                    "insertNulls": False,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                        "type": "linear"
                    },
                    "showPoints": "always",
                    "spanNulls": False,
                    "stacking": {
                        "group": "A",
                        "mode": "none"
                    },
                    "thresholdsStyle": {
                        "mode": "off"
                    }
                },
                "decimals": 2,
                "fieldMinMax": False,
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {
                            "color": "green",
                            "value": None
                        }
                    ]
                },
                "unit": "joule"
            },
            "overrides": []
        },
        "gridPos": {
            "h": 9,
            "w": 24,
            "x": 0,
            "y": 0
        },
        "id": 1,
        "options": {
            "legend": {
                "calcs": [],
                "displayMode": "list",
                "placement": "bottom",
                "showLegend": True
            },
            "tooltip": {
                "hideZeros": False,
                "mode": "single",
                "sort": "none"
            }
        },
        "pluginVersion": "11.5.2",
        "targets": targets,
        "title": config.name,
        "type": "timeseries"  # TODO support for non time series?
    }


def generate_dashboard(configs: List[PanelConfig]) -> dict:
    """
    Generate a Grafana dashboard configuration as a dictionary based on visualization configurations.

    :param configs: List of visualization configurations.
    :return: Grafana dashboard configuration as a dictionary.
    """
    panels = [generate_panel_from_config(config) for config in configs]

    return {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": {
                        "type": "grafana",
                        "uid": "-- Grafana --"
                    },
                    "enable": True,
                    "hide": True,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "type": "dashboard"
                }
            ]
        },
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 1,
        "id": 1,
        "links": [],
        "panels": panels,
        "preload": True,
        "refresh": "5s",
        "schemaVersion": 40,
        "tags": [],
        "templating": {
            "list": []
        },
        "time": {
            "from": "2025-02-25T23:07:27.503Z",
            "to": "2025-02-25T23:07:58.558Z"
        },
        "timepicker": {
            "refresh_intervals": []
        },
        "timezone": "browser",
        "title": "Energibridge Dashboard",
        "uid": "cLV5GDCkz",
        "version": 1,
        "weekStart": ""
    }
