from enum import Enum

class ExperimentType(Enum):
    """
    Enum to define the type of experiment.
    """
    SIGNIFICANCE_TEST = 1
    # TODO: Determine what experiments calculate what metrics
    DIFFERENCE = 2
