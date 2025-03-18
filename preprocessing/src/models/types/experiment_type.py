from enum import Enum


class ExperimentType(Enum):
    """
    Enum to define the type of experiment.
    """
    DIFFERENCE = 1
    SIGNIFICANCE_TEST = 2
    # TODO: Determine what experiments calculate what metrics

