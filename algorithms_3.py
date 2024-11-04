from relationships_table_2 import Table
import copy
import time
import random
import heapq
import sys

save_output = True

if save_output:
    file = open('output.txt', 'a')
    sys.stdout = file


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

    def is_same(self, other):
        return self.table.is_same(other.table)

    def add_layer(self):
        for i, current_row in enumerate(self.table.rows):
            for current_column in self.table.columns:
                if current_row.get_value(current_column) != '*':
                    new_table = Table(columns = self.table.columns, initial_list=self.table.rows, domains_cardinality=self.table.domains_cardinality, origin ='row objects')    # 1 min for 3x3
                    # TODO: possible optimization, keep a set of existing row objects, if the new row already exists from before add a pointer to that instead of copying into a new one, else add to all objects list
                    new_table.make_null_copying_row(current_row, current_column)
                    new_nullings = copy.deepcopy(self.nullings)
                    new_nullings.append((current_row.get_id(), current_column))
                    new_node = TableTreeNode(new_table, new_nullings)
                    self.children.append(new_node)


class NodeScore():
    def __init__(self, node, certains, possibles):
        self.node = node
        self.certains = certains
        self.possibles = possibles

    def __lt__(self, other):        # NB: since heapq uses minheap, here scores are inverted
        if self.certains == other.certains:
            return self.possibles < other.possibles
        else:
            return self.certains > other.certains

    def get_node(self):
        return self.node

class TableTree():
    '''
    root: node with original table
    
    '''
    def __init__(self, table):
        self.root = TableTreeNode(table)


    def sorted_order_algorithm(self, desired_size: int, nth = 1, loading_progress = False): # n-th: stop at the n-th valid answer
        # reset children:
        self.root.children = []

        if loading_progress:
            print('Starting sorted order algorithm')

        best_valids = []
        max_certains = 0
        min_possibles = 'inf'

        n_count = 0

        if self.root.get_size() <= desired_size:
            return [self.root.table]

        current_node = self.root

        current_layer = 0

        # TODO: switch rev sorted nodes from list to sth like an AVL tree
        # rev_sorted_nodes = []
        node_scores_heap = []

        end_loop = False

        while not end_loop:
            # print(current_node)

        # loading progress
            if loading_progress:
                if current_node.get_layer() != current_layer:
                    current_layer = current_node.get_layer()
                    print('Layer',current_layer)

            current_node.add_layer()        # creates all children of node
            if len(current_node.children) > 0:
                for child in current_node.children:

                    node_score = NodeScore(child, child.get_certains(), child.get_exp_possibles())
                    if child.get_size() <= desired_size:
                        # print('valid found', n_count)
                        # print(child)
                        if min_possibles == 'inf':
                                best_valids = [child]
                                max_certains = node_score.certains
                                min_possibles = node_score.possibles
                                n_count += 1
                        elif node_score.certains > max_certains:
                            best_valids = [child]
                            max_certains = node_score.certains
                            min_possibles = node_score.possibles
                            n_count += 1
                        elif node_score.certains == max_certains:
                            if node_score.possibles < min_possibles:
                                best_valids = [child]
                                min_possibles = node_score.possibles
                                n_count += 1
                            elif node_score.possibles == min_possibles:
                                best_valids.append(child)
                        if n_count == nth:
                            end_loop = True
                            break
                    else:       # if child is not valid, add to heap to keep searching
                        heapq.heappush(node_scores_heap, node_score)
            

                if len(node_scores_heap) > 0:
                    highest_score = heapq.heappop(node_scores_heap)
                    current_node = highest_score.get_node()

                # sort the list of nodes in reverse (sorting works in descending order)
                    # it is faster to pop the last than the first item in a list
                #        (score 2 gets a minus sign, as it is a non-negative value that needs to be minimized
                    # rev_sorted_nodes = sorted(rev_sorted_nodes, key=lambda score: (score[1], -score[2]))   
                    # print('rev sorted_nodes')
                    # print(rev_sorted_nodes)
                # take best node
                    # current_node = rev_sorted_nodes.pop(-1)[0]


                    
# only continue looping if the score of the best sorted is better than the current valid score
                    if len(best_valids) > 0:       
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
                if len(best_valids) > 0:
                    end_loop = True
                    break
                else:
                    raise ValueError('No valid answer found') # should never happen if desired_size>0, *** is always valid

        # remove duplicates
        unique_bests = []
        for current_node in best_valids:
            if not any(existing_table.is_same(current_node) for existing_table in unique_bests):
                unique_bests.append(current_node)
        return unique_bests

    def greedy_algorithm(self, desired_size: int, loading_progress = False):
                # reset children
        self.root.children = []
        
        if loading_progress:
            print('Starting greedy algorithm')

        valids = set()
        if self.root.get_size() <= desired_size:
            return [self.root.table]

        valid_answer_exists = False
        new_to_check = [[self.root]]


        current_layer = 0


        while not valid_answer_exists:
            to_check = random.choice(new_to_check)
            new_to_check = []
            for tree_node in to_check:

                # loading progress
                if loading_progress:
                    if tree_node.get_layer() != current_layer:
                        current_layer = tree_node.get_layer()
                        print('Layer',current_layer)

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
                        else:
                            certains = child.get_certains()
                            possibles = child.get_exp_possibles()
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
                new_to_check.append(current_bests)

        if len(valids) == 1:
            for v in valids:
                return [v]

        # compare all found valid solutions
        max_certains = 0
        current_bests = []
        for i, v in enumerate(valids):
            certains = v.get_certains()
            possibles = v.get_exp_possibles()
            if i == 0:
                min_possibles = possibles
            if max_certains < certains:
                current_bests = [v]
                max_certains = certains
                min_possibles = possibles       # certains override possibles
            elif max_certains == certains:
                if min_possibles > possibles:
                    current_bests = [v]
                elif min_possibles == possibles:
                    current_bests.append(v)

        # remove duplicates
        unique_bests = []
        for current_node in current_bests:
            if not any(existing_node.is_same(current_node) for existing_node in unique_bests):
                unique_bests.append(current_node)

        return unique_bests

    def exhaustive_algorithm(self, desired_size: int, pruning = True, loading_progress = True):
        # reset children
        if loading_progress:
            print('Starting exhaustive algorithm')

        self.root.children = []
        
        if self.root.get_size() <= desired_size:
            return [self.root.table]

        new_to_check = [self.root]

        best_valids = []
        max_certains = 0
        min_possibles = 'inf'
        
        current_layer = 0

        while len(new_to_check) > 0:
            to_check = new_to_check
            new_to_check = []
            
            for tree_node in to_check:

                if loading_progress:
                    if tree_node.get_layer() != current_layer:
                        current_layer = tree_node.get_layer()
                        print('Layer',current_layer)

                tree_node.add_layer()
                current_bests = []
                if len(tree_node.children) > 0:
                    for i, child in enumerate(tree_node.children):
                        if child.get_size() <= desired_size:    # child is valid
                            certains = child.get_certains()
                            possibles = child.get_exp_possibles()
                            if min_possibles == 'inf':
                                max_certains = certains
                                min_possibles = possibles
                            elif max_certains < certains:
                                best_valids = [child]
                                max_certains = certains
                                min_possibles = possibles
                            elif max_certains == certains:
                                if min_possibles > possibles:
                                    best_valids = [child]
                                    min_possibles = possibles
                                elif min_possibles == possibles:
                                    best_valids.append(child)
                                    
                        else:           # child is not valid
                            if pruning and min_possibles != 'inf':
                                certains = child.get_certains()
                                possibles = child.get_exp_possibles()
                                if max_certains < certains:
                                    current_bests.append(child)
                                elif max_certains == certains:
                                    if min_possibles >= possibles:
                                        current_bests.append(child)
                            else:
                                current_bests.append(child)
                new_to_check += current_bests

    
        if len(best_valids) == 1:
            return best_valids

        # remove duplicates
        unique_bests = []
        for current_node in best_valids:
            if not any(existing_node.is_same(current_node) for existing_node in unique_bests):
                unique_bests.append(current_node)

        return unique_bests


    def random_walks_algorithm(self, desired_size, walks_count = 1, pruning = True, loading_progress = False):
        # reset children
        if loading_progress:
            print('Starting random walks')

        self.root.children = []

        best_valids = []

        if self.root.get_size() <= desired_size:
            return [self.root.table]

        new_to_check = [[self.root]]

        best_valids = []
        max_certains = 0
        min_possibles = 'inf'

        valid_answer_exists = False

        for i in range(walks_count):

            if loading_progress:
                print('Walk',i+1,'out of',walks_count)

            while not valid_answer_exists:
                to_check = random.choice(new_to_check)
                new_to_check = []


                if pruning and min_possibles != 'inf':
                    tree_node = to_check[0]
                    certains = tree_node.get_certains()
                    possibles = tree_node.get_exp_possibles()
                    if certains < max_certains:
                        break
                    else:
                        if certains == max_certains and possibles > min_possibles:
                            break

                for tree_node in to_check:     
                    tree_node.add_layer()
                    currents = []
                    if len(tree_node.children) > 0:
                        for i, child in enumerate(tree_node.children):
                            if child.get_size() <= desired_size:    # child is valid
                                valid_answer_exists = True
                                certains = child.get_certains()
                                possibles = child.get_exp_possibles()
                                if min_possibles == 'inf':
                                    max_certains = certains
                                    min_possibles = possibles
                                elif max_certains < certains:
                                    best_valids = [child]
                                    max_certains = certains
                                    min_possibles = possibles
                                elif max_certains == certains:
                                    if min_possibles > possibles:
                                        best_valids = [child]
                                        min_possibles = possibles
                                    elif min_possibles == possibles:
                                        best_valids.append(child)
                            else:           # child is not valid
                                # if walking_with_purpose:
                                #     # only append the non-valid children which score better or equal than best answer
                                # else:
                                    # currents.append(child)
                                currents.append(child)
                    new_to_check.append(currents)

        if len(best_valids) == 1:
            return best_valids

        # remove duplicates
        unique_bests = []
        for current_node in best_valids:
            if not any(existing_node.is_same(current_node) for existing_node in unique_bests):
                unique_bests.append(current_node)

        return unique_bests


def find_answer(table, desired_size, alg = ['exhaustive', 'greedy','random walks','sorted order'], walks_count = 1, time_to_show = 0, show_answers = True):
    tree = TableTree(table)
    print('alg is',alg)
    if alg == 'all except exhaustive' or 'greedy' in alg:
        start_greedy= time.time()
        greedy_answers = tree.greedy_algorithm(desired_size)
        end_greedy = time.time()
        if show_answers:
            print('greedy answers:')
            for answer in greedy_answers:
                print(answer)
                print('Score (certains, possibles):',f'({answer.get_certains()}, {answer.get_exp_possibles()})')
                print(len(answer.nullings),'nullings:',answer.nullings)
        time_greedy = end_greedy - start_greedy
        if time_greedy > time_to_show:
            print('Greedy took', time_greedy,'seconds')
    if alg == 'all except exhaustive' or 'random walks' in alg:
        start_walks = time.time()
        walks_answers = tree.random_walks_algorithm(desired_size, walks_count)
        end_walks = time.time()
        if show_answers:
            print('random walks answers:')
            for answer in walks_answers:
                print(answer)
                print('Score (certains, possibles):',f'({answer.get_certains()}, {answer.get_exp_possibles()})')
                print(len(answer.nullings),'nullings:',answer.nullings)
        time_walks = end_walks - start_walks
        if time_walks > time_to_show:
            print(walks_count,'random walks took', time_walks,'seconds')
    if alg == 'all except exhaustive' or 'sorted order' in alg:
        start_sorted_order = time.time()
        sorted_order_answers = tree.sorted_order_algorithm(desired_size)
        end_sorted_order = time.time()
        if show_answers:
            print('sorted order answers:')
            for answer in sorted_order_answers:
                print(answer)
                print('Score (certains, possibles):',f'({answer.get_certains()}, {answer.get_exp_possibles()})')
                print(len(answer.nullings),'nullings:',answer.nullings)
        time_sorted_order = end_sorted_order - start_sorted_order
        if time_sorted_order > time_to_show:
            print('Sorted order took', time_sorted_order,'seconds')
    if alg != 'all except exhaustive' and 'exhaustive' in alg:
    # if True:
        start_comp = time.time()
        comp_answers = tree.exhaustive_algorithm(desired_size)
        end_comp = time.time()
        if show_answers:
            print('exhaustive answers:')
            for answer in comp_answers:
                print (answer)
                print('Score (certains, possibles):',f'({answer.get_certains()}, {answer.get_exp_possibles()})')
                print(len(answer.nullings),'nullings:',answer.nullings)
        time_comp = end_comp - start_comp
        if time_comp > time_to_show:
            print('Exhaustive calculation took',time_comp,'seconds')            



test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']
domains_cardinality = {'Col1':3, 'Col2':3, 'Col3':3, 'Col4':2}


print('========================================================================================================')
print('test 1')
t1 = Table(test_columns, test_table, {'Col1':3, 'Col2':3, 'Col3':3})
print(t1)
find_answer(t1, 1, walks_count = 2)

print('-----------------------------------------------')
print('test 2')
t2 = Table(test_columns,  [['A','B','C'],['A','C','B']], domains_cardinality)
print(t2)
find_answer(t2,1, walks_count = 20)


print('-----------------------------------------------')
print('test 3')
t3 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A']], domains_cardinality)     
print('original table:')
print(t3)
start = time.time()
find_answer(t3,2,walks_count=3)         # comp took 53,58, 67, 74, 120 sec to run
                                                # best answer is 2x (3,14)                                                
end = time.time()
print('total time elapsed for test 3:',str(end-start))

print('-----------------------------------------------------------------------------------------------------')
print('test 4')
t3 = Table(test_columns+['Col4'],  [['A','B','C','A'],['A','C','B','A'],['C','B','A','B']], domains_cardinality)
print('original table:')
print(t3)
start = time.time()
# find_answer(t3,2,'all except exhaustive', walks_count=4)           # sorted 3s, exh 21s, same answer
find_answer(t3,2, 'all except exhaustive', walks_count= 10000)           #   best answer is 1x (7,20)


end = time.time()
print('total time elapsed for test 4:',str(end-start))


print('--------------------------------------------------------------------------------------------------------')
print('test 5')
t3 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A'],['A','C','C']], domains_cardinality)      
print('original table:')
print(t3)
start = time.time()
# find_answer(t3,2, ['greedy, random walks', 'sorted order'], walks_count=5)                    # n=1 sorted took 843 sec, got (3,14)
# find_answer(t3,2, ['greedy', 'random walks', 'exhaustive'], walks_count=10000)          
find_answer(t3,2, ['greedy', 'random walks', 'sorted order', 'exhaustive'], walks_count=100000)          

end = time.time()
print('total time elapsed for test 5:',str(end-start))     

# greedy took 0.03s and got 1x(3,24), [ACB, ***]
# 100 walks took 0.13s and got 1x(3,24), [ACB, ***]
# 10000 walks took 0.05s and got same
# sorted order took 746s with list and 32s with heap and got 1x(3,14), [CBA, A**]
    # 6 nullings: [(13, 'Col3'), (10, 'Col2'), (13, 'Col2'), (11, 'Col3'), (11, 'Col2'), (10, 'Col3')]
# exhaustive took 357s, 308s, 327s and got 1x(3,14), [CBA, A**]
    # 5 nullings:[(10, 'Col2'), (10, 'Col3'), (13, 'Col3'), (11, 'Col3'), (13, 'Col2')]
        # TODO: fix whatever reason is causing the last null not to appear, (11, Col2)

print('--------------------------------------------------------------------------------------------------------')
print('test 6')
t3 = Table(test_columns,  [['A','B','C'],['D','B','E'],['A','E','C'],['A','B','F']])      
print('original table:')
print(t3)
start = time.time()
find_answer(t3,3, ['greedy', 'random walks', 'sorted order', 'exhaustive'], walks_count=10000)          
# find_answer(t3,2, ['greedy', 'random walks', 'sorted order', 'exhaustive'], walks_count=10000) 
end = time.time()
print('total time elapsed for test 6:',str(end-start))  





if save_output:
    file.close()