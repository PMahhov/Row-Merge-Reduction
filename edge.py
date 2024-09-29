"""Class implementing a simple edge."""

from graph_object import GraphObject
from node import Node


class Edge(GraphObject):
    """
     Class for edges.
     An edge connects a head (of type Node) and a tail (of type Node).
     An edge has a label, a name and an id.
     Furthermore, a dictionary for attributes.
     """

    def __init__(self,  tail: Node, head: Node,
                 label: str = "",
                 name: str = "",
                 attributes=None):
        """Initialize attributes of the parent class."""
        super().__init__(label, name, attributes)
        self.tail = tail
        self.head = head

    @property
    def tail(self) -> Node:
        return self.__tail

    @tail.setter
    def tail(self, tail: Node) -> None:
        if isinstance(tail, Node):
            self.__tail = tail
        else:
            raise ValueError("The provided tail {} is not of type Node.".format(tail))

    @property
    def head(self) -> Node:
        return self.__head

    @head.setter
    def head(self, head: Node) -> None:
        if isinstance(head, Node):
            self.__head= head
        else:
            raise ValueError("The provided head {} is not of type Node.".format(head))
