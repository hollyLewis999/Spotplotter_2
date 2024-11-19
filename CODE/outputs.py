import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats as scipy_stats
from pathlib import Path
import seaborn as sns
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as ImageR
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from io import BytesIO
import cv2
import sys
from PIL import Image 
from datetime import datetime
from tkinter import filedialog, simpledialog
import os
import sys
import openpyxl



#DILUTIONSERIES = [1, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
ATCCOLOURS = ["#D24C4A", "#D3784A", "#DFA24F", "#EBCB53"]
NOATCCOLORS = ["#073B3A", "#0B614D", "#0F8660", "#7DB46F"]

GREENCOLOURS = ["#073B3A", "#0B614D", "#0F8660", "#7DB46F"] #https://coolors.co/073b3a-0b614d-0f8660-7db46f
REDCOLOURS = ["#D24C4A", "#D3784A", "#DFA24F", "#EBCB53"] #https://coolors.co/d24c4a-d3784a-dfa24f-ebcb53
BLUECOLOURS = ["#0C546B", "#0F7D87", "#46A2A2", "#7CC7BC"] #https://coolors.co/0c546b-0f7d87-46a2a2-7cc7bc
PURPLESCOLOURS =["#591C5F", "#81377E", "#A9599C", "#D07BB9"] #https://coolors.co/591c5f-81377e-a9599c-d07bb9
    
FONT = "Microsoft New Tai Lue"
plt.rcParams['font.family'] = FONT
sns.set_style("whitegrid")
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


def normalize_array(arr, norm_value):
    """Normalize an array by a given value"""
    return [100 * x / norm_value for x in arr]


def calculate_statistics(x_values, y_values, label, log_base=10):
    """
    Calculate statistics for the data series using specified log base
    """
    valid_points = [(x, y) for x, y in zip(x_values, y_values) if x > 0 and y > 10]
    if len(valid_points) < 2:
        return None
        
    # Use the specified log base instead of always using log10
    valid_x = [np.log(point[0])/np.log(log_base) for point in valid_points]
    valid_y = [point[1] for point in valid_points]
    
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(valid_x, valid_y)
    r_squared = r_value ** 2
    
    # Update formula to show correct log base
    if log_base == 10:
        formula = f"y = {slope:.2f}log(x) + {intercept:.2f}"
    elif log_base == np.e:
        formula = f"y = {slope:.2f}ln(x) + {intercept:.2f}"
    else:
        formula = f"y = {slope:.2f}log_{log_base}(x) + {intercept:.2f}"
    
    return {
        'label': label,
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'formula': formula
    }

def plot_multiadditive_graph(data_series, dilution_series, title, log_base=10):
    sorted_positions = get_sorted_positions(dilution_series)
    dilution_series = extract_values_at_positions(dilution_series, sorted_positions)
    
    # Create figure with vertical subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 16))
    sns.set_context("notebook", font_scale=1.2)
    
    # Set log scale and style
    for ax in [ax1, ax2]:
        ax.set_xscale('log', base=log_base)
        ax.set_facecolor('#F5F5F5')

    # Modify additive handling
    def safe_additive(series):
        additive = series.get('additive')
        return 'none' if additive is None else str(additive)

    # Custom sorting for additives: 'none' first, then alphabetically
    additives = sorted(
        set(safe_additive(series) for series in data_series), 
        key=lambda x: (x != 'none', x)
    )

    # Initialize averaged data with correct key types
    averaged_data = {str(additive): {float(x): [] for x in dilution_series} for additive in additives}
    
    # Modify normalization to handle None consistently
    none_series = [series['y_values'][0] for series in data_series 
                   if safe_additive(series) == 'none']
    if not none_series:
        raise ValueError("Must have at least one series with additive='none' for normalization")
    norm_value = sum(none_series) / len(none_series)
    
    max_y = max(max(series['y_values']) for series in data_series)
    y_max = max_y + 10

    # Modify color mapping to handle None
    color_map = {}
    for additive in additives:
        if additive.lower() == 'none':
            color_map[additive] = BLUECOLOURS
        elif additive.lower() == 'atc':
            color_map[additive] = REDCOLOURS
        elif len(color_map) % 2 == 0:
            color_map[additive] = GREENCOLOURS
        else:
            color_map[additive] = PURPLESCOLOURS
    
    # Initialize data collection for averaging
    series_statistics = []
    additive_counts = {additive: 0 for additive in additives}
    default_markers = ['o', 's', '^', 'D']
    
    for idx, series in enumerate(data_series):
        y_norm = normalize_array(series['y_values'], norm_value)
        additive = safe_additive(series)
        
        # Debugging: print out additive and its type
        print(f"Current series additive: {additive}, type: {type(additive)}")
        
        # Ensure the additive is in color_map
        if additive not in color_map:
            print(f"Warning: Additive '{additive}' not in color_map. Using default color.")
            color_map[additive] = BLUECOLOURS  # Default color
        
        # Plot individual series
        color = color_map[additive][additive_counts[additive] % len(color_map[additive])]
        additive_counts[additive] += 1
        
        marker = series.get('marker', default_markers[idx % len(default_markers)])
        
        # Calculate and store statistics
        stats = calculate_statistics(dilution_series, y_norm, series['label'], log_base)
        if stats is not None:
            series_statistics.append(stats)
            plot_label = f"{additive} ({series['label']})"
            
            # Plot points
            ax1.scatter(dilution_series, y_norm, color=color, 
                       marker=marker, label=plot_label, s=80)
            
            # Plot trend line
            x_fit = np.logspace(np.log(min(dilution_series))/np.log(log_base),
                              np.log(max(dilution_series))/np.log(log_base),
                              num=100, base=log_base)
            y_fit = stats['slope'] * np.log(x_fit)/np.log(log_base) + stats['intercept']
            ax1.plot(x_fit, y_fit, color=color, linestyle='--',
                    label=f"R² = {stats['r_squared']:.3f}\n{stats['formula']}\n")
        
        # Collect data for averaging
        for x, y in zip(dilution_series, y_norm):
            if x > 0 and y > 0:
                averaged_data[additive][x].append(y)
    
    # Plot averaged data
    for additive in additives:
        valid_x = []
        valid_means = []
        valid_stds = []
        
        for x in dilution_series:
            if averaged_data[additive][x]:
                valid_x.append(x)
                valid_means.append(np.mean(averaged_data[additive][x]))
                valid_stds.append(np.std(averaged_data[additive][x]) 
                                if len(averaged_data[additive][x]) > 1 else 0)
        
        if valid_x:

            # Calculate regression for averaged data
            log_x = np.log(valid_x) / np.log(log_base)
            slope, intercept, r_value, _, _ = scipy_stats.linregress(log_x, valid_means)
            r_squared = r_value ** 2
            
            if log_base == 10:
                formula = f"y = {slope:.2f}log(x) + {intercept:.2f}"
            elif log_base == np.e:
                formula = f"y = {slope:.2f}ln(x) + {intercept:.2f}"
            else:
                formula = f"y = {slope:.2f}log_{log_base}(x) + {intercept:.2f}"
            
            # Plot averaged points with error bars
            ax2.errorbar(valid_x, valid_means, yerr=valid_stds,
                        color=color_map[additive][0], marker='o',
                        label=f'{additive} (Average)\nError bars = ±1 SD\nR² = {r_squared:.3f}\n{formula}',
                        capsize=5, capthick=1, markersize=8, linewidth=2,
                        ls='none')
            
            # Plot trend line
            x_fit = np.logspace(np.log(min(valid_x))/np.log(log_base),
                              np.log(max(valid_x))/np.log(log_base),
                              num=100, base=log_base)
            y_fit = slope * np.log(x_fit)/np.log(log_base) + intercept
            ax2.plot(x_fit, y_fit, color=color_map[additive][0], linestyle='--')
    
    # Style plots
    for ax in [ax1, ax2]:
        ax.set_xlabel('Dilution Series', fontsize=16, fontweight='bold')
        ax.set_ylabel('Relative Growth (%)', fontsize=16, fontweight='bold')
        ax.legend(
            fontsize=8,  # Smaller font
            loc='upper right', 
            bbox_to_anchor=(1, 1),
            ncol=2,  # Two columns to compress
            frameon=True, 
            facecolor='white', 
            edgecolor='gray',
            framealpha=0.5
        )
        ax.tick_params(axis='both', which='major', labelsize=14)
    
    ax1.set_title(f"Individual Growth Curves for {title}",
                 fontsize=20, fontweight='bold', pad=20)
    ax2.set_title(f"Average Growth Curves for {title}",
                 fontsize=20, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.show()
    
    return fig, series_statistics




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
    # print('extract_values_at_positions')
    # print(array)
    # print(positions)
    return [array[row, col] for row, col in positions]  


# dilution_array = calculate_dilution_series(8,12,10,2)   
# sorted_positions = get_sorted_positions(dilution_array)
# ordered_values = extract_values_at_positions(dilution_array, sorted_positions)
# print(ordered_values)






y1 = [32104, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0]
y2 = [35381, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0]
y3 = [18909, 16152, 13604, 12738, 12577, 8611, 14617, 6462, 3661, 1967, 3733, 990, 1650, 590, 662, 0, 203, 0, 161, 0, 0, 0, 0, 0, 0, 165, 0, 0, 0, 0, 0, 0]
y4 = [20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
y5 = [30000, 20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0]
# Example usage:
data_series = [
    {
        'y_values': y1,
        'label': 'Series 1',
        'color': '#073B3A',  # optional
        'marker': 'o',       # optional
        'atc': False       # optional
    },
    {
        'y_values': y2,
        'label': 'Series 2',
        'atc': False
    },
    {
        'y_values': y3,
        'label': 'Series 3',
        'atc': True
    },
    {
        'y_values': y4,
        'label': 'Series 4',
        'atc': True
    },
    {
        'y_values': y5,
        'label': 'Series 2',
        'atc': False
    }
    # Add as many series as needed...
]

y1 = [32104, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0]
y2 = [35381, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0]
y3 = [18909, 16152, 13604, 12738, 12577, 8611, 14617, 6462, 3661, 1967, 3733, 990, 1650, 590, 662, 0, 203, 0, 161, 0, 0, 0, 0, 0, 0, 165, 0, 0, 0, 0, 0, 0]
y4 = [20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
y5 = [30000, 20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0]
# Example usage:


# fig, stats = plot_logarithmic_graph(data_series, DILUTIONSERIES, "My Title", log_base=10)
