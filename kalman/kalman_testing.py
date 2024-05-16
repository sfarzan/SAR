from kalman import KalmanFilter
import csv


CSV_FILEPATH = './outdoor_powtest/outdoor_test_5meter.csv'
OUTPUT_FILEPATH = '5meter_kf_results.csv'

#arrays that you fill with the kf filters you want

processNoiseArray = [.008, .1]
measurementNoiseArray = [.1,.1]

# arrays that are filled with csv data
data = []
rawRssi = []
kfRssi = []
varArray = []

#change this to change which power level you look at
POWLEVEL = "powLevel00"
def readCSV(input_file):
    # reads the csv and puts raw rssi data into rawRssi list
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    
    for row in data[1:]: #skip the header
        powerLevel = row[1]
        rssiVal = row[2]
        if powerLevel == POWLEVEL:
            rawRssi.append(float(rssiVal))
            
    print(rawRssi)


def csvProcess(output_file, processNoise, measurementNoise):
    
    if len(processNoise) != len(measurementNoise):
        raise ValueError("arrays are not same len")
    # make arrays for kf and var values
    
    kfArray = []
    varArray = []

    for lenProcessArray in range(len(processNoise)):
        kfArray.append([])
        varArray.append([])
    for listCounter in range(len(processNoise)):
        kf = KalmanFilter(processNoise[listCounter], measurementNoise[listCounter])
        for rawRssiCounter in range(len(rawRssi)):
            kfArray[listCounter].append(kf.filter(rawRssi[rawRssiCounter]))
            varArray[listCounter].append(kf.get_cov())

    writeCSV(output_file, kfArray, varArray)

def writeCSV(output_file, kfArray, varArray):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Raw RSSI', 'Filtered RSSI', 'Variance', 'Process Noise', 'Measurement Noise'])
        for i in range(len(rawRssi)):
            row = [rawRssi[i]]
            for j in range(len(processNoiseArray)):
                row.append(kfArray[j][i])
                row.append(varArray[j][i])
            writer.writerow(row)
        #
        # for rawRssiLen in range(len(rawRssi)):
        #     print(f"len of processnoisearray{processNoiseArray}")
        #     for num_of_KF in range(len(processNoiseArray)):
        #         
        #
        #         writer.writerow([rawRssi[i], kfArray[j][i], varArray[j][i], '', ''])
        print("DONE")

readCSV(CSV_FILEPATH)
csvProcess(OUTPUT_FILEPATH,[.008, .1], [.1, .1])
# test = KalmanFilter(0.008, 0.1)
# testData = [66,64,63,63,63,66,65,67,58]
# for x in testData:
#     print("Data:", x)
#     print("Filtered Data: ", test.filter(x), test.get_cov())





























