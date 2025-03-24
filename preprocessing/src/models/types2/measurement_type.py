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
    SYSTEM_POWER = 1
    # SYSTEM_ENERGY = ['SYSTEM_POWER (Watts)']
    CPU_ENERGY = 2
    # CPU_ENERGY = ['CPU_ENERGY (J)', 'PACKAGE_ENERGY (J)']
    CPU_POWER = 3
    # CPU_POWER = ['CPU_POWER (W)', 'PACKAGE_POWER (W)']

    POWER_PER_CORE = 4
    # POWER_PER_CORE = [r'CORE\d+_POWER (W)', 'PP1_POWER (W)']
    ENERGY_PER_CORE = 5
    # ENERGY_PER_CORE = [r'CORE\d+_ENERGY (J)', 'PP1_ENERGY (J)']
    VOLTAGE_PER_CORE = 6
    # VOLTAGE_PER_CORE = [r'CORE\d+_VOLT (V)']

    FREQUENCIES = 7
    # FREQUENCIES = [r'CPU_FREQUENCY_\d+', r'CORE\d+_FREQ (MHZ)']

    USAGES_PER_LOGICAL_PROCESSOR = 8
    # USAGES_PER_LOGICAL_PROCESSOR = [r'CPU_USAGE_\d+']

    MEMORY = 10  # available for all (yay)
    # MEMORY = ['TOTAL_MEMORY', 'TOTAL_SWAP', 'USED_MEMORY', 'USED_SWAP']
    TEMPERATURE = 11
    # TEMPERATURE = [r'CPU_TEMP_\d+']
    GPU_METRICS = 12
    # GPU_METRICS = [r'GPU*'] # TODO: check (EG, GPU0_MEMORY_TOTAL,GPU0_MEMORY_USED,GPU0_TEMPERATURE,GPU0_USAGE)

    # TODO: Add column names that can be used for analysis
    # TODO: how to deal w/ platform-dependent columns (DRAM, GPU usage, etc.)