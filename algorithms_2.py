from relationships_table_2 import Table
import copy
import time
import random

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
        return self.table.get_expanded_possible_relationships_count()

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
            for i, child in enumerate(self.children):
                if child.get_size() <= desired_size:
                    valid_tables.add(child.table)
                      # you can't get a better result by performing more nullings, so can stop recursion here 
                      # (need to prove it in-paper)
                else:
                    if loading_screen and self.get_layer() < 2 and len(self.children) > 8: # loading screen
                        print('child',i+1,'of',len(self.children),'in layer',self.get_layer())
                    valid_tables.update(child.check_children_thoroughly(desired_size, valid_tables))
        return valid_tables

class TableTree():
    '''
    root: node with original table
    
    '''
    def __init__(self, table):
        self.root = TableTreeNode(table)

    def comprehensive_algorithm(self, desired_size: int, printing = False):
        # reset children:   
               # TODO: even if there might be benefits from running multiple algorithms at once, that's not the point of the study
               # for the purposes of this work, they must be independent so they can be compared
        self.root.children = []

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

    def greedy_algorithm_deterministic(self, desired_size: int):      # we pursue all equally best layers instead of choosing random
        return self.greedy_algorithm(desired_size, deterministic = True)

    # for the current node:
        # check all children
        # take all the best children, add to queue to become current node

    def greedy_algorithm_random(self, desired_size: int):
        return self.greedy_algorithm(desired_size, deterministic = False)

    # for the current node:
        #check all children
        # out of the best children, pick one at random



        # mechanically same as deterministic except new_to_check is now a list of lists
            # when we new_to_check += current_bests, it becomes adding a new list
            # before we do for tree_node in to_check, we choose one of the lists at random from new_to_check

# comprehensive up to valid is like comprehensive but stops when a layer has a valid size answer
    def comp_up_to_valid_det(self,desired_size: int):
        return self.greedy_algorithm(desired_size, deterministic = True, comp_up_to_valid=True)

    def comp_up_to_valid_rand(self,desired_size: int):
        return self.greedy_algorithm(desired_size, deterministic = False, comp_up_to_valid=True)

    def greedy_algorithm(self, desired_size: int, deterministic, comp_up_to_valid = False):      # we pursue all equally best layers instead of choosing random
        # reset children
        self.root.children = []
        
        valids = set()
        if self.root.get_size() <= desired_size:
            return self.root.table

        valid_answer_exists = False
        if deterministic:
            new_to_check = [self.root]
        else:
            new_to_check = [[self.root]]
        while not valid_answer_exists:
            if deterministic:
                to_check = new_to_check
            else:
                to_check = random.choice(new_to_check)
            new_to_check = []
            for tree_node in to_check:
                # print('checking:')
                # print(tree_node.table)
                # print(tree_node.get_certains(), tree_node.get_exp_possibles())
                tree_node.add_layer()
                current_bests = []
                if len(tree_node.children) > 0:
                    max_certains = 0
                    for i, child in enumerate(tree_node.children):
                        if child.get_size() <= desired_size:
                            valid_answer_exists = True
                            valids.add(child)
                        elif valid_answer_exists:
                            pass
                        elif comp_up_to_valid:
                            current_bests.append(child)   # add all children to next layer if no valid found
                        else:
                            # certains = tree_node.get_certains()
                            # possibles = tree_node.get_exp_possibles()
                            # print('child is')
                            # print(child.table)
                            # print(child.get_certains(), child.get_exp_possibles())
                            certains = child.get_certains()
                            # print(child.table.certain_rels)
                            possibles = child.get_exp_possibles()
                            # print(certains, possibles)
                            if i == 0:
                                min_possibles = possibles
                            if max_certains < certains:
                                current_bests = [child]
                                max_certains = certains
                                min_possibles = possibles
                            elif max_certains == certains:
                                if min_possibles > possibles:
                                    current_bests = [child]
                                    min_possibles = possibles
                                elif min_possibles == possibles:
                                    current_bests.append(child)
                if deterministic:
                    new_to_check += current_bests
                else:
                    new_to_check.append(current_bests)


        # print('valids')
        # for v in valids:
        #     print(v.table)

        if len(valids) == 1:
            for v in valids:
                return [v.table]

        # compare all found valid solutions

        max_certains = 0
        current_bests = []
        for i, v in enumerate(valids):
            certains = v.get_certains()
            possibles = v.get_exp_possibles()
            if i == 0:
                min_possibles = possibles
            if max_certains < certains:
                current_bests = [v.table]
                max_certains = certains
                min_possibles = possibles       # certains override possibles (this is a matter of preference)
            elif max_certains == certains:
                if min_possibles > possibles:
                    current_bests = [v.table]
                elif min_possibles == possibles:
                    current_bests.append(v.table)

        # remove duplicates
        unique_current_bests = []
        for current_table in current_bests:
            if not any(existing_table.is_same(current_table) for existing_table in unique_current_bests):
                unique_current_bests.append(current_table)

        return unique_current_bests

# t1 = Table(test_columns, test_table, domains)
# tr1 = TableTree(t1)
# answers = tr1.comprehensive_algorithm(1)
# print('comprehensive answers:')
# for answer in answers:
#     print(answer)

def find_answer(table, desired_size, alg = ['comp','greedy_det','greedy_random','CVD','CVR'], time_to_show = 0):
    tree = TableTree(table)
    print('alg is',alg)
    if alg == 'all except comp' or 'greedy_random' in alg:
        start_greedy_random = time.time()
        greedy_random_answers = tree.greedy_algorithm_random(desired_size)
        end_greedy_random = time.time()
        print('greedy_random_answers:')
        for answer in greedy_random_answers:
            print(answer)
            print('certain rels:',answer.get_certain_relationships_count())
            print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_greedy_random = end_greedy_random - start_greedy_random
        if time_greedy_random > time_to_show:
            print('Greedy random took',time_greedy_random,'seconds')
    if alg == 'all except comp' or 'greedy_det' in alg:
        start_greedy_det = time.time()
        greedy_det_answers = tree.greedy_algorithm_deterministic(desired_size)
        end_greedy_det = time.time()
        print('greedy_det_answers:')
        for answer in greedy_det_answers:
            print(answer)
            print('certain rels:',answer.get_certain_relationships_count())
            print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_greedy_det = end_greedy_det - start_greedy_det
        if time_greedy_det > time_to_show:
            print('Greedy deterministic took', time_greedy_det, 'seconds')
    if alg == 'all except comp' or 'CVR' in alg:
        start_cvr = time.time()
        cvr_answers = tree.comp_up_to_valid_rand(desired_size)
        end_cvr = time.time()
        print('cvr answers:')
        for answer in cvr_answers:
            print (answer)
            print('certain rels:',answer.get_certain_relationships_count())
            print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_cvr = end_cvr - start_cvr
        if time_cvr > time_to_show:
            print('CVR calculation took',time_cvr,'seconds')
    if alg == 'all except comp' or 'CVD' in alg:
        start_cvd = time.time()
        cvd_answers = tree.comp_up_to_valid_det(desired_size)
        end_cvd = time.time()
        print('cvd answers:')
        for answer in cvd_answers:
            print (answer)
            print('certain rels:',answer.get_certain_relationships_count())
            print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_cvd = end_cvd - start_cvd
        if time_cvd > time_to_show:
            print('CVD calculation took',time_cvd,'seconds')
    if alg != 'all except comp' and 'comp' in alg:
        start_comp = time.time()
        comp_answers = tree.comprehensive_algorithm(desired_size)
        end_comp = time.time()
        print('comprehensive answers:')
        for answer in comp_answers:
            print (answer)
            print('certain rels:',answer.get_certain_relationships_count())
            print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_comp = end_comp - start_comp
        if time_comp > time_to_show:
            print('Comprehensive calculation took',time_comp,'seconds')

test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']
domains = {'Col1':3, 'Col2':3, 'Col3':3, 'Col4':2}

t1 = Table(test_columns, test_table, {'Col1':3, 'Col2':3, 'Col3':3})
print(t1)
find_answer(t1, 1)
# find_answer(t1, 1, ['greedy_det','greedy_random'])


print('-----------------------------------------------')
print('test 2')
t2 = Table(test_columns,  [['A','B','C'],['A','C','B']], domains)
print(t2)
find_answer(t2,1)
# find_answer(t2,1, 'all except comp')

# TODO: ADD TO PAPER THIS EXAMPLE ON WHEN GREEDY DOESNT WORK
# AT ABC, A**, greedy always chooses to remove last A in second column because it doesnt
# reduce certain rels, but then *** is the only option
# a better solution would be to do A**, A**




print('-----------------------------------------------')
print('test 3')
t3 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A']], domains)     
print('original table:')
print(t3)
start = time.time()
# find_answer(t3,2, ['greedy_det','greedy_random'])
find_answer(t3,2, 'all except comp')
# find_answer(t3,2)         # comp took 53,58, 67, 74, 120 sec to run

end = time.time()
print('total time elapsed for test 3:',str(end-start))

print('-----------------------------------------------')
print('test 4')
t3 = Table(test_columns+['Col4'],  [['A','B','C','A'],['A','C','B','A'],['C','B','A','B']], domains)
print('original table:')
print(t3)
start = time.time()
find_answer(t3,2,'all except comp')           # cvd 2 sec

end = time.time()
print('total time elapsed for test 4:',str(end-start))


print('-----------------------------------------------')
print('test 5')
t3 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A'],['A','C','C']], domains)      
print('original table:')
print(t3)
start = time.time()
find_answer(t3,2, 'all except comp')
# find_answer(t3,2,['greedy_det','greedy_random'])        # CVD 30s

end = time.time()
print('total time elapsed for test 5:',str(end-start))

