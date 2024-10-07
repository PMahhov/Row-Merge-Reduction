from relationships_table_2 import Table
import copy
import time


class TableTreeNode():
    '''
    table (Table)
    children (list): list of nodes
    nullings: list of nulling operations conducted to get to this point
    
    '''
    def __init__(self, table, nullings = []):
        self.table = table
        self.nullings = nullings            # TODO: be able to track nullings
        self.children = []

    def __str__(self):
        return str(self.table)

    def add_child(self, child):
        self.children.append(child)

    def get_layer(self):
        return len(self.nullings)

    def get_size(self):
        return self.table.get_size()

    def get_certains(self):
        return self.table.get_certain_relationships_count()

    def get_exp_possibles(self):
        return self.root_table.get_expanded_possible_relationships_count()

    def add_layer(self):
        for i, current_row in enumerate(self.table.rows):
            for current_column in self.table.columns:
                if current_row.get_value(current_column) != '*':
                # current_datapoint = current_row.get_value(column)
                # row_id = current_row.get_id()
                # new_rows = copy.copy(self.table.rows)
                # new_table = Table(columns = self.table.columns, initial=self.table.rows)
                    # new_table = copy.deepcopy(self.table)       # for 3x3,  2 minutes down from 40
                    new_table = Table(columns = self.table.columns, initial_list=self.table.rows, domains=self.table.domains, origin ='row objects')    # 1 min for 3x3
                    new_table.make_null_copying_row(current_row, current_column)
                    new_nullings = copy.deepcopy(self.nullings)
                    new_nullings.append((current_row.get_id(), current_column))
                    new_node = TableTreeNode(new_table, new_nullings)
                    self.children.append(new_node)
        # print('children of')
        # print(self.table)
        # print('are')
        # print(self.children)
        # for c in self.children:
        #     print(c.table)

    def check_children_thoroughly(self, desired_size: int, valid_tables = set(), loading_screen = True):
        self.add_layer()
        if len(self.children) > 0:
            # print('children of')
            # print(self.table)
            # print('are')
            # print(self.children)
            # for c in self.children:
            #     print(c.table)
            for i, child in enumerate(self.children):
                if child.get_size() <= desired_size:
                    valid_tables.add(child.table)
                      # you can't get a better result by performing more nullings, so can stop recursion here 
                      # (need to prove it in-paper)
                else:
                    if loading_screen and self.get_layer() < 4 and len(self.children) > 8: # loading screen
                        print('child',i,'of',len(self.children),'in layer',self.get_layer())
                    # print('child',i,'of',len(self.children),'in layer',self.get_layer())
                    valid_tables.update(child.check_children_thoroughly(desired_size, valid_tables))
        return valid_tables

class TableTree():
    '''
    root: node with original table
    
    '''
    def __init__(self, table):
        self.root = TableTreeNode(table)

    def comprehensive_algorithm(self, desired_size: int, printing = False):
        print('starting comprehensive algorithm with table size',self.root.get_size())
        valid_tables = set()

        if self.root.get_size() <= desired_size:
            return self.root.table        # if the first table already qualifies, can't get a better result by nulling more

        # get all tables of the right size
        valid_tables.update(self.root.check_children_thoroughly(desired_size, valid_tables))

        # choose the right table --> max certain, min possible rels
        valid_tables = list(valid_tables)
        unique_valid_tables = []
        for current_table in valid_tables:
            if not any(existing_table.is_same(current_table) for existing_table in unique_valid_tables):
                unique_valid_tables.append(current_table)

        if printing:
            print('unique valid tables:')
            for t in unique_valid_tables:
                print(t)                


        # check number of certain relationships
        candidate_tables = []
        max_certain_rels = 0
        for current_table in unique_valid_tables:
            current_certains = current_table.get_certain_relationships_count() 
            if current_certains > max_certain_rels:
                max_certain_rels = current_certains
                candidate_tables = [current_table]
            elif current_certains == max_certain_rels:
                candidate_tables.append(current_table)


        if len(candidate_tables) == 0:
            raise ValueError ('No solution found for desired size '+str(desired_size))
        elif len(candidate_tables) == 1:
            return candidate_tables
        else:       # check number of possible relationships
            min_possible_rels = None
            for current_table in candidate_tables:
                current_possibles = current_table.get_expanded_possible_relationships_count()
                if min_possible_rels == None or current_possibles < min_possible_rels:
                    min_possible_rels = current_possibles
                    final_tables = [current_table]
                elif current_possibles == min_possible_rels:
                    final_tables.append(current_table)
            return final_tables


test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']
domains = {'Col1':3, 'Col2':3, 'Col3':2}

# t1 = Table(test_columns, test_table, domains)
# tr1 = TableTree(t1)
# answers = tr1.comprehensive_algorithm(1)
# print('comprehensive answers:')
# for answer in answers:
#     print(answer)

def find_answer(table, desired_size, alg = ['comp','greedy']):
    tree = TableTree(table)
    if 'comp' in alg:
        comp_answers = tree.comprehensive_algorithm(desired_size)
        print('comprehensive answers:')
        for comp_answer in comp_answers:
            print (comp_answer)

t1 = Table(test_columns, test_table, domains)
print(t1)
find_answer(t1, 1)

print('-----------------------------------------------')
print('test 2')
t2 = Table(test_columns,  [['A','B','C'],['A','C','B']], domains)
print(t2)
find_answer(t2,1)

print('-----------------------------------------------')
print('test 3')
t3 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A']], domains)         # comp took 0.43 sec to run
print('original table:')
print(t3)
start = time.time()
find_answer(t3,2)

end = time.time()
print('time elapsed:',str(end-start))


# test_t = Table(['Col1','Col2'],[['A','B'],['C','D']], domains)
# ttn = TableTreeNode(test_t)
# print(ttn.table)
# ttn.add_layer()
# for c in ttn.children:
#     print(c)