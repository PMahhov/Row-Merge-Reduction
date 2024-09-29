
from idgenerator import IdGenerator
from graph_object import GraphObject
from node import Node
from edge import Edge
from graph import Graph

import copy

printing_mode = True

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

# two datapoints are the same if they have the same value and are in the same column
    # two datapoints in different rows can be the same
    def is_same(self, other) -> bool:
        return self.name == other.name and self.label == other.label

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
# '''    
# def get_relationship(self):
#     return ((edge.head.label,edge.head.name),(edge.tail.label,self.tail.name))
#     # This returns ((Col1,Val1),(Col2,Val2))

# # adding this method to the core edge function
# Edge.get_relationship = get_relationship


class Row(Graph):
    '''
	- nodes: set of datapoints
	- edges: set of relationships
    - first: first node
    - id: id
    - next_row: pointer to the next row, None if last
    - prev_row: pointer to the previous row, None if first
    '''
    def __init__(self, id):
        super().__init__()
        self.first = None
        self.id = id
        self.next_row = None
        self.prev_row = None

    def __str__(self):
        return  ', '.join([str(node) for node in self.nodes])


    # def __eq__(self, other) -> bool:
    #     if len(self.nodes) != len(other.nodes):    
    #         return False
    #     else:
    #         current_node = self.first
    #         second_node = other.first
    #         while current_node.next != None:        # no need to check for second node, since lengths are the same
    #             if current_node.is_same(second_node) == False:
    #                 return False
    #             current_node = current_node.next     
    #             second_node = second_node.next
    #         return True  

    # def __hash__(self) -> int:
    #     return hash(self.first)

    def is_same(self, other) -> bool:
        if len(self.nodes) != len(other.nodes):    
            return False
        else:
            current_node = self.first
            second_node = other.first
            while current_node.next != None:        # no need to check for second node, since lengths are the same
                if current_node.is_same(second_node) == False:    
                    return False
                current_node = current_node.next     
                second_node = second_node.next
            return True   
    

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
            rel = ((edge.head.label,edge.head.name),(edge.tail.label,edge.tail.name))
            relationships.add(rel)  # This returns a relationship in the form ((Col1,Val1),(Col2,Val2))
        return relationships

    def get_id(self):
        return str(self.id)

    def get_node_by_column(self, label):
        # Search for a node whose label matches the given column label
        for node in self.nodes:
            if node.label == label:
                return node
        return None  # Return None if no node matches the label

    def make_null(self, label):
        self.make_null_by_obj(self.get_node_by_column(label))

    def make_null_by_obj(self, node:Datapoint):
        node.make_null()


    

class Table:
    '''
    - rows: set of rows
    - relationships: set of all relationships
    - latest_row_id
    - first_row (Row)
    - rows_dict: dict of id:row
    - certain_rels: set of certain relationships
    - possible_rels: set of possible relationships

    '''
    def __init__(self, column_labels, initial_table):
        self.column_labels = column_labels
        self.rows = set()
        self.latest_row_id = 0
        self.rows_dict = dict()
        prev_row = None
        new_row = None
        for initial_row in initial_table:
            new_row = self.add_row(initial_row, prev_row)
            if prev_row == None:                                # each row gets a prev and next pointer
                self.first_row = new_row
            else:
                prev_row.next_row = new_row
                
            prev_row = new_row

        self.update_all_relationships()


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

    def add_row(self, datapoints_list, prev_row = None):
        self.latest_row_id += 1
        new_row = Row(self.latest_row_id)     
        new_row.prev_row = prev_row
        self.rows_dict[self.latest_row_id] = new_row
        prev_datapoint = None
        for i, datapoint_name in enumerate(datapoints_list):
            current_datapoint = Datapoint(label = self.column_labels[i], 
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
        return new_row

        # print(new_row.get_relationships_count())
        # print(new_row.get_relationships())
    
    def update_all_relationships(self):
        self.relationships = set()
        for row in self.rows:
            r_set = row.get_relationships()
            self.relationships.update(r_set)
        self.certain_rels = set()
        self.possible_rels = set()
        for rel in self.relationships:
            if rel[0][1] == '*' or rel[1][1] == '*':
                self.possible_rels.add(rel)
            else:
                self.certain_rels.add(rel)

    def get_all_relationships_count(self):
        return len(self.relationships)

    def get_certain_relationships_count(self):
        return len(self.certain_rels)
    
    def get_possible_relationships_count(self):
        return len(self.possible_rels)

    def get_row(self, id):
        return self.rows_dict[id]
    
    def make_null(self, row_id, column_label, printing = printing_mode):
        row = self.rows_dict[row_id]
        row.make_null(column_label)
        self.update_all_relationships()
        merge_count = self.check_merges()
        if printing:
            print('nulled',column_label, 'on row',row_id)
            print('merges:',merge_count)

    def get_size(self):
        return len(self.rows)
        
            
    def check_merges(self):
        
        new_rows = copy.copy(self.rows)

        merge_count = 0
        current_row = self.first_row
        other_row = current_row.next_row
        while current_row.next_row != None:         # current row will be compared to all and deleted if duplicate
            while other_row != None:                    # other row is the one being compared to current
                if current_row.is_same(other_row):
                    new_rows.remove(current_row)      
                                                        # we adjust prev/next/first on deletion of a row
                    second_row = current_row.next_row   # second row comes immediately after current
                    if self.first_row == current_row:
                        self.first_row = second_row
                        second_row.prev_row = None
                    else:
                        second_row.prev_row = current_row.prev_row
                        current_row.prev_row.next_row = second_row

                    merge_count += 1
                    break
                else:
                    other_row = other_row.next_row      # if not equal, keep iterating the other row
            current_row = current_row.next_row

        self.rows = new_rows

        return merge_count
    
    

test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']

t1 = Table(test_columns, test_table)
print('TABLE 1')
print (t1)
print('Total relationships:',t1.get_all_relationships_count())
print(t1.relationships)
t1.make_null(row_id=1,column_label='Col2')
print (t1)
print('table size:', t1.get_size())
print('Certain relationships:',t1.get_certain_relationships_count())
print(t1.certain_rels)
print('Possible relationships:',t1.get_possible_relationships_count())
print(t1.possible_rels)

t2 = Table(test_columns, test_table)
t2.make_null(row_id=1, column_label='Col3')
t2.make_null(row_id=2, column_label='Col3')
print('------------------------------------------')
print('TABLE 2')
print (t2)
print('table size:', t2.get_size())
print('Certain relationships:',t2.get_certain_relationships_count())
print(t2.certain_rels)
print('Possible relationships:',t2.get_possible_relationships_count())
print(t2.possible_rels)