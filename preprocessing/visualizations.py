"""
Module containing functionality regarding visualizations.
"""
from dataclasses import dataclass
from enum import Enum


class VisualizationType(Enum):
    """
    Enum class definining visualization types for dashboards.
    Make sure the number matches with the one in the HTML template.
    """
    SYSTEM_ENERGY = 1

    def __str__(self) -> str:
        """
        Custom to string method for enum.

        :return: Human-readable string for visualization.
        """
        return " ".join([word[0].capitalize() + word[1:] for word in self.name.replace("_", " ").lower().split(" ")])


@dataclass
class VisualizationConfig:
    """
    Data class representing visualization configuration.
    """
    name: str
    type: VisualizationType
    csv_path: str

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary parseable by frontend.

        :return: Dictionary representation of configuration.
        """
        return {'name': self.name, 'type': str(self.type), 'csv_path': self.csv_path}
