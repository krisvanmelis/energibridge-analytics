from typing import List

from models.group import Group
from models.panel_config import PanelConfig
from models.types.measurement_type import MeasurementType
from models.types.grafana_panel import GrafanaPanel


# TODO make sure all columns above appear in aggregated.csv
# TODO visualize quantiles
# TODO add support for info per core

def measurement_type_to_panel(config: PanelConfig, measurement_type: MeasurementType, groups: List[Group]) -> dict:
    targets = []
    for group in groups:
        for target in measurement_type.to_grafana_columns().to_targets(group):
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
        # PanelConfig(panel_name, groups, measurement_types, experiment_type)
        for mt in config.experiment.measurement_types:
            panels.append(GrafanaPanel(config.name, mt, config.experiment.groups).to_dict())
        # for panel in generate_panels_from_config(config):
        #     panels.append(panel)

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