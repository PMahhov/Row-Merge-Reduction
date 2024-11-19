import random
import time
import sys
from collections import defaultdict
from algorithms_3 import TableTreeNode, NodeScore, TableTree, find_answer
from relationships_table_2 import Table
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


ignore_possibles = False        # if true, only use certain relationships
save_output = True

single_table_test = False
columns_test = True
domains_test = True
rows_test = True



if save_output:
    file = open('synthetic_output.txt', 'a')
    sys.stdout = file


random.seed(7)

def generate_table(rows_num: int, columns_num: int, domain_size: int, inferred_domains = False):        # TODO: non-uniform domains
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

    return Table(columns, rows, domains)


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

    # plt.show()
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

    plt.savefig('performance_4-3-4-2.png')


    # plt.show()
    plt.close()



# Random walks

algs = ['random walks']

walks_count = [1,2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50]
# walks_count = [1, 2, 3]
t1 = generate_table(rows_num = 5, columns_num = 5, domain_size = 5)
answers, scores, times = find_answer(t1, 2, algs, walks_count, show_answers=False)


score_values = []
time_values = []

categories = walks_count
labels = []

for alg in algs:
    if 'random walks' in alg:
        for i in range(len(walks_count)):
            alg = 'random walks ' + str(walks_count[i])
            # i += 1
            # print (alg,scores[alg])
            score_values.append(scores[alg][0])
            # categories.append(alg)
            labels.append(scores[alg][1])
            time_values.append(times[alg])
    else:
        # print (alg,scores[alg])
        score_values.append(scores[alg][0])
        # categories.append(alg)
        labels.append(scores[alg][1])
        time_values.append(times[alg])
        

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
plt.ylabel('Score')
plt.title('Random Walks quality')

plt.xticks(rotation=20, fontsize=9) 
plt.yticks(range(0, round(max(score_values)*1.2), 1))

plt.tight_layout()

plt.savefig('random_walks_quality.png')
# plt.show()

plt.close()


# Random walks Performance: 

plt.figure()
plt.plot(categories, time_values)

plt.xlabel('Number of Walks')
plt.ylabel('Time')
plt.title('Random Walks performance')

plt.xticks(rotation=20, fontsize=9) 
# plt.yticks(range(0, round(max(score_values)*1.2), 1))

# plt.yscale('log')

plt.tight_layout()

plt.savefig('random_walks_performance.png')


# plt.show()
plt.close()




# Changing number of columns
if columns_test:
    # test_columns = [2,3,4,5] 
    test_columns = [2,3,4,5,7,9]
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    walks_count = [10]
    rows_num = 4
    domain_size = 4
    desired_size = 2

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_columns
    labels = defaultdict(list)
    lines = []

    for j, col_num in enumerate(test_columns):
        table = generate_table(rows_num, col_num, domain_size)
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
        print(categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    plt.ylabel('Score')
    plt.title('Score as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    plt.savefig('columns_quality.png')
    # plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    plt.ylabel('Time')
    plt.title('Time as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))
    # plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    plt.savefig('columns_performance.png')
    # plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of Columns')
    plt.ylabel('Log10(Time)')
    plt.title('Log Time as columns increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))
    # plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.yscale('log')

    plt.tight_layout()

    plt.savefig('columns_log_performance.png')
    # plt.show()

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
        print(categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    plt.ylabel('Score')
    plt.title('Score as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    plt.savefig('domains_quality.png')
    # plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    plt.ylabel('Time')
    plt.title('Time as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    plt.savefig('domains_performance.png')
    # plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Size of column domain')
    plt.ylabel('Log10(Time)')
    plt.title('Log Time as domains increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    plt.savefig('domains_log_performance.png')
    # plt.show()

    plt.close()




# Changing number of rows

if rows_test:
    # test_rows = [3,4,5,6] 
    test_rows = [3,4,5,6,8,10,20]
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    walks_count = [10]
    columns_num = 4
    desired_size = 2
    domain_size = 4

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = test_rows
    labels = defaultdict(list)
    lines = []

    for j, rows_num in enumerate(categories):
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
        print(categories, score_values[alg], str(alg))
        plt.plot(categories, score_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    plt.ylabel('Score')
    plt.title('Score as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    plt.savefig('rows_quality.png')
    # plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    plt.ylabel('Time')
    plt.title('Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    plt.savefig('rows_performance.png')
    # plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories, time_values[alg], label=str(alg))

    plt.xlabel('Number of rows')
    plt.ylabel('Log10(Time)')
    plt.title('Log Time as rows increase')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    plt.savefig('rows_log_performance.png')
    # plt.show()

    plt.close()




if save_output:
    file.close()