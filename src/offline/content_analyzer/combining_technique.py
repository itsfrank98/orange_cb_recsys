from src.offline.content_analyzer.field_content_production_technique import CombiningTechnique


class Centroid(CombiningTechnique):
    """"
    Class that implements the Abstract Class CombiningTechnique.
    This class calculate the centroid given the list of weights.

    Args:
        weights (list): list of weights, used to calculate the centroid.
    """
    def __init__(self, weights: list = None):
        super().__init__()
        self.__weights: list = weights

    def combine(self):
        """"
        Implements the Abstract Method combine in Combining Technique.
        """
        pass

# your combining technique