import csv
import re
POWLEVEL = "powLevel00"


INPUT_FILES = ['outdoor_test_5meter.csv', 'outdoor_test_10meter.csv',
               'outdoor_test_20meter.csv', 'outdoor_test_30meter.csv',
               'outdoor_test_50meter.csv', 'outdoor_test_75meter.csv',
               'outdoor_test_100meter.csv']

OUTPUT_FILEPATH =""

def data_collection(INPUT_FILES, POWLEVEL):

    data_dict = {}

    for inputFile in INPUT_FILES:
        with open(inputFile, 'r') as file:
            reader = csv.reader(file)
            temp_data = []
            
            for row in reader:
                temp_data.append(row)
            
            for row in temp_data:
                key = inputFile
                if row[1] == POWLEVEL:
                    if key in data_dict:
                        data_dict[key].append(row[2])
                    else:
                        data_dict[key] = []
                        data_dict[key].append(row[2])
    print(data_dict)
    return data_dict

def writeCSV(data_dict, OUTPUT_FILEPATH):
    with open(OUTPUT_FILEPATH, 'w') as file:
        writer = csv.writer(file)
        for key in data_dict:
            powLevel = extract_number_from_filename(key)
            message = f"{powLevel} meters"
            writer.writerow([message])
            writer.writerow(data_dict[key])



def extract_number_from_filename(filename):
    # Use regular expression to find the number in the filename
    pattern = r'(\d+)meter'
    match = re.search(pattern, filename)
    
    if match:
        # If a match is found, return the number as an integer
        return (match.group(1))
    else:
        # If no match is found, return None
        return None


if __name__ == "__main__":
    data_dict = data_collection(INPUT_FILES, POWLEVEL)
    writeCSV(data_dict, "testoutput.csv")
































