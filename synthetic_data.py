import random
import time
import sys
from collections import defaultdict
from algorithms_3 import TableTreeNode, NodeScore, TableTree, find_answer
from relationships_table_2 import Table
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


ignore_possibles = False        # if true, only use certain relationships
save_output = False
save_graphs = True
show_graphs = True

# enable/disable testing some aspects
single_table_test = False
random_walks_test = False
columns_test = True
domains_test = False
rows_test = False
similarity_test = False

num_of_tries = 2    # run each test this many times and take the avg result

first_time = time.time()
print('started testing with synthetic data')

if save_output:
    file = open('synthetic_output.txt', 'a')
    sys.stdout = file
    print('================================================================================')
    print('TEST START')
    print('================================================================================')


random.seed(7)

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


# TODO: get score/performance averages instead of one random table

if single_table_test:
    # for i in range(3):
    t1 = generate_table(rows_num = 4, columns_num = 3, domain_size = 4)
        # print(t1)


    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order']

    walks_count = [1,2, 3]
    answers, scores, times = find_answer(t1, 2, algs, walks_count, show_answers=True)

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
        plt.savefig('quality_4-3-4-2.png')
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
        plt.savefig('performance_4-3-4-2.png')

    if show_graphs:
        plt.show()

    plt.close()


if random_walks_test:
    # Random walks

    algs = ['random walks']

    walks_count = [1,2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50]
    # walks_count = [1, 2, 3]
    rows_num = 5
    columns_num = 5
    domain_size = 5
    desired_size = 2

    print('testing random walks with',rows_num,'rows,',columns_num,'columns, domain size',domain_size, 'and desired size',desired_size)

    categories = walks_count

    score_values = []
    time_values = []
    labels = []

    for t in range(num_of_tries):
        t1 = generate_table(rows_num, columns_num, domain_size, local_ignore_possibles=ignore_possibles)
        answers, scores, times = find_answer(t1, desired_size, algs, walks_count, show_answers=False)

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
        plt.ylabel('Average Score from',num_of_tries,'tables')
    plt.title('Random Walks quality')

    plt.xticks(rotation=20, fontsize=9) 
    plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('random_walks_quality.png')

    if show_graphs:
        plt.show()
    

    plt.close()


    # Random walks Performance: 

    plt.figure()
    plt.plot(categories, time_values)

    plt.xlabel('Number of Walks')
    if num_of_tries == 1:
        plt.ylabel('Time')
    else:
        plt.ylabel('Average Time from',num_of_tries,'tables')
    plt.title('Random Walks performance')

    plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    # plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('random_walks_performance.png')

    if show_graphs:
        plt.show()

    plt.close()




# Changing number of columns
if columns_test:
    test_columns = [2,3,4] 
    # test_columns = [2,3,4,5,7,9]
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    walks_count = [10]
    rows_num = 4
    domain_size = 4
    desired_size = 2

    print('testing columns with',rows_num,'rows,',test_columns,'columns, domain size',domain_size, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_columns
    labels = defaultdict(list)
    lines = []


    for t in range(num_of_tries):
        k_dict = defaultdict(lambda:0)

        for j, col_num in enumerate(test_columns):
            table = generate_table(rows_num, col_num, domain_size)
            answers, scores, times = find_answer(table, desired_size, algs, walks_count, show_answers=False)
        
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
        print('columns',categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from',num_of_tries,'tables')
    plt.title('Score as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('columns_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Time')
    else:
        plt.ylabel('Average Time from',num_of_tries,'tables')
    plt.title('Time as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))
    # plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('columns_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time)')
    else:
        plt.ylabel('Average Log10(Time) from',num_of_tries,'tables')
    plt.title('Log Time as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))
    # plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('columns_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()



# Changing size of domains
if domains_test:
    # test_domains = [2,3,4,5] #
    test_domains = [2,3,4,5,7,9]
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    walks_count = [10]
    rows_num = 4
    columns_num = 4
    desired_size = 2

    print('testing domains with',rows_num,'rows,',columns_num,'columns, domain size',test_domains, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_domains
    labels = defaultdict(list)
    lines = []

    for j, dom_num in enumerate(categories):
        table = generate_table(rows_num, columns_num, domain_size = dom_num)
        answers, scores, times = find_answer(table, desired_size, algs, walks_count, show_answers=False)
        for alg in algs:
            if 'random walks' in alg:
                for i in range(len(walks_count)):
                    alg = 'random walks ' + str(walks_count[i])
                    score_values[alg].append(scores[alg][0])
                    labels[alg].append(scores[alg][1])
                    time_values[alg].append(times[alg])
                    if j == 0:
                        lines.append(alg)
            else:
                score_values[alg].append(scores[alg][0])
                labels[alg].append(scores[alg][1])
                time_values[alg].append(times[alg])
                if j == 0:
                    lines.append(alg)

    plt.figure()
    for alg in lines:
        print('domains',categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from',num_of_tries,'tables')
    plt.title('Score as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('domains_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    if num_of_tries == 1:
        plt.ylabel('Time')
    else:
        plt.ylabel('Average Time from',num_of_tries,'tables')
    plt.title('Time as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('domains_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time)')
    else:
        plt.ylabel('Average Log10(Time) from',num_of_tries,'tables')
    plt.title('Log Time as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('domains_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()




# Changing number of rows

if rows_test:
    # test_rows = [3,4,5,6] 
    test_rows = [3,4,5,6,8,10,20]     
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    # algs = ['similarity', 'similarity minhash']#, 'greedy']
    walks_count = [10]
    columns_num = 4
    desired_size = 8
    domain_size = 4

    print('testing rows with',test_rows,'rows,',columns_num,'columns, domain size',domain_size, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_rows
    labels = defaultdict(list)
    lines = []

    for j, rows_num in enumerate(categories):
        print('starting rows test with', rows_num, 'rows')
        table = generate_table(rows_num, columns_num, domain_size)
        answers, scores, times = find_answer(table, desired_size, algs, walks_count, show_answers=False)
        for alg in algs:
            if 'random walks' in alg:
                for i in range(len(walks_count)):
                    alg = 'random walks ' + str(walks_count[i])
                    score_values[alg].append(scores[alg][0])
                    labels[alg].append(scores[alg][1])
                    time_values[alg].append(times[alg])
                    if j == 0:
                        lines.append(alg)
            else:
                score_values[alg].append(scores[alg][0])
                labels[alg].append(scores[alg][1])
                time_values[alg].append(times[alg])
                if j == 0:
                    lines.append(alg)

    plt.figure()
    for alg in lines:
        print('rows',categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from',num_of_tries,'tables')
    plt.title('Score as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('rows_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Time')
    else:
        plt.ylabel('Average Time from',num_of_tries,'tables')
    plt.title('Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('rows_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time)')
    else:
        plt.ylabel('Average Log10(Time) from',num_of_tries,'tables')
    plt.title('Log Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('rows_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

# Changing number of rows for fastest algs

if similarity_test:
    # test_rows = [3,4,5,6] 
    # test_rows = [3,4,5,6,8,10,20]     
    test_rows = [10,100,1000,10000,100000,1000000]
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    algs = ['similarity', 'similarity minhash']#, 'greedy'] #greedy should stop at 100
    walks_count = [10]
    columns_num = 5
    desired_size = 8
    domain_size = 10
    # domain_size = 1

    print('testing similarity with',test_rows,'rows,',columns_num,'columns, domain size',domain_size, 'and desired size',desired_size)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_rows
    labels = defaultdict(list)
    lines = []

    for j, rows_num in enumerate(categories):
        print('starting rows test with', rows_num, 'rows')
        table = generate_table(rows_num, columns_num, domain_size)
        answers, scores, times = find_answer(table, desired_size, algs, walks_count, show_answers=False)
        for alg in algs:
            if 'random walks' in alg:
                for i in range(len(walks_count)):
                    alg = 'random walks ' + str(walks_count[i])
                    score_values[alg].append(scores[alg][0])
                    labels[alg].append(scores[alg][1])
                    time_values[alg].append(times[alg])
                    if j == 0:
                        lines.append(alg)
            else:
                score_values[alg].append(scores[alg][0])
                labels[alg].append(scores[alg][1])
                time_values[alg].append(times[alg])
                if j == 0:
                    lines.append(alg)

    plt.figure()
    for alg in lines:
        print('rows',categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from',num_of_tries,'tables')
    plt.title('Score as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('similarity_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Time')
    else:
        plt.ylabel('Average Time from',num_of_tries,'tables')
    plt.title('Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('similarity_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time)')
    else:
        plt.ylabel('Average Log10(Time) from',num_of_tries,'tables')
    plt.title('Log Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('rows_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

last_time = time.time()

if save_output:
    print('ended testing with synthetic data, it took',last_time-first_time,'seconds total')
    file.close()

print('ended testing with synthetic data, it took',last_time-first_time,'seconds total')