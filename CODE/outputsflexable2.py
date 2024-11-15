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
    
FONT = "Microsoft New Tai Lue"
plt.rcParams['font.family'] = FONT
sns.set_style("whitegrid")
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Define color schemes
ATCCOLOURS = ["#D24C4A", "#D3784A", "#DFA24F", "#EBCB53"]
NOATCCOLORS = ["#073B3A", "#0B614D", "#0F8660", "#7DB46F"]


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

def plot_logarithmic_graph(data_series, dilution_series, title, log_base=10):
    """
    Plot two graphs: individual series and averaged ATC vs non-ATC comparison
    Handles different numbers of series for each condition safely.
    """
    # Calculate normalization value
    non_atp_first_values = [series['y_values'][0] for series in data_series
                           if not series['atc']][:2]
    norm_value = sum(non_atp_first_values) / len(non_atp_first_values)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 8))
    sns.set_context("notebook", font_scale=1.2)
    
    # Set custom log base for both axes
    ax1.set_xscale('log', base=log_base)
    ax2.set_xscale('log', base=log_base)
    
    ax1.set_facecolor('#F5F5F5')
    
    series_statistics = []
    atc_count = 0
    no_atc_count = 0
    default_markers = ['o', 's', '^', 'D']
    
    # Initialize dictionaries to store data for each dilution point
    atc_data = {x: [] for x in dilution_series}
    no_atc_data = {x: [] for x in dilution_series}
    
    # First pass: collect data for each dilution point
    for series in data_series:
        y_norm = normalize_array(series['y_values'], norm_value)
        
        for x, y in zip(dilution_series, y_norm):
            if x > 0 and y > 10:  # Only include valid points
                if series['atc']:
                    atc_data[x].append(y)
                else:
                    no_atc_data[x].append(y)
    
    # Plot individual series
    for idx, series in enumerate(data_series):
        y_norm = normalize_array(series['y_values'], norm_value)
        
        if series['atc']:
            color = ATCCOLOURS[atc_count % len(ATCCOLOURS)]
            atc_count += 1
            atc_label = '+ATc'
        else:
            color = NOATCCOLORS[no_atc_count % len(NOATCCOLORS)]
            no_atc_count += 1
            atc_label = '-ATc'
        
        marker = series.get('marker', default_markers[idx % len(default_markers)])
        
        # Pass log_base to calculate_statistics
        stats = calculate_statistics(dilution_series, y_norm, series['label'], log_base)
        if stats is not None:
            series_statistics.append(stats)
            plot_label = f"{atc_label} ({series['label']})"
            
            ax1.scatter(dilution_series, y_norm, color=color, 
                       marker=marker, label=plot_label, s=80)
            
            x_fit = np.logspace(np.log(min(dilution_series))/np.log(log_base),
                              np.log(max(dilution_series))/np.log(log_base),
                              num=100, base=log_base)
            y_fit = stats['slope'] * np.log(x_fit)/np.log(log_base) + stats['intercept']
            ax1.plot(x_fit, y_fit, color=color, linestyle='--',
                    label=f"R² = {stats['r_squared']:.3f}\n{stats['formula']}\n")
    
    # Style first subplot
    ax1.set_title(f"Individual Growth Curves for {title}", 
                 fontsize=20, fontweight='bold', pad=20)
    ax1.set_ylim(0, 120)
    ax1.set_xlabel('Dilution Series', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Relative Growth (%)', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=14, loc='upper right', bbox_to_anchor=(0.98, 0.98),
              ncol=1, frameon=True, facecolor='white', edgecolor='none',
              framealpha=0.7)
    ax1.tick_params(axis='both', which='major', labelsize=14)
    
    # Second subplot - Averaged comparison
    ax2.set_facecolor('#F5F5F5')
    
    # Calculate averages and error bars
    valid_x_atc = []
    valid_means_atc = []
    valid_stds_atc = []
    valid_x_no_atc = []
    valid_means_no_atc = []
    valid_stds_no_atc = []
    
    # Process ATC data
    for x in dilution_series:
        if atc_data[x]:  # If there are valid points for this x
            valid_x_atc.append(x)
            valid_means_atc.append(np.mean(atc_data[x]))
            valid_stds_atc.append(np.std(atc_data[x]) if len(atc_data[x]) > 1 else 0)
            
    # Process no-ATC data
    for x in dilution_series:
        if no_atc_data[x]:  # If there are valid points for this x
            valid_x_no_atc.append(x)
            valid_means_no_atc.append(np.mean(no_atc_data[x]))
            valid_stds_no_atc.append(np.std(no_atc_data[x]) if len(no_atc_data[x]) > 1 else 0)
    
    # Plot averaged data with error bars and trend lines
    if valid_x_atc:
        log_x_atc = np.log(valid_x_atc) / np.log(log_base)
        slope_atc, intercept_atc, r_value_atc, _, _ = scipy_stats.linregress(log_x_atc, valid_means_atc)
        r_squared_atc = r_value_atc ** 2
        
        x_fit_atc = np.logspace(np.log(min(valid_x_atc))/np.log(log_base),
                               np.log(max(valid_x_atc))/np.log(log_base),
                               num=100, base=log_base)
        y_fit_atc = slope_atc * np.log(x_fit_atc)/np.log(log_base) + intercept_atc
        
        # Update formula based on log base
        if log_base == 10:
            formula_atc = f"y = {slope_atc:.2f}log(x) + {intercept_atc:.2f}"
        elif log_base == np.e:
            formula_atc = f"y = {slope_atc:.2f}ln(x) + {intercept_atc:.2f}"
        else:
            formula_atc = f"y = {slope_atc:.2f}log_{log_base}(x) + {intercept_atc:.2f}"
        
        ax2.errorbar(valid_x_atc, valid_means_atc, yerr=valid_stds_atc,
                    color=ATCCOLOURS[0], marker='o', 
                    label=f'+ATc (Average)\nError bars = ±1 SD\nR² = {r_squared_atc:.3f}\n{formula_atc}',
                    capsize=5, capthick=1, markersize=8, linewidth=2,
                    ls='none')
        ax2.plot(x_fit_atc, y_fit_atc, color=ATCCOLOURS[0], linestyle='--')
    
    if valid_x_no_atc:
        log_x_no_atc = np.log(valid_x_no_atc) / np.log(log_base)
        slope_no_atc, intercept_no_atc, r_value_no_atc, _, _ = scipy_stats.linregress(log_x_no_atc, valid_means_no_atc)
        r_squared_no_atc = r_value_no_atc ** 2
        
        x_fit_no_atc = np.logspace(np.log(min(valid_x_no_atc))/np.log(log_base),
                                  np.log(max(valid_x_no_atc))/np.log(log_base),
                                  num=100, base=log_base)
        y_fit_no_atc = slope_no_atc * np.log(x_fit_no_atc)/np.log(log_base) + intercept_no_atc
        
        # Update formula based on log base
        if log_base == 10:
            formula_no_atc = f"y = {slope_no_atc:.2f}log(x) + {intercept_no_atc:.2f}"
        elif log_base == np.e:
            formula_no_atc = f"y = {slope_no_atc:.2f}ln(x) + {intercept_no_atc:.2f}"
        else:
            formula_no_atc = f"y = {slope_no_atc:.2f}log_{log_base}(x) + {intercept_no_atc:.2f}"
        
        ax2.errorbar(valid_x_no_atc, valid_means_no_atc, yerr=valid_stds_no_atc,
                    color=NOATCCOLORS[0], marker='s', 
                    label=f'-ATc (Average)\nError bars = ±1 SD\nR² = {r_squared_no_atc:.3f}\n{formula_no_atc}',
                    capsize=5, capthick=1, markersize=8, linewidth=2,
                    ls='none')
        ax2.plot(x_fit_no_atc, y_fit_no_atc, color=NOATCCOLORS[0], linestyle='--')
    
    # Style second subplot
    ax2.set_title(f"Average Growth Curves for {title}",
                 fontsize=20, fontweight='bold', pad=20)
    ax2.set_ylim(0, 120)
    ax2.set_xlabel('Dilution Series', fontsize=16, fontweight='bold')
    ax2.set_ylabel('Relative Growth (%)', fontsize=16, fontweight='bold')
    ax2.legend(fontsize=14, loc='upper right', bbox_to_anchor=(0.98, 0.98),
              ncol=1, frameon=True, facecolor='white', edgecolor='none',
              framealpha=0.7)
    ax2.tick_params(axis='both', which='major', labelsize=14)
    
    plt.tight_layout()
    plt.show()
    
    return fig, series_statistics




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


dilution_array = calculate_dilution_series(8,4,np.e,2)   
sorted_positions = get_sorted_positions(dilution_array)
DILUTIONSERIES = extract_values_at_positions(dilution_array, sorted_positions)
print(DILUTIONSERIES)








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


fig, stats = plot_logarithmic_graph(data_series, DILUTIONSERIES, "My Title", log_base=10)

# For base 2
fig, stats =  plot_logarithmic_graph(data_series, DILUTIONSERIES, "My Title", log_base=np.e)

# For base 4
fig, stats =  plot_logarithmic_graph(data_series, DILUTIONSERIES, "My Title", log_base=4)