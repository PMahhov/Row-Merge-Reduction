"""Class implementing a simple node."""
from graph_object import GraphObject


class Node(GraphObject):
    """
    Base class for nodes.
    A node has a label, a name, an id, and stores node attributes.
    """

    def __init__(self, label: str = "", name: str="", attributes=None):
        """Initialize attributes of the parent class."""
        super().__init__(label, name, attributes)
