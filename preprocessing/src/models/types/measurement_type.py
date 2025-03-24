from enum import Enum


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


    def __str__(self):
        """
        String representation of the measurement type.
        """
        return " ".join([word[0].upper() + word[1:] for word in self.name.lower().split("_")])