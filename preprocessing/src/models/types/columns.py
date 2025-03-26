from dataclasses import dataclass

from models.group import Group
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

def measurement_type_to_columns(measurement: MeasurementType) -> [PrimaryColumn]:
    """
    Convert measuremnt type to Grafana columns.

    :return: List of columns
    """
    predefined_columns = {
        MeasurementType.SYSTEM_POWER: SYSTEM_POWER_COLUMN,
        MeasurementType.SYSTEM_ENERGY: SYSTEM_ENERGY_COLUMN,
        MeasurementType.CPU_ENERGY: CPU_ENERGY_COLUMN,
        MeasurementType.CPU_POWER: CPU_POWER_COLUMN,
        MeasurementType.MEMORY: TOTAL_MEMORY_COLUMN,
    }
    return predefined_columns[measurement]

# Predefined primary columns belonging to measurement types
SYSTEM_POWER_COLUMN = PrimaryColumn("SYSTEM_POWER (W)_median", "SYSTEM_POWER", "W", "number", True)
SYSTEM_ENERGY_COLUMN = PrimaryColumn("DIFF_SYSTEM_ENERGY (J)_median", "SYSTEM_ENERGY", "J", "number", True)
CPU_ENERGY_COLUMN = PrimaryColumn("DIFF_CPU_ENERGY (J)_median", "CPU_ENERGY", "J", "number", True)
CPU_POWER_COLUMN = PrimaryColumn("CPU_POWER (W)_median", "CPU_POWER", "W", "number", True)
TOTAL_MEMORY_COLUMN = PrimaryColumn("TOTAL_MEMORY_median", "TOTAL_MEMORY", "GB", "number", True)
