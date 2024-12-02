import csv

# Function to load the data into a 2D list and extract specific columns
def load_and_filter_data(file_path, selected_columns, max_rows = None):
    skipped_rowlength = 0
    skipped_invalid_state = 0
    skipped_rental = 0

    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file, delimiter='\t')  # Tab-separated file
        for i, row in enumerate(csv_reader):
            if max_rows != None and i >= max_rows:
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
