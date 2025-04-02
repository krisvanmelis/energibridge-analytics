import re
import shutil
from re import match
from scipy.stats import shapiro
import pandas as pd
import numpy as np
from typing import List

import seaborn as sns
from matplotlib import pyplot as plt
from numpy.ma.core import outer, argmax

from models.trial import Trial
from models.types.measurement_type import MeasurementType
import os


class Group:
    name: str
    trials: List[Trial]
    input_folder = 'csv-data/input/'  # always this folder
    output_folder = 'csv-data/output/'  # always this folder
    image_output_folder = 'images/output/'  # always this folder

    # Number of cores and logical processors (easier for exporting to Grafana)
    no_cores: int
    no_logical: int

    # Aggregated data from all trails (e.g. mean, median, std over time)
    aggregate_data_path: str
    aggregate_data: pd.DataFrame

    # Summary statistics for the whole group (e.g. total energy, peak power)
    summary_path: str
    summary: pd.DataFrame

    def __init__(self, name: str) -> None:
        self.name = name

        folder_path = os.path.join(self.input_folder, name)

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
        self.summarize_trials()
        self.generate_violin_plot()
        self.group_summary()

        self.no_cores = self.trials[0].no_cores()
        self.no_logical = self.trials[0].no_logical()


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
            dictionary[f'{c}_LQ'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].quantile(q=0.25, axis=1)
            dictionary[f'{c}_UQ'] = ndf[[f'{trial.filename}:{c}' for trial in self.trials]].quantile(q=0.75, axis=1)

        self.aggregate_data = pd.DataFrame(dictionary)
        self.aggregate_data_path = os.path.join(os.path.join(self.output_folder, self.name), 'aggregate_data.csv')
        self.aggregate_data.to_csv(self.aggregate_data_path, index=False)

    def summarize_trials(self) -> None:
        """
        Generate a summary CSV for each trial with:
        - Total energy used (CPU and CORE0–CORE7)
        - Peak power (CPU and CORE0–CORE7)
        Saves a summary CSV file to the trial output folder.
        """
        summary_data = []

        for trial in self.trials:
            data = trial.preprocessed_data
            trial_summary = {"Trial": trial.filename}

            # Total energy (sum of DIFF_*_ENERGY columns)
            trial_summary["CPU_Total_Energy (J)"] = data["DIFF_CPU_ENERGY (J)"].sum()
            trial_summary["CPU_Peak_Power (W)"] = data["CPU_POWER (W)"].max()

            for core in range(8):
                energy_col = f"DIFF_CORE{core}_ENERGY (J)"
                power_col = f"CORE{core}_POWER (W)"

                if energy_col in data.columns and power_col in data.columns:
                    trial_summary[f"CORE{core}_Total_Energy (J)"] = data[energy_col].sum()
                    trial_summary[f"CORE{core}_Peak_Power (W)"] = data[power_col].max()
                else:
                    trial_summary[f"CORE{core}_Total_Energy (J)"] = None
                    trial_summary[f"CORE{core}_Peak_Power (W)"] = None

            summary_data.append(trial_summary)

        summary_df = pd.DataFrame(summary_data)

        # Save to CSV
        summary_path = os.path.join(os.path.join(self.output_folder, self.name), 'trial_summary.csv')
        summary_df.to_csv(summary_path, index=False)

    def generate_violin_plot(self) -> None:
        """
        Generates violin plots of all numeric stats in the summary file
        and saves them as PNG images in self.image_output_folder.
        """
        # Load summary CSV
        summary_path = os.path.join(self.output_folder, self.name, 'trial_summary.csv')
        if not os.path.exists(summary_path):
            raise FileNotFoundError(f"Summary file not found at: {summary_path}")

        df = pd.read_csv(summary_path)

        # Make sure output folder exists
        os.makedirs(self.image_output_folder, exist_ok=True)

        # Remove non-numeric or identifier columns
        plot_df = df.drop(columns=["Trial"], errors="ignore")

        # For each stat, create a violin plot across all trials
        for column in plot_df.columns:
            plt.figure(figsize=(8, 6))
            sns.violinplot(data=df, y=column)
            plt.title(f"Violin Plot: {column}")
            plt.ylabel(column)
            plt.tight_layout()
            folder_path = os.path.join(self.image_output_folder, self.name)
            os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists

            # Create safe filename and full path
            safe_column = column.replace(' ', '_')
            output_path = os.path.join(folder_path, f"{safe_column}_violin.png")

            # Save the plot
            plt.savefig(output_path)
            plt.close()

    def group_summary(self) -> None:
        """
        Generate a group summary CSV file with statistics (mean, std, median, min, max, LQ, UQ)
        computed across all trials for each metric in trial_summary.csv.
        """
        # Load the trial_summary.csv
        summary_path = os.path.join(self.output_folder, self.name, 'trial_summary.csv')
        trial_summary_df = pd.read_csv(summary_path)

        # Transpose trial data for easier multi-trial stat calculations
        trial_summary_df.set_index("Trial", inplace=True)
        trial_summary_df = trial_summary_df.transpose()

        # Initialize result dictionary
        group_stats = {}

        for column in trial_summary_df.index:
            values = trial_summary_df.loc[column].dropna()  # Drop missing values for stat computation
            group_stats[f"{column}_mean"] = values.mean()
            group_stats[f"{column}_std"] = values.std()
            group_stats[f"{column}_median"] = values.median()
            group_stats[f"{column}_min"] = values.min()
            group_stats[f"{column}_max"] = values.max()
            group_stats[f"{column}_LQ"] = values.quantile(0.25)
            group_stats[f"{column}_UQ"] = values.quantile(0.75)

            if len(values) >= 3:  # Shapiro test requires at least 3 data points
                stat, p_value = shapiro(values)
                group_stats[f"{column}_p_value"] = p_value
                group_stats[f"{column}_normally_distributed"] = 1 if p_value >= 0.05 else 0
            else:
                group_stats[f"{column}_p_value"] = None
                group_stats[f"{column}_normally_distributed"] = None

        # Convert to DataFrame and transpose for CSV output
        group_summary_df = pd.DataFrame(group_stats, index=[0])
        group_summary_path = os.path.join(self.output_folder, self.name, 'group_summary.csv')
        group_summary_df.to_csv(group_summary_path, index=False)

    def visualize(self, measurement_types: List[MeasurementType]) -> dict:
        """
        Returns the panel as a dictionary for grafana dashboard.
        """

        # Aggregate data
        self.aggregate(measurement_types)


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
