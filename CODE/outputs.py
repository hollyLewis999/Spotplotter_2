import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as stats
from pathlib import Path
import pandas as pd
import seaborn as sns
import string
from matplotlib.patches import Patch


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as ImageR
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER 
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

import cv2
import sys
from PIL import Image 
from datetime import datetime
from tkinter import filedialog, simpledialog
import os
import openpyxl
import base64
import io
import math
from collections import defaultdict

from io import BytesIO

from PIL import Image, ImageTk
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH  / "Icons"
from matplotlib.colors import rgb2hex
import matplotlib.colors as mcolors
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from PIL import ImageTk


GREENCOLOURS = ["#073B3A", "#0B614D", "#0F8660", "#7DB46F"] #https://coolors.co/073b3a-0b614d-0f8660-7db46f
REDCOLOURS = ["#D24C4A", "#D3784A", "#DFA24F", "#EBCB53"] #https://coolors.co/d24c4a-d3784a-dfa24f-ebcb53
BLUECOLOURS = ["#0C546B", "#0F7D87", "#46A2A2", "#7CC7BC"] #https://coolors.co/0c546b-0f7d87-46a2a2-7cc7bc
PURPLESCOLOURS =["#591C5F", "#81377E", "#A9599C", "#D07BB9"] #https://coolors.co/591c5f-81377e-a9599c-d07bb9
PINKCOLOURS =["#FB6F92", "#FF8FAB", "#FFB3C6", "#FFC2D1"]
    
FONT = "Microsoft New Tai Lue"
plt.rcParams['font.family'] = FONT
sns.set_style("whitegrid")

#  .d8888b.
#  88   `8D 
#  88ooooY'
#  88~~~~b.
#  88    8D
#  Y88888P'

FOREGROUND_COLOR = '#073b3a'  # Darker blue for better visibility
CONTROL_COLOR = '#C1CEBE'     # Orange for better contrast
FACE_COLOR = '#F5F5F5'
TEXT_COLOR = 'black'
ALPHA = 0.8
LIGHT_ALPHA = 0.2 




# d8888b.  .d8b.  d888888b  .d8b.        .d88b.  d8888b. d8888b. d88888b d8888b. d888888b d8b   db  d888b  
# 88  `8D d8' `8b `~~88~~' d8' `8b      .8P  Y8. 88  `8D 88  `8D 88'     88  `8D   `88'   888o  88 88' Y8b 
# 88   88 88ooo88    88    88ooo88      88    88 88oobY' 88   88 88ooooo 88oobY'    88    88V8o 88 88      
# 88   88 88~~~88    88    88~~~88      88    88 88`8b   88   88 88~~~~~ 88`8b      88    88 V8o88 88  ooo 
# 88  .8D 88   88    88    88   88      `8b  d8' 88 `88. 88  .8D 88.     88 `88.   .88.   88  V888 88. ~8~ 
# Y8888D' YP   YP    YP    YP   YP       `Y88P'  88   YD Y8888D' Y88888P 88   YD Y888888P VP   V8P  Y888P  
                                                                                                      
                                                                                                      

def normalize_array(arr, norm_value):
    return [100 * x / norm_value for x in arr]

def normalize_array(values, norm_value):
    return np.array(values) / norm_value * 100

def calculate_strain_normalization_value(data_series, strain):
    norm_values = [
        series['y_values'][0] for series in data_series 
        if (series.get('additive') in [None, 'Control']) and (series['strain'] == strain)
    ]
    
    if not norm_values:
        raise ValueError(f"Must have at least one control series for strain {strain}")
    
    return sum(norm_values) / len(norm_values)

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
    

    result[0,0] = 1 #change the first point to 
    print (result)
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
    # print('extract_values_at_positions')
    # print(array)
    # print(positions)
    return [array[row, col] for row, col in positions]  

def generate_data_series(window):
    # Dictionary to store data series for each strain
    strain_data = defaultdict(list)
    dilution_series = window.all_plate_info[0]['dilutions']
   
    # Temporary list to collect all data series for normalization
    all_data_series = []
   
    # Iterate over all plates
    for plate in window.all_plate_info:
       
        additive = plate.get('additive', 'Control') or 'Control'
        filename = plate.get('filename', 'Unnamed Plate')
        strains = plate['strains']
        column_indexes = plate['column_indexes']
        ordered_quantifications = plate['ordered_quantifications']
       
        # Ensure ordered_quantifications and column_indexes match strain count
        if len(ordered_quantifications) != len(strains):
            raise ValueError("Mismatch between strains and ordered_quantifications length in plate.")
       
        # For each strain in the plate
        for strain_idx, strain in enumerate(strains):
            # Extract y_values for this strain
            y_values = ordered_quantifications[strain_idx]
            column_indexes_for_strain = column_indexes[strain_idx]
   
            # Calculate the range of column indexes
            start_col = min(column_indexes_for_strain)
            end_col = max(column_indexes_for_strain)
           
            # Generate a label for this series
            label = f"{additive if additive != 'none' else 'Control'} ({filename} {start_col}-{end_col})"
           
            # Create data series dictionary
            series_dict = {
                'y_values': y_values,
                'additive': additive,
                'label': label,
                'strain': strain,
                'filename': filename,
                'column_indexes': column_indexes_for_strain
            }
            
            # Add to temporary list for normalization calculation
            all_data_series.append(series_dict)
    
    # Calculate normalization values for each strain
    for strain in set(series['strain'] for series in all_data_series):
        # Calculate normalization value for this strain
        norm_value = calculate_strain_normalization_value(all_data_series, strain)
        
        # Update series with normalized values for this strain
        for series_dict in all_data_series:
            if series_dict['strain'] == strain:
                # Normalize values
                normalized_y_values = normalize_array(series_dict['y_values'], norm_value)
                
                # Update series with normalized values and normalization value
                series_dict['normalized_y_values'] = normalized_y_values
                series_dict['norm_value'] = norm_value
                
                # Add to strain data
                strain_data[strain].append(series_dict)
    
    # Convert strain_data to a list of series if needed
    data_series = []
    for strain, series_list in strain_data.items():
        data_series.extend(series_list)
   
    return strain_data, dilution_series

def process_split_order_quantifications(window):
    """
    Processes all_plate_info by calculating dilution series, splitting unordered quantifications
    into split_quantifications based on strain_positions, and saving ordered quantifications.

    Parameters:
    window (object): The window object containing all_plate_info
    """
    for plate in window.all_plate_info:
        # Extract plate layout and dilution factors
        rows = plate['layout']['rows']
        cols = len(plate['column_indexes'][0])
        x_dilution_factor = plate['layout']['x_dilution'] #see how many coloums each strain takes up
        y_dilution_factor = plate['layout']['y_dilution']

        # Calculate the dilution series
        dilution_array = calculate_dilution_series(rows, cols, x_dilution_factor, y_dilution_factor)
        plate['dilutions'] = dilution_array 

        # Get sorted positions based on dilution series
        sorted_positions = get_sorted_positions(dilution_array)
        
        # Split unorderedquantifications into split_quantifications
        unordered_quantifications = np.array(plate['unorderedquantifications'])
        strain_positions = plate['strain_positions']
        
        split_quantifications = []
        for strain, pos_range in strain_positions.items():
            start, end = pos_range
            split_quantifications.append(unordered_quantifications[:, start:end + 1])
        
        # Save split_quantifications to the plate
        plate['split_quantifications'] = split_quantifications
        
        # Create ordered_quantifications based on sorted positions
        ordered_quantifications = []
        for strain_data in split_quantifications:
            ordered_strain_values = extract_values_at_positions(strain_data, sorted_positions)
            ordered_quantifications.append(ordered_strain_values)
        
        # Save ordered_quantifications to the plate
        plate['ordered_quantifications'] = ordered_quantifications



#  .d8888b.
#  88   `8D 
#  88ooooY'
#  88~~~~b.
#  88    8D
#  Y88888P'
def analyze_plate_data(all_plate_info):
    """
    Analyze plate data and create three separate figures:
    1. Bar plot with means and dashed lines
    2. Knockdown plot
    3. Individual values plot
    """
    # Separate control and treatment data
    control_plates = []
    treatment_plates = []
    for plate in all_plate_info:
        additive = plate['additive']
        print(f"Additive: {additive}")
        
        if additive is None:
            control_plates.append(plate)
        else:
            treatment_plates.append(plate)
    
    # Ensure we have both control and treatment data
    if not control_plates or not treatment_plates:
        raise ValueError("Must have both control and treatment plates")
    
    # Get all control and treatment quantifications
    control_quants_list = [plate['unorderedquantifications'].flatten() 
                          for plate in control_plates]
    treatment_quants_list = [plate['unorderedquantifications'].flatten() 
                            for plate in treatment_plates]
    
    # Convert to arrays
    control_quants_array = np.array(control_quants_list)
    treatment_quants_array = np.array(treatment_quants_list)
    
    # Calculate averages
    control_means = np.mean(control_quants_array, axis=0)
    treatment_means = np.mean(treatment_quants_array, axis=0)
    
    # Generate labels
    rows, cols = control_plates[0]['unorderedquantifications'].shape
    labels = generate_plate_labels(rows, cols)
    
    # Prepare DataFrame
    df = pd.DataFrame({
        'Position': labels,
        'Control Mean': control_means,
        'Treatment Mean': treatment_means
    })
    
    df['Knockdown'] = np.where(
        (df['Control Mean'] == 0) | (df['Treatment Mean'] == 0),
        np.nan,
        df['Treatment Mean'] / df['Control Mean']
    )
    
    # Create categorical column for sorting
    df['Category'] = 'both_nonzero'
    df.loc[df['Treatment Mean'] == 0, 'Category'] = 'treatment_zero'
    df.loc[df['Control Mean'] == 0, 'Category'] = 'control_zero'
    df.loc[(df['Control Mean'] == 0) & (df['Treatment Mean'] == 0), 'Category'] = 'both_zero'
    
    # Remove pairs where both values are zero
    df = df[df['Category'] != 'both_zero']
    df = df.reset_index(drop=True)
    
    # Create three separate figures
    mean_fig = create_mean_plot(df, control_quants_list, treatment_quants_list, 
                              control_plates, treatment_plates)
    knockdown_fig = create_knockdown_plot(df)
    individual_fig = create_individual_plot(df, control_quants_list, treatment_quants_list,
                                          control_plates, treatment_plates)
    
    return df, mean_fig, knockdown_fig, individual_fig




# d888888b .88b  d88.  .d8b.   d888b  d88888b   db   db d88888b db      d8888b. d88888b d8888b. 
#   `88'   88'YbdP`88 d8' `8b 88' Y8b 88'       88   88 88'     88      88  `8D 88'     88  `8D 
#    88    88  88  88 88ooo88 88      88ooooo   88ooo88 88ooooo 88      88oodD' 88ooooo 88oobY' 
#    88    88  88  88 88~~~88 88  ooo 88~~~~~   88~~~88 88~~~~~ 88      88~~~   88~~~~~ 88`8b   
#   .88.   88  88  88 88   88 88. ~8~ 88.       88   88 88.     88booo. 88      88.     88 `88. 
# Y888888P YP  YP  YP YP   YP  Y888P  Y88888P   YP   YP Y88888P Y88888P 88      Y88888P 88   YD 
                                                                                              
                                                                                              
def cv2_to_pil(cv2_img, convertColour = True):
    if cv2_img is None:
        return None
    if len(cv2_img.shape) == 2: #2 channels = greyscale
        return Image.fromarray(cv2_img)
    elif len(cv2_img.shape) == 3 and convertColour:  #3 channels = color
        return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))
    else:
        return Image.fromarray(cv2_img) 


def get_image_size(img, max_width, max_height):
    img_width, img_height = img.size
    aspect_ratio = img_width / img_height
    if img_width > max_width:
        img_width = max_width
        img_height = img_width / aspect_ratio
    if img_height > max_height:
        img_height = max_height
        img_width = img_height * aspect_ratio
    return img_width, img_height



def resize_for_display(image, max_width=1280, max_height=720):
    h, w = image.shape[:2]
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image


#  d888b  d8888b.  .d8b.  d8888b. db   db .d8888.        .d8b.
# 88' Y8b 88  `8D d8' `8b 88  `8D 88   88 88'  YP       d8' `8b 
# 88      88oobY' 88ooo88 88oodD' 88ooo88 `8bo.         88ooo88
# 88  ooo 88`8b   88~~~88 88~~~   88~~~88   `Y8b.       88~~~88
# 88. ~8~ 88 `88. 88   88 88      88   88 db   8D       88   88
#  Y888P  88   YD YP   YP 88      YP   YP `8888Y'       YP   YP
                                                
                                                

def plot_multiadditive_graphs(data_series, dilution_series, title, log_base=10):
    
    figures_and_stats = []
    # Create two separate figures
    fig_individual = plt.figure(figsize=(30, 20))  # Increased width to accommodate legend
    ax1 = fig_individual.add_subplot(111)
    
    fig_average = plt.figure(figsize=(30, 20))  # Increased width to accommodate legend
    ax2 = fig_average.add_subplot(111)
    
    sns.set_context("notebook", font_scale=3)
    
    # Set log scale and style
    for ax in [ax1, ax2]:
        ax.set_xscale('log', base=log_base)
        ax.set_facecolor('#F5F5F5')

    # Get unique additives for averaging - handle None values
    additives = set(series.get('additive', 'Control') for series in data_series)
    additives = ['Control' if x is None else x for x in additives]
    additives = sorted(additives)
    
    # Initialize averaged data
    averaged_data = {additive: {float(x): [] for x in dilution_series} for additive in additives}
    
    max_y = max(max(series['normalized_y_values']) for series in data_series)
    y_max = max_y + 10

    # Color mapping (rest of the function remains the same as before)
    color_map = {}
    for additive in additives:
        if additive == 'Control':
            color_map[additive] = BLUECOLOURS
        elif len(color_map) % 4 == 0:
            color_map[additive] = REDCOLOURS
        elif len(color_map) % 4 == 1:
            color_map[additive] = GREENCOLOURS
        elif len(color_map) % 4 == 2:
            color_map[additive] = PURPLESCOLOURS
        elif len(color_map) % 4 == 3:
            color_map[additive] = PINKCOLOURS    
    
    individual_statistics = []
    average_statistics = []
    additive_counts = {additive: 0 for additive in additives}
    default_markers = ['o', 's', '^', 'D']
    
    # Create custom legend handles
    custom_handles = []
    custom_labels = []

    # Plot individual series
    for idx, series in enumerate(data_series):
        y_norm = series['normalized_y_values']
        additive = 'Control' if series.get('additive') is None else series.get('additive')
        
        color = color_map[additive][additive_counts[additive] % len(color_map[additive])]
        additive_counts[additive] += 1
        marker = series.get('marker', default_markers[idx % len(default_markers)])
        
        # Use new statistics calculation
        stats = calculate_statistics(dilution_series, y_norm, color, series['label'], additive)
        
        if stats is not None:
            individual_statistics.append(stats)
            
            # Scatter plot
            scatter = ax1.scatter(dilution_series, y_norm, color=color, 
                       marker=marker, label=series['label'], s=80)
            
            # Plot trend line using new statistics
            x_fit = np.logspace(0, np.log10(max(dilution_series)), num=100)
            y_fit = stats['slope'] * np.log10(x_fit) + stats['intercept']
            # Only plot positive y values
            mask = y_fit >= 0
            x_fit = x_fit[mask]
            y_fit = y_fit[mask]
            trend_line, = ax1.plot(x_fit, y_fit, color=color, linestyle='--',
                    label=f"R² = {stats['r_squared']:.3f}\n{stats['formula']}\n")
            
            # Create a custom label that combines both scatter and trend line information
            custom_label = f"{series['label']}\n(R² = {stats['r_squared']:.3f}\n{stats['formula']})"
            
            # Create a custom handle that will display both scatter and trend line
            custom_handle = plt.Line2D([0], [0], marker=marker, color=color, 
                                        linestyle='--', markersize=10, 
                                        label=custom_label)
            
            custom_handles.append(custom_handle)
            custom_labels.append(custom_label)
        
        # Collect data for averaging
        for x, y in zip(dilution_series, y_norm):
            if x > 0 and y > 10:  # Updated threshold as per new statistics function
                averaged_data[additive][x].append(y)
    
    # Create custom legend handles for average plots
    custom_handles_avg = []
    custom_labels_avg = []
    
    # Plot averaged data
    avg_additive_count = 0
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
            # Calculate statistics for averaged data using new function
            stats = calculate_statistics(valid_x, valid_means, color_map[additive][1], additive, additive)
            
            if stats is not None:
                average_statistics.append(stats)
                
                # Choose a marker for the averaged plot
                marker = default_markers[avg_additive_count % len(default_markers)]
                avg_additive_count += 1
                
                # Errorbar plot
                ax2.errorbar(valid_x, valid_means, yerr=valid_stds,
                            color=color_map[additive][1], marker=marker,
                            label=f'{additive}\nError bars = ±1 SD\nR² = {stats["r_squared"]:.3f}\n{stats["formula"]}',
                            capsize=5, capthick=1, markersize=8, linewidth=2,
                            ls='none')
                
                # Plot trend line using new statistics
                x_fit = np.logspace(0, np.log10(max(valid_x)), num=100)
                y_fit = stats['slope'] * np.log10(x_fit) + stats['intercept']
                mask = y_fit >= 0
                x_fit = x_fit[mask]
                y_fit = y_fit[mask]
                ax2.plot(x_fit, y_fit, color=color_map[additive][1], linestyle='--')
                
                # Create custom handle and label for average plot legend
                custom_label_avg = f"{additive}\n(R² = {stats['r_squared']:.3f}\n{stats['formula']})"
                custom_handle_avg = plt.Line2D([0], [0], marker=marker, color=color_map[additive][1], 
                                               linestyle='--', markersize=10, 
                                               label=custom_label_avg)
                
                custom_handles_avg.append(custom_handle_avg)
                custom_labels_avg.append(custom_label_avg)
    
    # Style plots
    fontS = 20
    for ax, fig, plot_title, custom_handles_input, custom_labels_input in [
        (ax1, fig_individual, "Individual Growth Curves", custom_handles, custom_labels),
        (ax2, fig_average, "Average Growth Curves", custom_handles_avg, custom_labels_avg)
    ]:
        ax.set_xlabel('Dilution Series', fontsize=20, fontweight='bold')
        ax.set_ylabel('Relative Growth (%)', fontsize=20, fontweight='bold')
        
        # Create legend with custom handles
        legend = ax.legend(
            custom_handles_input,  # Use custom handles
            custom_labels_input,   # Use custom labels
            fontsize=20,
            loc='upper center',
            bbox_to_anchor=(0.5, -0.15),
            ncol=3,  # 3 sets per row
            frameon=True, 
            facecolor='white', 
            edgecolor='gray',
            framealpha=0.5,
            title='Experimental Conditions'
        )
        
        # Make legend labels bold
        for text in legend.get_texts():
            text.set_fontweight('bold')
        
        # Customize legend title separately
        legend.get_title().set_fontsize(20)
        legend.get_title().set_fontweight('bold')
        
        # Adjust figure size to make room for the legend
        fig.subplots_adjust(bottom=0.2)  # Leaves room at the bottom for the legend
        ax.tick_params(axis='both', which='major', labelsize=15)
        ax.set_title(f"{plot_title} for {title}",
                    fontsize=40, fontweight='bold', pad=20)
        fig.tight_layout(rect=[0, 0.1, 1, 0.9]) 
    figures_and_stats.append((fig_individual, individual_statistics, "Individual Growth Curves"))
    figures_and_stats.append((fig_average, average_statistics, "Average Growth Curves"))
    return figures_and_stats


def save_graph_image(fig, filename):
    fig.savefig(filename, format='png', dpi=300, bbox_inches='tight')


def calculate_statistics(x, y, color, label, additive):
    valid_x = []
    valid_y = []
    excluded_points = []
    

    
    # Track points excluded from calculations
    for xi, yi in zip(x, y):
        if xi > 0 and yi > 10:
            # Convert to log 10 because of the dilution sequence
            valid_x.append(np.log10(xi))
            valid_y.append(yi)

    

    if len(valid_x) > 1:
        # Getting statistics for filtered data
        slope, intercept, r_value, p_value, std_err = stats.linregress(valid_x, valid_y)
        r_squared = r_value ** 2
        m, b = np.polyfit(valid_x, valid_y, 1)
        y_cut = b
        x_cut = 10 ** (-b / m)
        x_at_y50 = 10 ** ((50 - b) / m)
        formula = f"y = {m:.2f} * log10(x) + {b:.2f}"
    
    
        # Return as a dictionary since it's nice to call values from
        return {
            'slope': m,
            'intercept': b,
            'r_squared': r_squared,
            'formula': formula,
            'y_cut': y_cut,
            'x_cut': x_cut,
            'x_at_y50': x_at_y50,
            'label': label,
            'additive':additive,
            'color': color,  # Add the color to the statistics dictionary
            'full_line_formula': formula # Include full line formula
        }
    
    return None

#  d888b  d8888b.  .d8b.  d8888b. db   db .d8888.       .d8888b.
# 88' Y8b 88  `8D d8' `8b 88  `8D 88   88 88'  YP       88   `8D 
# 88      88oobY' 88ooo88 88oodD' 88ooo88 `8bo.         88ooooY'
# 88  ooo 88`8b   88~~~88 88~~~   88~~~88   `Y8b.       88~~~~b.
# 88. ~8~ 88 `88. 88   88 88      88   88 db   8D       88    8D
#  Y888P  88   YD YP   YP 88      YP   YP `8888Y'       Y88888P'





def generate_plate_labels_excelFormat(rows, cols):
    col_labels = list(string.ascii_uppercase[:cols])
    return [f"{col}{row+1}" for row in range(rows) for col in col_labels]

def generate_plate_labels(rows, cols):
    col_labels = list(string.ascii_uppercase[:cols])
    return [f"{col}{row+1}" for row in range(rows) for col in col_labels]    

def create_mean_plot(df, control_quants_list, treatment_quants_list, 
                    control_plates, treatment_plates):
    """Create the mean bar plot with dashed lines"""
    plt.style.use('default')
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'
    
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.set_facecolor(FACE_COLOR)
    fig.patch.set_facecolor('white')
    
    for i, row in df.iterrows():
        control_mean = row['Control Mean']
        treatment_mean = row['Treatment Mean']
        
        # Plot bars for means
        if control_mean > treatment_mean:
            ax.bar(i, control_mean, color=CONTROL_COLOR, alpha=ALPHA, 
                  edgecolor='black', linewidth=1)
            ax.bar(i, treatment_mean, color=FOREGROUND_COLOR, alpha=ALPHA,
                  edgecolor='black', linewidth=1)
        else:
            ax.bar(i, treatment_mean, color=FOREGROUND_COLOR, alpha=ALPHA,
                  edgecolor='black', linewidth=1)
            ax.bar(i, control_mean, color=CONTROL_COLOR, alpha=ALPHA,
                  edgecolor='black', linewidth=1)
        
        # # Plot dashed lines for individual values
        # for control_values in control_quants_list:
        #     ax.plot([i-0.2, i+0.2], [control_values[i], control_values[i]], 
        #            color=CONTROL_COLOR, linestyle='--', linewidth=1.5, alpha=0.8)
        
        # for treatment_values in treatment_quants_list:
        #     ax.plot([i-0.2, i+0.2], [treatment_values[i], treatment_values[i]], 
        #            color=FOREGROUND_COLOR, linestyle=':', linewidth=1.5, alpha=0.8)
    
    # Create legend
    legend_elements = [
        Patch(facecolor=CONTROL_COLOR, alpha=ALPHA, edgecolor='black', 
              label=f'Average Control Quantication (No additive)', linewidth=1),
        Patch(facecolor=FOREGROUND_COLOR, alpha=ALPHA, edgecolor='black', 
              label=f'Average Additive Quantification ({treatment_plates[0]["additive"]})', linewidth=1)
        # plt.Line2D([0], [0], color=CONTROL_COLOR, linestyle='--',
        #           label='Individual Control Values', linewidth=1.5),
        # plt.Line2D([0], [0], color=FOREGROUND_COLOR, linestyle=':',
        #           label='Individual Treatment Values', linewidth=1.5)
    ]
    ax.legend(handles=legend_elements, loc='upper right', 
             fontsize=8, frameon=True, facecolor='white')
    
    style_axis(ax, df)
    ax.set_title('Average Quantification Between Control and Additive Plates',
                color=TEXT_COLOR, pad=20, fontsize=25, fontweight='bold')
    ax.set_ylabel('Quantification Value', color=TEXT_COLOR, 
                 fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_knockdown_plot(df):
    """Create the knockdown plot"""
    plt.style.use('default')
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'
    
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.set_facecolor(FACE_COLOR)
    fig.patch.set_facecolor('white')
    
    df_filtered = df.dropna(subset=['Knockdown']).copy()
    df_filtered = df_filtered.sort_values('Knockdown', ascending=False)

    knockdown_mean = df_filtered['Knockdown'].mean()
    df_filtered = df_filtered[df_filtered['Knockdown'] <= 5 * knockdown_mean]
    
    for i, row in df_filtered.iterrows():
        idx = df_filtered.index.get_loc(i)
        color = FOREGROUND_COLOR if row['Knockdown'] > 1 else CONTROL_COLOR
        ax.bar(idx, row['Knockdown'], color=color, alpha=ALPHA,
               edgecolor='black', linewidth=1)
        
        # plt.text(idx, row['Knockdown'],
        #         f"{row['Knockdown']:.2f}",
        #         horizontalalignment='center',
        #         verticalalignment='bottom',
        #         color='black',
        #         fontsize=6,
        #         fontweight='bold')
    
    ax.axhline(y=1, color='black', linestyle='--', alpha=0.5, linewidth=1)
    
    style_axis(ax, df_filtered)
    excluded_count = len(df) - len(df_filtered)
    ax.set_title(f'Average Knockdown by Position\n{len(df_filtered)} positions shown ({excluded_count} positions with zero values excluded)',
                color=TEXT_COLOR, pad=20, fontsize=25, fontweight='bold')
    ax.set_ylabel('Knockdown (Treatment/Control)', color=TEXT_COLOR,
                 fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_individual_plot(df, control_quants_list, treatment_quants_list,
                         control_plates, treatment_plates):
    """Create plot showing individual values as circles"""
    plt.style.use('default')
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'
    
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.set_facecolor(FACE_COLOR)
    fig.patch.set_facecolor('white')
    
    for i, row in df.iterrows():
        control_mean = row['Control Mean']
        treatment_mean = row['Treatment Mean']
        
        # Plot light background bars
        if control_mean > treatment_mean:
            ax.bar(i, control_mean, color=CONTROL_COLOR, alpha=LIGHT_ALPHA, 
                  edgecolor='gray', linewidth=0.5)
            ax.bar(i, treatment_mean, color=FOREGROUND_COLOR, alpha=LIGHT_ALPHA,
                  edgecolor='gray', linewidth=0.5)
        else:
            ax.bar(i, treatment_mean, color=FOREGROUND_COLOR, alpha=LIGHT_ALPHA,
                  edgecolor='gray', linewidth=0.5)
            ax.bar(i, control_mean, color=CONTROL_COLOR, alpha=LIGHT_ALPHA,
                  edgecolor='gray', linewidth=0.5)
        
        # Plot individual values as circles
        for control_values in control_quants_list:
            ax.scatter(i, control_values[i], color=CONTROL_COLOR, 
                      edgecolor='black', linewidth=1, s=50, alpha=0.8)
        
        for treatment_values in treatment_quants_list:
            ax.scatter(i, treatment_values[i], color=FOREGROUND_COLOR,
                      edgecolor='black', linewidth=1, s=50, alpha=0.8)
    
    # Create legend
    legend_elements = [
        Patch(facecolor=CONTROL_COLOR, alpha=LIGHT_ALPHA, edgecolor='gray', 
              label=f'Average Control', linewidth=0.5),
        Patch(facecolor=FOREGROUND_COLOR, alpha=LIGHT_ALPHA, edgecolor='gray', 
              label=f'Average Additive', linewidth=0.5),
        plt.scatter([], [], color=CONTROL_COLOR, edgecolor='black',
                   label='Individual Control Quantifications', s=50),
        plt.scatter([], [], color=FOREGROUND_COLOR, edgecolor='black',
                   label='Individual Additive Quantificaitons', s=50)
    ]
    ax.legend(handles=legend_elements, loc='upper right', 
             fontsize=8, frameon=True, facecolor='white')
    
    style_axis(ax, df)
    ax.set_title('Individual Quantications Over Average Quantifications',
                color=TEXT_COLOR, pad=20, fontsize=25, fontweight='bold')
    ax.set_ylabel('Quantification Value', color=TEXT_COLOR,
                 fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig

def style_axis(ax, df):
    """Apply common styling to all axes"""
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax.yaxis.grid(True, linestyle='-', alpha=0.7, color='gray')
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(1.5)
    
    plt.sca(ax)
    plt.xticks(range(len(df)), df['Position'], rotation=45, ha='right')
    ax.set_xlim(-0.5, len(df) - 0.5)
    ax.set_xlabel('Position', color=TEXT_COLOR, fontsize=10, fontweight='bold')









# d88888b db    db  .o88b. d88888b db      
# 88'     `8b  d8' d8P  Y8 88'     88      
# 88ooooo  `8bd8'  8P      88ooooo 88      
# 88~~~~~  .dPYb.  8b      88~~~~~ 88      
# 88.     .8P  Y8. Y8b  d8 88.     88booo. 
# Y88888P YP    YP  `Y88P' Y88888P Y88888P 
                                         


def export_strain_data_to_excel(strain_data, dilution_series, output_filename='strain_data_export.xlsx'):
    """
    Export strain data to an Excel workbook in tidy (long) format.
    
    Args:
        strain_data (dict): Dictionary of strain data 
        dilution_series (list): List of dilution values
        output_filename (str): Name of the Excel file to save
    
    Returns:
        pd.DataFrame: Exported dataframe for additional processing if needed
    """
    # Prepare a list to collect all rows
    tidy_data = []
    
    # Iterate through each strain
    for strain, series_list in strain_data.items():
        for series in series_list:
            # Extract data from series
            filename = str(series['filename'])  # Ensure string
            additive = str(series.get('additive', 'Control'))  # Ensure string
            y_values = series['y_values']
            norm_value = float(series['norm_value'])  # Ensure float
            normalized_y_values = series['normalized_y_values']
            
            # Create rows for each quantification
            for dilution, y_value, norm_y_value in zip(dilution_series, y_values, normalized_y_values):
                tidy_data.append({
                    'filename': filename,
                    'additive': additive,
                    'strain': str(strain),  # Ensure string
                    'quantification': float(y_value),  # Ensure float
                    'dilution': float(dilution),  # Ensure float
                    'normalised_quantification': float(norm_y_value),  # Ensure float
                    'normalisation_value': norm_value
                })
    
    # Convert to DataFrame
    df = pd.DataFrame(tidy_data)
    
    # Sort without using categorical
    df = df.sort_values(
        by=['strain', 'additive', 'filename', 'dilution'], 
        key=lambda col: col.astype(str)
    )
    
    # Export to Excel
    df.to_excel(output_filename, index=False)
    
    print(f"Data exported to {output_filename}")
    
    return df

def generate_plate_labels(rows, cols):
    col_labels = list(string.ascii_uppercase[:cols])
    return [f"{col}{row+1}" for row in range(rows) for col in col_labels]
    
def export_plate_data_to_excel(all_plate_info, output_path='plate_analysis.xlsx'):
    """
    Export plate data to Excel in tidy format with one position per row.
    
    Parameters:
    all_plate_info (list): List of dictionaries containing plate information
    output_path (str): Path where the Excel file should be saved
    
    Returns:
    pd.DataFrame: The tidy format dataframe that was exported
    """
    # Generate position labels
    rows, cols = all_plate_info[0]['unorderedquantifications'].shape
    positions = generate_plate_labels(rows, cols)
    
    # Initialize the dataframe with positions
    df = pd.DataFrame({'Position': positions})
    
    # Separate control and treatment plates
    control_plates = [plate for plate in all_plate_info if plate['additive'] is None]
    treatment_plates = [plate for plate in all_plate_info if plate['additive'] is not None]
    
    # Add individual plate data
    for plate in all_plate_info:
        filename = plate['filename']
        quants = plate['unorderedquantifications'].flatten()
        additive = plate['additive'] if plate['additive'] is not None else 'Control'
        
        df[f'{filename}_quantification'] = quants
        df[f'{filename}_additive'] = additive
        df[f'{filename}_filename'] = filename
    
    # Calculate and add average quantifications
    control_quants = np.array([plate['unorderedquantifications'].flatten() 
                              for plate in control_plates])
    treatment_quants = np.array([plate['unorderedquantifications'].flatten() 
                                for plate in treatment_plates])
    
    df['Average_Control_Quantification'] = np.mean(control_quants, axis=0)
    df['Average_Additive_Quantification'] = np.mean(treatment_quants, axis=0)
    
    # Calculate knockdown
    df['Knockdown'] = np.where(
        (df['Average_Control_Quantification'] == 0) | 
        (df['Average_Additive_Quantification'] == 0),
        np.nan,
        df['Average_Additive_Quantification'] / df['Average_Control_Quantification']
    )
    
    # Export to Excel
    df.to_excel(output_path, index=False)
    
    return df

def export_tidy_data_to_excel(window, output_filename='tidy_data.xlsx'):
    """
    Export tidy data to an Excel workbook.
    
    Args:
        window: The window object containing plate information
        output_filename: Name of the Excel file to save (default: 'tidy_data.xlsx')
    
    Returns:
        str: Path to the saved Excel file
    """
    # Generate tidy dataframe
    tidy_df = generate_tidy_dataframe(window)
    
    # Export to Excel
    tidy_df.to_excel(output_filename, index=False)
    
    print(f"Tidy data exported to {output_filename}")
    return output_filename

def generate_tidy_dataframe(window):
    """
    Generate a tidy dataframe from plate quantification data.
    
    Args:
        window: The window object containing plate information
    
    Returns:
        pd.DataFrame: A tidy dataframe with one row per quantification point
    """
    # Initialize lists to collect data
    tidy_data = []
    
    # Iterate over all plates
    for plate in window.all_plate_info:
        additive = plate.get('additive', 'Control') or 'Control'
        filename = plate.get('filename', 'Unnamed Plate')
        strains = plate['strains']
        column_indexes = plate['column_indexes']
        dilutions = plate['dilutions']
        ordered_quantifications = plate['ordered_quantifications']
        
        # Ensure ordered_quantifications and column_indexes match strain count
        if len(ordered_quantifications) != len(strains):
            raise ValueError("Mismatch between strains and ordered_quantifications length in plate.")
        
        # For each strain in the plate
        for strain_idx, strain in enumerate(strains):
            # Extract y_values for this strain
            y_values = ordered_quantifications[strain_idx]
            column_indexes_for_strain = column_indexes[strain_idx]
            
            # Calculate normalisation value (using first value of control series)
            norm_values = [
                series['ordered_quantifications'][0] for series in window.all_plate_info 
                if series.get('additive') in [None, 'Control']
            ]
            norm_value = sum(norm_values) / len(norm_values) if norm_values else 1
            
            # Normalize the y_values
            normalized_y_values = [y / norm_value * 100 for y in y_values]
            
            # Prepare data for tidy format
            for col_idx, (raw_value, normalized_value) in enumerate(zip(y_values, normalized_y_values)):
                # Find the corresponding dilution
                dilution_index = col_idx % len(dilutions[0])
                dilution_value = dilutions[0][dilution_index]
                
                tidy_data.append({
                    'filename': filename,
                    'additive': additive,
                    'strain': strain,
                    'quantification': raw_value,
                    'dilution': dilution_value,
                    'normalization_value': norm_value,
                    'normalized_value': normalized_value
                })
    
    # Convert to DataFrame
    df = pd.DataFrame(tidy_data)
    
    return df





# d8888b. d8888b. d88888b 
# 88  `8D 88  `8D 88'     
# 88oodD' 88   88 88ooo   
# 88~~~   88   88 88~~~   
# 88      88  .8D 88      
# 88      Y8888D' YP      


def add_info_page(plate_info, story, logo, title_style, body_style):
    """Helper function to add plate information page"""  
    # Add title with plate name + Log
    story.append(Spacer(1, 10))
    title_text = f"\n{plate_info['filename']} Log"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 10))
    
    max_width = 280
    max_height = 170
    def create_image_with_caption(img_key, caption, max_width=280, max_height=170):
        """
        Creates an image and caption for the PDF report using ReportLab components.
        Handles both OpenCV images and base64-encoded preview images.
        Limits maximum image resolution to 2500x2500 pixels.
        Caption is centered and placed above the image.
        """
        try:
            if img_key == "IMGPreview":
                # Check if the preview image exists in the nested structure
                if plate_info.get('layout', {}).get('IMGPreview') is not None:
                    # Decode base64 string to PIL Image
                    img_data = base64.b64decode(plate_info['layout']['IMGPreview'])
                    pil_img = Image.open(io.BytesIO(img_data))
                else:
                    raise KeyError("IMGPreview not found in layout")
            else:
                # Handle other image types
                if plate_info.get(img_key) is not None:
                    if img_key == "IMGgrid":
                        pil_img = cv2_to_pil(plate_info[img_key], False)
                    else:
                        pil_img = cv2_to_pil(plate_info[img_key])
                else:
                    raise KeyError(f"{img_key} not found in plate_info")

            if pil_img:
                # Convert to RGB if needed
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Check and limit maximum resolution
                orig_width, orig_height = pil_img.size
                if orig_width > 2500 or orig_height > 2500:
                    # Calculate scaling factor to fit within 2500x2500
                    scale_factor = min(2500 / orig_width, 2500 / orig_height)
                    new_width = int(orig_width * scale_factor)
                    new_height = int(orig_height * scale_factor)
                    pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
                
                # Resize image maintaining aspect ratio for PDF display
                img_width, img_height = get_image_size(pil_img, max_width, max_height)
                
                # Save to bytes buffer
                img_data = BytesIO()
                pil_img.save(img_data, format='JPEG', quality=40)
                img_data.seek(0)
                
                # Create ReportLab image without border
                img = ImageR(img_data, width=img_width, height=img_height)
                
                # Create centered, bold, and italic caption style
                caption_style = ParagraphStyle(
                    'CaptionStyle',
                    parent=body_style,
                    fontWeight='bold',
                    fontStyle='italic',
                    alignment=TA_CENTER  # Center align the text
                )
                
                # Return caption first, then the image
                return [
                    Paragraph(caption, caption_style),  # Centered caption
                    img  # Image below the caption
                ]
        except Exception as e:
            print(f"Error creating image with caption: {e}")
            return []
    def create_info_text(plate_info):
        if (plate_info['layout']['x_dilution'] == -1  and plate_info['layout']['y_dilution'] == -1):
            info_text = f"""
            <b>Filename:</b> {plate_info.get('filename', 'Not specified')}<br/>
            <b>Additive:</b> {plate_info.get('additive', 'None')}<br/>
            <b>Threshold:</b> {plate_info['threshold']}<br/>
            <b>Minimum Area:</b> {plate_info['smallArea']}<br/>
            <b>Block Size:</b> {plate_info['blocksize']}<br/>
            """
        else:
            info_text = f"""
            <b>Filename:</b> {plate_info.get('filename', 'Not specified')}<br/>
            <b>Additive:</b> {plate_info.get('additive', 'None')}<br/>
            <b>X Dilution:</b> {plate_info['layout']['x_dilution']}<br/>
            <b>Y Dilution:</b> {plate_info['layout']['y_dilution']}<br/>
            <b>Strains:</b> {", ".join(plate_info.get('strains', [])) if plate_info.get('strains') else 'None'}<br/>
            <b>Column Indexes:</b> {plate_info.get('column_indexes', 'Not specified')}<br/>
            <b>Gap Between Strains:</b> {plate_info['layout']['gap_between_strains']}<br/>
            <b>Threshold:</b> {plate_info['threshold']}<br/>
            <b>Minimum Area:</b> {plate_info['smallArea']}<br/>
            <b>Block Size:</b> {plate_info['blocksize']}<br/>
            """

        return Paragraph(info_text, body_style)

    # Row 1: Preview and Info
    row1_data = [
        [create_image_with_caption('IMGPreview', "Assay Layout"),
            create_info_text(plate_info)]
    ]
    row1_table = Table(row1_data, colWidths=[max_width, max_width])
    
    # Row 2: Binary Images
    row2_data = [
        [create_image_with_caption('IMGToolUsage', "Tool Usage: Red(+) Blue(-)"),
        # [create_image_with_caption('IMGbinary', "Tool Usage: Red(+) Blue(-))"),
        create_image_with_caption('IMGbinary', "Final Binary Image")]
    ]
    row2_table = Table(row2_data, colWidths=[max_width, max_width])
    # Row 3: Grid and Contours
    row3_data = [
        [create_image_with_caption('IMGgrid', "Detected Grid and Quantifications"),
            create_image_with_caption('IMGcontours', "Contours overaly")]
    ]
    row3_table = Table(row3_data, colWidths=[max_width, max_width])
    
    # Apply consistent styling to all tables
    table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ])
    
    for table in [row1_table, row2_table, row3_table]:
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 10))
    story.append(PageBreak())    
    

def add_title_page(doc, logo_path="Icons/LogoVerticalDark.png", version="1.0"):
    """
    Create a title page for the document with logo, date, and version.
    
    Args:
        doc (SimpleDocTemplate): The document to add the title page to.
        logo_path (str): Path to the logo image.
        version (str): Version of the software.
    
    Returns:
        list: A list of flowable elements for the title page.
    """
    # Title page story elements
    title_story = []
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='MainTitle',
        parent=styles['Title'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        name='Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    credit_style = ParagraphStyle(
        name='Credit',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.gray
    )
    
    # Add more vertical space before logo
    title_story.append(Spacer(1, 2*inch))  # Increased from 2 to 3 inches
    
    # Load and resize logo while maintaining proportions
    try:
        logo_img = Image.open(logo_path)
        original_width, original_height = logo_img.size
        # Set a maximum width for the logo (e.g., 5 inches)
        max_logo_width = 7 * inch
        width_ratio = max_logo_width / original_width
        scaled_width = max_logo_width
        scaled_height = original_height * width_ratio
        
        # Use HAlign to ensure logo is centered
        logo = ImageR(logo_path, width=scaled_width, height=scaled_height, hAlign='CENTER')
        title_story.append(logo)
    except Exception as e:
        print(f"Error loading logo: {e}")
    
    # Add current date and version
    current_date = datetime.now().strftime("%Y-%m-%d")
    version_text = f"Version {version} | Generated on {current_date}"
    title_story.append(Paragraph(version_text, subtitle_style))
    

    
    # Optional: Add additional text or credits
    credit_text = "Created by Holly Lewis<br/>Supervised by R. Verrinder and Dr. M. Mason"
    title_story.append(Paragraph(credit_text, credit_style))
    title_story.append(PageBreak())
    return title_story


def generate_pdf_report_MODEA(all_plate_info, all_strain_data, output_filename, version="1.0.0"):
    
    """
    Generates a single PDF report containing data for all strains.
    Each strain's figures are on consecutive pages with statistics underneath.
    Tables are split if they contain more than 4 entries, with colors matching the plots.
    
    Args:
        all_plate_info: List of plate information dictionaries
        all_strain_data: List of tuples (strain_name, figures_and_stats)
        output_filename: Path to save the PDF
        version: Spotplotter version number
    """
    # Create footer style
    footer_style = ParagraphStyle(
        'Footer',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1  # Center alignment
    )
    
    # Create footer function
    def add_footer(canvas, doc):
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} using Spotplotter v{version}"
        footer = Paragraph(footer_text, footer_style)
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
    
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        topMargin=0*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1
    )
    strain_style = ParagraphStyle(
        name='StrainTitle',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=1,
        spaceAfter=30
    )
    body_style = styles['Normal']
    
    # Add logo
    logo_path = ("Icons/LogoHorizontalDark.png")
    logo = ImageR(logo_path, width=1170/4, height=407/4)




    def add_final_info_page():
        story.append(logo)
        story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

        current_date = datetime.now().strftime("%Y-%m-%d")
        
        
        info_text = f"""
        This report was generated by <b>Spotplotter</b> version <b>1.0</b> on <b>{current_date}</b>

        Spotplotter was created by <b>Holly Lewis</b> with supervision from <b>R Verrinder</b> and <b>Dr. M Mason</b> as BSc (Eng) final year project submitted in partial fulfilment of the requirements for the degree of Bachelor of Science in Electrical and Computer Engineering in the Department of Electrical Engineering at the University of Cape Town.


        <b>Formula:</b> The formula represents the linear regression equation that models determined using the by linregress function from scipy.stats which determines the relationship between the logarithm of the dilution series and relative growth. It follows the form:
        y = m ⋅ log10(x) + b

        <b>Normalization:</b> The relative growth values were normalized to a baseline to make the results comparable across different conditions. The quantified values of each spot were divided by the average value of the first spot in the -ATP for each strain.

        <b>The slope (m):</b> indicates the rate of change in relative growth as the dilution series increases (on a logarithmic scale). A steep slope indicated that the growth has a faster knockdown as the dilution changes. A shallow slope indicates that the growth is more stable across dilutions.

        <b>The intercept (b)</b> and y-cut is the relative growth when the solution is not diluted.

        <b>The R-squared value</b> measures how well the linear regression line fits the data, where 1 represents a perfect fit and 0 represents no relationship. Higher R² values indicates that the growth follows a linear relationship.

        <b>The X-cut</b> refers to the point where the regression line crosses the x-axis, indicating the dilution value at which the relative growth would theoretically be zero (no growth).

        <b>X at Y = 50:</b> This value represents the dilution series value when the relative growth is 50% i.e., the knockdown is 50% in comparison to the -ATP series.
        """

        for paragraph in info_text.split('\n\n'):
            story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 6))



    story = add_title_page(doc)
    # Add plate info pages
    for plate_info in all_plate_info:
        add_info_page(plate_info, story, logo, title_style, body_style)
    
    def create_stats_table(stats_subset):
        """Create a statistics table for a subset of stats (max 4 entries)"""
        # Dynamically adjust column widths based on number of entries
            # If 3 or fewer entries, use wider columns
        col_widths = [1.8 * inch]  # First column (row labels)
        col_widths.extend([1.8 * inch] * len(stats_subset))  # Wider data columns



        header_row = ['']
        for stat in stats_subset:
            label = stat['label']
            # If label is longer than column width, split it
            if len(label) > col_widths[1] / 6:  # Rough character estimate 
                mid = len(label) // 2
                label = label[:mid] + '\n' + label[mid:]
            header_row.append(label)
        
        table_data = [header_row]
        for row_label in ['Formula', 'Slope', 'Intercept', 'R-squared', 'y-cut', 'x-cut', 'x_at_y50']:
            row = [row_label]
            for stat in stats_subset:
                if row_label == 'Formula':
                    value = stat['formula']
                    # Split long formulas across two lines if needed
                elif row_label == 'R-squared':
                    value = f"{stat['r_squared']:.3f}"
                elif row_label == 'x_at_y50':
                    if abs(stat['x_at_y50']) >= 1e5:  # 5 digits before the decimal
                        value = f"{stat['x_at_y50']:.2e}"  # Scientific notation
                    else:
                        value = f"{stat['x_at_y50']:.2f}"
                else:
                    key = row_label.lower().replace('-', '_')
                    # Handle scientific notation for values with more than 5 digits before the decimal
                    raw_value = stat[key]
                    if abs(raw_value) >= 1e5:  # 5 digits before the decimal
                        value = f"{raw_value:.2e}"  # Scientific notation
                    else:
                        value = f"{raw_value:.2f}"
                row.append(value)
            table_data.append(row)

        table = Table(table_data, colWidths=col_widths)
        table_style = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            # Ensure text wrapping for all cells
            ('WORDWRAP', (0, 0), (-1, -1), 1),  # Explicitly set word wrapping
        ]

        # Add matched colors from the stats
        for i, stat in enumerate(stats_subset, start=1):
            # Convert matplotlib color to reportlab color
            if isinstance(stat.get('color'), str):
                if stat['color'].startswith('#'):
                    bg_color = colors.HexColor(stat['color'])
                else:
                    # Handle named colors
                    bg_color = colors.HexColor(rgb2hex(mcolors.to_rgb(stat['color'])))
            else:
                # Handle RGB tuples
                bg_color = colors.HexColor(rgb2hex(stat['color']))
    
            table_style.append((
                'BACKGROUND',
                (i, 0),
                (i, 0),
                bg_color
            ))

        table.setStyle(TableStyle(table_style))
        return table
        
    # Process each strain's data
    for strain_name, figures_and_stats in all_strain_data:
        # Process each figure and its statistics for this strain
        for fig, stats, plot_title in figures_and_stats:
            
            story.append(Paragraph(" ", styles['Normal']))  # Add a space as a first element
            story.append(Spacer(1, 1*inch))
            # Add figure
            img_data = BytesIO()
            fig.savefig(img_data, format='png', dpi=150, bbox_inches='tight')
            img_data.seek(0)

            # Calculate aspect ratio
            with Image.open(img_data) as img:
                width, height = img.size
                aspect_ratio = width / height

            # Desired width while maintaining aspect ratio
            desired_width = 6 * inch
            desired_height = desired_width / aspect_ratio

            # Reset img_data pointer
            img_data.seek(0)

            # Add image to the story
            story.append(ImageR(img_data, width=desired_width, height=desired_height))
            story.append(Spacer(1, 20))
            
            # Split stats into groups of 4 and create multiple tables if needed
            def group_stats_by_additive(stats):
                # Separate Control entries and other entries
                control_groups = []
                other_groups = []
                
                # Group stats by additive
                additive_groups = {}
                for stat in stats:
                    additive = stat['additive']
                    if additive not in additive_groups:
                        additive_groups[additive] = []
                    additive_groups[additive].append(stat)
                
                # Process Control groups first
                if 'Control' in additive_groups:
                    control_stats = additive_groups['Control']
                    for i in range(0, len(control_stats), 4):
                        control_groups.append(control_stats[i:i+4])
                
                # Process other additives
                for additive, group_stats in additive_groups.items():
                    if additive != 'Control':
                        for i in range(0, len(group_stats), 4):
                            other_groups.append(group_stats[i:i+4])
                
                # Combine groups with Control first
                return control_groups + other_groups
            
            # Updated table creation loop
            grouped_stats = group_stats_by_additive(stats)
            #SO THAT IF ITS AVEAGES THEY WILL SHARE A TABLE
            #  
            def consolidate_grouped_stats(grouped_stats):
                # Check if all groups have only one entry (average values)
                if all(len(group) == 1 for group in grouped_stats):
                    # Flatten the groups while maintaining their original order
                    flattened_groups = [stat for group in grouped_stats for stat in group]
                    
                    # Combine into groups of 3 or less
                    consolidated_groups = []
                    for i in range(0, len(flattened_groups), 3):
                        consolidated_groups.append(flattened_groups[i:i+3])
                    return consolidated_groups
                
                # If not all groups have single entries, return original grouped_stats
                return grouped_stats
            grouped_stats = consolidate_grouped_stats(grouped_stats)
            print(grouped_stats )
            if len(stats) < 3:
                # Combine all stats into one table if less than 3 groups
                combined_stats = [stat for group in grouped_stats for stat in group]  # Flatten grouped stats
                table = create_stats_table(combined_stats)
                story.append(table)
                story.append(Spacer(1, 10))  
            else:
                # Normal logic for more than 3 groups
                i = 0
                for stats_subset in grouped_stats:
                    if i ==2 or i== 6:
                        story.append(PageBreak())
                    table = create_stats_table(stats_subset)
                    story.append(table)
                    story.append(Spacer(1, 10))
                    i += 1

            # Add page break after each strain except the last one
            story.append(PageBreak())
        
    
    # Build the PDF with footer
    story.append(add_final_info_page())
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

def generate_pdf_report_MODEB(all_plate_info, output_filename, mean_fig, knockdown_fig, individual_fig, version="1.0.0"):
    from reportlab.lib.units import inch
    from io import BytesIO
    
    # Create footer style
    footer_style = ParagraphStyle(
        'Footer',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1  # Center alignment
    )
    
    # Create footer function
    def add_footer(canvas, doc):
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} using Spotplotter v{version}"
        footer = Paragraph(footer_text, footer_style)
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
    
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    story = []
    story = add_title_page(doc)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1
    )


    strain_style = ParagraphStyle(
        name='StrainTitle',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=1,
        spaceAfter=30
    )
    body_style = styles['Normal']
    
    
    # Add logo
    logo_path = ("Icons/LogoHorizontalDark.png")
    logo = ImageR(logo_path, width=1170/4, height=407/4)

    def add_final_info_page():
        story.append(logo)
        story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

        current_date = datetime.now().strftime("%Y-%m-%d")
        
        
        info_text = f"""
        This report was generated by <b>Spotplotter</b> version <b>1.0</b> on <b>{current_date}</b>

        Spotplotter was created by <b>Holly Lewis</b> with supervision from <b>R Verrinder</b> and <b>Dr. M Mason</b> as BSc (Eng) final year project submitted in partial fulfilment of the requirements for the degree of Bachelor of Science in Electrical and Computer Engineering in the Department of Electrical Engineering at the University of Cape Town.
        """

        for paragraph in info_text.split('\n\n'):
            story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 6))
    

    
    def save_figure_for_pdf(fig, width=7.5*inch, height=3*inch):
        """Save matplotlib figure to bytes buffer and return as ReportLab image"""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        return ImageR(buf, width=width, height=height)
    
    
        # Add logo
    logo_path = ("Icons/LogoHorizontalDark.png")
    logo = ImageR(logo_path, width=1170/4, height=407/4)
    # Add existing content (plate info pages)
    for plate_info in all_plate_info:
        add_info_page(plate_info, story, logo, title_style, body_style)
    
    # Save and add graphs to PDF
    # Calculate dimensions to maintain 15:6 aspect ratio while fitting on page
    page_width = 7.5 * inch  # Standard letter page width minus margins
    graph_height = (page_width * 6) / 15  # Maintain 15:6 aspect ratio
    
    # Add Mean Plot
    mean_image = save_figure_for_pdf(mean_fig, width=page_width, height=graph_height)
    # Add Knockdown Plot
    knockdown_image = save_figure_for_pdf(knockdown_fig, width=page_width, height=graph_height)
    # Add Individual Plot
    individual_image = save_figure_for_pdf(individual_fig, width=page_width, height=graph_height)


    
    story.append(mean_image)
    story.append(knockdown_image)
    story.append(individual_image)


    add_final_info_page()
    # Add final info page

    
    # Build the PDF with footer
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)





















