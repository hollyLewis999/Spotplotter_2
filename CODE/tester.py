import numpy as np

def calculate_dilution_series(rows, cols, x_dilution_factor, y_dilution_factor):
    rows = rows+1
    cols = cols+1
    # Initialize the result array
    result = np.zeros((rows, cols))
    
    # Calculate dilutions along x-axis (first row)
    for j in range(cols):
        result[0,j] = (x_dilution_factor ** j)
    
    # Calculate dilutions along y-axis for each column
    for i in range(1, rows):
        for j in range(cols):
            result[i,j] = result[0,j] * (y_dilution_factor ** i)
    
    print (result)
    return result




calculate_dilution_series(7, 3, 10, 2)