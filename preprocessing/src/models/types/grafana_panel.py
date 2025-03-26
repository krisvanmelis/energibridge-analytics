from models.group import Group
from models.types.measurement_type import MeasurementType


class Target:
    """
    Represents a datasource in Grafana for a visualisation. This project uses the Infinity plugin's CSV to import CSVs.
    """
    group: Group
    columns: [dict]

    # TODO: selection of columns needs to be fixed for some measurement types to exclude std, min, max

    def __init__(self, source: Group, measurement_type: MeasurementType) -> None:
        self.group = source
        self.columns = [{
            "selector": "Time",
            "text": "Time",
            "type": "number"
        }] + measurement_type.column_names_to_targets(source.aggregate_data.columns)

    def to_dict(self) -> dict:
        return {
            "columns": self.columns,
            "datasource": {
                "type": "yesoreyeram-infinity-datasource",
                "uid": "PEB6B42F54C42D283"
            },
            "filters": [],
            "format": "table",
            "global_query_id": "",
            "parser": "backend",
            "refId": self.group.name,
            "root_selector": "",
            "source": "url",
            "type": "csv",
            "url": f"http://nginx/{self.group.aggregate_data_path}",
            "url_options": {
                "data": "",
                "method": "GET"
            }
        }


class MeasurementPanelConfig:
    type: MeasurementType
    fieldConfig: dict
    options: dict
    transformations: [dict]
    graph_type: str

    def __init__(self, type: MeasurementType) -> None:
        self.type = type
        if type == MeasurementType.CPU_POWER:
            self.power_config()
        elif type == MeasurementType.POWER_PER_CORE:
            self.power_per_core_config()
        else:
            raise ValueError("No Grafana config for selected measurement type")

    def power_config(self):
        self.transformations = [  # TODO: If 1+ groups, at least join here
            {
              "id": "calculateField",
              "options": {
                "alias": "Time (s)",
                "binary": {
                  "left": {
                    "matcher": {
                      "id": "byName",
                      "options": "Time"
                    }
                  },
                  "operator": "/",
                  "right": {
                    "fixed": "1000"
                  }
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }
            },
            {
              "id": "organize",
              "options": {
                "excludeByName": {
                  "Time": True
                },
                "includeByName": {},
                "indexByName": {
                  "CPU_POWER (W)_LQ": 3,
                  "CPU_POWER (W)_UQ": 4,
                  "CPU_POWER (W)_median": 2,
                  "Time": 0,
                  "Time (s)": 1
                },
                "renameByName": {}
              }
            }
          ]
        self.fieldConfig = {
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
                "fillOpacity": 14,
                "gradientMode": "hue",
                "hideFrom": {
                  "legend": False,
                  "tooltip": False,
                  "viz": False
                },
                "insertNulls": False,
                "lineInterpolation": "linear",
                "lineStyle": {
                  "fill": "solid"
                },
                "lineWidth": 1,
                "pointSize": 5,
                "scaleDistribution": {
                  "type": "linear"
                },
                "showPoints": "auto",
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
              "unit": "watt"
            },
            "overrides": [
              {
                "matcher": {
                  "id": "byName",
                  "options": "CPU_POWER (W)_UQ"
                },
                "properties": [
                  {
                    "id": "custom.fillBelowTo",
                    "value": "CPU_POWER (W)_LQ"
                  },
                  {
                    "id": "custom.lineStyle",
                    "value": {
                      "dash": [
                        5,
                        10
                      ],
                      "fill": "dash"
                    }
                  }
                ]
              },
              {
                "matcher": {
                  "id": "byName",
                  "options": "CPU_POWER (W)_median"
                },
                "properties": [
                  {
                    "id": "custom.fillOpacity",
                    "value": 0
                  },
                  {
                    "id": "custom.lineWidth",
                    "value": 3
                  }
                ]
              },
              {
                "matcher": {
                  "id": "byName",
                  "options": "CPU_POWER (W)_LQ"
                },
                "properties": [
                  {
                    "id": "custom.fillOpacity",
                    "value": 0
                  },
                  {
                    "id": "custom.lineStyle",
                    "value": {
                      "dash": [
                        0,
                        3,
                        3
                      ],
                      "fill": "dot"
                    }
                  }
                ]
              },
                {
                    "matcher": {
                        "id": "byName",
                        "options": "Time (s)"
                    },
                    "properties": [
                        {
                            "id": "unit",
                            "value": "s"
                        }
                    ]
                }
            ]
        }
        self.options = {
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
            },
            "xField": "Time (s)"
          }
        self.graph_type = "trend"

    def power_per_core_config(self):
        self.transformations = [{
          "id": "calculateField",
          "options": {
            "alias": "Time (s)",
            "binary": {
              "left": {
                "matcher": {
                  "id": "byName",
                  "options": "Time"
                }
              },
              "operator": "/",
              "right": {
                "fixed": "1000"
              }
            },
            "mode": "binary",
            "reduce": {
              "reducer": "sum"
            }
          }
        }, {
          "id": "organize",
          "options": {
            "excludeByName": {
              "Time": True
            },
            "includeByName": {},
            "indexByName": {
              "CPU_POWER_LQ": 3,
              "CPU_POWER_UQ": 4,
              "CPU_POWER_median": 2,
              "Time": 0,
              "Time (s)": 1
            },
            "renameByName": {}
          }
        }]
        self.fieldConfig = {
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
                "fillOpacity": 14,
                "gradientMode": "hue",
                "hideFrom": {
                  "legend": False,
                  "tooltip": False,
                  "viz": False
                },
                "insertNulls": False,
                "lineInterpolation": "linear",
                "lineStyle": {
                  "fill": "solid"
                },
                "lineWidth": 1,
                "pointSize": 5,
                "scaleDistribution": {
                  "type": "linear"
                },
                "showPoints": "auto",
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
              "unit": "watt"
            },
            "overrides": []
          }
        self.options = {
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
            },
            "xField": "Time (s)"
          }
        self.graph_type = "trend"

    def memory_config(self):
        self.fieldConfig = {
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
                "showPoints": "auto",
                "spanNulls": False,
                "stacking": {
                  "group": "A",
                  "mode": "none"
                },
                "thresholdsStyle": {
                  "mode": "off"
                }
              },
              "mappings": [],
              "thresholds": {
                "mode": "absolute",
                "steps": [
                  {
                    "color": "green",
                    "value": None
                  },
                  {
                    "color": "red",
                    "value": 80
                  }
                ]
              },
              "unit": "decbytes"
            },
            "overrides": [
              {
                "matcher": {
                  "id": "byName",
                  "options": "USED_MEMORY_UQ"
                },
                "properties": [
                  {
                    "id": "custom.fillBelowTo",
                    "value": "USED_MEMORY_LQ"
                  },
                  {
                    "id": "custom.fillOpacity",
                    "value": 10
                  }
                ]
              },
              {
                "matcher": {
                  "id": "byName",
                  "options": "USED_SWAP_UQ"
                },
                "properties": [
                  {
                    "id": "custom.fillBelowTo",
                    "value": "USED_SWAP_LQ"
                  }
                ]
              },
              {
                "matcher": {
                  "id": "byName",
                  "options": "Time"
                },
                "properties": [
                  {
                    "id": "unit",
                    "value": "ms"
                  }
                ]
              }
            ]
          }
        self.options = {
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
            },
            "xField": "Time"
          }
        self.transformations = [
            {
              "id": "organize",
              "options": {
                "excludeByName": {
                  "USED_SWAP": True,
                  "USED_SWAP_LQ": True,
                  "USED_SWAP_UQ": True
                },
                "includeByName": {},
                "indexByName": {},
                "renameByName": {}
              }
            },
            {
              "id": "filterByValue",
              "options": {
                "filters": [
                  {
                    "config": {
                      "id": "equal",
                      "options": {
                        "value": "0"
                      }
                    },
                    "fieldName": "USED_MEMORY"
                  },
                  {
                    "config": {
                      "id": "equal",
                      "options": {
                        "value": "0"
                      }
                    },
                    "fieldName": "USED_MEMORY_LQ"
                  },
                  {
                    "config": {
                      "id": "equal",
                      "options": {
                        "value": "0"
                      }
                    },
                    "fieldName": "USED_MEMORY_UQ"
                  }
                ],
                "match": "any",
                "type": "exclude"
              }
            }
          ]
        self.graph_type = "trend"


class GrafanaPanel:

    name: str  # panel name
    targets: [Target]
    panelConfig: MeasurementPanelConfig
    #TODO: column names?

    def __init__(self, name: str, measurement_type: MeasurementType, groups: [Group]) -> None:
        self.name = name
        self.targets = [Target(group, measurement_type) for group in groups]
        self.panelConfig = MeasurementPanelConfig(measurement_type)

    # TODO: handle multiple targets ->> transformations for joining and such

    def to_dict(self) -> dict:
        return {
          "datasource": {
            "type": "yesoreyeram-infinity-datasource",
            "uid": "PEB6B42F54C42D283"
          },
          "fieldConfig": self.panelConfig.fieldConfig,
          "gridPos": { # TODO: check if right
            "h": 9,
            "w": 24,
            "x": 0,
            "y": 0
          },
          "id": 1,
          "options": self.panelConfig.options,
          "pluginVersion": "11.5.2",
          "targets": [t.to_dict() for t in self.targets],
          "title": self.name,
          "transformations": self.panelConfig.transformations,
          "type": self.panelConfig.graph_type,
        }




