"""
Module containing functionality for Grafana dashboards.
"""
from typing import List

from visualizations import VisualizationConfig, VisualizationType


def generate_dashboard(configs: List[VisualizationConfig]) -> dict:
    """
    Generate a Grafana dashboard configuration as a dictionary based on visualization configurations.

    :param configs: List of visualization configurations.
    :return: Grafana dashboard configuration as a dictionary.
    """
    panels = []

    for config in configs:
        columns = [
            {
                "selector": "Time",
                "text": "Time",
                "type": "timestamp_epoch",
            }
        ]

        if config.type == VisualizationType.SYSTEM_ENERGY:
            columns.append({
                "selector": "SYSTEM_ENERGY (J)",
                "text": "SYSTEM_ENERGY (J)",
                "type": "number",
            })
        target = {
            "columns": columns,
            "datasource": {
                "type": "yesoreyeram-infinity-datasource",
                "uid": "PEB6B42F54C42D283"
            },
            "filters": [],
            "format": "table",
            "global_query_id": "",
            "parser": "backend",
            "refId": "A",
            "root_selector": "",
            "source": "url",
            "type": "csv",
            "url": f"http://nginx/{config.csv_path}",
            "url_options": {
                "data": "",
                "method": "GET"
            }
        }
        panel = {
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
            "targets": [
                target
            ],
            "title": config.name,
            "type": "timeseries"
        }
        panels.append(panel)

    # For now use csv of first configuration
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
