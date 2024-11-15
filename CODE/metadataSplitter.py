import numpy as np
from typing import Dict, List, Tuple, Optional

def split_and_process_variable(array, strains, column_indexes, rows, cols, x_dilution_factor, y_dilution_factor):
    calculate_dilution_series(rows, cols, x_dilution_factor, y_dilution_factor)
    # Validate inputs
    if len(strains) != len(column_indexes):
        raise ValueError("Number of strains must match number of column index groups")

    processed_data = {}
    
    # Process each strain
    for strain_name, indexes in zip(strains, column_indexes):
        # Extract data for current strain using column indexes
        strain_data = []
        for row in array:
            extracted_row = [row[i] for i in indexes if i < len(row)]
            strain_data.append(extracted_row)
            
        # Add to processed data dictionary
        processed_data[f"{strain_name}"] = process_strain(strain_data)
        processed_data[f"{strain_name} data"] = strain_data
        
    return processed_data

def process_strain(strain_data, dilution_array):
    # dilution_array = calculate_dilution_series(8,4,10,2)   
    sorted_positions = get_sorted_positions(dilution_array)
    strain_data_sorted = extract_values_at_positions(strain_data, sorted_positions)
    # Add your strain processing logic here
    return strain_data_sorted  # Replace with actual processing



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


def get_sorted_positions(dilution_array):
    # Create list of positions and values
    positions = []
    for i in range(dilution_array.shape[0]):
        for j in range(dilution_array.shape[1]):
            positions.append((i, j, dilution_array[i,j]))
    
    # Sort by value and extract only the positions
    sorted_positions = [(row, col) for row, col, _ in sorted(positions, key=lambda x: x[2])]
    
    return sorted_positions

def extract_values_at_positions(array, positions):
    return [array[row, col] for row, col in positions]  


# dilution_array = calculate_dilution_series(8,4,10,2)   
# sorted_positions = get_sorted_positions(dilution_array)
# DILUTIONSERIES = extract_values_at_positions(dilution_array, sorted_positions)

# print(DILUTIONSERIES)
# Example usage:
if __name__ == "__main__":

plate_info = [
    {
        'filename': 'Plate1',
        'atc': True,
        'dilutions': [],
        'unorderedquantifications': [[0] * 12 for _ in range(8)],  # 8x12 matrix of zeros
        'IMGcontours': None,
        'IMGbinary': None,
        'IMGgrid': None,
        'threshold': 0,
        'smallArea': 0,
        'blocksize': 0,
        'strains': ['strain5', 'strain4', 'strain3', 'strain2'],
        'column_indexes': [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]],
        'ordered_quantifications': {},
        'strain_positions': {
            0: (0, 2),
            1: (3, 5),
            2: (6, 8),
            3: (9, 11)
        },
        'removed_positions': [],
        'layout': {
            'rows': 8,
            'columns': 12,
            'x_dilution': 10,
            'y_dilution': 2,
            'gap_between_strains': False
        }
    },
    {
        'filename': 'plate2',
        'atc': True,
        'dilutions': [],
        'unorderedquantifications': [[0] * 12 for _ in range(8)],  # 8x12 matrix of zeros
        'IMGcontours': None,
        'IMGbinary': None,
        'IMGgrid': None,
        'threshold': 0,
        'smallArea': 0,
        'blocksize': 0,
        'strains': ['strain5', 'strain4', 'strain3', 'strain2'],
        'column_indexes': [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]],
        'ordered_quantifications': {},
        'strain_positions': {
            0: (0, 2),
            1: (3, 5),
            2: (6, 8),
            3: (9, 11)
        },
        'removed_positions': [],
        'layout': {
            'rows': 8,
            'columns': 12,
            'x_dilution': 10,
            'y_dilution': 2,
            'gap_between_strains': False
        }
    },
    {
        'filename': 'plate3',
        'atc': True,
        'dilutions': [],
        'unorderedquantifications': [[0] * 12 for _ in range(8)],  # 8x12 matrix of zeros
        'IMGcontours': None,
        'IMGbinary': None,
        'IMGgrid': None,
        'threshold': 0,
        'smallArea': 0,
        'blocksize': 0,
        'strains': ['strain5', 'strain4', 'strain3', 'strain2'],
        'column_indexes': [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]],
        'ordered_quantifications': {},
        'strain_positions': {
            0: (0, 2),
            1: (3, 5),
            2: (6, 8),
            3: (9, 11)
        },
        'removed_positions': [],
        'layout': {
            'rows': 8,
            'columns': 12,
            'x_dilution': 10,
            'y_dilution': 2,
            'gap_between_strains': False
        }
    }
]

# Example of how to access the data:
def print_plate_info(plates):
    for plate in plates:
        print(f"Filename: {plate['filename']}")
        print(f"Number of strains: {len(plate['strains'])}")
        print(f"Matrix dimensions: {len(plate['unorderedquantifications'])}x{len(plate['unorderedquantifications'][0])}")
        print("---")

