
from idgenerator import IdGenerator
from graph_object import GraphObject
from node import Node
from edge import Edge
from graph import Graph

import copy

printing_mode = False
short_printing = False

class Datapoint(Node):
    '''
	- name: value
	- label: column name
	- id: id
    - attributes: empty dict
    - next: pointer to next datapoint in row if exists
    - former_value: if nulled, what this used to be
    '''
    def __init__(self, label: str = "", name: str="", next = None, attributes=None):
        super().__init__(label, name, attributes)
        self.next = next
        self.former_value = self.name


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

    def get_column(self):
        return self.label

    def revert_nulling(self):
        self.name = self.former_value

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
        curr = self.first
        output = []
        while True:
            output.append(str(curr))
            if curr.next != None:
                curr = curr.next
            else:
                break
        return  ', '.join(output)


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
            if current_node.is_same(second_node) == False:      # must check last column as well
                return False
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
        return self.id

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
    - domains: dict of column_label:domain size

    '''
    def __init__(self, column_labels, initial_table, domains):      # TODO: make domains optional, give equal value if not specified
        self.column_labels = column_labels
        self.domains = domains
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
            row_values.append('--id: '+str(row.get_id()))
            row_strs.append(', '.join(row_values))
        return f'{column_header}\n' + '\n'.join(row_strs)

    def is_same(self, other) -> bool:
        if self.get_size() != other.get_size():
            return False
        else:
            current_row = self.first_row
            other_row = other.first_row
        while True:
            if current_row.is_same(other_row) == False:
                return False
            if current_row.next_row != None:
                current_row = current_row.next_row
                other_row = other_row.next_row
            else:
                return True

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

    # def get_wrong_answers_count(self):
    def get_expanded_possible_relationships_count(self, printing = printing_mode):
        # a relationship is in the form ((Col1,Val1),(Col2,Val2))

        unknowns = dict()     # unknowns[frozenset([column, other column])][column] =
                            # = for either column it gives a dictionary of other value:own value
                            # for each column pair that has incompleteness, the unknown answers are dom(own column)*len(other values) - len of all (own values)

                            # using frozenset so it can be used as an unordered immutable key to dict

        for possible_rel in self.possible_rels:
            # print('starting',possible_rel)
            ((col1,val1),(col2,val2)) = possible_rel
            current_set = frozenset([col1, col2])
            if current_set not in unknowns.keys():
                unknowns[current_set] = {col1: dict(), col2: dict()}
                # unknowns[current_set] = {}


            if val1 == '*' and val2 == '*':    # if the rel is * *
                unknowns[current_set] = {col1:'full', col2:'full'}
            else:
                if val1 == '*':                   # if the rel is * X
                    if col2 not in unknowns[current_set].keys():
                        unknowns[current_set][col2] = dict()
                    if unknowns[current_set][col2] != 'full':
                        if val2 not in unknowns[current_set][col2]:
                            unknowns[current_set][col2][val2] = set()                                	            # add other value if not present
                        for certain_rel in self.certain_rels:
                            ((cer_col1,cer_val1),(cer_col2,cer_val2)) = certain_rel
                            if cer_col1 == col1 and cer_col2 == col2 and cer_val2 == val2 :           # the columns must match and the other value must match
                                if cer_val2 not in unknowns[current_set][col2]:
                                    unknowns[current_set][col2][cer_val2] = set()
                                unknowns[current_set][col2][cer_val2].add(cer_val1)                                                   # add X if not in dict already


                else:
                    if col1 not in unknowns[current_set].keys():
                        unknowns[current_set][col1] = dict()
                    if unknowns[current_set][col1] != 'full':
                        if val1 not in unknowns[current_set][col1]:
                            unknowns[current_set][col1][val1] = set()  
                        for certain_rel in self.certain_rels:
                            ((cer_col1,cer_val1),(cer_col2,cer_val2)) = certain_rel
                            if cer_col1 == col1 and cer_col2 == col2 and cer_val1 == val1 :           # the columns must match and the other value must match
                                if cer_val1 not in unknowns[current_set][col1]:
                                    unknowns[current_set][col1][cer_val1] = set()
                                unknowns[current_set][col1][cer_val1].add(cer_val2)


        # go through the entirety of the wrongs dict and get the dom - wrongs values or self.domains[col1] * self.domains[col2] if both full
        if printing:
            print('unknowns final:',unknowns)
        expanded_possible_rel_count = 0
        for current_dict in unknowns.values():            
            col1, col2 = current_dict.keys()
            if printing:
                print('current_dict',current_dict)
                print('col 1 and col2', col1, col2)
            if current_dict[col1] == 'full' and current_dict[col2] == 'full':
                expanded_possible_rel_count += self.domains[col1] * self.domains[col2]
            else:
                own_vals = 0
                for key in current_dict[col1].keys():
                    own_vals += len(current_dict[col1][key])
                expanded_possible_rel_count += self.domains[col2] * len(current_dict[col1].keys()) - own_vals
                if printing:
                    print('self.domains[col2]',self.domains[col2])
                    print('current_dict[col1]',current_dict[col1])
                    print('length:',len(current_dict[col1].keys()))
                    print('own vals:', own_vals)
                    print(self.domains[col2] * len(current_dict[col1].keys()) - own_vals)
                own_vals = 0
                for key in current_dict[col2].keys():
                    own_vals += len(current_dict[col2][key])
                expanded_possible_rel_count += self.domains[col1] * len(current_dict[col2].keys()) - own_vals
                if printing:
                    print('self.domains[col1]',self.domains[col1])
                    print('current_dict[col2]',current_dict[col2])
                    print('length:',len(current_dict[col2].keys()))
                    print('own vals:', own_vals)
                    print(self.domains[col1] * len(current_dict[col2].keys()) - own_vals)
        return expanded_possible_rel_count
     


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

    def make_null_by_obj(self, row, datapoint):
        row.make_null_by_obj(datapoint)
        self.update_all_relationships()
        merge_count = self.check_merges()

    
    def make_null_get_copy(self, row_id, column_label, printing = printing_mode):
        new_table = copy.deepcopy(self)
        row = new_table.rows_dict[row_id]
        row.make_null(column_label)
        new_table.update_all_relationships()
        merge_count = new_table.check_merges()
        if printing:
            print('nulled',column_label, 'on row',row_id)
            print('merges:',merge_count)
        return new_table

    def get_size(self):
        return len(self.rows)
        
            
    def check_merges(self, printing = printing_mode):         # guarantees that only one identical row exists in a table

        merge_count = 0
        current_row = self.first_row
        
        while current_row != None:
            prev_row = current_row
            next_row = current_row.next_row

            while next_row != None:
                if current_row.is_same(next_row):
                    prev_row.next_row = next_row.next_row
                    self.rows.remove(next_row)
                    merge_count += 1
                else:
                    prev_row = next_row
                
                next_row = next_row.next_row
            
            current_row = current_row.next_row


        return merge_count



        # new_rows = copy.copy(self.rows)
        # other_row = current_row.next_row
        # print('current_row is now',current_row, 'with id',current_row.id)
        # # print('other row is now', other_row, 'with id', other_row.id)
        # while current_row.next_row != None:         # current row will be compared to all and deleted if duplicate
        #     if current_row == other_row:
        #         other_row = other_row.next_row
        #     while other_row != None:                    # other row is the one being compared to current
        #         print('other row is now', other_row, 'with id', other_row.id)
        #         if current_row.is_same(other_row):
        #             new_rows.remove(current_row)      
        #             # if printing:
        #             # print(self)
        #             print('removing row',current_row, 'it is same as',other_row)
        #                                                 # we adjust prev/next/first on deletion of a row
        #             second_row = current_row.next_row   # second row comes immediately after current
        #             if self.first_row == current_row:
        #                 self.first_row = second_row
        #                 second_row.prev_row = None
        #             else:
        #                 second_row.prev_row = current_row.prev_row
        #                 current_row.prev_row.next_row = second_row

        #             merge_count += 1
        #             break
        #         else:
        #             other_row = other_row.next_row      # if not equal, keep iterating the other row
        #     current_row = current_row.next_row          # the last row does not need to be compared
        #     print('current_row is now',current_row, 'with id',current_row.id)

        # self.rows = new_rows
        # print('after',self)
        # return merge_count
    

def perform_nulling(table, nulls, get_copy = False, short_printing = True, long_printing = printing_mode):
    # print (table)
    if get_copy:
        table = copy.deepcopy(table)
    if long_printing:
        short_printing = True
        print('Original table size:',table.get_size())
    # if long_printing:
    #     print('Original relationships:',table.get_all_relationships_count())
    #     print(table.relationships)
    for row_id, column_label in nulls:
        table.make_null(row_id,column_label)
    if short_printing:
        print (table)
        print('Final table size:', table.get_size())
        print('Certain relationships:',table.get_certain_relationships_count())
    if long_printing:
        print(table.certain_rels)
    if short_printing:
        print('Possible relationships:',table.get_possible_relationships_count())
    if long_printing:
        print(table.possible_rels)
        print('Domains:',domains)
    if short_printing:
        print('Count of expanded possible relationships:', table.get_expanded_possible_relationships_count())
    return table


test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']
domains = {'Col1':3, 'Col2':3, 'Col3':2}


if printing_mode:
    short_printing = True

'''
if short_printing:
    print('TABLE 1')

t1 = Table(test_columns, test_table, domains)
t1 = perform_nulling(t1, [(1, 'Col2')], short_printing=short_printing)
assert (t1.get_expanded_possible_relationships_count() == 5)



if short_printing:
    print('------------------------------------------')
    print('TABLE 2')

t2 = Table(test_columns, test_table, domains)
t2 = perform_nulling(t2, [(1,'Col3'),(2,'Col3')], short_printing=short_printing)
assert(t2.get_expanded_possible_relationships_count()==4)


if short_printing:
    print('------------------------------------------')
    print('TABLE 3')

t3 = Table(['Col2','Col3'], [['A','A'],['B','B']], domains)
t3 = perform_nulling(t3, [(1,'Col2'),(2,'Col3')], short_printing=short_printing)
assert(t3.get_expanded_possible_relationships_count() == 5)


if short_printing:
    print('------------------------------------------')
    print('TABLE 4')
t4 = Table(['Col2','Col3'], [['A','A'],['B','B']], domains)
t4 = perform_nulling(t4, [(1,'Col2'),(2,'Col3'),(1,'Col3'),(2,'Col2')], short_printing=short_printing)
assert(t4.get_expanded_possible_relationships_count() == 6)

# short_printing = True
if short_printing:
    print('------------------------------------------')
    print('TABLE 5')
t5 = Table(test_columns, test_table, domains)
t5 = perform_nulling(t5, [(1,'Col3'),(1,'Col1'),(1,'Col2')], short_printing=short_printing)
assert(t5.get_expanded_possible_relationships_count() == 21)


if short_printing:
    print('------------------------------------------')
    print('TABLE 6')
t6 = Table(test_columns, test_table, domains)
t6 = perform_nulling(t6, [(1,'Col3'),(1,'Col1'),(1,'Col2'),(2,'Col1'),(2,'Col2'),(2,'Col3')], short_printing=short_printing)
assert(t6.get_expanded_possible_relationships_count() == 21)


short_printing = True
if short_printing:
    print('------------------------------------------')
    print('TABLE 7')
t7 = Table(test_columns, test_table, domains)
t7 = perform_nulling(t7, [(1,'Col3'),(1,'Col2'),(2,'Col2'),(2,'Col3')], short_printing=short_printing)
'''