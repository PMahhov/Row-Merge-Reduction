import random
import time
import sys
from collections import defaultdict
from algorithms_3 import TableTreeNode, NodeScore, TableTree, find_answer
from relationships_table_2 import Table
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


random.seed(8)

ignore_possibles = True        # if true, only use certain relationships
save_output = True
save_graphs = True
show_graphs = True


# enable/disable testing some aspects
single_table_test = False
random_walks_test = False
columns_test = False
domains_test = False
rows_test = False
similarity_test = False
similarity_test_2 = False
sim_columns_test = True

num_of_tries = 3    # run each test this many times (ex: 3) and take the avg result
similar_tables = True       # if true, add columns or rows instead of making completely new table in sequence


#TODO: 1 time vs many, drop first maybe

# TODO: alg_screen_names dictionary to change how they are described


# algorithm will not run on tables larger than this many columns
alg_col_limit = {
    'exhaustive': 4,
    'sorted order': 6,
    'merge greedy': 8,
    'random walks': 10,
    'greedy': 20,
    'similarity': None,
    'similarity minhash': None 
}

# algorithm will not run on tables larger than this many rows
alg_row_limit = {
    'exhaustive': 4,
    'sorted order': 5,
    'merge greedy': 20,
    'random walks': 12,
    'greedy': 20,
    'similarity': None,
    'similarity minhash': None 
}


first_time = time.time()
print('started testing with synthetic data')

if save_output:
    file = open('synthetic_output.txt', 'a')
    sys.stdout = file
    print('================================================================================')
    print('TEST START')
    print('================================================================================')


def generate_table(rows_num: int, columns_num: int, domain_size: int, inferred_domains = False, local_ignore_possibles = ignore_possibles):        # TODO: non-uniform domains
    start = time.time()
    columns = []
    rows = []
    domains = defaultdict(lambda: domain_size)
    for i in range(columns_num):
        columns.append('Col'+str(i+1))

    for i in range(rows_num):
        row = []
        for j in range(columns_num):
            row.append(str(random.randint(1, domains['Col'+str(j+1)])))
        rows.append(row)

    end = time.time()

    if inferred_domains:
        domains = None
    return Table(columns, rows, domains, ignore_possibles=local_ignore_possibles)



if single_table_test:
    # for i in range(3):
    t1 = generate_table(rows_num = 4, columns_num = 3, domain_size = 4)
        # print(t1)


    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order']

    walks_count = [1,2, 3]
    answers, scores, times = find_answer(t1, 2, algs, walks_count, show_answers=True, ignore_possibles = ignore_possibles)

    # print('answers')
    # print(answers)
    # print('scores')
    # print(scores)
    # print('times')
    # print(times)



    score_values = []
    time_values = []

    categories = []
    labels = []

    for alg in algs:
        if 'random walks' in alg:
            for i in range(len(walks_count)):
                alg = 'random walks ' + str(walks_count[i])
                # i += 1
                # print (alg,scores[alg])
                score_values.append(scores[alg][0])
                categories.append(alg)
                labels.append(scores[alg][1])
                time_values.append(times[alg])
        else:
            # print (alg,scores[alg])
            score_values.append(scores[alg][0])
            categories.append(alg)
            labels.append(scores[alg][1])
            time_values.append(times[alg])
            

    # Quality: Score per Algorithm for a single table
    plt.figure()
    bars = plt.bar(categories, score_values)


    if not ignore_possibles:
        for i, bar in enumerate(bars):          # adding possibles as labels
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval,   
                    str(labels[i]),  
                    ha='center', va='bottom', fontsize=10)

    plt.xlabel('Algorithm')
    plt.ylabel('Score')
    plt.title('Algorithm quality')

    plt.xticks(rotation=20, fontsize=9) 
    plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if show_graphs:
        plt.show()

    if save_graphs:
        plt.savefig('./images/quality_4-3-4-2.png')
    plt.close()


    # Performance: Time per Algorithm for a single table

    plt.figure()
    bars = plt.bar(categories, time_values)

    plt.xlabel('Algorithm')
    plt.ylabel('Time')
    plt.title('Algorithm performance')

    plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.yscale('log')
    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/performance_4-3-4-2.png')

    if show_graphs:
        plt.show()

    plt.close()


#random walks test 3x3
if random_walks_test:
    # Random walks

    algs = ['random walks']

    walks_count = [1,2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50]
    # walks_count = [1, 2, 3]
    rows_num = 3
    columns_num = 3
    domain_size = 3
    desired_size = 2

    print('testing random walks with',rows_num,'rows,',columns_num,'columns, domain size',domain_size, 'and desired size',desired_size)

    categories = walks_count

    score_values = []
    time_values = []
    labels = []

    for t in range(num_of_tries):
        t1 = generate_table(rows_num, columns_num, domain_size, local_ignore_possibles=ignore_possibles)
        answers, scores, times = find_answer(t1, desired_size, algs, walks_count, show_answers=False, ignore_possibles = ignore_possibles)

        k = 0
        for alg in algs:
            if 'random walks' in alg:
                for i in range(len(walks_count)):
                    alg = 'random walks ' + str(walks_count[i])
                    # i += 1
                    # print (alg,scores[alg])
                    if t == 0:
                        score_values.append(scores[alg][0])
                        labels.append(scores[alg][1])
                        time_values.append(times[alg])
                    else:
                        score_values[k] += scores[alg][0]
                        labels[k] += scores[alg][1]
                        time_values[k] += times[alg]
                        k += 1
            else:
                # print (alg,scores[alg])
                if t == 0:
                    score_values.append(scores[alg][0])
                    labels.append(scores[alg][1])
                    time_values.append(times[alg])
                else:
                    score_values[k] += scores[alg][0]
                    labels[k] += scores[alg][1]
                    time_values[k] += times[alg]
                    k += 1

    for k in range(len(score_values)):
        score_values[k] = score_values[k]/num_of_tries
        time_values[k] = time_values[k]/num_of_tries
        labels[k] = labels[k]/num_of_tries
    print(score_values)
    print(time_values)            

    # Random Walks Quality: 
    plt.figure()
    plt.plot(categories, score_values)


    # if not ignore_possibles:
    #     for i, bar in enumerate(bars):          # adding possibles as labels
    #         yval = bar.get_height()
    #         plt.text(bar.get_x() + bar.get_width() / 2, yval,   
    #                 str(labels[i]),  
    #                 ha='center', va='bottom', fontsize=10)

    plt.xlabel('Number of Walks')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Random Walks quality')

    plt.xticks(rotation=20, fontsize=9) 
    plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/random_walks_3x3_quality.png')

    if show_graphs:
        plt.show()
    

    plt.close()


    # Random walks Performance: 

    plt.figure()
    plt.plot(categories, time_values)

    plt.xlabel('Number of Walks')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Random Walks performance')

    plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    # plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/random_walks_3x3_performance.png')

    if show_graphs:
        plt.show()

    plt.close()

#random walks test 4x4
if random_walks_test:
    # Random walks

    algs = ['random walks']

    walks_count = [1,2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50]
    # walks_count = [1, 2, 3]
    rows_num = 4
    columns_num = 4
    domain_size = 3
    desired_size = 2

    print('testing random walks with',rows_num,'rows,',columns_num,'columns, domain size',domain_size, 'and desired size',desired_size)

    categories = walks_count

    score_values = []
    time_values = []
    labels = []

    for t in range(num_of_tries):
        t1 = generate_table(rows_num, columns_num, domain_size, local_ignore_possibles=ignore_possibles)
        answers, scores, times = find_answer(t1, desired_size, algs, walks_count, show_answers=False, ignore_possibles = ignore_possibles)

        k = 0
        for alg in algs:
            if 'random walks' in alg:
                for i in range(len(walks_count)):
                    alg = 'random walks ' + str(walks_count[i])
                    # i += 1
                    # print (alg,scores[alg])
                    if t == 0:
                        score_values.append(scores[alg][0])
                        labels.append(scores[alg][1])
                        time_values.append(times[alg])
                    else:
                        score_values[k] += scores[alg][0]
                        labels[k] += scores[alg][1]
                        time_values[k] += times[alg]
                        k += 1
            else:
                # print (alg,scores[alg])
                if t == 0:
                    score_values.append(scores[alg][0])
                    labels.append(scores[alg][1])
                    time_values.append(times[alg])
                else:
                    score_values[k] += scores[alg][0]
                    labels[k] += scores[alg][1]
                    time_values[k] += times[alg]
                    k += 1

    for k in range(len(score_values)):
        score_values[k] = score_values[k]/num_of_tries
        time_values[k] = time_values[k]/num_of_tries
        labels[k] = labels[k]/num_of_tries
    print(score_values)
    print(time_values)            

    # Random Walks Quality: 
    plt.figure()
    plt.plot(categories, score_values)


    # if not ignore_possibles:
    #     for i, bar in enumerate(bars):          # adding possibles as labels
    #         yval = bar.get_height()
    #         plt.text(bar.get_x() + bar.get_width() / 2, yval,   
    #                 str(labels[i]),  
    #                 ha='center', va='bottom', fontsize=10)

    plt.xlabel('Number of Walks')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Random Walks quality')

    plt.xticks(rotation=20, fontsize=9) 
    plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/random_walks_4x4_quality.png')

    if show_graphs:
        plt.show()
    

    plt.close()


    # Random walks Performance: 

    plt.figure()
    plt.plot(categories, time_values)

    plt.xlabel('Number of Walks')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Random Walks performance')

    plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    # plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/random_walks_4x4_performance.png')

    if show_graphs:
        plt.show()

    plt.close()


# Changing number of columns
if columns_test:
    # test_columns = [2,3,4] 
    test_columns = [2,3,4,5,6,8,10,12,20,50,100,200,300,500,1000]
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks']
    walks_count = [10]
    rows_num = 3    #4
    domain_size = 3
    desired_size = 2

    print('testing columns with',rows_num,'rows,',test_columns,'columns, domain size',domain_size, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = defaultdict(list)
    labels = defaultdict(list)
    lines = []


    for t in range(num_of_tries):
        print('Runthrough number',t,'of columntest')
        k_dict = defaultdict(lambda:0)

        if similar_tables:
            table = generate_table(rows_num, test_columns[0], domain_size)


        for j, col_num in enumerate(test_columns):
            print('starting columns test with', col_num, 'cols')
            if similar_tables == False:
                table = generate_table(rows_num, col_num, domain_size)
            elif j > 0:
                prev_cols = test_columns[j-1]
                new_count = col_num - prev_cols
                for m in range(new_count):
                    # make new col
                    column_name = 'Col'+str(prev_cols + m + 1)
                    column_contents = []
                    for j in range(rows_num):
                        column_contents.append(str(random.randint(1, domain_size)))
                    # add new col
                    if m == (new_count-1):
                        table.add_column(column_name = column_name, column_contents = column_contents, column_domain = domain_size, update_rels=True)
                    else:
                        table.add_column(column_name = column_name, column_contents = column_contents, column_domain = domain_size)

            
            answers = dict()
            scores = dict()
            times = dict()

            # print(table)

            for alg in algs:

                print('starting columns test on', alg ,'with', col_num, 'cols')
                
                if 'random walks' in alg and (alg_col_limit['random walks'] != None and col_num > alg_col_limit['random walks']):
                    print('Cancelled',alg,'on test with',col_num,'columns')
                    continue  
                elif (alg_col_limit[alg] != None and col_num > alg_col_limit[alg]):  # skips the current algorithm if over the limit
                    print('Cancelled',alg,'on test with',col_num,'columns')
                    continue
                
                else:
                    new_answers, new_scores, new_times = find_answer(table, desired_size, [alg], walks_count, show_answers=False, ignore_possibles = ignore_possibles)
                    answers = {**answers, **new_answers} # merging the two dictionaries
                    scores = {**scores, **new_scores}
                    times = {**times, **new_times}

                if 'random walks' in alg:
                    for i in range(len(walks_count)):
                        alg = 'random walks ' + str(walks_count[i])
                        if t == 0:
                            score_values[alg].append(scores[alg][0])
                            labels[alg].append(scores[alg][1])
                            time_values[alg].append(times[alg])
                            categories[alg].append(col_num)
                            if j == 0:
                                lines.append(alg)
                        else:
                            score_values[alg][k_dict[alg]] += scores[alg][0]
                            labels[alg][k_dict[alg]] += scores[alg][1]
                            time_values[alg][k_dict[alg]] += times[alg]
                            k_dict[alg] += 1
                else:
                    if t == 0:
                        score_values[alg].append(scores[alg][0])
                        labels[alg].append(scores[alg][1])
                        time_values[alg].append(times[alg])
                        categories[alg].append(col_num)
                        if j == 0:
                            lines.append(alg)
                    else:
                        score_values[alg][k_dict[alg]] += scores[alg][0]
                        labels[alg][k_dict[alg]] += scores[alg][1]
                        time_values[alg][k_dict[alg]] += times[alg]
                        k_dict[alg] += 1


    plt.figure()
    for alg in lines:
        for k in range(len(score_values[alg])):
            score_values[alg][k] = score_values[alg][k]/num_of_tries
            time_values[alg][k] = time_values[alg][k]/num_of_tries
            labels[alg][k] = labels[alg][k]/num_of_tries
        print('columns',categories[alg], score_values[alg], str(alg))
        plt.plot(categories[alg], score_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Score as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/columns_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories[alg], time_values[alg], str(alg))
        plt.plot(categories[alg], time_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Time as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))
    # plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/columns_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories[alg], time_values[alg], str(alg))
        plt.plot(categories[alg], time_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time (s))')
    else:
        plt.ylabel('Average Log10(Time (s)) from '+str(num_of_tries)+' tables')
    plt.title('Log Time as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))
    # plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/columns_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()



# Changing size of domains
if domains_test:
    # test_domains = [2,3,4] 
    test_domains = [2,3,4,5,7]
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    walks_count = [10]
    rows_num = 3                # perhaps also try 4x4
    columns_num = 3
    desired_size = 2

    print('testing domains with',rows_num,'rows,',columns_num,'columns, domain size',test_domains, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_domains
    labels = defaultdict(list)
    lines = []

    for t in range(num_of_tries):
        k_dict = defaultdict(lambda:0)

        for j, dom_num in enumerate(categories):
            table = generate_table(rows_num, columns_num, domain_size = dom_num)
            answers, scores, times = find_answer(table, desired_size, algs, walks_count, show_answers=False, ignore_possibles = ignore_possibles)
            
            for alg in algs:
                if 'random walks' in alg:
                    for i in range(len(walks_count)):
                        alg = 'random walks ' + str(walks_count[i])
                        if t == 0:
                            score_values[alg].append(scores[alg][0])
                            labels[alg].append(scores[alg][1])
                            time_values[alg].append(times[alg])
                            if j == 0:
                                lines.append(alg)
                        else:
                            score_values[alg][k_dict[alg]] += scores[alg][0]
                            labels[alg][k_dict[alg]] += scores[alg][1]
                            time_values[alg][k_dict[alg]] += times[alg]
                            k_dict[alg] += 1
                else:
                    if t == 0:
                        score_values[alg].append(scores[alg][0])
                        labels[alg].append(scores[alg][1])
                        time_values[alg].append(times[alg])
                        if j == 0:
                            lines.append(alg)
                    else:
                        score_values[alg][k_dict[alg]] += scores[alg][0]
                        labels[alg][k_dict[alg]] += scores[alg][1]
                        time_values[alg][k_dict[alg]] += times[alg]
                        k_dict[alg] += 1

    plt.figure()
    for alg in lines:
        for k in range(len(score_values[alg])):
            score_values[alg][k] = score_values[alg][k]/num_of_tries
            time_values[alg][k] = time_values[alg][k]/num_of_tries
            labels[alg][k] = labels[alg][k]/num_of_tries
        print('domains',categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Score as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/domains_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Time as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/domains_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time (s))')
    else:
        plt.ylabel('Average Log10(Time (s)) from '+str(num_of_tries)+' tables')
    plt.title('Log Time as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/domains_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()




# Changing number of rows
if rows_test:
    # test_rows = [3,4,5,6] 
    test_rows = [3,4,5,6,8,10,12,20]     
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    # algs = ['similarity', 'similarity minhash']#, 'greedy']
    walks_count = [10]
    columns_num = 3
    domain_size = 3
    desired_size = 2
    

    print('testing rows with',test_rows,'rows,',columns_num,'columns, domain size',domain_size, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = defaultdict(list)
    labels = defaultdict(list)
    lines = []

    for t in range(num_of_tries):
        print('Runthrough number',t,'of rowtest')
        k_dict = defaultdict(lambda:0)

        if similar_tables:
            table = generate_table(test_rows[0], columns_num, domain_size)

        for j, rows_num in enumerate(test_rows):
            print('starting rows test with', rows_num, 'rows')

            if similar_tables == False:
                table = generate_table(rows_num, columns_num, domain_size)
            elif j > 0:
                prev_rows = test_rows[j-1]
                new_count = rows_num - prev_rows
                for m in range(new_count):
                    # make new row
                    row_contents = []
                    for j in range(columns_num):
                        row_contents.append(str(random.randint(1, domain_size)))
                    # add new row
                    if m == (new_count-1):
                        table.create_row(new_row = row_contents, update_rels=True)
                    else:
                        table.create_row(new_row = row_contents)
            
            answers = dict()
            scores = dict()
            times = dict()

            for alg in algs:

                print('starting rows test on', alg ,'with', rows_num, 'rows')

                if 'random walks' in alg and (alg_row_limit['random walks'] != None and rows_num > alg_row_limit['random walks']):
                    print('Cancelled',alg,'on test with',rows_num,'rows')
                    continue  
                elif (alg_row_limit[alg] != None and rows_num > alg_row_limit[alg]):  # skips the current algorithm if over the limit
                    print('Cancelled',alg,'on test with',rows_num,'rows')
                    continue

                else:
                    new_answers, new_scores, new_times = find_answer(table, desired_size, [alg], walks_count, show_answers=False, ignore_possibles = ignore_possibles)
                    answers = {**answers, **new_answers} # merging the two dictionaries
                    scores = {**scores, **new_scores}
                    times = {**times, **new_times}

                if 'random walks' in alg:
                    for i in range(len(walks_count)):
                        alg = 'random walks ' + str(walks_count[i])
                        if t == 0:
                                score_values[alg].append(scores[alg][0])
                                labels[alg].append(scores[alg][1])
                                time_values[alg].append(times[alg])
                                categories[alg].append(rows_num)
                                if j == 0:
                                    lines.append(alg)
                        else:
                            score_values[alg][k_dict[alg]] += scores[alg][0]
                            labels[alg][k_dict[alg]] += scores[alg][1]
                            time_values[alg][k_dict[alg]] += times[alg]
                            k_dict[alg] += 1
                else:
                    if t == 0:
                        score_values[alg].append(scores[alg][0])
                        labels[alg].append(scores[alg][1])
                        time_values[alg].append(times[alg])
                        categories[alg].append(rows_num)
                        if j == 0:
                            lines.append(alg)
                    else:
                        score_values[alg][k_dict[alg]] += scores[alg][0]
                        labels[alg][k_dict[alg]] += scores[alg][1]
                        time_values[alg][k_dict[alg]] += times[alg]
                        k_dict[alg] += 1

    plt.figure()
    for alg in lines:
        for k in range(len(score_values[alg])):
            score_values[alg][k] = score_values[alg][k]/num_of_tries
            time_values[alg][k] = time_values[alg][k]/num_of_tries
            labels[alg][k] = labels[alg][k]/num_of_tries
        print('rows',categories[alg], score_values[alg], str(alg))
        plt.plot(categories[alg], score_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Score as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/rows_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories[alg], time_values[alg], str(alg))
        plt.plot(categories[alg], time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/rows_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories[alg], time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time (s))')
    else:
        plt.ylabel('Average Log10(Time (s)) from '+str(num_of_tries)+' tables')
    plt.title('Log Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/rows_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

# Changing number of rows for fastest algs

if similarity_test:
    # test_rows = [3,4,5,6] 
    # test_rows = [3,4,5,6,8,10,20]     
    test_rows = [10,50,100,200,300,500,1000,2000,5000,10000,20000,50000,100000] # 100: 0.46s/.56s, 1000: 268s/263s, 10000: 13035s/?s
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    algs = ['similarity', 'similarity minhash']
    walks_count = [10]
    columns_num = 4         # also try 5
    desired_size = 2        # also try 8
    domain_size = 3         # also try 5
    

    print('testing similarity with',test_rows,'rows,',columns_num,'columns, domain size',domain_size, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_rows
    labels = defaultdict(list)
    lines = []

    for t in range(num_of_tries):
        k_dict = defaultdict(lambda:0)

        for j, rows_num in enumerate(categories):
            print('starting rows test with', rows_num, 'rows')
            table = generate_table(rows_num, columns_num, domain_size)
            answers, scores, times = find_answer(table, desired_size, algs, walks_count, show_answers=False, ignore_possibles = ignore_possibles)
            
            for alg in algs:
                if 'random walks' in alg:
                    for i in range(len(walks_count)):
                        alg = 'random walks ' + str(walks_count[i])
                        if t == 0:
                            score_values[alg].append(scores[alg][0])
                            labels[alg].append(scores[alg][1])
                            time_values[alg].append(times[alg])
                            if j == 0:
                                lines.append(alg)
                        else:
                            score_values[alg][k_dict[alg]] += scores[alg][0]
                            labels[alg][k_dict[alg]] += scores[alg][1]
                            time_values[alg][k_dict[alg]] += times[alg]
                            k_dict[alg] += 1
                else:
                    if t == 0:
                        score_values[alg].append(scores[alg][0])
                        labels[alg].append(scores[alg][1])
                        time_values[alg].append(times[alg])
                        if j == 0:
                            lines.append(alg)
                    else:
                        score_values[alg][k_dict[alg]] += scores[alg][0]
                        labels[alg][k_dict[alg]] += scores[alg][1]
                        time_values[alg][k_dict[alg]] += times[alg]
                        k_dict[alg] += 1

    plt.figure()
    for alg in lines:
        for k in range(len(score_values[alg])):
            score_values[alg][k] = score_values[alg][k]/num_of_tries
            time_values[alg][k] = time_values[alg][k]/num_of_tries
            labels[alg][k] = labels[alg][k]/num_of_tries
        print('rows',categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Score as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/similarity_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/similarity_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time (s))')
    else:
        plt.ylabel('Average Log10(Time (s)) from '+str(num_of_tries)+' tables')
    plt.title('Log Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/similarity_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

if similarity_test_2:
    # test_rows = [3,4,5,6] 
    # test_rows = [3,4,5,6,8,10,20]     
    test_rows = [10,50,100,200,300,500,1000]#,10000] # 100: 0.46s/.56s, 1000: 268s/263s, 10000: 13035s/?s
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    algs = ['similarity', 'similarity minhash','merge greedy']#, 'greedy'] #greedy should stop at 100
    walks_count = [10]
    columns_num = 3        
    desired_size = 2       
    domain_size = 3        
    

    print('testing similarity with',test_rows,'rows,',columns_num,'columns, domain size',domain_size, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_rows
    labels = defaultdict(list)
    lines = []

    for t in range(num_of_tries):
        k_dict = defaultdict(lambda:0)

        for j, rows_num in enumerate(categories):
            print('starting rows test with', rows_num, 'rows')
            table = generate_table(rows_num, columns_num, domain_size)
            answers, scores, times = find_answer(table, desired_size, algs, walks_count, show_answers=False, ignore_possibles = ignore_possibles)
            
            for alg in algs:
                if 'random walks' in alg:
                    for i in range(len(walks_count)):
                        alg = 'random walks ' + str(walks_count[i])
                        if t == 0:
                            score_values[alg].append(scores[alg][0])
                            labels[alg].append(scores[alg][1])
                            time_values[alg].append(times[alg])
                            if j == 0:
                                lines.append(alg)
                        else:
                            score_values[alg][k_dict[alg]] += scores[alg][0]
                            labels[alg][k_dict[alg]] += scores[alg][1]
                            time_values[alg][k_dict[alg]] += times[alg]
                            k_dict[alg] += 1
                else:
                    if t == 0:
                        score_values[alg].append(scores[alg][0])
                        labels[alg].append(scores[alg][1])
                        time_values[alg].append(times[alg])
                        if j == 0:
                            lines.append(alg)
                    else:
                        score_values[alg][k_dict[alg]] += scores[alg][0]
                        labels[alg][k_dict[alg]] += scores[alg][1]
                        time_values[alg][k_dict[alg]] += times[alg]
                        k_dict[alg] += 1

    plt.figure()
    for alg in lines:
        for k in range(len(score_values[alg])):
            score_values[alg][k] = score_values[alg][k]/num_of_tries
            time_values[alg][k] = time_values[alg][k]/num_of_tries
            labels[alg][k] = labels[alg][k]/num_of_tries
        print('rows',categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Score as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/similarity2_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/similarity2_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time (s))')
    else:
        plt.ylabel('Average Log10(Time (s)) from '+str(num_of_tries)+' tables')
    plt.title('Log Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/similarity2_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()


# Changing number of cols for fastest algs
if sim_columns_test:
    # test_columns = [2,3,4] 
    test_columns = [10,50,100,200,300,400,500,600,700,800,900,1000,1200,1500]#,1700,2000]
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks']
    walks_count = [10]
    rows_num = 4    #4
    domain_size = 3
    desired_size = 2

    print('testing columns with',rows_num,'rows,',test_columns,'columns, domain size',domain_size, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = defaultdict(list)
    labels = defaultdict(list)
    lines = []


    for t in range(num_of_tries):
        print('Runthrough number',t,'of columntest')
        k_dict = defaultdict(lambda:0)

        if similar_tables:
            table = generate_table(rows_num, test_columns[0], domain_size)


        for j, col_num in enumerate(test_columns):
            print('starting sim columns test with', col_num, 'cols')
            if similar_tables == False:
                table = generate_table(rows_num, col_num, domain_size)
            elif j > 0:
                prev_cols = test_columns[j-1]
                new_count = col_num - prev_cols
                for m in range(new_count):
                    # make new col
                    column_name = 'Col'+str(prev_cols + m + 1)
                    column_contents = []
                    for j in range(rows_num):
                        column_contents.append(str(random.randint(1, domain_size)))
                    # add new col
                    if m == (new_count-1):
                        table.add_column(column_name = column_name, column_contents = column_contents, column_domain = domain_size, update_rels=True)
                    else:
                        table.add_column(column_name = column_name, column_contents = column_contents, column_domain = domain_size)

            
            answers = dict()
            scores = dict()
            times = dict()

            # print(table)

            for alg in algs:

                print('starting columns test on', alg ,'with', col_num, 'cols')
                
                if 'random walks' in alg and (alg_col_limit['random walks'] != None and col_num > alg_col_limit['random walks']):
                    print('Cancelled',alg,'on test with',col_num,'columns')
                    continue  
                elif (alg_col_limit[alg] != None and col_num > alg_col_limit[alg]):  # skips the current algorithm if over the limit
                    print('Cancelled',alg,'on test with',col_num,'columns')
                    continue
                
                else:
                    new_answers, new_scores, new_times = find_answer(table, desired_size, [alg], walks_count, show_answers=False, ignore_possibles = ignore_possibles)
                    answers = {**answers, **new_answers} # merging the two dictionaries
                    scores = {**scores, **new_scores}
                    times = {**times, **new_times}

                if 'random walks' in alg:
                    for i in range(len(walks_count)):
                        alg = 'random walks ' + str(walks_count[i])
                        if t == 0:
                            score_values[alg].append(scores[alg][0])
                            labels[alg].append(scores[alg][1])
                            time_values[alg].append(times[alg])
                            categories[alg].append(col_num)
                            if j == 0:
                                lines.append(alg)
                        else:
                            score_values[alg][k_dict[alg]] += scores[alg][0]
                            labels[alg][k_dict[alg]] += scores[alg][1]
                            time_values[alg][k_dict[alg]] += times[alg]
                            k_dict[alg] += 1
                else:
                    if t == 0:
                        score_values[alg].append(scores[alg][0])
                        labels[alg].append(scores[alg][1])
                        time_values[alg].append(times[alg])
                        categories[alg].append(col_num)
                        if j == 0:
                            lines.append(alg)
                    else:
                        score_values[alg][k_dict[alg]] += scores[alg][0]
                        labels[alg][k_dict[alg]] += scores[alg][1]
                        time_values[alg][k_dict[alg]] += times[alg]
                        k_dict[alg] += 1


    plt.figure()
    for alg in lines:
        for k in range(len(score_values[alg])):
            score_values[alg][k] = score_values[alg][k]/num_of_tries
            time_values[alg][k] = time_values[alg][k]/num_of_tries
            labels[alg][k] = labels[alg][k]/num_of_tries
        print('columns',categories[alg], score_values[alg], str(alg))
        plt.plot(categories[alg], score_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Score as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/sim_columns_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories[alg], time_values[alg], str(alg))
        plt.plot(categories[alg], time_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Time as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))
    # plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/sim_columns_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories[alg], time_values[alg], str(alg))
        plt.plot(categories[alg], time_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time (s))')
    else:
        plt.ylabel('Average Log10(Time (s)) from '+str(num_of_tries)+' tables')
    plt.title('Log Time as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))
    # plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./images/sim_columns_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()



last_time = time.time()

if save_output:
    print('ended testing with synthetic data, it took',last_time-first_time,'seconds total')
    file.close()

print('ended testing with synthetic data, it took',last_time-first_time,'seconds total')