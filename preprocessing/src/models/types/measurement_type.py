from enum import Enum
from typing import List

from models.types.experiment_type import ExperimentType


class MeasurementType(Enum):
    """
    Enum class defining measurement types for experiments.
    These measurement types are based on the columns available in the CSV data files.
    Each measurement type has an associated column_name that specifies the column in the CSV file.
    Some column names include placeholders (e.g., {core_num}) that should be replaced
    with appropriate values when accessing the actual columns.
    
    The third parameter in each enum member defines the compatible experiment types.
    """
    ALL = (0, "all", {ExperimentType.PLOT_OVER_TIME, ExperimentType.SIGNIFICANCE_TEST, ExperimentType.STATISTICS})
    
    # Time-related measurements
    TIME = (1, "Time", {ExperimentType.PLOT_OVER_TIME})
    DELTA = (2, "Delta", {ExperimentType.PLOT_OVER_TIME})

    # CPU-level aggregated measurements
    CPU_POWER = (21, "CPU_POWER (W)", "watt", {ExperimentType.PLOT_OVER_TIME})
    
    # Per-core energy and power measurements
    CORE_POWER = (31, "CORE{core_num}_POWER (W)", "watt", {ExperimentType.PLOT_OVER_TIME})
    
    # Per-core frequency, voltage, and p-state measurements
    CORE_VOLTAGE = (41, "CORE{core_num}_VOLT (V)", "volt", {ExperimentType.PLOT_OVER_TIME})
    
    # CPU usage and frequency per logical processor
    CPU_USAGE_LOGICAL = (51, "CPU_USAGE_{core_num}", "percent", {ExperimentType.PLOT_OVER_TIME})
    
    # Memory metrics
    USED_MEMORY = (61, "USED_MEMORY", "decbytes", {ExperimentType.PLOT_OVER_TIME})
    USED_SWAP = (63, "USED_SWAP", "decbytes", {ExperimentType.PLOT_OVER_TIME})

    # Special statistics types - only compatible with STATISTICS experiment type
    CPU_STATS = (70, "CPU STATS", "", {ExperimentType.STATISTICS})
    CORE_STATS = (71, "CORE_STATS", "", {ExperimentType.STATISTICS})

    COMPARE_TOTAL_ENERGY = (80, "COMPARE_TOTAL_ENERGY", "", {ExperimentType.SIGNIFICANCE_TEST})
    COMPARE_PEAK_POWER = (81, "COMPARE_PEAK_POWER", "", {ExperimentType.SIGNIFICANCE_TEST})
    COMPARE_POWER_OVER_TIME = (82, "COMPARE_POWER_OVER_TIME", "", {ExperimentType.SIGNIFICANCE_TEST})
    COMPARE_MEMORY_OVER_TIME = (83, "COMPARE_MEMORY_OVER_TIME", "", {ExperimentType.SIGNIFICANCE_TEST})
    COMPARE_SWAP_OVER_TIME = (85, "COMPARE_SWAP_OVER_TIME", "", {ExperimentType.SIGNIFICANCE_TEST})
    COMPARE_ENERGY_VIOLIN_PLOT = (86, "COMPARE_ENERGY_-_VIOLIN_PLOT", "", {ExperimentType.SIGNIFICANCE_TEST})
    COMPARE_POWER_VIOLIN_PLOT = (87, "COMPARE_POWER_-_VIOLIN_PLOT", "", {ExperimentType.SIGNIFICANCE_TEST})


    def __init__(self, value, column_name, unit=None, compatible_experiment_types=None):
        """
        Initialize the enum with a value, column name, unit, and compatible experiment types.
        
        Args:
            value: The enum value
            column_name: The corresponding column name in CSV files (may include placeholders)
            unit: The unit of measurement (for display in visualizations)
            compatible_experiment_types: Set of ExperimentType values this measurement is compatible with
        """
        self._value_ = value
        self.column_name = column_name
        self.unit = unit
        # Default to all experiment types if not specified
        self.compatible_experiment_types = compatible_experiment_types or set()

    def __str__(self):
        """
        String representation of the measurement type.
        """
        return self.name
    
    def is_compatible_with(self, experiment_type: ExperimentType) -> bool:
        """
        Check if this measurement type is compatible with the given experiment type.
        
        Args:
            experiment_type: The experiment type to check compatibility with
            
        Returns:
            bool: True if compatible, False otherwise
        """
        return experiment_type in self.compatible_experiment_types
        
    @classmethod
    def get_compatible_types(cls, experiment_type: ExperimentType) -> List['MeasurementType']:
        """
        Get all measurement types compatible with the given experiment type.
        
        Args:
            experiment_type: The experiment type to filter by
            
        Returns:
            List[MeasurementType]: List of compatible measurement types
        """
        return [mt for mt in cls if mt.is_compatible_with(experiment_type)]
        
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
