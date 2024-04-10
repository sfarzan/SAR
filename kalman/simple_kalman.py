from kalman import KalmanFilter


test = KalmanFilter(0.008, 0.1)
testData = [66,64,63,63,63,66,65,67,58]
for x in testData:
    print("Data:", x)
    print("Filtered Data: ", test.filter(x), test.get_cov())
