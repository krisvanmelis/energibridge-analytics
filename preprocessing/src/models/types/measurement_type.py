import re
from enum import Enum


class MeasurementType(Enum):
    """
    Enum class defining measurement types for experiments.
    These measurement types are based on the columns available in the CSV data files.
    Each measurement type has an associated column_name that specifies the column in the CSV file.
    Some column names include placeholders (e.g., {core_num}) that should be replaced
    with appropriate values when accessing the actual columns.
    """
    ALL = (0, "all")
    
    # Time-related measurements
    TIME = (1, "Time")
    DELTA = (2, "Delta")
    
    # System-level measurements
    SYSTEM_ENERGY = (10, "SYSTEM_ENERGY")
    SYSTEM_POWER = (11, "SYSTEM_POWER")
    
    # CPU-level aggregated measurements
    CPU_ENERGY = (20, "CPU_ENERGY (J)")
    CPU_POWER = (21, "CPU_POWER (W)")
    
    # Per-core energy and power measurements
    CORE_ENERGY = (30, "CORE{core_num}_ENERGY (J)")
    CORE_POWER = (31, "CORE{core_num}_POWER (W)")
    
    # Per-core frequency, voltage, and p-state measurements
    CORE_FREQUENCY = (40, "CORE{core_num}_FREQ (MHZ)")
    CORE_VOLTAGE = (41, "CORE{core_num}_VOLT (V)")
    CORE_PSTATE = (42, "CORE{core_num}_PSTATE")
    
    # CPU usage and frequency per logical processor
    CPU_FREQUENCY_LOGICAL = (50, "CPU_FREQUENCY_{core_num}")
    CPU_USAGE_LOGICAL = (51, "CPU_USAGE_{core_num}")
    
    # Memory metrics
    # TOTAL_MEMORY = (60, "TOTAL_MEMORY") Seems to be the same value for all rows
    USED_MEMORY = (61, "USED_MEMORY")
    TOTAL_SWAP = (62, "TOTAL_SWAP")
    USED_SWAP = (63, "USED_SWAP")
    
    # Temperature metrics
    TEMPERATURE = (70, "TEMPERATURE")
    
    # GPU metrics
    GPU_METRICS = (80, "GPU_METRICS")

    def __init__(self, value, column_name):
        """
        Initialize the enum with a value and column name.
        
        Args:
            value: The enum value
            column_name: The corresponding column name in CSV files (may include placeholders)
        """
        self._value_ = value
        self.column_name = column_name

    def __str__(self):
        """
        String representation of the measurement type.
        """
        return self.name
        
    @classmethod
    def _missing_(cls, value):
        """
        Custom handler for missing enum values.
        Helps with more user-friendly error messages.
        
        Args:
            value: The value that was not found
            
        Returns:
            None (and raises ValueError with a helpful message)
        """
        try:
            # For int values, try to provide better error messages
            if isinstance(value, int):
                valid_values = [m.value for m in cls]
                raise ValueError(f"{value} is not a valid {cls.__name__}. Valid values are: {valid_values}")
            # For string values
            elif isinstance(value, str):
                try:
                    # Try to convert to int first
                    return cls(int(value))
                except ValueError:
                    # If that fails, try to find by name
                    for member in cls:
                        if member.name.lower() == value.lower():
                            return member
                    raise ValueError(f"'{value}' is not a valid {cls.__name__} name")
        except Exception as e:
            # Fallback error message
            raise ValueError(f"Invalid {cls.__name__} value: {value}. Error: {str(e)}")

    @property
    def get_column_name(self):
        """
        Get the column name associated with this measurement type.
        
        Returns:
            str: The column name pattern in the CSV file
        """
        return self.column_name
    
    def get_column_name_for_core(self, core_num):
        """
        Get the column name for a specific core number.
        
        Args:
            core_num: The core number to substitute in the column name
            
        Returns:
            str: The column name with the core number substituted
        """
        if "{core_num}" in self.column_name:
            return self.column_name.format(core_num=core_num)
        return self.column_name
    
    def get_column_name_with_statistic(self, statistic=None):
        """
        Get the column name with a statistical suffix.
        
        Args:
            statistic: Statistical suffix (mean, std, median, min, max, LQ, UQ)
            
        Returns:
            str: The column name with the statistical suffix appended
        """
        if not statistic:
            return self.column_name
            
        return f"{self.column_name}_{statistic}"
    
    def get_full_column_name(self, core_num=None, statistic=None):
        """
        Get the complete column name with core number and statistical suffix.
        
        Args:
            core_num: The core number to substitute (if applicable)
            statistic: Statistical suffix (mean, std, median, min, max, LQ, UQ)
            
        Returns:
            str: The complete column name
        """
        col_name = self.column_name
        if core_num is not None and "{core_num}" in col_name:
            col_name = col_name.format(core_num=core_num)
            
        if statistic:
            col_name = f"{col_name}_{statistic}"
            
        return col_name
