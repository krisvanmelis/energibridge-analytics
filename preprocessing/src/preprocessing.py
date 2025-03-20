import pandas as pd
import numpy as np
import re
import os
from pprint import pprint


# ------------------------------------------------------------------------------------------------------

# Preprocessing file/module


def preprocess(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Takes imported csv as DataFrame and do necessary preprocessing. This includes finding differences in energy and
    adding converted where necessary. Adds missing power or energy columns where necessary.
    :param raw_data: Loaded csv as a DataFrame
    :return: Preprocessed DataFrame
    """
    # Go through all dataframe columns and preprocess where necessary
    res = raw_data.copy()
    res['Time'] = res['Time'] - res['Time'].min()

    # Loop through all columns in res
    for column in res.columns:
        # Check if the column name matches the regex pattern
        if re.search(r'_ENERGY \(J\)$', column):
            # Call the energy_preprocessing function on res and the column
            res = energy_preprocessing(res, column)
        elif re.search(r'_POWER \(Watts\)$', column):
            # Call the power_preprocessing function on res and the column
            res = power_preprocessing(res, column)
        else:
            continue

    return res


def energy_preprocessing(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Preprocess energy data and add power column. Will find delta if energy metric is cumulative
    :param df: Pandas DataFrame with columns ['Time', 'Delta', r'*_ENERGY (J)'].
    :param column: Name of column to preprocess.
    :return: Pandas DataFrame with the added power column and delta column.
    """
    ndf = df.copy()

    ndf[f'DIFF_{column}'] = ndf[column].diff().fillna(0)

    # Add power column
    cat = column.split('_')[0]
    ndf[f'{cat}_POWER (W)'] = (ndf[f'DIFF_{column}'] / (ndf['Delta'] / 1000)).fillna(0)

    return ndf


def power_preprocessing(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Preprocessing for power columns. Adds energy column.
    :param df: Pandas DataFrame with columns ['Time', 'Delta'] and the column to preprocess
    :param column: Name of the column to preprocess
    :return: Copy of the DataFrame with the added energy column.
    """
    ndf = df.copy()
    # Add energy column
    cat = column.split('_')[0]
    ndf[f'DIFF_{cat}_ENERGY (J)'] = (ndf[column] * (ndf['Delta']/1000)).fillna(0)
    return ndf

# ------------------------------------------------------------------------------------------------------

# Loading and saving / main?


def load_data_and_preprocess(input_folder: str, files: list, output_folder: str) -> [str]:
    """
    Loads the specified csvs and calls the preprocess function on them. Saves the preprocessed files in the output
    folder and returns a list with the new filenames.
    :param input_folder: File path to the folder containing the csv files to be processed.
    :param files: List of filenames of the files to be processed.
    :param output_folder: File path to the folder which to save the processed csvs to.
    :return: List of the new filenames of the processed files.
    """
    if not os.path.exists(input_folder):
        raise Exception(f"Folder specified does not exist: {input_folder}")
    if not os.path.exists(output_folder):
        raise Exception(f"Folder specified does not exist: {output_folder}")

    saved_filenames = []
    # Loop through all files in the input folder
    for f in files:
        if not os.path.exists(os.path.join(input_folder, f)):
            raise Exception(f"File specified does not exist: {f}")
        # Check if the file is a csv file
        if f.endswith('.csv'):
            # Load CSV file
            pdf = pd.read_csv(os.path.join(input_folder, f))
            # do preprocessing
            npdf = preprocess(pdf)
            # Save the preprocessed file
            name = f'{os.path.splitext(f)[0]}_processed.csv'
            npdf.to_csv(os.path.join(output_folder, name), index=False)
            saved_filenames.append(name)

    print(f'Finished! Following new files were created:')
    print(f'Folder: {output_folder}')
    print(f'Files created:')
    pprint(saved_filenames)
    return saved_filenames


