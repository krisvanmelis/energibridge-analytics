"""
Module containing functionality regarding visualizations.
"""
class VisualizationConfig:
    def __init__(self, name, kind, csv_path):
        self.name = name
        self.kind = kind
        self.csv_path = csv_path

    def to_dict(self):
        return {'name': self.name, 'kind': self.kind, 'csv_path': self.csv_path}
