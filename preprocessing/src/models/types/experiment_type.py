from enum import Enum


class ExperimentType(Enum):
    """
    Enum to define the type of experiment.
    """
    PLOT_OVER_TIME = 1
    SIGNIFICANCE_TEST = 2
    STATISTICS = 3


    def __str__(self):
        """
        String representation of the experiment type.
        """
        return " ".join([word[0].upper() + word[1:] for word in self.name.lower().split("_")])

