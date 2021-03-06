import os
import time
from abc import ABC, abstractmethod
from typing import List

from orange_cb_recsys.content_analyzer.information_processor.information_processor import TextProcessor
from orange_cb_recsys.content_analyzer.information_processor.nlp import NLTK
from orange_cb_recsys.content_analyzer.raw_information_source import RawInformationSource
from orange_cb_recsys.utils.const import DEVELOPING, home_path


class EmbeddingLearner(ABC):
    """
    Abstract Class for the different kinds of embedding.

    Args:
        source (RawInformationSource): Source where the content is stored.
        preprocessor (InformationProcessor): Instance of the class InformationProcessor,
            specify how to process (can be None) the source data, before
            use it for model computation
        field_list (List<str>): Field name list.
    """
    def __init__(self, source: RawInformationSource,
                 preprocessor: TextProcessor,
                 field_list: List[str]):
        self.__source: RawInformationSource = source
        if preprocessor is None:
            self.__preprocessor: TextProcessor = NLTK()
        else:
            self.__preprocessor: TextProcessor = preprocessor
        self.__preprocessor.set_lang("")
        self.__field_list = field_list
        self.__model = None

    @abstractmethod
    def fit(self, **kwargs):
        """
        This method creates the model, in different ways according to the various implementations.
        The model isn't then returned, but gets stored in the 'model' class attribute.
        """
        raise NotImplementedError

    def get_source(self):
        return self.__source

    def get_preprocessor(self):
        return self.__preprocessor

    def get_field_list(self):
        return self.__field_list

    def set_model(self, model):
        self.__model = model

    def get_model(self):
        return self.__model

    def extract_corpus(self) -> list:
        """
        Extracts the datas from the source and processes them

        Returns:
            corpus (list): List of processed data
        """
        corpus = []
        # iter the source
        for doc in self.get_source():
            doc_data = ""
            for field_name in self.get_field_list():
                # apply preprocessing and save the data in the list
                doc_data += " " + doc[field_name].lower()
            corpus.append(self.get_preprocessor().process(doc_data))
        return corpus

    def save(self):
        """
        Saves the model. If you are in developing mode, the model is saved in the src directory.
        If you are not in developing mode, the model will be saved in the embeddings
        directory under the home path.
        """
        embeddings_path = './'
        if not DEVELOPING:
            embeddings_path = os.path.join(home_path, 'embeddings')
        self.__model.save(embeddings_path + str(time.time()) + ".model")
