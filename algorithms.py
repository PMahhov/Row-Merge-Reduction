from relationships_table import Table
from graph import Graph
import copy
import time

tested_tables = []

class TableTree():
    def __init__(self, table, children = None, nullings = []):
        self.id = id
        self.root_table = table
        self.root_size = table.get_size()
        self.children = []
        self.nullings = nullings
        if children != None:
            for child in children:
                self.add_child(child)
        else:
            self.children = []
    
    def add_child(self, child):
        self.children.append(child)

    def get_layer_nr(self):
        return len(self.nullings)

    def get_nullings(self):
        return self.nullings

    def get_certains(self):
        return self.root_table.get_certain_relationships_count()

    def get_exp_possibles(self):
        return self.root_table.get_expanded_possible_relationships_count()

    def add_layer(self):              # adds
        table = self.root_table
        current_row = table.first_row
        while True:
            current_datapoint = current_row.first
            while True:
                if not current_datapoint.isnull():
                    row_id = current_row.get_id()
                    column_label = current_datapoint.get_column()
                    new_table = table.make_null_get_copy(row_id, column_label)
                    # print(new_table)
                            # TODO: making copies takes a long time, maybe store changes and revert later? do everything in the same
                                        # would need to add a 'change value'(row_id, col_label, value) function to a table
                    new_nullings = copy.deepcopy(self.get_nullings())
                    new_nullings.append((row_id, column_label))
                            # TODO: maybe only do this is new_table is unique compared to all tested tables
                    # if not any(tested_table.is_same(new_table) for tested_table in tested_tables):
                    #     self.add_child(TableTree(new_table, nullings = new_nullings))
                    # else:
                    #     print('child not added')
                    self.add_child(TableTree(new_table, nullings = new_nullings))
                if current_datapoint.next != None:
                    current_datapoint = current_datapoint.next
                else:
                    break
            if current_row.next_row != None:
                current_row = current_row.next_row
            else:
                break

def comprehensive_algorithm(table, desired_size: int):
    tabletree = TableTree(table)
    valid_tables = set()
    
    if tabletree.root_size <= desired_size:
        return tabletree.root_table                 # if the first table already qualifies, can't get a better result by nulling more

    valid_tables.update(check_children(tabletree, desired_size, valid_tables))


    # choose the right table --> max certain, min possible rels

    valid_tables = list(valid_tables)
    unique_valid_tables = []
    for current_table in valid_tables:
        if not any(existing_table.is_same(current_table) for existing_table in unique_valid_tables):
            unique_valid_tables.append(current_table)


    # print('unique valid tables:')
    # for t in unique_valid_tables:
    #     print(t)

    candidate_tables = []
    max_certain_rels = 0
    for current_table in unique_valid_tables:
        current_certains = table.get_certain_relationships_count() 
        if current_certains > max_certain_rels:
            max_certain_rels = current_certains
            candidate_tables = [current_table]
        elif current_certains == max_certain_rels:
            candidate_tables.append(current_table)
    

    if len(candidate_tables) == 0:
        raise ValueError ('No solution found for desired size '+str(desired_size))
    elif len(candidate_tables) == 1:
        return candidate_tables
    else:
        min_possible_rels = None
        for current_table in candidate_tables:
            current_possibles = current_table.get_expanded_possible_relationships_count()
            if min_possible_rels == None or current_possibles < min_possible_rels:
                min_possible_rels = current_possibles
                final_tables = [current_table]
            elif current_possibles == min_possible_rels:
                final_tables.append(current_table)
        return final_tables


    
def check_children(tabletree, desired_size: int, valid_tables):
    tabletree.add_layer()
    # print('the',len(tabletree.children),'children of')
    # print(tabletree.root_table)
    # print('are')
    # for c in tabletree.children:
    #     print(c.root_table)
    if len(tabletree.children) > 0:
        for i, child in enumerate(tabletree.children):
            # if child.root_table in valid_tables:        # TODO: does this actually happen?
            #     print('already in valid')             # or do I need to use the 'any' construction
            #     pass
            if child.root_size <= desired_size:
                valid_tables.add(child.root_table)       # you can't get a better result by performing more nullings (need to prove it in-paper)
            else:
                if tabletree.get_layer_nr() < 4 and len(tabletree.children) > 5:        # loading screen
                    print('child',i,'of',len(tabletree.children),'in layer',tabletree.get_layer_nr())
                valid_tables.update(check_children(child, desired_size, valid_tables))
    return valid_tables
    

def print_result(result):
    print(len(result),'final table(s):')
    for table in result:
        print(table)
        print('Final table size:', table.get_size())
        print('Certain relationships:',table.get_certain_relationships_count())
        print('Expanded possible relationships:', table.get_expanded_possible_relationships_count())



def greedy_algorithm(table, desired_size: int):
    tabletree = TableTree(table)
    valids = set()              # this one is a set of tabletrees, not trees like in the comprehensive
    
    if tabletree.root_size <= desired_size:
        return tabletree.root_table   

    valid_answer_exists = False

    new_to_check = [tabletree]
    while not valid_answer_exists:
        to_check = new_to_check
        new_to_check = []
        for tabletree in to_check:
            tabletree.add_layer()
            current_bests = []            
            if len(tabletree.children) > 0:
                max_certains = 0
                for i, child in enumerate(tabletree.children):
                    if child.root_size <= desired_size:
                        valid_answer_exists = True
                        valids.add(child)
                    elif valid_answer_exists:
                        pass
                    else:
                        certains = tabletree.get_certains()
                        possibles = tabletree.get_exp_possibles()
                        if i == 0:
                            min_possibles = possibles
                        if max_certains < certains:
                            current_bests = [child]
                            max_certains = certains
                        elif max_certains == certains:
                            if min_possibles < possibles:
                                current_bests = [child]
                                min_possibles = possibles
                            elif min_possibles == possibles:
                                current_bests.append(child)
            new_to_check += current_bests
        # else:
        #     raise ValueError('Greedy found no solution') # should never happen I think

    max_certains = 0
    if len(valids) == 1:
        for v in valids:
            return [v.root_table]
    
    current_bests = []
    for i, v in enumerate(valids):
        table = v.root_table
        certains = v.get_certains()
        possibles = v.get_exp_possibles()
        if i == 0:
            min_possibles = possibles
        if max_certains < certains:
            current_bests = [table]
            max_certains = certains
        elif max_certains == certains:
            if min_possibles < possibles:
                current_bests = [table]
            elif min_possibles == possibles:
                current_bests.append(table)
    # return (current_best.root_table, current_best.get_nullings())

    unique_current_bests = []
    for current_table in current_bests:
        if not any(existing_table.is_same(current_table) for existing_table in unique_current_bests):
            unique_current_bests.append(current_table)

    return unique_current_bests
    

test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']
domains = {'Col1':3, 'Col2':3, 'Col3':2}

print('-----------------------------------------------')
print('test 1')
t1 = Table(test_columns, test_table, domains)
print('original table:')
print(t1)
comp_result = comprehensive_algorithm(t1, 1)
print('comprehensive result:')          # A B *
print_result(comp_result)
print('greedy result:')                 # A B *
greedy_result = greedy_algorithm(t1, 1)
print_result(greedy_result)

print('-----------------------------------------------')
print('test 2')
t2 = Table(test_columns,  [['A','B','C'],['A','C','B']], domains)
print('original table:')
print(t2)

comp_result = comprehensive_algorithm(t2, 1)
print('comprehensive result:') 
print_result(comp_result)
print('greedy result:')
greedy_result = greedy_algorithm(t2, 1)
print_result(greedy_result)


print('-----------------------------------------------')
print('test 3')
t2 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A']], domains)
print('original table:')
print(t2)
# comp_result = comprehensive_algorithm(t2, 2)
# print_result(comp_result)             # CBA, A** OR ACB, *B*, took 41 mins to run, 3 cert, 11 pos

start = time.time()

print('greedy result:')
greedy_result = greedy_algorithm(t2, 2)      
print_result(greedy_result)

end = time.time()
print('time elapsed:',str(end-start))

print('-----------------------------------------------')
print('test 4')
t2 = Table(['Col1', 'Col2'],  [['A','B'],['A','C'],['C','B']], domains)
print('original table:')
print(t2)
comp_result = comprehensive_algorithm(t2, 2)
print('comprehensive result:') 
print_result(comp_result)
print('greedy result:')
greedy_result = greedy_algorithm(t2, 2)
print_result(greedy_result)


print('-----------------------------------------------')
print('test 5')
t2 = Table(['Col1', 'Col2'],  [['A','*'],['*','*'],['C','*']], domains)
print('original table:')
print(t2)

comp_result = comprehensive_algorithm(t2, 2)
print('comprehensive result:') 
print_result(comp_result)
print('greedy result:')
greedy_result = greedy_algorithm(t2, 2)
print_result(greedy_result)


print('-----------------------------------------------')
print('test 6')
t2 = Table(['Col1','Col2'],  [['A','B'],['A','C']], domains)
print('original table:')
print(t2)
print('greedy result:')
greedy_result = greedy_algorithm(t2, 1)
print_result(greedy_result)


print('-----------------------------------------------')
print('test 7')
t2 = Table(['Col1', 'Col2', 'Col3'],  [['A','B','C'],['A','B','D']], domains)
print('original table:')
print(t2)

comp_result = comprehensive_algorithm(t2, 1)
print('comprehensive result:') 
print_result(comp_result)
print('greedy result:')
greedy_result = greedy_algorithm(t2, 1)
print_result(greedy_result)

# TODO: figure out how this still works, shouldnt greedy choose ABC *BD for first? 
# print out and see or evaluate manually on custom tables