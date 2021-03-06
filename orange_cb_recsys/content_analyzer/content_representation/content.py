import lzma
import os
from typing import Dict
import pickle
import re

from orange_cb_recsys.content_analyzer.content_representation.content_field import ContentField
from orange_cb_recsys.utils.const import logger


class Content:
    """
    Class that represents a content. A content can be an item or a user.
    A content is identified by a string id and is composed by different fields
    Args:
        content_id (str): identifier
        field_dict (dict[str, ContentField]): dictionary
            containing the fields instances for the content,
            and their name as dictionary key
        lod_properties (Dict[str, str]): dictionary that contains
            exogenous knowledge from a ontology via LOD cloud
    """
    def __init__(self, content_id: str,
                 field_dict: Dict[str, ContentField] = None,
                 lod_properties: Dict[str, str] = None):
        self.__lod_properties: Dict[str, str] = lod_properties
        if field_dict is None:
            field_dict = {}       # list o dict
        self.__index_document_id: int = None
        self.__content_id: str = content_id
        self.__field_dict: Dict[str, ContentField] = field_dict

    def set_lod_properties(self, lod_properties: Dict[str, str]):
        self.__lod_properties = lod_properties

    def get_lod_properties(self):
        return self.__lod_properties

    def set_index_document_id(self, index_document_id: int):
        self.__index_document_id = index_document_id

    def get_field_list(self):
        return self.__field_dict

    def get_field(self, field_name: str):
        return self.__field_dict[field_name]

    def get_index_document_id(self):
        return self.__index_document_id

    def append(self, field_name: str, field: ContentField):
        self.__field_dict[field_name] = field

    def remove(self, field_name: str):
        """
        Remove the field named field_name from the field dictionary
        Args:
            field_name (str): the name of the field to remove
        """
        self.__field_dict.pop(field_name)

    def serialize(self, output_directory: str):
        """
        Serialize a content instance using lzma compression algorithm,
        so the file extension is .xz

        Args:
            output_directory (str): Name of the directory in which serialize
        """
        logger.info("Serializing content %s in %s", self.__content_id, output_directory)

        file_name = re.sub(r'[^\w\s]', '', self.__content_id)
        path = os.path.join(output_directory, file_name + '.xz')
        with lzma.open(path, 'wb') as f:
            pickle.dump(self, f)

    def __str__(self):
        content_string = "Content: %s" % self.__content_id
        field_string = '\n'.join(str(field) for field in self.__field_dict.values())

        return "%s \n\n %s ##############################" % (content_string, field_string)

    def get_content_id(self):
        return self.__content_id

    def __eq__(self, other):
        return self.__content_id == other.__content_id and self.__field_dict == other.__field_dict


class RepresentedContentsRecap:
    """
    Class that collects a string list with id and types for each representation
    Args:
        representation_list (list<str>): List of the names of the representations
    """
    def __init__(self, representation_list: list = None):
        if representation_list is None:
            representation_list = []

        self.__representation_list = representation_list

    def append(self, representation: str):
        self.__representation_list.append(representation)

    def serialize(self):
        """
        Serialize strings
        """
        raise NotImplementedError

    def __str__(self):
        return '\n\n'.join(self.__representation_list)
