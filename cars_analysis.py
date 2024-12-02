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

use_full_db = True

# max_rows = 10  #None         # how many rows to take at most, None is unlimited
max_rows = 1000
# desired_size = [2000,3000,4000,5000,6000,7000,8000,9000]         # what is the maximum number of rows of the reduced database
# desired_size = [9000,8000,7000,6000,5000]#,4000,3000,2000] 
# desired_size = [4000,3000,2000] 
desired_size = [950,900,800,700,600,500,400,300,200,100,50] 
# desired_size = [20000,15000,10000]
# desired_size = [990000,900000,800000]
# desired_size = [99000,90000,80000]
# desired_size = [49000, 45000, 40000, 30000]

# Function to load the data into a 2D list and extract specific columns
def load_and_filter_data(file_path, selected_columns, max_rows = max_rows, delimiter = ','):
    skipped = 0

    data = []
    with open(file_path, 'r') as file:
        # csv_reader = csv.reader(file, delimiter='\t')  # Tab-separated file
        csv_reader = csv.reader(file, delimiter=delimiter) 
        for i, row in enumerate(csv_reader):
            if max_rows != None and i - (skipped) >= max_rows:
                break
            # Extract only the selected columns (convert 1-based to 0-based indexing)
            filtered_row = [row[i - 1] for i in selected_columns]
            for i, value in enumerate(filtered_row):
                if value in ['NULL','Dont Care']:
                    filtered_row[i] = '*'           # convert NULL to *
                elif value == 'NO':
                    filtered_row[i] = 'No'
                elif i == 1:
                    # filtered_row[1] = int(filtered_row[1].replace(',',''))      # removing separators from price
                    price = int(filtered_row[1].replace(',',''))      # removing separators from price
                    if price < 10000:                  # binning price into 4 categories
                        filtered_row[1] = '<10k'
                    elif price < 20000:
                        filtered_row[1] = '10k-20k'
                    elif price < 30000:
                        filtered_row[1] = '20k-30k'
                    else:
                        filtered_row[1] = '>30k'
            data.append(filtered_row)
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


print('loading and filtering data')
if use_full_db:
    file_path = 'data/yahooAuto1M.CSV'
    selected_columns = [5, 6, 8] + list(range(10, 44))
    data = load_and_filter_data(file_path, selected_columns)
    
else:
    file_path = 'data/autos.CSV'
    selected_columns = [5, 6, 8] + list(range(10, 43)) + [45]
    data = load_and_filter_data(file_path, selected_columns, delimiter='\t')

column_names = ['state','price','color','cylinders','radio','air conditioning','alarm','anti lock brakes','cd changer','cd player','cassette player','child safety latch','driver air bag','fog lights','heated seats','keyless entries','navigation system','passenger airbag','power door locks','power seats','power steering','power window','premium sound','premium wheels','rear defroster','rear window wiper','roof rack','side airbag','spoiler','sunroof','climate control','cruise control','power mirrors','alloy wheels','steering wheel radio','tinted windows','make']

print('making uniques dict')
column_unique_dict = create_column_unique_dict(data, column_names)

domains = {}
for col, uniques in column_unique_dict.items():
    if '*' in uniques:
        domains[col] = len(uniques) - 1
    else:
        domains[col] = len(uniques)
    

# print("Filtered Data (2D List):")
# print(column_names)
# for row in data:
#     print(row)

print("\nUnique Values per Column:")
for col, unique_values in column_unique_dict.items():
    if col not in ['type']:
        print(f"Column {col}: {sorted(unique_values)}")




if desired_size_test: 
    # test_sizes = [2,3,4,5,6,7,8,9,10,12,15,20]
    test_sizes = desired_size
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy']
    # algs = ['similarity', 'similarity minhash', 'greedy','random walks','merge greedy','sorted order','exhaustive']
    algs = ['similarity', 'similarity minhash']
    walks_count = [10]
    print('testing desired size on Cars dataset with',len(data),'rows,',len(column_names),'columns, and desired size',test_sizes)

    score_values = defaultdict(list)           # dict[alg] = list of values
    time_values = defaultdict(list)   

    categories = defaultdict(list)
    labels = defaultdict(list)
    lines = []

    num_of_tries = 1        # there's no randomness involved

    for t in range(num_of_tries):
        print('Runthrough number',t,'of desired size test on Cars')
        k_dict = defaultdict(lambda:0)

        start = time.time()
        table = Table(columns = column_names, initial_list = data, domains_cardinality = domains, origin = 'lists', ignore_possibles=ignore_possibles)
        print('the created table starts with',table.get_size(),'rows')
        start2 = time.time()
        print('checking merges:')
        table.check_merges()
        print('now the table has',table.get_size(),'rows')
        end = time.time()
        print('Making the table object took', start2-start,'seconds, and removing duplicates took',end-start2,'seconds')

        for j, size_num in enumerate(test_sizes):
            print('starting desired size test with desired size', size_num)

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
        plt.savefig('./real_images/cars_from'+str(len(data))+'_to_'+str(test_sizes)+'_quality.png')
    
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
        plt.savefig('./real_images/cars_from'+str(len(data))+'_to_'+str(test_sizes)+'_performance.png')
    
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
        plt.savefig('./real_images/cars_from'+str(len(data))+'_to_'+str(test_sizes)+'_log_performance.png')
    
    if show_graphs:
        plt.show()

    plt.close()


