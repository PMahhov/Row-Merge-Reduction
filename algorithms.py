from relationships_table import Table
from graph import Graph
import copy


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


    print('unique valid tables:')
    for t in unique_valid_tables:
        print(t)

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
            if child.root_table in valid_tables:
                pass
            elif child.root_size <= desired_size:
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



#TODO: greedy algorithm

test_table = [['A','B','C'],['A','B','B']]
test_columns = ['Col1','Col2','Col3']
domains = {'Col1':3, 'Col2':3, 'Col3':2}

# t1 = Table(test_columns, test_table, domains)
# print('original table:')
# print(t1)
# comp_result = comprehensive_algorithm(t1, 1)
# print_result(comp_result)



# t2 = Table(test_columns,  [['A','B','C'],['A','C','B']], domains)
# print('original table:')
# print(t2)

# comp_result = comprehensive_algorithm(t2, 1)
# print_result(comp_result)


# t2 = Table(test_columns,  [['A','B','C'],['A','C','B'],['C','B','A']], domains)
t2 = Table(test_columns,  [['A','B'],['A','C'],['C','B']], domains)
print('original table:')
print(t2)

comp_result = comprehensive_algorithm(t2, 2)
print_result(comp_result)

# t2 = Table(['Col1', 'Col2'],  [['A','*'],['*','*'],['C','*']], domains)
# print('original table:')
# print(t2)

# comp_result = comprehensive_algorithm(t2, 2)
# print_result(comp_result)