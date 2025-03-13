import pandas as pd
import numpy as np
import re
import os
from pprint import pprint

# ------------------------------------------------------------------------------------------------------

# Preprocessing file/module

# TODO: check other cpu fields to see if necessary


def preprocess(csv: pd.DataFrame) -> pd.DataFrame:
    """
    Takes imported csv as DataFrame and do necessary preprocessing. This includes finding differences in energy and
    adding converted where necessary. Adds missing power or energy columns where necessary.
    :param csv: loaded csv as a DataFrame
    :return: preprocessed DataFrame
    """
    # Go through all dataframe columns and preprocess where necessary
    res = csv.copy()

    # Loop through all columns in res
    for column in res.columns:
        # Check if the column name matches the regex pattern
        if re.search(r'_ENERGY \(J\)$', column):
            # Call the energy_preprocessing function on res and the column
            res = energy_preprocessing(res, column)
        elif re.search(r'_POWER \(W\)$', column):
            # Call the power_preprocessing function on res and the column
            res = power_preprocessing(res, column)
        else:
            continue

    return res


def energy_preprocessing(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Preprocess energy data and add power column. Will find delta if energy metric is cumulative
    :param df: Pandas DataFrame with columns ['Time', 'Delta', r'*_ENERGY (J)']
    :param column: column name to preprocess
    :return: Pandas DataFrame with the added things
    """
    ndf = df.copy()

    # TODO: check if cumulative and find deltas if it is
    cumulative = True
    if cumulative:
        ndf[f'DIFF_{column}'] = ndf[column].diff().fillna(0)
    else:
        ndf[f'DIFF_{column}'] = ndf[column]

    # Add power column
    cat = column.split('_')[0]
    ndf[f'{cat}_POWER (W)'] = ndf[f'DIFF_{column}'] / ndf['Delta']

    return ndf


def power_preprocessing(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Preprocessing for power columns. Adds energy column.
    :param df:
    :param column:
    :return:
    """
    ndf = df.copy()
    # Add energy column
    cat = column.split('_')[0]
    ndf[f'{cat}_ENERGY (J)'] = ndf[column] / ndf['Delta']
    return ndf

# ------------------------------------------------------------------------------------------------------

# Loading and saving / main?

input_folder = '../csv_data/input'  # TODO: change
files = [] # TODO: max!!
output_folder = '../csv_data/output'  # TODO: change
# input is lijst van bestandnamen + folder_path

# laat errors throwen die in front-end gebruikt kunnen worden
# Errors: I/O (opening enz)
# Geen error is succes
# Return lijst niewe bestandnamen en nieuwe folder_path
# Mss issue:


def load_data_and_preprocess(input_folder: str, files: list, output_folder: str):
    """
    TODO: docstring
    :param input_folder:
    :param files:
    :param output_folder:
    :return:
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
            name = f'{f}_processed.csv'
            npdf.to_csv(os.path.join(output_folder, name), index=False)
            saved_filenames.append(name)

    print(f'Finished! Following new files were created:')
    print(f'Folder: {output_folder}')
    pprint(f'Files created:\n{saved_filenames}')




