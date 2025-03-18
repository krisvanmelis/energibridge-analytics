import re
from re import match

import pandas as pd
import numpy as np
from typing import List

# from preprocessing.src.app import OUTPUT_FOLDER
from trial import Trial
from preprocessing.src.models.types.measurement_type import MeasurementType
from preprocessing.src.models.types.visualization_type import VisualizationType
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
        # TODO: aggregation and summarisation

    # def add_trial(self, trial: Trial | str) -> None:
    #     """
    #     Add a trial to the group.
    #     """
    #     if trial is str:
    #         self.trials.append(Trial(trial))
    #     else:
    #         self.trials.append(trial)
    #     # re-aggregate and re-summarise?

    def aggregate(self, measurement_types: List[MeasurementType])-> str:
        """
                Aggregate the data from all trails in the group for the specified columns.
                TODO: have smth of a dictionary for the things to do?? idk > mode of each delta > round times and use those as index, interpolate missing values?
                TODO: aggregate for differing deltas?
                TODO: outlier detection?
                :return filepath to the aggregate dataframe
                """
        ndf = pd.DataFrame()

        # Quantise / synchronise time -> mode of Deltas is assumed delta?
        # get all deltas across all trials, take the mode (assumes this is the set delta in energibridge)
        deltas = pd.DataFrame([trial.preprocessed_data['Delta'] for trial in self.trials])
        delta = deltas.mode(axis=1).mode().iloc[0, 0]  # assume all deltas are the same

        # set the time to round to nearest delta
        time = np.arange(0, self.trials[0].preprocessed_data['Time'].max(), delta)
        deltal = np.full(len(time), delta)
        self.aggregate_data = pd.DataFrame({'Time': time, 'Delta': deltal})

        # retrieve the wanted columns for the measurement types
        columns = []
        for mt in measurement_types:
            columns += mt.columns()

        available_columns = self.trials[0].preprocessed_data.columns
        # filter out all columns in available_columns where the column name doesn't match any regex in columns
        matching_columns = [col for col in available_columns if any(re.search(pattern, col) for pattern in columns)]
        # fill in the data
        ndf = self.aggregate_data.copy()
        for trial in self.trials:
            for c in matching_columns:
                # do the funky inserting here if differing deltas are supported
                ndf[f'{trial.filename}\\{c}'] = trial.preprocessed_data[c]

        for c in matching_columns:
            self.aggregate_data[f'{c}_mean'] = ndf[[f'{trial.filename}\\{c}' for trial in self.trials]].mean(axis=1)
            self.aggregate_data[f'{c}_std'] = ndf[[f'{trial.filename}\\{c}' for trial in self.trials]].std(axis=1)
            self.aggregate_data[f'{c}_median'] = ndf[[f'{trial.filename}\\{c}' for trial in self.trials]].median(axis=1)
            self.aggregate_data[f'{c}_min'] = ndf[[f'{trial.filename}\\{c}' for trial in self.trials]].min(axis=1)
            self.aggregate_data[f'{c}_max'] = ndf[[f'{trial.filename}\\{c}' for trial in self.trials]].max(axis=1)

    def summarize(self, measurement_types: List[MeasurementType]) -> None:
        """
        Generate summary statistics for the group.
        - Total energy per trial
        - peak power per trial
        - average total energy overall
        - average peak power overall (Row)
        - ...
        """
        # TODO: Add summary statistics logic here for all trails as whole --- columns??
        # summary = pd.DataFrame(columns=['Total Energy (J)', 'Peak Power (W)', 'Average Power (W)'])
        # for trial in self.trials:
        #     summary.loc[trial.name] = [trial['Energy'].sum(), trial['Power'].max(), trial['Power'].mean()]

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
