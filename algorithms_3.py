from relationships_table_2 import Table
import copy
import time
import random
import heapq
import sys
from collections import defaultdict


save_output = False
testing = False
support_minhashing = True

if support_minhashing:  # this is the only non-default python package
    from datasketch import MinHash



if save_output:
    file = open('output.txt', 'a')
    sys.stdout = file


class TableTreeNode():
    '''
    table (Table)
    children (list): list of nodes
    nullings: list of nulling operations conducted to get to this point
    
    '''
    def __init__(self, table, nullings = [], ignore_possibles = False):
        self.table = table
        self.nullings = nullings        
        self.children = []
        self.ignore_possibles = ignore_possibles
        

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
        if self.children == []:
            for i, current_row in enumerate(self.table.rows):
                for current_column in self.table.columns:
                    if current_row.get_value(current_column) != '*':
                        new_table = Table(columns = self.table.columns, initial_list=self.table.rows, domains_cardinality=self.table.domains_cardinality, origin ='row objects', ignore_possibles=self.ignore_possibles)    # 1 min for 3x3
                        # TODO: possible optimization, keep a set of existing row objects, if the new row already exists from before add a pointer to that instead of copying into a new one, else add to all objects list
                        new_table.make_null_copying_row(current_row, current_column)
                        new_nullings = copy.deepcopy(self.nullings)
                        new_nullings.append((current_row.get_id(), current_column))
                        new_node = TableTreeNode(table = new_table, nullings = new_nullings, ignore_possibles=self.ignore_possibles)
                        self.children.append(new_node)


class NodeScore():
    def __init__(self, node, certains, possibles):
        self.node = node
        self.certains = certains
        self.possibles = possibles
        self.size = node.get_size()

    def __lt__(self, other):        # NB: since heapq uses minheap, here scores are inverted, so lower is better -> return True if self goes first
        if self.certains == other.certains:
            if self.possibles == other.possibles:
                return self.size < other.size
            else:
                return self.possibles < other.possibles
        else:
            return self.certains > other.certains

    def get_node(self):
        return self.node

class TableTree():
    '''
    root: node with original table
    
    '''
    def __init__(self, table, ignore_possibles = False):
        self.root = TableTreeNode(table = table, nullings = [], ignore_possibles=ignore_possibles)

# check similarities of 2-row combinations, then merge most similar, repeat
    def similarity_algorithm(self, desired_size: int, loading_progress = False, make_copy = True):
        if make_copy:       # you can set make copy to false to speed it up if you're not going to be reusing the same table again
            table = copy.deepcopy(self.root.table)
        else:
            table = self.root.table

        if loading_progress:
            print('Calculating initial similarities')

        # remove initial duplicates
        table.check_merges()

        if table.get_size() <= desired_size:
            return [TableTreeNode(table, nullings = [])]

        nullings = [] 
        similarity_heap = []
        
        for i in range(len(table.rows)):
            row_1 = table.rows[i]
            row_1_attributes = row_1.get_attributes_set()

            for j in range(i+1, len(table.rows)):
                row_2 = table.rows[j]
                pair = frozenset([row_1, row_2])
                row_2_attributes = row_2.get_attributes_set()
                intersection = row_1_attributes.intersection(row_2_attributes)
                union = row_1_attributes.union(row_2_attributes)
                jaccard_sim = float(len(intersection)) / float(len(union))
                
                heapq.heappush(similarity_heap, (-jaccard_sim, pair))
        
        if loading_progress:
            print('pairing and merging')

        columns = table.columns
        while table.get_size() > desired_size:
        # find best pair
            best_pair = heapq.heappop(similarity_heap)[1]
            rows = []
            for row in best_pair:
                rows.append(row)

            row_1 = rows[0]
            row_2 = rows[1]
            # print('row_1',row_1, row_1.get_id())
            # print('row_2',row_2, row_2.get_id())
        
        # merge best pair
            for column in columns:
                if row_1.get_value(column) != row_2.get_value(column):
                    table.make_null_in_place(row_1, column, row_input='object', update = False, merge = False)
                    table.make_null_in_place(row_2, column, row_input='object', update = False, merge = False)
                    nullings.extend([(row_1.get_id(), column),(row_2.get_id(), column)]) # append both nulling operation records
            table.update_all_relationships()
            # if row_1.is_same(row_2):
            #     print('should be same')
            table.check_merges()

        # replace old values with new values:

            # determine which row stayed, row 1 or row 2
            new_row = None
            # print('row_1',row_1, row_1.get_id())
            # print('row_2',row_2, row_2.get_id())
            # print(table)
            both_deleted = False
            for row in table.rows:
                if row.get_id() == row_1.get_id():
                    new_row = row_1
                    old_row = row_2
                elif row.get_id() == row_2.get_id():
                    new_row = row_2
                    old_row = row_1
            if new_row == None:
                both_deleted = True
                # print('Neither row could be found in table after merge')

            # go through the list, find those where that row is in pair, recalculate the value
            
            to_delete = []
            # print('sim heap', similarity_heap)
            for i, element in enumerate(similarity_heap):
                neg_sim, pair = element
                replace = False
                for row in pair:
                    if both_deleted:
                        if row == row_1 or row == row_2:
                            to_delete.append(i)
                    elif row == old_row:  # delete
                        to_delete.append(i)
                        # del similarity_heap[i]  <-- can't do this yet, it would mess up the indexes
                    elif row == new_row:   # replace
                        replace = True
                if replace:
                    # print(table)
                    rows = []
                    for row in pair:
                        rows.append(row)
                    row_1 = rows[0]
                    row_2 = rows[1]
                    row_1_attributes = row_1.get_attributes_set()
                    row_2_attributes = row_2.get_attributes_set()
                    intersection = row_1_attributes.intersection(row_2_attributes)
                    union = row_1_attributes.union(row_2_attributes)
                    jaccard_sim = float(len(intersection)) / float(len(union))
                    similarity_heap[i] = (-jaccard_sim, pair)

            # print('to delete', to_delete)
            for index in reversed(to_delete):
                # print('deleting', index)
                del similarity_heap[index]


            # resort the heap
            heapq.heapify(similarity_heap) 

        # repeat until desired size is reached
        
        return [TableTreeNode(table, nullings)]


# check similarities of 2-row combinations, then merge most similar, repeat
    def similarity_minhash_algorithm(self, desired_size: int, loading_progress = False, make_copy = True):
        if make_copy:
            table = copy.deepcopy(self.root.table)
        else:
            table = self.root.table

        # remove initial duplicates
        table.check_merges()

        if table.get_size() <= desired_size:
            return [TableTreeNode(table, nullings = [])]

        if loading_progress:
            print('Calculating initial similarities')

        nullings = [] 
        similarity_heap = []
        minhash_dict = defaultdict(lambda: None)
        
        for i in range(len(table.rows)):
            row_1 = table.rows[i]
            row_1_attributes = row_1.get_attributes_set()

            if minhash_dict[row_1] == None:     # TODO: possible optimization, use MinHash.generator to initialize all minhashes separately before
                m1 = MinHash()
                for d in row_1_attributes:
                    m1.update(d.encode('utf8'))
                minhash_dict[row_1] = m1
            for j in range(i+1, len(table.rows)):                
                row_2 = table.rows[j]
                pair = frozenset([row_1, row_2])
                row_2_attributes = row_2.get_attributes_set()

                if minhash_dict[row_2] == None:
                    m2 = MinHash()
                    for d in row_2_attributes:
                        m2.update(d.encode('utf8'))
                    minhash_dict[row_2] = m2

                m1 = minhash_dict[row_1]
                m2 = minhash_dict[row_2]
                if m1 == None or m2 == None:
                    raise ValueError ('A minhash value is none')
                jaccard_sim = m1.jaccard(m2)        # minhash estimate of jaccard similarity
                
                heapq.heappush(similarity_heap, (-jaccard_sim, pair))
        
        columns = table.columns
        while table.get_size() > desired_size:
        # find best pair
            best_pair = heapq.heappop(similarity_heap)[1]
            rows = []
            for row in best_pair:
                rows.append(row)

            row_1 = rows[0]
            row_2 = rows[1]
        
        # merge best pair
            for column in columns:
                if row_1.get_value(column) != row_2.get_value(column):
                    table.make_null_in_place(row_1, column, row_input='object', update = False, merge = False)
                    table.make_null_in_place(row_2, column, row_input='object', update = False, merge = False)
                    nullings.extend([(row_1.get_id(), column),(row_2.get_id(), column)]) # append both nulling operation records
            table.update_all_relationships()
            table.check_merges()

        # replace old values with new values:

            # determine which row stayed, row 1 or row 2
            new_row = None
            both_deleted = False
            for row in table.rows:
                if row == row_1:
                    new_row = row_1
                    old_row = row_2
                elif row == row_2:
                    new_row = row_2
                    old_row = row_1
            if new_row == None:
                both_deleted = True
                # print('Neither row could be found in table after merge')

            # recalculate minhash value for changed row
            if both_deleted:
                minhash_dict[row_1] == None
                minhash_dict[row_2] == None
            else:
                minhash_dict[old_row] == None
                m3 = minhash_dict[new_row]
                m3.clear()
                row_attributes = new_row.get_attributes_set()
                for d in row_attributes:
                    m3.update(d.encode('utf8'))
                minhash_dict[new_row] = m3



            # go through the list, find those where that row is in pair, recalculate the value
            
            to_delete = []
            # print('sim heap', similarity_heap)
            for i, element in enumerate(similarity_heap):
                neg_sim, pair = element
                replace = False
                for row in pair:
                    if both_deleted:
                        if row == row_1 or row == row_2:
                            to_delete.append(i)
                    elif row == old_row:  # delete
                        to_delete.append(i)
                        # del similarity_heap[i]  <-- can't do this yet, it would mess up the indexes
                    elif row == new_row:   # replace
                        replace = True
                if replace:
                    # print(table)
                    rows = []
                    for row in pair:
                        rows.append(row)
                    row_1 = rows[0]
                    row_2 = rows[1]
                    row_1_attributes = row_1.get_attributes_set()
                    row_2_attributes = row_2.get_attributes_set()

                    m1 = minhash_dict[row_1]
                    m2 = minhash_dict[row_2]
                    if m1 == None or m2 == None:
                        raise ValueError ('A minhash value is none')
                    jaccard_sim = m1.jaccard(m2)        # minhash estimate of jaccard similarity

                    similarity_heap[i] = (-jaccard_sim, pair)

            # print('to delete', to_delete)
            for index in reversed(to_delete):
                # print('deleting', index)
                del similarity_heap[index]


            # resort the heap
            heapq.heapify(similarity_heap) 

        # repeat until desired size is reached
        
        return [TableTreeNode(table, nullings)]



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
            
                # continue with the best node
                if len(node_scores_heap) > 0:
                    highest_score = heapq.heappop(node_scores_heap)
                    current_node = highest_score.get_node()

                    
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

        if len(best_valids) == 1:
            return best_valids

        # remove duplicates
        unique_bests = []
        for current_node in best_valids:
            if not any(existing_table.is_same(current_node) for existing_table in unique_bests):
                unique_bests.append(current_node)
        return unique_bests

    # sorted order but if a merge is found, only continue from there
    def merge_greedy_algorithm(self, desired_size: int, nth = 1, loading_progress = True):
        # reset children:
        self.root.children = []

        best_valids = []
        max_certains = 0
        min_possibles = 'inf'

        n_count = 0

        if self.root.get_size() <= desired_size:
            return [self.root.table]

        current_node = self.root

        current_size = self.root.get_size()

        node_scores_heap = []

        end_loop = False

        if loading_progress:
            print('Starting merge greedy algorithm')
            last_displayed_size = current_size
            print('Starting size:',current_size)

        while not end_loop:
                    # loading progress
            if loading_progress:
                if last_displayed_size != current_size:
                    last_displayed_size = current_size
                    print('Size:',current_size)


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
                    elif child.get_size() < current_size: # a merge is found, continue with this one
                        node_scores_heap = [node_score]  # reset heap
                        current_size = child.get_size()
                        break

                    else:       # if child is not valid, add to heap to keep searching
                        heapq.heappush(node_scores_heap, node_score)

                # continue with the best node
                if len(node_scores_heap) > 0:
                    highest_score = heapq.heappop(node_scores_heap)
                    current_node = highest_score.get_node()

                    
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

        if len(best_valids) == 1:
            return best_valids

        # remove duplicates
        unique_bests = []
        for current_node in best_valids:
            if not any(existing_table.is_same(current_node) for existing_table in unique_bests):
                unique_bests.append(current_node)
        return unique_bests



# take the highest score in layer, only continue with that one
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
                    for child in tree_node.children:
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


    def random_walks_algorithm(self, desired_size, walks_count = 1, pruning = True, loading_progress = False, show_latest_best = True):
        # reset children
        if loading_progress:
            print('Starting random walks')

        self.root.children = []

        best_valids = []

        if self.root.get_size() <= desired_size:
            return [self.root.table]


        best_valids = []
        max_certains = 0
        min_possibles = 'inf'


        for i in range(walks_count):

            if loading_progress:
                print('Walk',i+1,'out of',walks_count)

            valid_answer_exists = False
            new_to_check = [[self.root]]


            while not valid_answer_exists:
                to_check = random.choice(new_to_check)
                new_to_check = []

                # print('checking', to_check[0])

                if pruning and min_possibles != 'inf':
                    tree_node = to_check[0]
                    certains = tree_node.get_certains()
                    possibles = tree_node.get_exp_possibles()
                    if certains < max_certains:
                        if loading_progress:
                            print ('pruned because of certains')
                        break
                    else:
                        if certains == max_certains and possibles > min_possibles:
                            if loading_progress:
                                print ('pruned because of possibles')
                            break

                for tree_node in to_check:     
                    tree_node.add_layer()
                    currents = []
                    if len(tree_node.children) > 0:
                        for child in tree_node.children:
                            if child.get_size() <= desired_size:    # child is valid
                                valid_answer_exists = True
                                certains = child.get_certains()
                                possibles = child.get_exp_possibles()
                                if min_possibles == 'inf':
                                    best_valids = [child]
                                    max_certains = certains
                                    min_possibles = possibles
                                    latest_best_walk = i+1
                                elif max_certains < certains:
                                    best_valids = [child]
                                    max_certains = certains
                                    min_possibles = possibles
                                    latest_best_walk = i+1
                                elif max_certains == certains:
                                    if min_possibles > possibles:
                                        best_valids = [child]
                                        min_possibles = possibles
                                        latest_best_walk = i+1
                                    elif min_possibles == possibles:
                                        best_valids.append(child)
                            else:           # child is not valid
                                # if walking_with_purpose:
                                #     # only append the non-valid children which score better or equal than best answer
                                # else:
                                    # currents.append(child)
                                currents.append(child)
                    new_to_check.append(currents)
                    
    


        if (loading_progress or show_latest_best):
            print('best walk on walk number', latest_best_walk,'out of',walks_count,'with score','('+str(max_certains)+','+str(min_possibles)+')')
        if len(best_valids) == 1:
            return best_valids
        # remove duplicates
        unique_bests = []
        for current_node in best_valids:
            if not any(existing_node.is_same(current_node) for existing_node in unique_bests):
                unique_bests.append(current_node)

        return unique_bests


def find_answer(table, desired_size, alg = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive'], walks_count = [2, 10], time_to_show = 0, show_answers = True, show_time = True, ignore_possibles = False):
    tree = TableTree(table, ignore_possibles = ignore_possibles)
    answers = defaultdict(lambda: None)
    scores = defaultdict(lambda: None)
    times = defaultdict(lambda: None)

    if show_answers:
        print('alg is',alg)
    if alg == 'all except exhaustive' or 'similarity' in alg:
        start_similarity = time.time()
        # if alg == ['similarity']:
        #     similarity_answers = tree.similarity_algorithm(desired_size, make_copy = False)
        # else:
        #     similarity_answers = tree.similarity_algorithm(desired_size)
        similarity_answers = tree.similarity_algorithm(desired_size)
        end_similarity = time.time()
        if show_answers:
            print('similarity answers:')
            for answer in similarity_answers:
                print(answer)
                print('Score (certains, possibles):',f'({answer.get_certains()}, {answer.get_exp_possibles()})')
                print(len(answer.nullings),'nullings:',answer.nullings)
        time_similarity = end_similarity - start_similarity
        if time_similarity > time_to_show and show_time:
            print('Similarity took', time_similarity,'seconds')

        answers['similarity'] = similarity_answers
        scores['similarity'] = (similarity_answers[0].get_certains(), similarity_answers[0].get_exp_possibles())
        times['similarity'] = time_similarity

    if alg == 'all except exhaustive' or 'similarity minhash' in alg:
        start_similarity_minhash = time.time()
        # if alg == ['similarity minhash']:
        #     similarity_minhash_answers = tree.similarity_minhash_algorithm(desired_size, make_copy = False)
        # else:
        #     similarity_minhash_answers = tree.similarity_minhash_algorithm(desired_size)
        similarity_minhash_answers = tree.similarity_minhash_algorithm(desired_size)
        end_similarity_minhash = time.time()
        if show_answers:
            print('similarity minhash answers:')
            for answer in similarity_minhash_answers:
                print(answer)
                print('Score (certains, possibles):',f'({answer.get_certains()}, {answer.get_exp_possibles()})')
                print(len(answer.nullings),'nullings:',answer.nullings)
        time_similarity_minhash = end_similarity_minhash - start_similarity_minhash
        if time_similarity_minhash > time_to_show and show_time:
            print('Similarity minhash took', time_similarity_minhash,'seconds')     

        answers['similarity minhash'] = similarity_minhash_answers
        scores['similarity minhash'] = (similarity_minhash_answers[0].get_certains(), similarity_minhash_answers[0].get_exp_possibles())
        times['similarity minhash'] = time_similarity_minhash

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
        if time_greedy > time_to_show and show_time:
            print('Greedy took', time_greedy,'seconds')

        answers['greedy'] = greedy_answers
        scores['greedy'] = (greedy_answers[0].get_certains(), greedy_answers[0].get_exp_possibles())
        times['greedy'] = time_greedy

    if alg == 'all except exhaustive' or 'random walks' in alg:
        if type(walks_count) == int:
            num_walks = 1
            # print('int')
            single_walk = True
        else:
            num_walks = len(walks_count)
            # print(num_walks)
            single_walk = False
        
        for i in range(num_walks):
            start_walks = time.time()
            if type(walks_count) == int:
                walks_answers = tree.random_walks_algorithm(desired_size, walks_count)
            else:
                walks_answers = tree.random_walks_algorithm(desired_size, walks_count[i])
            end_walks = time.time()
            if show_answers:
                if single_walk:
                    print(walks_count,'random walks answers:')
                else:
                    print(walks_count[i],'random walks answers:')
                for answer in walks_answers:
                    print(answer)
                    print('Score (certains, possibles):',f'({answer.get_certains()}, {answer.get_exp_possibles()})')
                    print(len(answer.nullings),'nullings:',answer.nullings)
            time_walks = end_walks - start_walks
            if time_walks > time_to_show and show_time:
                if single_walk:
                    print(walks_count,'random walks took', time_walks,'seconds')
                else:
                    print(walks_count[i],'random walks took', time_walks,'seconds')
            if single_walk:
                answers['random walks '+str(walks_count)] = walks_answers
                scores['random walks '+str(walks_count)] = (walks_answers[0].get_certains(), walks_answers[0].get_exp_possibles())
                times['random walks '+str(walks_count)] = time_walks
            else:
                answers['random walks '+str(walks_count[i])] = walks_answers
                scores['random walks '+str(walks_count[i])] = (walks_answers[0].get_certains(), walks_answers[0].get_exp_possibles())
                times['random walks '+str(walks_count[i])] = time_walks

    if alg == 'all except exhaustive' or 'merge greedy' in alg:
        start_merge_greedy = time.time()
        merge_greedy_answers = tree.merge_greedy_algorithm(desired_size)
        end_merge_greedy = time.time()
        if show_answers:
            print('merge greedy answers:')
            for answer in merge_greedy_answers:
                print(answer)
                print('Score (certains, possibles):',f'({answer.get_certains()}, {answer.get_exp_possibles()})')
                print(len(answer.nullings),'nullings:',answer.nullings)
        time_merge_greedy = end_merge_greedy - start_merge_greedy
        if time_merge_greedy > time_to_show and show_time:
            print('Merge greedy took', time_merge_greedy,'seconds')         

        answers['merge greedy'] = merge_greedy_answers
        scores['merge greedy'] = (merge_greedy_answers[0].get_certains(), merge_greedy_answers[0].get_exp_possibles())
        times['merge greedy'] = time_merge_greedy

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
        if time_sorted_order > time_to_show and show_time:
            print('Sorted order took', time_sorted_order,'seconds')

        answers['sorted order'] = sorted_order_answers
        scores['sorted order'] = (sorted_order_answers[0].get_certains(), sorted_order_answers[0].get_exp_possibles())
        times['sorted order'] = time_sorted_order

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
        if time_comp > time_to_show and show_time:
            print('Exhaustive calculation took',time_comp,'seconds')  

        answers['exhaustive'] = comp_answers
        scores['exhaustive'] = (comp_answers[0].get_certains(), comp_answers[0].get_exp_possibles())
        times['exhaustive'] = time_comp       

    return (answers, scores, times)   

if testing:

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
    find_answer(t2,1, walks_count = 15)


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
    find_answer(t3,2, 'all except exhaustive', walks_count= 10)           #   best answer is 1x (7,20)


    end = time.time()
    print('total time elapsed for test 4:',str(end-start))


    print('--------------------------------------------------------------------------------------------------------')
    print('test 5')
    t3 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A'],['A','C','C']], domains_cardinality)      
    print('original table:')
    print(t3)
    start = time.time()
    find_answer(t3,2, 'all except exhaustive', walks_count=10)                    # n=1 sorted took 843 sec, got (3,14)
    # find_answer(t3,2, ['greedy', 'random walks', 'exhaustive'], walks_count=10)          
    # find_answer(t3,2, ['greedy', 'random walks', 'sorted order', 'exhaustive'], walks_count=10)          

    end = time.time()
    print('total time elapsed for test 5:',str(end-start))     

    # greedy took 0.03s and got 1x(3,24), [ACB, ***]

    # sorted order took 746s with list and 32s with heap and got 1x(3,14), [CBA, A**]
        # 6 nullings: [(13, 'Col3'), (10, 'Col2'), (13, 'Col2'), (11, 'Col3'), (11, 'Col2'), (10, 'Col3')]
    # exhaustive took 357s, 308s, 327s and got 1x(3,14), [CBA, A**]
        # 5 nullings:[(10, 'Col2'), (10, 'Col3'), (13, 'Col3'), (11, 'Col3'), (13, 'Col2')]
            # 5 operations for 6 nulls because a merge takes place before

    print('--------------------------------------------------------------------------------------------------------')
    print('test 6')
    t3 = Table(test_columns,  [['A','B','C'],['D','B','E'],['A','E','C'],['A','B','F']])      
    print('original table:')
    print(t3)
    start = time.time()
    find_answer(t3,3, walks_count=10)
    end = time.time()
    print('total time elapsed for test 6:',str(end-start))            
    print('--------------------------------------------------------------------------------------------------------')
    print('test 7')
    print('original table:')
    print(t3)
    start = time.time()
    find_answer(t3,2, 'all except exhaustive', walks_count=10)     
    # find_answer(t3,2, walks_count=10)     
    # find_answer(t3,2, ['greedy', 'random walks', 'sorted order', 'exhaustive'], walks_count=10) 
    end = time.time()
    print('total time elapsed for test 7:',str(end-start))  
    
    
    print('--------------------------------------------------------------------------------------------------------')
    print('test 8')
    t3 = Table(['Col1','Col2','Col3','Col4'],  [['A','B','C','A'],['D','B','E','A'],['A','E','C','B'],['A','B','F','B'],['D','E','C','A']])      
    print('original table:')
    print(t3)
    start = time.time()
    find_answer(t3,3, ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy'], walks_count=10)
    end = time.time()
    print('total time elapsed for test 8:',str(end-start))     

    print('--------------------------------------------------------------------------------------------------------')
    print('test 9')
    t3 = Table(['Col1','Col2','Col3','Col4','Col5'],  [['A','B','C','A','B'],['D','B','E','A','A'],['A','E','C','B','B'],['A','B','F','B','A'],['D','E','C','A','A']])      
    print('original table:')
    print(t3)
    start = time.time()
    find_answer(t3,3, ['similarity', 'similarity minhash', 'greedy','random walks'], walks_count=10)
    end = time.time()
    print('total time elapsed for test 9:',str(end-start))     




if save_output:
    file.close()