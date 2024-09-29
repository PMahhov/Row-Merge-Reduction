"""Class for graph objects."""

from idgenerator import IdGenerator

class GraphObject:
    """
    A class for a graph object. A graph object is the class from
    which a node or an edge inherits.

    The graph object's main properties are:

    'id'            :   An id for graph object.
    'label'         :   A label for the graph object.
    'name'          :   A name for the graph object.
    'attributes'    :   A dictionary.

    """

    def __init__(self, label: str = "", name: str = "", attributes=None):
        if attributes is None:
            attributes = {}
        self.id = id
        self.label = label
        self.name = name
        self.__attributes = attributes

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, id) -> None:
        """Obtains an id by creating an instance of the class IdGenerator
        and gets unique id from this instance. After providing this id,
        this instance is never re-used.
        """
        new_id = IdGenerator()
        self.__id = new_id.get_id

    # Used for type comparisons
    def __lt__(self, other):
        return self.id < other.id

    @property
    def label(self) -> str:
        return self.__label

    @label.setter
    def label(self, label) -> None:
        self.__label = label

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name) -> None:
        self.__name = name

    @property
    def attributes(self) -> dict:
        return self.__attributes

    def set_attributes(self, **kwargs):
        for name, value in kwargs.items():
            self.__attributes[name] = value

    def add_attribute(self, name, value, time=None):
        if name not in self.__attributes.keys():
            self.__attributes[name]=[]
        self.__attributes[name].append((value, time))

    def remove_attribute(self, attribute_name):
        if attribute_name in self.__attributes.keys():
            del self.__attributes[attribute_name]
        else:
            print("This object has not an attribute with key {}.".format(
                attribute_name))

