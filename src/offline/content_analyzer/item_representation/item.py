from src.offline.content_analyzer.item_representation.item_field import ItemField


class Item:
    """
    A Item is a list of his fields, identified by a string id
    Args:
        item_id (str): identifier
        fields (list[ItemField]): list of the fields of an item
    """
    def __init__(self, item_id: str, fields: list[ItemField] = None):
        if fields is None:
            fields = []         # list o dict
        self.__id: str = item_id
        self.__fields: list = fields

    def append(self, field: ItemField):
        """
        append a field to the fields list
        Args:
            field (ItemField): the field to append
        """
        self.__fields.append(field)

    def remove(self, field_name: str):
        """
        remove the field with field_name in the fields list
        Args:
            field_name (str): the name of the field to remove
        """
        self.__fields.pop(self.__fields.index(ItemField(field_name)))

    def serialize(self):
        """
        Serialize an item
        """
        pass


class RepresentedItems:
    """
    Class that collect the Items created and serialize the entire collection.
    Args:
        items (list<Item>): list of Items
        length:
    """
    def __init__(self, items: list[Item], length: int):
        self.__items: list[Item] = []
        self.__length: int = length

    def serialize(self):
        """
        Serialize the entire collection
        Returns:

        """
        pass                # forse non necessario (?)