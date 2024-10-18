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
                    new_table = Table(columns = self.table.columns, initial_list=self.table.rows, domains_cardinality=self.table.domains_cardinality, origin ='row objects')    # 1 min for 3x3
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

    def sorted_nodes_algorithm(self, desired_size: int, nth = None):
        # reset children:
        self.root.children = []

        valids = set()
        max_certains = 0
        min_possibles = None

        n_count = 0

        if self.root.get_size() <= desired_size:
            return [self.root.table]

        current_node = self.root
        rev_sorted_nodes = []

        end_loop = False
        while not end_loop:
            # print(current_node)
            current_node.add_layer()        # creates all children of node
            if len(current_node.children) > 0:
                for child in current_node.children:

                    node_score = (child, child.get_certains(), child.get_exp_possibles())
                    if child.get_size() <= desired_size:
                        # print('valid found', n_count)
                        # print(child)
                        if min_possibles == None:
                                min_possibles = node_score[2]
                        if node_score[1] > max_certains:
                            valids = {child.table}
                            max_certains = node_score[1]
                            min_possibles = node_score[2]
                            n_count += 1
                        elif node_score[1] == max_certains:
                            if node_score[2] < min_possibles:
                                valids = {child.table}
                                min_possibles = node_score[2]
                                n_count += 1
                            elif node_score[2] == min_possibles:
                                valids.add(child.table)
                        if n_count == nth:
                            end_loop = True
                            break
                    else:       # if child is not valid, add to list to keep searching
                        rev_sorted_nodes.append(node_score)
            

                if len(rev_sorted_nodes) > 0:
                # sort the list of nodes in reverse (sorting works in descending order)
                    # it is faster to pop the last than the first item in a list
                #        (score 2 gets a minus sign, as it is a non-negative value that needs to be minimized
                    rev_sorted_nodes = sorted(rev_sorted_nodes, key=lambda score: (score[1], -score[2]))   
                    # print('rev sorted_nodes')
                    # print(rev_sorted_nodes)
                # take best node
                    current_node = rev_sorted_nodes.pop(-1)[0]

                    
# only continue looping if the score of the best sorted is better than the current valid score
                    if len(valids) > 0:       
                        next_certains = current_node.get_certains() 
                        next_possibles = current_node.get_exp_possibles()
                        # print(next_certains, next_possibles, 'vs', max_certains, min_possibles)
                        if next_certains < max_certains:
                            end_loop = True
                            break
                        elif next_certains == max_certains:
                            if next_possibles >= min_possibles: # this could be == if it is important to not lose potential identical-scoring answers
                                end_loop = True
                                break

                else:
                    end_loop = True
                    break

                if end_loop:
                    break

            else:                       
                if len(valids) > 0:
                    end_loop = True
                    break
                else:
                    raise ValueError('No valid answer found') # should never happen if desired_size>0, *** is always valid

        # remove duplicates
        print('final n_count:',n_count)
        unique_current_bests = []
        for current_table in valids:
            if not any(existing_table.is_same(current_table) for existing_table in unique_current_bests):
                unique_current_bests.append(current_table)
        return unique_current_bests


    # DFS comprehensive
    def comprehensive_algorithm(self, desired_size: int, printing = False):
        # reset children:   
               # TODO: even if there might be benefits from running multiple algorithms at once, that's not the point of the study
               # for the purposes of this work, they must be independent so they can be compared
        self.root.children = []

        print('starting comprehensive algorithm with table size',self.root.get_size())
        valid_tables = set()

        if self.root.get_size() <= desired_size:
            return [self.root.table]        # if the first table already qualifies, can't get a better result by nulling more

        # get all tables of the right size
        valid_tables.update(self.root.check_children_thoroughly(desired_size, valid_tables))

        # choose the right table --> max certain, min possible rels

        # remove duplicates
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



    '''
algorithm qualities
greedy (vs wide): 
in a current layer, don't pick the children that are not the best in the layer

random (vs deterministic): 
in a current layer, if you would choose many children to continue with, only pick one of them at random

deep (vs shallow): 
don't stop even if a valid answer has been found in the latest layer


algorithms:
comp/wdd - wide, deep, deterministic
wsd - wide, shallow, deterministic
wsr - wide, shallow, random
greedy_deep_det - greedy, deep, deterministic
greedy_det - greedy, shallow, deterministic
greedy random - greedy, shallow, random

wdr - wide, deep, random
greedy_deep_rand
'''

    def greedy_algorithm_deterministic(self, desired_size: int):      # we pursue all equally best layers instead of choosing random
        return self.shallow_algorithm(desired_size, deterministic = True, greedy = True)

    # for the current node:
        # check all children
        # take all the best children, add to queue to become current node

    def greedy_algorithm_random(self, desired_size: int):
        return self.shallow_algorithm(desired_size, deterministic = False, greedy = True)

    # for the current node:
        #check all children
        # out of the best children, pick one at random



        # mechanically same as deterministic except new_to_check is now a list of lists
            # when we new_to_check += current_bests, it becomes adding a new list
            # before we do for tree_node in to_check, we choose one of the lists at random from new_to_check

# wide-shallow-deep (WSD) is like comprehensive but BFS and stops when a layer has a valid size answer
    # e.g. if there is a valid answer on layer 2, no layer 3 calculations are performed
    def wide_shallow_det(self,desired_size: int):
        return self.shallow_algorithm(desired_size, deterministic = True, greedy = False)

# the random version (WSR) picks a random node to continue with for the next layer out of all the children without looking at the metrics
    def wide_shallow_rand(self,desired_size: int):
        return self.shallow_algorithm(desired_size, deterministic = False, greedy = False)


# comp up to valid is the choice between greedy and not greedy
    def shallow_algorithm(self, desired_size: int, deterministic, greedy):      # we pursue all equally best layers instead of choosing random
        # reset children
        self.root.children = []
        
        valids = set()
        if self.root.get_size() <= desired_size:
            return [self.root.table]

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
                        elif not greedy:
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

    def greedy_deep_det(self, desired_size: int):
        return self.deep_algorithm(desired_size, deterministic=True, greedy = True)

    def greedy_deep_rand(self, desired_size: int):
        return self.deep_algorithm(desired_size, deterministic=False, greedy=True)

    def wide_deep_det(self, desired_size: int):
        return self.deep_algorithm(desired_size, deterministic = True, greedy=False)

    def wide_deep_rand(self, desired_size: int):
        return self.deep_algorithm(desired_size, deterministic=False, greedy=False)

# TODO: greedy algorithm that checks next layer even if current layer has valid answer
    def deep_algorithm(self, desired_size: int, deterministic = True, greedy = True):      # we pursue all equally best layers instead of choosing random
        # reset children
        self.root.children = []
        
        valids = set()
        if self.root.get_size() <= desired_size:
            return [self.root.table]

        if deterministic:
            new_to_check = [self.root]
        else:
            new_to_check = [[self.root]]
        while len(new_to_check) >0:
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
                            valids.add(child)
                        elif not greedy:
                            current_bests.append(child)
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

def find_answer(table, desired_size, alg = ['comp','greedy_det','greedy_random','WSD','WSR', 'WDR', 'greedy_deep_rand', 'greedy_deep_det','sorted_nodes' ], nth_list = [1], time_to_show = 0, show_answers = True):
    tree = TableTree(table)
    print('alg is',alg)
    if alg == 'all except comp' or 'greedy_random' in alg:
        start_greedy_random = time.time()
        greedy_random_answers = tree.greedy_algorithm_random(desired_size)
        end_greedy_random = time.time()
        if show_answers:
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
        if show_answers:
            print('greedy_det_answers:')
            for answer in greedy_det_answers:
                print(answer)
                print('certain rels:',answer.get_certain_relationships_count())
                print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_greedy_det = end_greedy_det - start_greedy_det
        if time_greedy_det > time_to_show:
            print('Greedy deterministic took', time_greedy_det, 'seconds')
    if alg == 'all except comp' or 'WSR' in alg:
        start_wsr = time.time()
        wsr_answers = tree.wide_shallow_rand(desired_size)
        end_wsr = time.time()
        if show_answers:
            print('WSR answers:')
            for answer in wsr_answers:
                print (answer)
                print('certain rels:',answer.get_certain_relationships_count())
                print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_wsr = end_wsr - start_wsr
        if time_wsr > time_to_show:
            print('Wide shallow random calculation took',time_wsr,'seconds')
    if alg == 'all except comp' or 'greedy_deep_det' in alg:
        start_gdd = time.time()
        gdd_answers = tree.greedy_deep_det(desired_size)
        end_gdd = time.time()
        if show_answers:
            print('Greedy deep deterministic answers:')
            for answer in gdd_answers:
                print (answer)
                print('certain rels:',answer.get_certain_relationships_count())
                print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_gdd = end_gdd - start_gdd
        if time_gdd > time_to_show:
            print('Greedy deep deterministic calculation took',time_gdd,'seconds')
    if alg == 'all except comp' or 'greedy_deep_rand' in alg:
        start_gdr = time.time()
        gdr_answers = tree.greedy_deep_det(desired_size)
        end_gdr = time.time()
        if show_answers:
            print('Greedy deep random answers:')
            for answer in gdr_answers:
                print (answer)
                print('certain rels:',answer.get_certain_relationships_count())
                # print('test part 1')
                print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_gdr = end_gdr - start_gdr
        if time_gdr > time_to_show:
            print('Greedy deep random calculation took',time_gdr,'seconds')
    if alg == 'all except comp' or 'WSD' in alg:
        start_wsd = time.time()
        wsd_answers = tree.wide_shallow_det(desired_size)
        end_wsd = time.time()
        if show_answers:
            print('WSD answers:')
            for answer in wsd_answers:
                print (answer)
                print('certain rels:',answer.get_certain_relationships_count())
                print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_wsd = end_wsd - start_wsd
        if time_wsd > time_to_show:
            print('Wide shallow det calculation took',time_wsd,'seconds')
    if alg == 'all except comp' or 'WDR' in alg:
        start_wdr = time.time()
        wdr_answers = tree.wide_shallow_det(desired_size)
        end_wdr = time.time()
        if show_answers:
            print('WDR answers:')
            for answer in wdr_answers:
                print (answer)
                print('certain rels:',answer.get_certain_relationships_count())
                print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_wdr = end_wdr - start_wdr
        if time_wdr > time_to_show:
            print('Wide deep random calculation took',time_wdr,'seconds')
    if alg != 'all except comp' and 'comp' in alg:
        start_comp = time.time()
        comp_answers = tree.comprehensive_algorithm(desired_size)
        end_comp = time.time()
        if show_answers:
            print('comprehensive DFS answers:')
            for answer in comp_answers:
                print (answer)
                print('certain rels:',answer.get_certain_relationships_count())
                print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_comp = end_comp - start_comp
        if time_comp > time_to_show:
            print('Comprehensive DFS calculation took',time_comp,'seconds')
    if alg != 'all except comp' and 'WDD' in alg:
    # if True:
        start_comp = time.time()
        comp_answers = tree.wide_deep_det(desired_size)
        end_comp = time.time()
        if show_answers:
            print('wdd (comp) answers:')
            for answer in comp_answers:
                print (answer)
                print('certain rels:',answer.get_certain_relationships_count())
                print('possible rels:',answer.get_expanded_possible_relationships_count())
        time_comp = end_comp - start_comp
        if time_comp > time_to_show:
            print('WDD Comprehensive (BFS) calculation took',time_comp,'seconds')
    if alg == 'all except comp' or 'sorted_nodes' in alg:
        for nth in nth_list:
            start_sorted = time.time()
            s_answers = tree.sorted_nodes_algorithm(desired_size, nth = nth)
            end_sorted = time.time()
            if show_answers:
                print('sorted alg answers (nth is '+str(nth)+')')
                for answer in s_answers:
                    print (answer)
                    print('certain rels:',answer.get_certain_relationships_count())
                    print('possible rels:',answer.get_expanded_possible_relationships_count())
            time_sorted = end_sorted - start_sorted
            if time_sorted > time_to_show:
                print('Sorted algorithm with nth of '+str(nth)+ ' took', time_sorted, 'seconds')
                

# TODO: check if wide deep random works properly, it seems to take too long

test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']
domains_cardinality = {'Col1':3, 'Col2':3, 'Col3':3, 'Col4':2}

# rev_sorted_nodes = []
# for t in [(1,1,1),(2,2,2),(1,1,2),(2,2,1)]:
#     rev_sorted_nodes.append(t)

# print(rev_sorted_nodes)
# rev_sorted_nodes = sorted(rev_sorted_nodes, key=lambda score: (score[1], -score[2]))   
# print(rev_sorted_nodes)
# print(rev_sorted_nodes.pop(-1))
# print(rev_sorted_nodes)


t1 = Table(test_columns, test_table, {'Col1':3, 'Col2':3, 'Col3':3})
print(t1)
find_answer(t1, 1, nth_list=[1,2, None])
# find_answer(t1, 1, ['greedy_det','greedy_deep_det'])
# find_answer(t1, 1, 'sorted_nodes', nth_list = [1,2])
# find_answer(t1, 1, 'sorted_nodes')




print('-----------------------------------------------')
print('test 2')
t2 = Table(test_columns,  [['A','B','C'],['A','C','B']], domains_cardinality)
print(t2)
find_answer(t2,1, nth_list=[1,2,3, None])
# find_answer(t2,1,['greedy_det','greedy_deep_det']) 
# find_answer(t2,1, 'all except comp')

# EXAMPLE ON WHEN GREEDY DOESNT WORK:
# AT ABC, A**, greedy always chooses to remove last A in second column because it doesnt
# reduce certain rels, but then *** is the only option
# a better solution would be to do A**, A**




print('-----------------------------------------------')
print('test 3')
t3 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A']], domains_cardinality)     
print('original table:')
print(t3)
start = time.time()
# find_answer(t3,2, ['greedy_det','greedy_random'])
find_answer(t3,2, 'all except comp')
# find_answer(t3,2, ['WDD','comp'])
# find_answer(t3,2,['greedy_det','greedy_deep_det']) 
find_answer(t3,2,nth_list=[1,2,3, None])         # comp took 53,58, 67, 74, 120 sec to run
                                                # best answer is 2x 3,14
                                                # sorted with nth of None took 1 second

end = time.time()
print('total time elapsed for test 3:',str(end-start))




print('-----------------------------------------------------------------------------------------------------')
print('test 4')
t3 = Table(test_columns+['Col4'],  [['A','B','C','A'],['A','C','B','A'],['C','B','A','B']], domains_cardinality)
print('original table:')
print(t3)
start = time.time()
# find_answer(t3,2,['greedy_det','greedy_deep_det']) 
find_answer(t3,2,'all except comp')           # wsd 2 sec

end = time.time()
print('total time elapsed for test 4:',str(end-start))



print('--------------------------------------------------------------------------------------------------------')
print('test 5')
t3 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A'],['A','C','C']], domains_cardinality)      
print('original table:')
print(t3)
start = time.time()
find_answer(t3,2, 'all except comp')                    # n=1 took 843 sec, got (3,14)
# find_answer(t3,2,['greedy_det','greedy_deep_det'])        # WSD 30s, 14s

end = time.time()
print('total time elapsed for test 5:',str(end-start))      #

