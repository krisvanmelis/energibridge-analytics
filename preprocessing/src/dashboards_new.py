from dataclasses import dataclass
from typing import List

from models.group import Group
from models.panel_config import PanelConfig
from models.types.measurement_type import MeasurementType


@dataclass
class PrimaryColumn:
    """
    A primary column will result in a single panel
    """
    selector: str
    text: str
    unit: str
    type: str
    quantiles: bool

    def to_cols_dicts(self):
        cols = [
            {
                "selector": "Time",
                "text": "Time",  # TODO add unit
                "type": "number",
            },
            {
                "selector": self.selector,
                "text": self.text + f" ({self.unit})",
                "type": self.type,
            }
        ]

        if self.quantiles:
            cols.append({
                "selector": self.selector.replace("median", "LQ"),
                "text": self.text + " LQ",
                "type": self.type,
            })
            cols.append({
                "selector": self.selector.replace("median", "UQ"),
                "text": self.text + " UQ",
                "type": self.type,
            })

        return cols

    def to_targets(self, group: Group):
        cols = self.to_cols_dicts()
        targets = [
            {
                "columns": cols[:2],
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
                "url_options": {
                    "data": "",
                    "method": "GET"
                }
            }
        ]
        if self.quantiles:
            lq_target = {
                "columns": [cols[0], cols[2]],
                "datasource": {
                    "type": "yesoreyeram-infinity-datasource",
                    "uid": "PEB6B42F54C42D283"
                },
                "filters": [],
                "format": "table",
                "global_query_id": "",
                "parser": "backend",
                "refId": group.name + "_lq",
                "root_selector": "",
                "source": "url",
                "type": "csv",
                "url": f"http://nginx/{group.aggregate_data_path}",
                "url_options": {
                    "data": "",
                    "method": "GET"
                }
            }
            uq_target = {
                "columns": [cols[0], cols[3]],
                "datasource": {
                    "type": "yesoreyeram-infinity-datasource",
                    "uid": "PEB6B42F54C42D283"
                },
                "filters": [],
                "format": "table",
                "global_query_id": "",
                "parser": "backend",
                "refId": group.name + "_uq",
                "root_selector": "",
                "source": "url",
                "type": "csv",
                "url": f"http://nginx/{group.aggregate_data_path}",
                "url_options": {
                    "data": "",
                    "method": "GET"
                }
            }
            targets.append(lq_target)
            targets.append(uq_target)
        return targets

# Predefined primary columns
SYSTEM_POWER_COLUMN = PrimaryColumn("SYSTEM_POWER (W)_median", "SYSTEM_POWER", "W", "number", True)
SYSTEM_ENERGY_COLUMN = PrimaryColumn("DIFF_SYSTEM_ENERGY (J)_median", "SYSTEM_ENERGY", "J", "number", True)
CPU_ENERGY_COLUMN = PrimaryColumn("DIFF_CPU_ENERGY (J)_median", "CPU_ENERGY", "J", "number", True)
CPU_POWER_COLUMN = PrimaryColumn("CPU_POWER (W)_median", "CPU_POWER", "W", "number", True)
TOTAL_MEMORY_COLUMN = PrimaryColumn("TOTAL_MEMORY_median", "TOTAL_MEMORY", "GB", "number", True)

def measurement_type_to_panel(config: PanelConfig, measurement_type: MeasurementType, groups: List[Group]) -> dict:
    targets = []
    predefined_columns = {
        MeasurementType.SYSTEM_POWER: SYSTEM_POWER_COLUMN,
        MeasurementType.SYSTEM_ENERGY: SYSTEM_ENERGY_COLUMN,
        MeasurementType.CPU_ENERGY: CPU_ENERGY_COLUMN,
        MeasurementType.CPU_POWER: CPU_POWER_COLUMN,
        MeasurementType.MEMORY: TOTAL_MEMORY_COLUMN,
    }
    for group in groups:
        for target in predefined_columns[measurement_type].to_targets(group):
            targets.append(target)

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
            "type": "trend"
        }

def generate_panels_from_config(config: PanelConfig) -> List[dict]:
    return [measurement_type_to_panel(config, measurement_type, config.experiment.groups) for measurement_type in config.experiment.measurement_types]

def generate_dashboard_v2(configs: List[PanelConfig]) -> dict:
    """
    Generate a Grafana dashboard configuration as a dictionary based on visualization configurations.

    :param configs: List of visualization configurations.
    :return: Grafana dashboard configuration as a dictionary.
    """
    panels = []
    for config in configs:
        for panel in generate_panels_from_config(config):
            panels.append(panel)

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