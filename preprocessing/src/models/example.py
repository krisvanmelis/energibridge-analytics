import pandas as pd
from typing import List
from trail import Trail
from preprocessing.src.models.types.measurement_type import MeasurementType
from experiment import Experiment
from group import Group
from preprocessing.src.models.types.experiment_type import ExperimentType
from preprocessing.src.models.types.visualization_type import VisualizationType

# This file shows how the functions get called
example_files = ["example1.csv", "example2.csv", "example3.csv"]

# Create a list of Trail objects
trails = [Trail(file) for file in example_files]

# Preprocess the data
for trail in trails:
    trail.preprocess()

# Create a Group object
group = Group("Control Group", trails)

# Create another group
group2 = Group("Test Group", trails[:1])

# Create an Experiment object
experiment = Experiment([group, group2], ExperimentType.SIGNIFICANCE_TEST, [MeasurementType.CPU_POWER, MeasurementType.SYSTEM_ENERGY])
experiment2 = Experiment([group, group2], ExperimentType.DIFFERENCE, [MeasurementType.CPU_POWER, MeasurementType.SYSTEM_ENERGY])

panels = []

# TODO Add visualization types for trail, group
# Experiment is hardcoded based on experiment type

# Visualize a single trail
panels.append(trails[0].visualize([MeasurementType.CPU_POWER, MeasurementType.SYSTEM_ENERGY], VisualizationType.GRAPH))

# Visualize a single group
panels.append(group.visualize([MeasurementType.CPU_POWER], VisualizationType.GRAPH))

# Visualize a single experiment
panels.append(experiment.visualize())


# TODO: Make sure the panels are displayed in the Grafana dashboard
