import csv
import time
import sys
import random
from collections import defaultdict
from algorithms_3 import find_answer
from relationships_table_2 import Table
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


random.seed(8)


ignore_possibles = True         # if true, only use certain relationships
show_graphs = False
save_graphs = True

single_table_test = False
desired_size_test = True

max_rows = 1000  #None         # how many rows to take at most, None is unlimited
# max_rows = None
# desired_size = [2000,3000,4000,5000,6000,7000,8000,9000]         # what is the maximum number of rows of the reduced database
# desired_size = [9000,8000,7000,6000,5000]#,4000,3000,2000] 
# desired_size = [4000,3000,2000] 
desired_size = [900,800,700,600,500,400,300,200,100] 
# desired_size = [20000,15000,10000]


# Function to load the data into a 2D list and extract specific columns
def load_and_filter_data(file_path, selected_columns, max_rows = max_rows):
    skipped_rowlength = 0
    skipped_invalid_state = 0
    skipped_rental = 0

    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file, delimiter='\t')  # Tab-separated file
        for i, row in enumerate(csv_reader):
            if max_rows != None and i - (skipped_invalid_state + skipped_rental + skipped_rowlength) >= max_rows:
                break
            elif len(row) < 43:
                # print('skipped row',i,row[0], 'for not enough data, row length',len(row))
                skipped_rowlength += 1
                continue
            elif row[1] not in ['TX','FL','NULL']:
                # print('skipped row',i,'for incorrect state')
                skipped_invalid_state += 1
                continue
            elif row[5] in ['Rental Property','NULL','Land Property']:       # we only look into houses for sale for better price standardization
                skipped_rental += 1
                continue
            # Extract only the selected columns (convert 1-based to 0-based indexing)
            filtered_row = [row[i - 1] for i in selected_columns]
            for i, value in enumerate(filtered_row):
                if value == 'NULL':
                    filtered_row[i] = '*'           # convert NULL to *
                elif i == 1:
                    price = int(filtered_row[1].replace(',',''))      # removing separators from price
                    if price < 100000:                  # binning price into 4 categories
                        filtered_row[1] = '<100k'
                    elif price < 500000:
                        filtered_row[1] = '100k-500k'
                    elif price < 1000000:
                        filtered_row[1] = '500k-1M'
                    else:
                        filtered_row[1] = '>1M'
            data.append(filtered_row)
        print('skipped',skipped_rowlength,'for broken input')
        print('skipped',skipped_invalid_state,'for invalid state')
        print('skipped',skipped_rental,'for being a rental or just land')
        print('kept',len(data),'rows')

    return data

# Function to create a dictionary with unique values for each selected column
def create_column_unique_dict(data, column_names):
    column_dict = {col: [] for col in column_names}
    
    for row in data:
        for i, col in enumerate(column_names):
            if row[i] not in column_dict[col]:
                column_dict[col].append(row[i])
    
    return column_dict

selected_columns = [2, 5] + list(range(27, 44))

file_path = 'data/realtordatabase.CSV'


data = load_and_filter_data(file_path, selected_columns)

column_names = ['state','price','bedroomcount','bathroomcount','fence','Deck','Swimming Pool','Smoke Detector','Garage','Parking','Automatic Gates', 'Porch','Playground','Community Clubhouse','Trees','Courtyard','Sidewalk','Cul-de-Sac','Landscaped']

column_unique_dict = create_column_unique_dict(data, column_names)

domains = {}
for col, uniques in column_unique_dict.items():
    if col in ['state','bedroomcount','bathroomcount']:
        domains[col] = len(uniques) - 1
    else:
        domains[col] = len(uniques)
    

# print("Filtered Data (2D List):")
# print(column_names)
# for row in data:
#     print(row)

# print("\nUnique Values per Column:")
# for col, unique_values in column_unique_dict.items():
#     if col not in ['type']:
#         print(f"Column {col}: {unique_values}")

if single_table_test:
    print('Started making the table')
    start = time.time()
    table = Table(columns = column_names, initial_list = data, domains_cardinality = domains, origin = 'lists', ignore_possibles=ignore_possibles)
        # print(table)
    end = time.time()
    print('Making the table object took',end-start,'seconds')

    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order']
    algs = ['similarity', 'similarity minhash']

    walks_count = [10]
    answers, scores, times = find_answer(table, desired_size[0], algs, walks_count, show_answers=False, ignore_possibles = ignore_possibles)

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
    plt.title('Algorithm quality for '+str(max_rows)+' rows from the Homes dataset')

    plt.xticks(rotation=20, fontsize=9) 
    plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if show_graphs:
        plt.show()

    if save_graphs:
        plt.savefig('./real_images/homes_from'+str(len(data))+'_to_'+str(desired_size)+'_quality.png')
    plt.close()


    # Performance: Time per Algorithm for a single table

    plt.figure()
    bars = plt.bar(categories, time_values)

    plt.xlabel('Algorithm')
    plt.ylabel('Time')
    plt.title('Algorithm performance for '+str(max_rows)+' rows from the Homes dataset')

    plt.xticks(rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.yscale('log')
    plt.tight_layout()

    if save_graphs:
        plt.savefig('./real_images/homes_from'+str(len(data))+'_to_'+str(desired_size)+'_performance.png')

    if show_graphs:
        plt.show()

    plt.close()


if desired_size_test: 
    # test_sizes = [2,3,4,5,6,7,8,9,10,12,15,20]
    test_sizes = desired_size
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    algs = ['similarity', 'similarity minhash']
    walks_count = [10]
    print('testing desired size on Homes dataset with',len(data),'rows,',len(column_names),'columns, and desired size',test_sizes)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = defaultdict(list)
    labels = defaultdict(list)
    lines = []

    num_of_tries = 1        # there's no randomness involved

    for t in range(num_of_tries):
        print('Runthrough number',t,'of desired size test on Homes')
        k_dict = defaultdict(lambda:0)

        for j, size_num in enumerate(test_sizes):
            print('starting desired size test with desired size', size_num)
            table = Table(columns = column_names, initial_list = data, domains_cardinality = domains, origin = 'lists', ignore_possibles=ignore_possibles)
            # print(table)
            
            answers = dict()
            scores = dict()
            times = dict()

            for alg in algs:

                print('starting desired size test on alg', alg, 'with desired size', size_num)

   
                new_answers, new_scores, new_times = find_answer(table, size_num, [alg], walks_count, show_answers=False, ignore_possibles = ignore_possibles)
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
                            categories[alg].append(size_num)
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
                        categories[alg].append(size_num)
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
        print('desired sizes',categories[alg], score_values[alg], str(alg))
        plt.plot(categories[alg], score_values[alg], label=str(alg))

    plt.xlabel('Final number of rows')
    if num_of_tries == 1:
        plt.ylabel('Score')
    else:
        plt.ylabel('Average Score from '+str(num_of_tries)+' tables')
    plt.title('Score as final count of rows increases')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(range(0, max(categories), 1))#, rotation=20, fontsize=9) 
    # plt.yticks(range(0, round(max(score_values)*1.2), 1))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./real_images/homes_from'+str(len(data))+'_to_'+str(test_sizes)+'_quality.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        print(categories[alg], time_values[alg], str(alg))
        plt.plot(categories[alg], time_values[alg], label=str(alg))

    plt.xlabel('Final number of rows')
    if num_of_tries == 1:
        plt.ylabel('Time (s)')
    else:
        plt.ylabel('Average Time from '+str(num_of_tries)+' tables (s)')
    plt.title('Time as final count of rows increases')
    

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./real_images/homes_from'+str(len(data))+'_to_'+str(test_sizes)+'_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()

    plt.figure()
    for alg in lines:
        # print(categories, time_values[alg], str(alg))
        plt.plot(categories[alg], time_values[alg], label=str(alg))

    plt.xlabel('Final number of rows')
    if num_of_tries == 1:
        plt.ylabel('Log10(Time (s))')
    else:
        plt.ylabel('Average Log10(Time (s)) from '+str(num_of_tries)+' tables')
    plt.title('Log Time as final count of rows increases')

    plt.legend()

    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.yscale('log')

    plt.tight_layout()

    if save_graphs:
        plt.savefig('./real_images/homes_from'+str(len(data))+'_to_'+str(test_sizes)+'_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()


