

def split_and_process(array):
    #three 8x4 arrays
    strain1 = [row[:4] for row in array]
    strain2 = [row[4:8] for row in array]
    strain3 = [row[8:] for row in array]

    #dictionary
    processed_data = {
        "Strain 1": process_strain(strain1),
        "Strain 2": process_strain(strain2),
        "Strain 3": process_strain(strain3)
    }

    return processed_data



import numpy as np

def calculate_dilution_series(rows, cols, x_dilution_factor, y_dilution_factor):

    # Initialize the result array
    result = np.zeros((rows, cols))
    
    # Calculate dilutions along x-axis (first row)
    for j in range(cols):
        result[0,j] = (x_dilution_factor ** j)
    
    # Calculate dilutions along y-axis for each column
    for i in range(1, rows):
        for j in range(cols):
            result[i,j] = result[0,j] * (y_dilution_factor ** i)
    
    return result

def print_dilution_series(dilution_array):
    """
    Print the dilution series in a formatted way.
    
    Parameters:
    dilution_array (numpy.ndarray): 2D array of dilution values
    """
    print("\nDilution Series:")
    for row in dilution_array:
        print([f"{x:.6g}" for x in row])

def get_sorted_positions(dilution_array):
    """
    Get the positions of entries in ascending order based on their values.
    
    Parameters:
    dilution_array (numpy.ndarray): 2D array of dilution values
    
    Returns:
    list: List of tuples containing (row, column) sorted by corresponding dilution values
    """
    # Create list of positions and values
    positions = []
    for i in range(dilution_array.shape[0]):
        for j in range(dilution_array.shape[1]):
            positions.append((i, j, dilution_array[i,j]))
    
    # Sort by value and extract only the positions
    sorted_positions = [(row, col) for row, col, _ in sorted(positions, key=lambda x: x[2])]
    
    return sorted_positions

def extract_values_at_positions(array, positions):
    """
    Extract values from an array using a list of positions.
    
    Parameters:
    array (numpy.ndarray): 2D array to extract values from
    positions (list): List of (row, column) tuples
    
    Returns:
    list: Values from the array at the specified positions
    """
    return [array[row, col] for row, col in positions]  


dilution_array = calculate_dilution_series(8,12,10,2)   
sorted_positions = get_sorted_positions(dilution_array)
ordered_values = extract_values_at_positions(dilution_array, sorted_positions)
print(ordered_values)
