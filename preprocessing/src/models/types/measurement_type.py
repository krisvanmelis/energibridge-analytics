from enum import Enum
from typing import Optional


class MeasurementType(Enum):
    """Enum representing the type of measurements available in the system."""
    
    # Core-specific measurements
    CORE_ENERGY = "CORE_ENERGY (J)"
    CORE_POWER = "CORE_POWER (W)"
    CORE_FREQUENCY = "CORE_FREQ (MHZ)"
    CORE_VOLTAGE = "CORE_VOLT (V)"
    CORE_PSTATE = "CORE_PSTATE"
    
    # CPU-wide measurements
    CPU_ENERGY = "CPU_ENERGY (J)"
    CPU_POWER = "CPU_POWER (W)"
    CPU_USAGE_LOGICAL = "CPU_USAGE"
    CPU_FREQUENCY_LOGICAL = "CPU_FREQUENCY"
    
    # Memory measurements
    TOTAL_MEMORY = "TOTAL_MEMORY"
    USED_MEMORY = "USED_MEMORY"
    TOTAL_SWAP = "TOTAL_SWAP"
    USED_SWAP = "USED_SWAP"
    
    # System-wide measurements
    SYSTEM_ENERGY = "SYSTEM_ENERGY (J)" 
    SYSTEM_POWER = "SYSTEM_POWER (W)"
    
    # Special
    ALL = "ALL"
    
    @property
    def get_column_name(self) -> str:
        """Get the column name in the CSV file corresponding to this measurement type."""
        return self.value
    
    def get_full_column_name(self, core_num: Optional[int] = None, statistic: str = "median") -> str:
        """
        Get the full column name including core number (if applicable) and statistic.
        
        :param core_num: The core number (if applicable).
        :param statistic: The statistic (mean, median, min, max, etc).
        :return: The full column name.
        """
        base_name = self.value
        
        if core_num is not None:
            if self in [MeasurementType.CORE_ENERGY, MeasurementType.CORE_POWER, 
                       MeasurementType.CORE_FREQUENCY, MeasurementType.CORE_VOLTAGE,
                       MeasurementType.CORE_PSTATE]:
                # Replace generic "CORE" with specific core number
                base_name = base_name.replace("CORE", f"CORE{core_num}")
            elif self in [MeasurementType.CPU_USAGE_LOGICAL, MeasurementType.CPU_FREQUENCY_LOGICAL]:
                # For logical CPU metrics, append the core number
                base_name = base_name + f"_{core_num}"
        
        # Append statistic suffix
        return f"{base_name}_{statistic}"
    
    def is_energy_metric(self) -> bool:
        """
        Check if this measurement type is an energy metric.
        
        :return: True if it's an energy metric, False otherwise.
        """
        return "ENERGY" in self.value
