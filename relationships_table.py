
from idgenerator import IdGenerator
from graph_object import GraphObject
from node import Node
from edge import Edge
from graph import Graph

import copy

class Datapoint(Node):
    '''
	- name: value
	- label: column name
	- id: id
    - attributes: empty dict
    - next: pointer to next datapoint in row if exists
    '''
    def __init__(self, label: str = "", name: str="", next = None, attributes=None):
        super().__init__(label, name, attributes)
        self.next = next

    def isnull(self):
        if self.name == "*":
            return True

    def __str__(self):
        return self.name

    def make_null(self):
        self.name = '*'

'''

    # a relationship is a bidirectional edge
    # we go in order of linked list of nodes
class Edge
    - name: value, default ''
	- label: ''
	- id: id
	- head (datapoint)
	- tail (datapoint)
    - attributes: empty dict
'''    
def get_relationship(self):
    return ((self.head.label,self.head.name),(self.tail.label,self.tail.name))  
    # This returns ((Col1,Val1),(Col2,Val2))

Edge.get_relationship = get_relationship


class Row(Graph):
    '''
	- nodes: set of datapoints
	- edges: set of relationships
    - first: first node
    - id: id
    '''
    def __init__(self, id):
        super().__init__()
        self.first = None
        self.id = id

    def __str__(self):
        return  ', '.join([str(node) for node in self.nodes])

    def create_all_edges(self):
        current_node = self.first
        while current_node.next != None:
            second_node = current_node.next
            while second_node != None:
                new_edge = self.create_edge(second_node, current_node)
                # print('added',second_node, current_node)
                second_node = second_node.next
                self.edges.add(new_edge)
            current_node = current_node.next
    

    def get_relationships_count(self):
        count = len(self.edges)
        assert(count.is_integer())
        return int(count)

    def get_relationships(self):
        relationships = set()
        for edge in self.edges:
            relationships.add(edge.get_relationship())
        return relationships

    def get_id(self):
        return str(self.id)

    def get_node_by_column(self, label):
        # Search for a node whose label matches the given column label
        for node in self.nodes:
            if node.label == label:
                return node
        return None  # Return None if no node matches the label

    def make_null_by_col(self, label):
        self.make_null(self.get_node_by_column(label))

    def make_null(self, node:Datapoint):
        node.make_null()
    

class Table:
    '''
    - rows: set of rows
    - relationships: set of all relationships
    - latest_row_id
    - rows_dict: dict of id:row
    '''
    def __init__(self, column_labels, initial_table):
        self.column_labels = column_labels
        self.rows = set()
        self.latest_row_id = 0
        self.rows_dict = dict()
        for initial_row in initial_table:
            self.add_row(initial_row)
        self.get_all_relationships()


    def __str__(self):      # printing out the table
        column_header = ', '.join(self.column_labels)        
        # rows_str = '\n'.join([str(row) for row in self.rows])
        # return f'{column_header}\n{row_strs}'

        # Format each row based on the correct column order
        row_strs = []
        for row in self.rows:
            # For each label in column_labels, fetch the corresponding node
            row_values = []
            for label in self.column_labels:
                node = row.get_node_by_column(label)
                if node:
                    row_values.append(str(node))
                else:
                    row_values.append('')  # Empty string if no node for this label
            row_values.append('--id: '+row.get_id())
            row_strs.append(', '.join(row_values))
        return f'{column_header}\n' + '\n'.join(row_strs)

    def add_row(self, datapoints_list):
        self.latest_row_id += 1
        new_row = Row(self.latest_row_id)     
        self.rows_dict[self.latest_row_id] = new_row
        prev_datapoint = None
        for i, datapoint_name in enumerate(datapoints_list):
            current_datapoint = Datapoint(  label = self.column_labels[i], 
                        name = datapoint_name
            )
            if prev_datapoint == None:
                new_row.first = current_datapoint
            else:
                prev_datapoint.next = current_datapoint
            prev_datapoint = current_datapoint
            new_row.add_node(current_datapoint)

        new_row.create_all_edges()
        self.rows.add(new_row)

        # print(new_row.get_relationships_count())
        # print(new_row.get_relationships())
    
    def get_all_relationships(self):
        self.relationships = set()
        for row in self.rows:
            r_set = row.get_relationships()
            self.relationships.update(r_set)

    def get_all_relationships_count(self):
        return len(self.relationships)

    def get_row(self, id):
        return self.rows_dict[id]
    




    
    

test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']

created_test_table = Table(test_columns, test_table)
print (created_test_table)
print('Total relationships:',created_test_table.get_all_relationships_count())
print(created_test_table.relationships)