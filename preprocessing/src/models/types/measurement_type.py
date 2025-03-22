from enum import Enum


class MeasurementType(Enum):
    SYSTEM_ENERGY = 1
    CPU_POWER = 2
    # TODO: Add column names that can be used for analysis

    def __str__(self):
        """
        String representation of the measurement type.
        """
        return " ".join([word[0].upper() + word[1:] for word in self.name.lower().split("_")])