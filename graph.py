"""Class implementing simple graph."""

# TODO: Add method to generate a unique id for a node.

import json
from edge import Edge
from node import Node


class Graph:
    """
    Base class for a graph.

    This is a basic implementation of a directed graph. This can be expanded
    upon with adding other properties and methods.

    The nodes and edges are in a set.
    The incoming, outgoing edges, to, from a node are in a dict.

    """

    def __init__(self) -> None:
        """Initialize a graph as an empty dictionary."""

        self.__nodes = set()
        self.__edges = set()
        self.__incoming = dict()
        self.__outgoing = dict()

    # Helper functions below.
    def _add_node(self, candidate_node):
        """Function to add a new node to the graph."""

        # First add it to the node set.
        self.__nodes.add(candidate_node)

        # Then add entries for the node in the incoming/outgoing dictionaries.
        self.__incoming[candidate_node] = set()
        self.__outgoing[candidate_node] = set()

    def _check_node_for_new_edge(self, candidate_node) -> bool:
        """Function to test if node for edge exists."""

        if candidate_node not in self.__nodes:
            raise ValueError("The provided node {} for this edge does not "
                             "exist in the graph".format(candidate_node))

        return True

    def _node_remover(self, node_to_remove):
        """Helper function to remove the node from the node set."""

        self.__nodes.remove(node_to_remove)

    def _edge_remover(self, edge_to_remove):
        """Helper function to remove the edge from the edge set."""

        # Remove the edge.
        self.__edges.remove(edge_to_remove)

    # Functions below.
    def add_node(self, candidate_node: Node) -> None:
        """Adds a node to the self.__nodes dictionary in the graph."""

        # First test if it is a node in the set and if not raise error.
        if isinstance(candidate_node, Node):
            if candidate_node not in self.__nodes:
                self._add_node(candidate_node)
            else:
                raise ValueError("The node cannot be added as a node with id {} already exists.".\
                                 format(candidate_node.id))
        else:
            raise ValueError("The provided entry {} is not a node.".format(candidate_node))

    def create_edge(self, candidate_tail: Node, candidate_head: Node) -> Edge:
        """Creates an edge. It checks if candidate tail and head exist."""

        new_edge = object
        if (self._check_node_for_new_edge(candidate_tail) and
                self._check_node_for_new_edge(candidate_head)):
            new_edge = Edge(candidate_tail, candidate_head)

        return new_edge

    def add_edge(self, new_edge: Edge) -> None:
        """Adds an edge to the self.__edges dictionary in the graph."""

        # Test if edge already exists in self.__edges and if not add edge.

        if new_edge in self.__edges:
            raise ValueError("The edge already exists.")
        else:
            self.__edges.add(new_edge)
            self.__incoming[new_edge.head].add(new_edge)
            self.__outgoing[new_edge.tail].add(new_edge)

    @property
    def nodes(self) -> set:
        """Provides nodes of the graph."""

        return self.__nodes

    def provide_adjacency_out(self, node: Node) -> dict:
        """Provides adjacency out list for a node."""

        return self.__outgoing[node]

    def provide_adjacency_in(self, node: Node):
        """Provides adjacency in list for a node, given node_id."""

        return self.__incoming[node]

    @property
    def edges(self) -> set:
        """Shows edges of the graph."""

        return self.__edges

    def remove_node(self, node: Node) -> None:
        """Removes a node."""

        # First check if the node is a node.
        if type(node) != Node:
            raise ValueError("The provided node is not of type Node.")

        if node in self.__nodes:

            # Remove the edge entries in incoming/outgoing dictionaries.
            for edge_to_remove in self.__incoming[node]:
                for tail, edge_set in self.__outgoing.items():
                    if edge_to_remove in edge_set:
                        self.__outgoing[tail].remove(edge_to_remove)

            for edge_to_remove in self.__outgoing[node]:
                for head, edge_set in self.__incoming.items():
                    if edge_to_remove in edge_set:
                        self.__incoming[head].remove(edge_to_remove)

            # Then remove the edges connected to the node.
            edges_to_remove = self.__incoming[node] | self.__outgoing[node]
            for edge_to_remove in edges_to_remove:
                self.remove_edge(edge_to_remove)

            # Remove the keys in the incoming/outgoing dictionaries.
            del self.__incoming[node]
            del self.__outgoing[node]

            # Then remove the node.
            self._node_remover(node)

        else:
            print("The node is not part of the graph.")

    def remove_edge(self, edge_to_remove: Edge) -> None:
        """Removes an edge."""
        # TODO: Update
        if type(edge_to_remove) == Edge:
            self._edge_remover(edge_to_remove)
        else:
            raise ValueError("The provided edge is not of type Edge.")


    def load_graph(self, graph_data_name):
        with open(graph_data_name) as graph_file:
            graph_data = json.load(graph_file)
            for node_name, node_data in graph_data["nodes"].items():
                new_node = Node(label=node_data["label"],
                                    name=node_name,
                                    attributes=node_data["attribute_data"])
                self.add_node(new_node)

            for edge_name, edge_data in graph_data["edges"].items():
                head_node = [node for node in self.__nodes if node.name ==
                             edge_data["head"]]
                tail_node = [node for node in self.__nodes if node.name ==
                             edge_data["tail"]]
                new_edge = self.create_edge(tail_node[0], head_node[0])
                new_edge.name = edge_name
                new_edge.label = edge_data["label"]
                new_edge.set_attributes(**edge_data["attribute_data"])
                self.add_edge(new_edge)

"""
# Test of functionality.
# First create a graph and a few nodes.
graph = Graph()
node1 = Node()
node2 = Node()

# Create a node with a label and id.
node3 = Node("City")

# Create a node with an id and fill the attributes' dictionary.
node4 = Node("City")

# The functionality below is now disabled
# node4.attributes["pm"] = "Winston Churchill"
# node4.attributes["mayor"] = "Boris Johnson"


# Show the nodes
print("Show the nodes.")
print(node1, node2, node3, node4)
print()
# And the content of the nodes.
nodes = [node1, node2, node3, node4]
print("Show nodes including id, label and attributes.")
for i in range(len(nodes)):
    print("node{}: Node id {}, Node label {}, Node attributes {} ".
          format(i, nodes[i].id, nodes[i].label,nodes[i].attributes))
print()

# Other node functionality.
print("Create another node and add some attributes.")
node5 = Node()
node5.set_attributes(name="Zorro", street="Calz. Ignacio Zaragoza",
                     city="Mexico City")
print("This is node {} with the following attributes {}.".
      format(node5.id, node5.attributes))
print()
print("another test")
print(node5.attributes["name"])

print("Create again another node and add some other attributes.")
node6 = Node()
node6.set_attributes(name=[("Fonda", 2005)], city="Orlando")
print("This is node {} with the following attributes {}.".
      format(node6.id, node6.attributes))
print()

print("And adding additional attributes.")
node6.add_attribute("address", "Utrecht", 2010)
print("This is node {} with the following attributes {}.".
      format(node6.id, node6.attributes))
print()

print("Adding additional attributes again.")
node6.add_attribute("name", "Moore", 2012)
print(node6.attributes)
print()

print("And again...")
node6.add_attribute("name", "Fonda")
print(node6.attributes)
print()

print("Removing the 'city' attribute...")
node6.remove_attribute("city")
print("And indeed it's gone:")
print(node6.attributes)
print()

node7 = Node(attributes={"pm":"Churchill"})
print("This is node {} with the attributes {} created at instantiation.".
      format(node7.id, node7.attributes))
print()

# Add the nodes to the graph.
for node in nodes:
    graph.add_node(node)

# A test to fail
# graph.add_node(node1)

# Show the nodelist.
print("Show all nodes in the graph.")
print(graph.nodes)
print()

# Create an edge.
an_edge = graph.create_edge(node1, node2)
print("Creating an edge from nodes in the graph.")
print("Showing edge with edge-id {} {} and tail {} and head {}.".format(
    an_edge.id, an_edge, an_edge.tail, an_edge.head))
print()

# Create another edge.
another_edge = graph.create_edge(node1, node4)

# A test to fail
# fail_edge = Edge(node1, "Fail_node")

# Create other edge to node 1.
yet_another_edge = graph.create_edge(node1, node3)

# Add the edges to the graph.
edge_list = [an_edge, another_edge, yet_another_edge]
print("Created a few more edges and add them to the graph.")
for e in edge_list:
    graph.add_edge(e)
    print("Added edge {} with head {} and tail {}".format(e, e.head, e.tail))
print()

# Adding more edges to demo incoming/outgoing edges.
print("Adding two more edges.")
n_edge = graph.create_edge(node2, node4)
n_edge2 = graph.create_edge(node2, node1)
n_edge_list = [n_edge, n_edge2]
for e in n_edge_list:
    graph.add_edge(e)

# Show the outgoing and incoming edges from/to a node
print("Showing outgoing and incoming edges per node.")
print(graph.provide_adjacency_out(node1))
for ex_node in graph.nodes:
    for ex_edge in graph.provide_adjacency_out(ex_node):
        print("Node {} has outgoing edge {}.".format(ex_node.id,
                                                         ex_edge.id))
        print("Edge {} starts with node {} and ends with node {}.".format(
            ex_edge.id, ex_edge.tail.id, ex_edge.head.id))

    for ex_edge in graph.provide_adjacency_in(ex_node):
        print("Node {} has incoming edge {}.".format(ex_node.id, ex_edge.id) )
        print("Edge {} starts with node {} and ends with node {}.".format(
            ex_edge.id, ex_edge.tail.id, ex_edge.head.id))

# Remove a node.
print("Removing node4.")
graph.remove_node(node4)
print("Remaining nodes: expect 3 as we delete 1 node.")
print(graph.nodes)
print("Remaining edges: expect 3 as this node was connected to 1 edge.")
print(graph.edges)


# Remove another node.
print("Removing node1")
graph.remove_node(node1)
print("Remaining nodes: expect 2.")
print(graph.nodes)
print("And the remaining edges: expect 0, as node 1 had all remaining "
      "edges.")
print(graph.edges)
print("No edges shown.")

# Test load functionality.
print()
print("Demonstrating load facility.")
new_graph = Graph()
print("Loading file 'graph_data.json'.")
new_graph.load_graph('../testdir/graph_data.json')
print("Done")
for demo_node in new_graph.nodes:
    print("Showing node with node_object: {}, node_id: {}, node_name: {}.".format(
    demo_node, demo_node.id, demo_node.name))
    print("Showing the node location for node: {}, x = {}, y = {}.".format(
        demo_node.name,
        demo_node.attributes["x_pos"],
        demo_node.attributes["y_pos"]))

for demo_edge in new_graph.edges:
    print("Showing edge with edge_object: {}, edge_id: {}, edge_name: {}.".
          format(demo_edge, demo_edge.id, demo_edge.name))
print()
for demo_edge in new_graph.edges:
    print("Now showing the attributes of {}.".format(demo_edge.name))
    print(demo_edge.attributes)
    print("Or just the road type: {}.".format(demo_edge.attributes[
              "road_type"]))
print("Demonstrating we can add new attributes to the edge e.g. a lane list.")
for edge in new_graph.edges:
    if edge.name == "Edge1":
        edge.set_attributes(lanes=[])
for demo_edge in new_graph.edges:
    print("Now showing the attributes of {}.".format(demo_edge.name))
    print(demo_edge.attributes)
print()
print("Add a number of lanes.")
number_of_lanes = 3

for demo_edge in new_graph.edges:
    if demo_edge.name == "Edge1":
        demo_edge.attributes["lanes"] = [number for number in range(
            number_of_lanes)]
        print(demo_edge.attributes)"""