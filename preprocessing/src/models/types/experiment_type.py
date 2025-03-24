from enum import Enum


class ExperimentType(Enum):
    """
    Enum to define the type of experiment.
    """
    DIFFERENCE = 1
    SIGNIFICANCE_TEST = 2
    # TODO: Determine what experiments calculate what metrics

    def __str__(self):
        """
        String representation of the experiment type.
        """
        return " ".join([word[0].upper() + word[1:] for word in self.name.lower().split("_")])

