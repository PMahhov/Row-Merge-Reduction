
from node import Node

import json
import copy

printing_mode = False
short_printing = False
testing = False

class Row(Node):
    '''
    - id: id
    - label: unused
    - order: if original, then sequence number of creation (int), otherwise None
    - attributes: dict of column:value
    - original_attributes? [not implemented yet]
    - relationships: list of set((Col1,Val1),(Col2,Val2))
    
    '''
    def __init__(self, order = None, label: str = "", name: str = "", attributes=None):
        super().__init__(label, name, attributes)
        self.order = order

    def __str__(self) -> str:
        return str(self.attributes)

    def get_value(self, column):
        return self.attributes[column]

    def set_value(self, column, value):
        self.attributes[column] = value

    def get_id(self):
        return self.id

    def is_same(self, other_row):
        if set(self.attributes.items()) == set(other_row.attributes.items()):
            return True
        else:
            return False

    def calc_relationships(self):
        cols = list(self.attributes.keys())
        self.relationships = list()
        for i, col in enumerate(cols):
            for col2 in cols[i+1:]:
                if i != len(cols):
                    # rel = set()
                    # rel.add((col, self.attributes[col]))
                    # rel.add((col2, self.attributes[col2]))
                    rel = list()
                    rel.append((col, self.attributes[col]))
                    rel.append((col2, self.attributes[col2]))
                    rel = frozenset(rel)
                    self.relationships.append(rel)


    def get_relationships(self):
        return self.relationships

    def get_relationship_count(self):
        return len(self.relationships)

class Table:
    '''
    - rows: list of row objects
    # - rows_dict: dict of id:row
    - columns: list of column names
    - domains: dict of column_label:domain size
    - relationships: set of all relationships
    - certain_rels: set of certain relationships
    - possible_rels: set of possible relationships
    - origin: 'lists', 'row objects', 'json'?? [TODO]
    '''
    def __init__(self, columns:list, initial_list: list, domains: dict, origin = 'lists'):
        self.rows = []
        if origin == 'lists':
            self.columns = columns
            self.domains = domains
            # self.rows_dict = {}
            for i, initial_row in enumerate(initial_list):
                self.create_row(initial_row, i)
        elif origin == 'row objects':
            self.columns = columns
            self.domains = domains
            for row_object in initial_list:
                self.rows.append(row_object)
        else:
            raise ValueError ('Unimplemented table origin format')


        self.update_all_relationships()

    def __str__(self):      # printing out the table
        column_header = ', '.join(self.columns)        

        row_strs = []
        for row in self.rows:
            row_values = []
            for column in self.columns:
                row_values.append(row.attributes[column])
            row_values.append('--id: '+str(row.get_id()))       # show row id as well
            row_strs.append(', '.join(row_values))
        return f'{column_header}\n' + '\n'.join(row_strs)

    # def load_table(self):
    #     with open(self.name) as graph_file:
    #         graph_data = json.load(graph_file)
    #         for node_name, node_data in graph_data["nodes"].items():
    #             new_node = Node(label=node_data["label"],
    #                                 name=node_name,
    #                                 attributes=node_data["attribute_data"])
    #             self.add_node(new_node)        

    def create_row(self, new_row, order):
        row_object = Row(order)
        if len(new_row) != len(self.columns):
            raise ValueError('Added row length does not match the number of columns')
        for i, value in enumerate(new_row):
            row_object.set_value(self.columns[i], value)
        self.rows.append(row_object)
        # self.rows_dict[row_object.get_id()] = row_object

    def remove_row(self, row):
        self.rows.remove(row)

    def get_size(self):
        return len(self.rows)

    def update_all_relationships(self):
        self.relationships = set()
        for row in self.rows:
            row.calc_relationships()
            for rel in row.get_relationships():
                self.relationships.add(rel)

        self.possible_rels = set()
        self.certain_rels = set()

        for rel in self.relationships:
            possible = False
            for component in rel:
                if component[1] == '*':
                    self.possible_rels.add(rel)
                    possible = True
            if possible == False:
                self.certain_rels.add(rel)

    def get_relationships(self):
        return self.relationships

    def get_certain_relationships_count(self):
        return len(self.certain_rels)

    def get_unexp_possible_relationships_count(self):
        return len(self.possible_rels)

    def get_expanded_possible_relationships_count(self, printing = printing_mode):
         # a relationship is in the form frozenset((Col1,Val1),(Col2,Val2))

        unknowns = dict()     # unknowns[frozenset([column, other column])][column] =
                            # = for either column it gives a dictionary of other value:own value
                            # for each column pair that has incompleteness, the unknown answers are dom(own column)*len(other values) - len of all (own values)

                            # using frozenset so it can be used as an unordered immutable key to dict
        # print('all possibles:',self.possible_rels)
        # print('all certains', self.certain_rels)

        double_counting_compensation = 0
        double_counting = False
        double_star_adjustment = 0

        for possible_rel in self.possible_rels:
            ((col1,val1),(col2,val2)) = possible_rel
            current_set = frozenset([col1, col2])
            if current_set not in unknowns.keys():
                unknowns[current_set] = {col1: dict(), col2: dict()}
                # unknowns[current_set] = {}

            if val1 == '*' and val2 == '*':    # if the rel is * *
                if unknowns[current_set][col1] != 'full':
                    unknowns[current_set] = {col1:'full', col2:'full'}
                    for certain_rel in self.certain_rels:
                        ((cer_col1,cer_val1),(cer_col2,cer_val2)) = certain_rel         # every certain rel with same columns needs to be removed
                        if (cer_col1 == col1 and cer_col2 == col2) or (cer_col1 == col2 and cer_col2 == col1):
                            double_star_adjustment += 1
            else:
                if val1 == '*':                   # if the rel is * X
                    if col2 not in unknowns[current_set].keys():
                        unknowns[current_set][col2] = dict()
                    if unknowns[current_set][col2] != 'full':
                        if val2 not in unknowns[current_set][col2]:
                            unknowns[current_set][col2][val2] = set()                                	            # add other value if not present
                        for certain_rel in self.certain_rels:
                            ((cer_col1,cer_val1),(cer_col2,cer_val2)) = certain_rel
                            # print(possible_rel,'vs',certain_rel)
                            if cer_col1 == col1 and cer_col2 == col2 and cer_val2 == val2 :           # the columns must match and the other value must match
                                if cer_val2 not in unknowns[current_set][col2]:
                                    unknowns[current_set][col2][val2] = set()
                                unknowns[current_set][col2][val2].add(cer_val1)              # add X if not in dict already
                                # print('adding', cer_val1)
                            elif cer_col2 == col1 and cer_col1 == col2 and cer_val1 == val2:
                                # print('option 2a')
                                if cer_val1 not in unknowns[current_set][col2]:
                                    unknowns[current_set][col2][val2] = set()
                                unknowns[current_set][col2][val2].add(cer_val2)
                                # print('adding', cer_val2)
                                # print('now it is', unknowns[current_set][col2][val2])
                        for possible_rel_2 in self.possible_rels:               # check for * X, X * situation
                            # print('checking',possible_rel_2,'vs',possible_rel)
                            if possible_rel_2 != possible_rel:
                                ((pos_col1,pos_val1),(pos_col2,pos_val2)) = possible_rel_2
                                if pos_col1 == col1 and pos_col2 == col2 and pos_val2 == '*':
                                    if pos_val2 not in unknowns[current_set][col2]:
                                        unknowns[current_set][col2][val2] = set()               # here the other row's '*' stands for whatever is in the original row beside its '*'
                                    unknowns[current_set][col2][val2].add(pos_val1)
                                    # print('adding', pos_val1, 'other is', pos_val2)
                                    if double_counting == True:
                                        double_counting_compensation += 1
                                        double_counting = False
                                    else:
                                        double_counting = True

                                elif pos_col1 == col2 and pos_col2 == col1 and pos_val1 == '*':
                                    if pos_val1 not in unknowns[current_set][col2]:
                                        unknowns[current_set][col2][val2] = set()
                                    unknowns[current_set][col2][val2].add(pos_val2)
                                    # print('adding', pos_val2, 'other is', pos_val1)
                                    if double_counting == True:
                                        double_counting_compensation += 1
                                        double_counting = False
                                    else:
                                        double_counting = True


                else:
                    if col1 not in unknowns[current_set].keys():
                        unknowns[current_set][col1] = dict()
                    if unknowns[current_set][col1] != 'full':
                        if val1 not in unknowns[current_set][col1]:
                            unknowns[current_set][col1][val1] = set()  
                        for certain_rel in self.certain_rels:
                            ((cer_col1,cer_val1),(cer_col2,cer_val2)) = certain_rel
                            # print(possible_rel,'vs',certain_rel)
                            if cer_col1 == col1 and cer_col2 == col2 and cer_val1 == val1 :           # the columns must match and the other value must match
                                if cer_val1 not in unknowns[current_set][col1]:
                                    unknowns[current_set][col1][val1] = set()
                                unknowns[current_set][col1][val1].add(cer_val2)
                                # print('adding', cer_val2)
                            elif cer_col2 == col1 and cer_col1 == col2 and cer_val2 == val1 :           # the columns must match and the other value must match
                                if cer_val2 not in unknowns[current_set][col1]:
                                    unknowns[current_set][col1][val1] = set()
                                # print('before it is', unknowns[current_set][col1][val1])
                                unknowns[current_set][col1][val1].add(cer_val1)              # add X if not in dict already
                                # print('adding', cer_val1)
                                # print('now it is', unknowns[current_set][col1][val1])

                        for possible_rel_2 in self.possible_rels:               # check for * X, X * situation
                            if possible_rel_2 != possible_rel:
                                ((pos_col1,pos_val1),(pos_col2,pos_val2)) = possible_rel_2
                                if pos_col1 == col1 and pos_col2 == col2 and pos_val1 == '*':
                                    if pos_val1 not in unknowns[current_set][col1]:
                                        unknowns[current_set][col1][val1] = set()               # here the other row's '*' stands for whatever is in the original row beside its '*'
                                    unknowns[current_set][col1][val1].add(pos_val2)
                                    # print('adding', pos_val2, 'other is', pos_val1)
                                    if double_counting == True:
                                        double_counting_compensation += 1
                                        double_counting = False
                                    else:
                                        double_counting = True
                                    
                                elif pos_col1 == col2 and pos_col2 == col1 and pos_val2 == '*':
                                    if pos_val2 not in unknowns[current_set][col1]:
                                        unknowns[current_set][col1][val1] = set()
                                    unknowns[current_set][col1][val1].add(pos_val1)
                                    # print('adding', pos_val1, 'other is', pos_val2)
                                    if double_counting == True:
                                        double_counting_compensation += 1
                                        double_counting = False
                                    else:
                                        double_counting = True
                                    
        # go through the entirety of the wrongs dict and get the dom - wrongs values or self.domains[col1] * self.domains[col2] if both full
        if printing:
            print('unknowns final:',unknowns)
        

        expanded_possible_rel_count = 0 + double_counting_compensation - double_star_adjustment
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
        # if printing:
        print('final exp rel count', expanded_possible_rel_count, 'with compensation of', double_counting_compensation, 'and adjustment of', double_star_adjustment)
        return expanded_possible_rel_count

    def make_null_in_place(self, row, column_name, row_input = 'order'):     # row object or row id
        if row_input == 'order' and (type(row) == int or type(row) == str):
            for r in self.rows:
                if r.order == row:
                    row = r
                    break
        elif row_input == 'current_order':
            row = self.rows[int(row)]
        elif row_input == 'id':       # important when testing multiple tables
            for r in self.rows:
                if r.get_id() == row:
                    row = r
                    break
        row.set_value(column_name, '*')
        self.update_all_relationships()         # there might be a way to keep track of which rels come from which row, and then edit the list in a targeted way
        merge_count = self.check_merges()
        return merge_count

    def make_null_copying_row(self,row,column_name):
        if type(row) == int or type(row) == str:
            row = self.rows[int(row)]
        new_row = copy.deepcopy(row)
        new_row.set_value(column_name, '*')

        old_id = row.get_id()
        for i,current_row in enumerate(self.rows):
            if current_row.get_id() == old_id:
                self.rows[i] = new_row

        self.update_all_relationships() 
        merge_count = self.check_merges()
        return merge_count

    def check_merges(self):
        merge_count = 0
        new_rows = []
        for i, current_row in enumerate(self.rows):
            unique = True
            for next_row in self.rows[i+1:]:  
                if i != len(self.rows):
                    if current_row.is_same(next_row):
                        unique = False
                        merge_count += 1
                        break
            if unique:
                new_rows.append(current_row)
        self.rows = new_rows
        return merge_count

    def is_same(self, other_table):
        if self.get_size() != other_table.get_size():
            return False
        else:
            for i, current_row in enumerate(self.rows):
                if current_row.is_same(other_table.rows[i]):
                    continue
                else:
                    return False
            return True


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
        table.make_null_in_place(row_id,column_label)
    if short_printing:
        print (table)
        print('Final table size:', table.get_size())
        print('Certain relationships:',table.get_certain_relationships_count())
    if long_printing:
        print(table.certain_rels)
    if short_printing:
        print('Possible relationships:',table.get_unexp_possible_relationships_count())
    if long_printing:
        print(table.possible_rels)
    if short_printing:
        print('Domains:',domains)
        print('Count of expanded possible relationships:', table.get_expanded_possible_relationships_count())
    return table


testing = False


test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']
domains = {'Col1':3, 'Col2':3, 'Col3':2}

if testing:
    if short_printing:
        print('TABLE 1')


    # t1 = Table(columns=test_columns, initial_table=test_table, domains=domains)
    # print(t1)
    # # print(t1.get_relationships())
    # t1.make_null(0,'Col3')
    # print(t1)
    # # t1.make_null(1,'Col3')
    # # print(t1)
    # print(t1.get_certain_relationships_count(),t1.get_unexp_possible_relationships_count())
    # print(t1.certain_rels)
    # print(t1.possible_rels)
    # print(t1.get_expanded_possible_relationships_count())


    t1 = Table(test_columns, test_table, domains)
    t1 = perform_nulling(t1, [(0, 'Col2')], short_printing=short_printing)
    # print(t1)
    # print('exp rels count:',t1.get_expanded_possible_relationships_count())
    # assert (t1.get_expanded_possible_relationships_count() == 5)



    if short_printing:
        print('------------------------------------------')
        print('TABLE 2')

    t2 = Table(test_columns, test_table, domains)
    t2 = perform_nulling(t2, [(0,'Col3'),(1,'Col3')], short_printing=short_printing)
    assert(t2.get_expanded_possible_relationships_count()==4)

    if short_printing:
        print('------------------------------------------')
        print('TABLE 3')

    t3 = Table(['Col2','Col3'], [['A','A'],['B','B']], domains)
    t3 = perform_nulling(t3, [(0,'Col2'),(1,'Col3')], short_printing=short_printing)
    assert(t3.get_expanded_possible_relationships_count() == 4)


    if short_printing:
        print('------------------------------------------')
        print('TABLE 4')
    t4 = Table(['Col2','Col3'], [['A','A'],['B','B']], domains)
    t4 = perform_nulling(t4, [(0,'Col2'),(1,'Col3'),(0,'Col3'),(1,'Col2')], short_printing=short_printing)
    assert(t4.get_expanded_possible_relationships_count() == 6)

    # short_printing = True
    if short_printing:
        print('------------------------------------------')
        print('TABLE 5')
    t5 = Table(test_columns, test_table, domains)
    t5 = perform_nulling(t5, [(0,'Col3'),(0,'Col1'),(0,'Col2')], short_printing=short_printing)
    assert(t5.get_expanded_possible_relationships_count() == 21)


    if short_printing:
        print('------------------------------------------')
        print('TABLE 6')
    t6 = Table(test_columns, test_table, domains)
    t6 = perform_nulling(t6, [(0,'Col3'),(0,'Col1'),(0,'Col2'),(1,'Col1'),(1,'Col2'),(1,'Col3')], short_printing=short_printing)
    assert(t6.get_expanded_possible_relationships_count() == 21)


    if short_printing:
        print('------------------------------------------')
        print('TABLE 7')
    t7 = Table(test_columns, test_table, domains)
    t7 = perform_nulling(t7, [(0,'Col3'),(0,'Col2'),(1,'Col2'),(1,'Col3')], short_printing=short_printing)
    assert(t7.get_expanded_possible_relationships_count() == 11)


    if short_printing:
        print('------------------------------------------')
        print('TABLE 8')
    t8 = Table(test_columns, test_table, domains)
    print(t8)
    t8 = perform_nulling(t8, [(0,'Col3')], short_printing=short_printing)
    printing_mode = True
    t8 = perform_nulling(t8, [(1,'Col2')], short_printing=short_printing)
    assert(t8.get_expanded_possible_relationships_count() == 7)



    if short_printing:
        print('------------------------------------------')
        print('TABLE 9')
    t9 = Table(test_columns, [['C','B','A'],['A','*','*']], domains)
    print(t9)
    print(t9.get_expanded_possible_relationships_count())
    assert(t9.get_expanded_possible_relationships_count() == 10)


    if short_printing:
        print('------------------------------------------')
        print('TABLE 10')
    t10 = Table(test_columns, [['A','C','B'],['*','B','*']], domains)
    print(t10)
    print(t10.get_expanded_possible_relationships_count())
    assert(t10.get_expanded_possible_relationships_count() == 10)


# t11 = Table(test_columns, [['A','B','C'],['A','C','B'],['C','B','A']], domains)
# print(t11)
# t11 = perform_nulling(t11, [(0,'Col1'),(0,'Col3'),(2,'Col1'),(2,'Col3')])
# print(t11)
# print(t11.get_expanded_possible_relationships_count())
# print(t11.get_certain_relationships_count())