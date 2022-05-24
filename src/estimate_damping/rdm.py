import numpy as np

def find_crossing(timeseries : np.array, threshold : float):
    crossing_indices = list()
    print(len(timeseries))
    for i in range(1, len(timeseries) - 1):
        print(f"timeseries[{i}] = {timeseries[i]} threshold = {threshold}")
        #if timeseries[i] > threshold and timeseries[i-1] < threshold:
        if timeseries[i] > threshold:
            print(f"above threshold")
            # upcrossing
            if timeseries[i - 1] <= threshold:
                print("upcrossing")
                crossing_indices.append(i)
                continue
            if timeseries[i + 1] <= threshold:
                print("downcrossing")
                crossing_indices.append(i)
                continue
    return crossing_indices

if __name__ == "__main__":
    l = np.array([1,2,3,4,5,6,5,4,3,2,3,4,5,5,4,4,3,2,1])
    print(find_crossing(l, threshold=4))

