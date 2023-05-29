import numpy as np

# Example 2D array
array_2d = np.array([[3, 9, 5],
                     [1, 4, 2],
                     [6, 8, 7]])

# Sort the array based on the values in the first column
sorted_array = array_2d[array_2d[:, 0].argsort()]

# Print the sorted array
print(sorted_array)
print(array_2d[:, 0].argsort())