"""
Module containing functionality regarding visualizations.
"""
from dataclasses import dataclass
from enum import Enum


class VisualizationType(Enum):
    DELTA_OVER_TIME = 1

    def __str__(self):
        return " ".join([word[0].capitalize() + word[1:] for word in self.name.replace("_", " ").lower().split(" ")])


@dataclass
class VisualizationConfig:
    name: str
    type: VisualizationType
    csv_path: str

    def to_dict(self):
        return {'name': self.name, 'kind': str(self.type), 'csv_path': self.csv_path}
