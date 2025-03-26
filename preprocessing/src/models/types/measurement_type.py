from dataclasses import dataclass
from enum import Enum


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


# Predefined primary columns belonging to measurement types
SYSTEM_POWER_COLUMN = PrimaryColumn("SYSTEM_POWER (W)_median", "SYSTEM_POWER", "W", "number", True)
SYSTEM_ENERGY_COLUMN = PrimaryColumn("DIFF_SYSTEM_ENERGY (J)_median", "SYSTEM_ENERGY", "J", "number", True)
CPU_ENERGY_COLUMN = PrimaryColumn("DIFF_CPU_ENERGY (J)_median", "CPU_ENERGY", "J", "number", True)
CPU_POWER_COLUMN = PrimaryColumn("CPU_POWER (W)_median", "CPU_POWER", "W", "number", True)
TOTAL_MEMORY_COLUMN = PrimaryColumn("TOTAL_MEMORY_median", "TOTAL_MEMORY", "GB", "number", True)


class MeasurementType(Enum):
    """
    Enum class defining measurement types for experiments.
    TODO: finish doc
    - SYSTEM_ENERGY: System energy consumption, Apple CPUs only
    - CPU_ENERGY: overall CPU energy consumption
    - CPU_POWER: overall CPU power consumption
    - POWER_PER_CORE: power consumption separated per core, only available for AMD
    - VOLTAGE_PER_CORE: voltage per core, only available for AMD
    - FREQUENCIES: CPU frequencies per logical processor and core
    - USAGES_PER_LOGICAL_PROCESSOR: CPU usages per logical processor

    - MEMORY: Memory usages
    - GPU_METRICS: GPU metrics

    TODO: make numbers a list of possible interesting columns and make the parsing in respective functions check for existence
    """
    ALL = 0
    SYSTEM_ENERGY = 1
    SYSTEM_POWER = 2
    CPU_ENERGY = 3
    CPU_POWER = 4

    POWER_PER_CORE = 5
    ENERGY_PER_CORE = 6
    VOLTAGE_PER_CORE = 7
    FREQUENCIES = 8
    USAGES_PER_LOGICAL_PROCESSOR = 9
    MEMORY = 10
    TEMPERATURE = 11
    GPU_METRICS = 12

    # TODO: Add column names that can be used for analysis
    # TODO: how to deal w/ platform-dependent columns (DRAM, GPU usage, etc.)

    def columns(self) -> [str]:
        dictionary = {
            'SYSTEM_POWER': [r'SYSTEM_POWER .*'],
            'SYSTEM_ENERGY': ['SYSTEM_ENERGY .*'],
            'CPU_ENERGY': [r'.*CPU_ENERGY .*', 'PACKAGE_ENERGY .*'],
            'CPU_POWER': ['CPU_POWER .*', 'PACKAGE_POWER .*'],
            'POWER_PER_CORE': [r'CORE\d+_POWER .*', 'PP1_POWER .*'],
            'ENERGY_PER_CORE': [r'CORE\d+_ENERGY .*', 'PP1_ENERGY .*'],
            'VOLTAGE_PER_CORE': [r'CORE\d+_VOLT .*'],
            'FREQUENCIES': [r'CPU_FREQUENCY_\d+', r'CORE\d+_FREQ .*'],
            'USAGES_PER_LOGICAL_PROCESSOR': [r'CPU_USAGE_\d+'],
            'MEMORY': ['TOTAL_MEMORY', 'TOTAL_SWAP', 'USED_MEMORY', 'USED_SWAP'],
            'TEMPERATURE': [r'CPU_TEMP_\d+'],
            'GPU_METRICS': [r'GPU*']
        }
        return dictionary[self.name]


    def to_grafana_columns(self) -> [PrimaryColumn]:
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
        return predefined_columns[self]

    def __str__(self):
        """
        String representation of the measurement type.
        """
        return " ".join([word[0].upper() + word[1:] for word in self.name.lower().split("_")])
