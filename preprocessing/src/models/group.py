import re
from re import match

import pandas as pd
import numpy as np
from typing import List

from numpy.ma.core import outer, argmax

# from preprocessing.src.models.trial import Trial
# from preprocessing.src.models.types.measurement_type import MeasurementType
# from preprocessing.src.models.types.visualization_type import VisualizationType

from models.trial import Trial
from models.types.measurement_type import MeasurementType
from models.types.visualization_type import VisualizationType
import os


class Group:
    name: str
    trials: List[Trial]

    # Aggregated data from all trails (e.g. mean, median, std over time)
    aggregate_data: pd.DataFrame

    # Summary statistics for the whole group (e.g. total energy, peak power)
    statistics_summary: pd.DataFrame

    def __init__(self, name: str, folder_path: str, output_folder='') -> None:
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f'Group folder {folder_path} does not exist.')

        self.name = name

        output_folder_path = os.path.join(output_folder, name)
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        self.trials = [Trial(os.path.join(folder_path, file_name), os.path.join(output_folder_path, file_name))
                       for file_name in os.listdir(folder_path) if file_name.endswith(".csv")]

        self.aggregate()
        self.summarize()

    def aggregate(self) -> str:
        """
                Aggregate the data from all trails in the group for the specified columns
                TODO: good aggregation with interpolation for differing deltas
                TODO: outlier detection? -> flag possible?
                :return filepath to the aggregate dataframe
                """
        # retrieve the wanted columns for the measurement types
        columns = self.trials[0].preprocessed_data.columns

        # concatenate all trials into one dataframe
        ndf = pd.concat(
            [trial.preprocessed_data for trial in self.trials],
            axis=1,
            join='outer',
            keys=[trial.filename for trial in self.trials],
            names=['Trial name', 'Column ID']
        ).fillna(0).replace([np.inf, -np.inf], 0, inplace=False)

        # flatten the multiindex to a dataframe by renaming columns to '{trial name}_{column id}'
        ndf.columns = [f'{trial}:{column}' for trial, column in ndf.columns.to_flat_index()]
        print(ndf.columns)

        max_length_index = argmax([len(trial.preprocessed_data) for trial in self.trials])
        dictionary = {
            'Time': self.trials[max_length_index].preprocessed_data['Time'],
            'Delta': self.trials[max_length_index].preprocessed_data['Delta']
        }
        for c in columns:
            dictionary[f'{c}_mean'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].mean(axis=1)
            dictionary[f'{c}_std'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].std(axis=1)
            dictionary[f'{c}_median'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].median(axis=1)
            dictionary[f'{c}_min'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].min(axis=1)
            dictionary[f'{c}_max'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].max(axis=1)
        self.aggregate_data = pd.DataFrame(dictionary)

    def summarize(self) -> None:
        """
        Generate summary statistics for the group. - BROKEN, WILL BE FIXED ASAP
        - Total energy per trial
        - peak power per trial
        - average total energy overall
        - average peak power overall (Row)
        - TODO: normal tests? (for energy consumption, peak power, etc.)
        """
        # TODO: Add summary statistics logic here for all trails as whole --- columns??
        summary = pd.DataFrame(columns=['Trial name', 'Total Energy (J)', 'Peak Power (W)', 'Median Power (W)']).set_index('Trial name')
        for trial in self.trials:
            row = [
                trial.preprocessed_data['CPU_ENERGY (J)'].iloc[-1] - trial.preprocessed_data['CPU_ENERGY (J)'].iloc[0],
                trial.preprocessed_data['CPU_POWER (W)'].max(),
                trial.preprocessed_data['CPU_POWER (W)'].median()
                ]
            summary.loc[trial.filename] = row
        summary.loc['Mean Overall'] = [
            summary['Total Energy (J)'].mean(),
            summary['Peak Power (W)'].mean(),
            summary['Median Power (W)'].mean()
        ]
        summary.loc['Median Overall'] = [
            summary['Total Energy (J)'].median(),
            summary['Peak Power (W)'].median(),
            summary['Median Power (W)'].median()
        ]
        self.statistics_summary = summary

    def visualize(self, measurement_types: List[MeasurementType], visualization_type: VisualizationType) -> dict:
        """
        Returns the panel as a dictionary for grafana dashboard.
        """

        # Aggregate data
        self.aggregate(measurement_types)

        # Summarize data
        self.summarize(measurement_types)

        # TODO: Add logic to visualize the group data to a panel

    def print(self) -> None:
        print(f"Group: {self.name}")
        for trial in self.trials:
            print(trial.raw_file_path)
        if self.aggregate_data is not None:
            print("Aggregate Data:")
            print(self.aggregate_data)
        if self.statistics_summary is not None:
            print("Statistics Summary:")
            print(self.statistics_summary)
