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
    output_folder = 'csv-data/output/'  # always this folder

    # Aggregated data from all trails (e.g. mean, median, std over time)
    aggregate_data_path: str
    aggregate_data: pd.DataFrame

    # Summary statistics for the whole group (e.g. total energy, peak power)
    summary_path: str
    summary: pd.DataFrame

    def __init__(self, name: str, folder_path: str = '', is_import: bool = False) -> None:
        self.name = name

        if not is_import:
            if not os.path.exists(folder_path):
                raise FileNotFoundError(f'Group folder {folder_path} does not exist.')

            # check and create output folder for group
            output_folder_path = os.path.join(self.output_folder, name)
            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path)

            # preprocess all trials in input folder and save them to output folder
            self.trials = [Trial(os.path.join(folder_path, file_name), os.path.join(output_folder_path, file_name))
                           for file_name in os.listdir(folder_path) if file_name.endswith(".csv")]
            if len(self.trials) == 0:
                raise FileNotFoundError(f'No trials found in folder: "{folder_path}"')
            # aggregate and summarize the group
            self.aggregate()
            self.summarize()
        else:
            # for importing existing groups from the output folder.
            group_folder_path = os.path.join(self.output_folder, name)

            # find all trial csvs in folder, identified by the ending of the filename
            self.trials = [Trial(preprocessed_path=os.path.join(group_folder_path, f))
                           for f in os.listdir(group_folder_path)
                           if f.endswith("_preprocessed.csv")]

            if len(self.trials) == 0:
                raise FileNotFoundError(f'No trials found in folder: "{group_folder_path}"')

            # Check if the aggregate data and summary statistics are already present, load if yes, create if no.
            if os.path.join(group_folder_path, 'aggregate_data.csv') in os.listdir(group_folder_path):
                self.aggregate_data = pd.read_csv(os.path.join(group_folder_path, 'aggregate_data.csv'))
            else:
                self.aggregate()
            if os.path.join(group_folder_path, 'summary.csv') in os.listdir(group_folder_path):
                self.summary = pd.read_csv(os.path.join(group_folder_path, 'summary.csv'))
            else:
                self.summarize()


    def aggregate(self) -> None:
        """
                Aggregate the data from all trails in the group for the specified columns
                TODO: aggregation with interpolation for differing deltas
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
        # print(ndf.columns)

        max_length_index = argmax([len(trial.preprocessed_data) for trial in self.trials])
        dictionary = {
            'Time': self.trials[max_length_index].preprocessed_data['Time'].astype(int),
            'Delta': self.trials[max_length_index].preprocessed_data['Delta'].astype(int)
        }
        for c in columns:
            if c in ['Time', 'Delta']:
                continue
            dictionary[f'{c}_mean'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].mean(axis=1)
            dictionary[f'{c}_std'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].std(axis=1)
            dictionary[f'{c}_median'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].median(axis=1)
            dictionary[f'{c}_min'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].min(axis=1)
            dictionary[f'{c}_max'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].max(axis=1)
        self.aggregate_data = pd.DataFrame(dictionary)
        self.aggregate_data_path = os.path.join(os.path.join(self.output_folder, self.name), 'aggregate_data.csv')
        self.aggregate_data.to_csv(self.aggregate_data_path, index=False)

    def summarize(self) -> None:
        """
        Generate summary statistics for the group. - BROKEN, WILL BE FIXED ASAP
        - Total energy per trial
        - peak power per trial
        - average total energy overall
        - average peak power overall (Row)
        - TODO: normal tests? (for energy consumption, peak power, etc.)
        """
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
        self.summary = summary
        self.summary_path = os.path.join(os.path.join(self.output_folder, self.name), 'summary.csv')
        self.summary.to_csv(self.summary_path, index=True)

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
        if self.summary is not None:
            print("Statistics Summary:")
            print(self.summary)


    def to_dict(self) -> dict:
        """
        Convert group to dictionary parseable by frontend.
        """
        return {'name': self.name, 'trial_count': str(len(self.trials))}
