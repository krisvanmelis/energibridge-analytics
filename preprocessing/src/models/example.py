import pandas as pd
from typing import List
from trail import Trail
from preprocessing.src.models.types.measurement_type import MeasurementType
from experiment import Experiment
from group import Group
from preprocessing.src.models.types.experiment_type import ExperimentType

# This file shows how the functions get called
example_files = ["example1.csv", "example2.csv", "example3.csv"]

# Create a list of Trail objects
trails = [Trail(file) for file in example_files]

# Preprocess the data
for trail in trails:
    trail.preprocess()

# Create a Group object
group = Group("Control Group", trails)

# Aggregate the data
group.aggregate([MeasurementType.CPU_POWER, MeasurementType.SYSTEM_ENERGY])

# Summarize the data
group.summarize([MeasurementType.CPU_POWER, MeasurementType.SYSTEM_ENERGY])

# Print the summary statistics
print(group.statistics_summary)

# Create another group
group2 = Group("Test Group", trails[:1])


# Create an Experiment object
experiment = Experiment([group, group2], ExperimentType.SIGNIFICANCE_TEST, [MeasurementType.CPU_POWER, MeasurementType.SYSTEM_ENERGY])
experiment2 = Experiment([group, group2], ExperimentType.DIFFERENCE, [MeasurementType.CPU_POWER, MeasurementType.SYSTEM_ENERGY])

experiments = [experiment, experiment2]


# Analyze the data
for experiment in experiments:
    experiment.analyze()

panels = []

for experiment in experiments:
    panels.append(experiment.visualize())

# TODO: Make sure the panels are displayed in the Grafana dashboard
