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
import openpyxl
import base64
import io
import math
from collections import defaultdict
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.graphics import renderPDF
from PIL import Image
from io import BytesIO
import base64
import pandas as pd
import numpy as np

from PIL import Image, ImageTk
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\GUI\assets\frame0")
from matplotlib.colors import rgb2hex
import matplotlib.colors as mcolors
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)



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

def plot_multiadditive_graphs(data_series, dilution_series, title, log_base=10):
    
    figures_and_stats = []
    # Create two separate figures
    fig_individual = plt.figure(figsize=(24, 10))  # Increased width to accommodate legend
    ax1 = fig_individual.add_subplot(111)
    
    fig_average = plt.figure(figsize=(24, 10))  # Increased width to accommodate legend
    ax2 = fig_average.add_subplot(111)
    
    sns.set_context("notebook", font_scale=1.2)
    
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
        elif len(color_map) % 3 == 0:
            color_map[additive] = REDCOLOURS
        elif len(color_map) % 3 == 1:
            color_map[additive] = GREENCOLOURS
        elif len(color_map) % 3 == 2:
            color_map[additive] = PURPLESCOLOURS
    
    individual_statistics = []
    average_statistics = []
    additive_counts = {additive: 0 for additive in additives}
    default_markers = ['o', 's', '^', 'D']
    
    # Plot individual series
    for idx, series in enumerate(data_series):
        y_norm = series['normalized_y_values']
        additive = 'Control' if series.get('additive') is None else series.get('additive')
        
        color = color_map[additive][additive_counts[additive] % len(color_map[additive])]
        additive_counts[additive] += 1
        marker = series.get('marker', default_markers[idx % len(default_markers)])
        
        # Use new statistics calculation
        stats = calculate_statistics(dilution_series, y_norm, color, series['label'])
        
        if stats is not None:
            individual_statistics.append(stats)
            
            ax1.scatter(dilution_series, y_norm, color=color, 
                       marker=marker, label=series['label'], s=80)
            
            # Plot trend line using new statistics
            x_fit = np.logspace(0, np.log10(max(dilution_series)), num=100)
            y_fit = stats['slope'] * np.log10(x_fit) + stats['intercept']
            # Only plot positive y values
            mask = y_fit >= 0
            x_fit = x_fit[mask]
            y_fit = y_fit[mask]
            ax1.plot(x_fit, y_fit, color=color, linestyle='--',
                    label=f"R² = {stats['r_squared']:.3f}\n{stats['formula']}\n")
        
        # Collect data for averaging
        for x, y in zip(dilution_series, y_norm):
            if x > 0 and y > 10:  # Updated threshold as per new statistics function
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
            # Calculate statistics for averaged data using new function
            stats = calculate_statistics(valid_x, valid_means, color_map[additive][1], additive)
            
            if stats is not None:
                average_statistics.append(stats)
                
                ax2.errorbar(valid_x, valid_means, yerr=valid_stds,
                            color=color_map[additive][1], marker='o',
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
    
    # Style plots
# Style plots
    for ax, fig, plot_title in [(ax1, fig_individual, "Individual Growth Curves"), 
                               (ax2, fig_average, "Average Growth Curves")]:
        ax.set_xlabel('Dilution Series', fontsize=16, fontweight='bold')
        ax.set_ylabel('Relative Growth (%)', fontsize=16, fontweight='bold')
        
        # Adjust legend to be a single column on the right
        legend = ax.legend(
            fontsize=10,  # Increased font size
            loc='center left',  # Positioned on the left side of the plot 
            bbox_to_anchor=(1, 0.5),  # Centered vertically on the right side
            ncol=1,  # Single column
            frameon=True, 
            facecolor='white', 
            edgecolor='gray',
            framealpha=0.5,
            title_fontsize=12  # Optional: if you want a title for the legend
        )
        
        # Adjust figure size to make room for the legend
        fig.subplots_adjust(right=0.75)  # Leaves 25% of the width for the legend
        
        ax.set_ylim(0, 110)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.set_title(f"{plot_title} for {title}",
                    fontsize=20, fontweight='bold', pad=20)
        fig.tight_layout()
    
    figures_and_stats.append((fig_individual, individual_statistics, "Individual Growth Curves"))
    figures_and_stats.append((fig_average, average_statistics, "Average Growth Curves"))
    return figures_and_stats


def normalize_array(values, norm_value):
    """
    Normalize an array of values relative to a normalization value.
    
    Args:
        values (list or np.array): Original values to normalize
        norm_value (float): Value to normalize against
    
    Returns:
        np.array: Normalized values as percentages
    """
    return np.array(values) / norm_value * 100

def calculate_strain_normalization_value(data_series, strain):
    """
    Calculate normalization value for a specific strain from control series.
    
    Args:
        data_series (list): List of data series dictionaries
        strain (str): Strain to calculate normalization for
    
    Returns:
        float: Normalization value (average of first values in control series for the strain)
    """
    # Find control series (None or 'Control' additive) for the specific strain
    norm_values = [
        series['y_values'][0] for series in data_series 
        if (series.get('additive') in [None, 'Control']) and (series['strain'] == strain)
    ]
    
    if not norm_values:
        raise ValueError(f"Must have at least one control series for strain {strain}")
    
    return sum(norm_values) / len(norm_values)


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

def save_graph_image(fig, filename):
    fig.savefig(filename, format='png', dpi=300, bbox_inches='tight')




#  d888b  d8888b.  .d8b.  d8888b. db   db .d8888. 
# 88' Y8b 88  `8D d8' `8b 88  `8D 88   88 88'  YP 
# 88      88oobY' 88ooo88 88oodD' 88ooo88 `8bo.   
# 88  ooo 88`8b   88~~~88 88~~~   88~~~88   `Y8b. 
# 88. ~8~ 88 `88. 88   88 88      88   88 db   8D 
#  Y888P  88   YD YP   YP 88      YP   YP `8888Y' 





def calculate_statistics(x, y, color, label):
    valid_x = []
    valid_y = []
    #only using ones that are above 10% becuse at that point there are a lot of very light ones that arent quantified and otherwise there are a lot of zeros
    for xi, yi in zip(x, y):
        if xi > 0 and yi > 10:
            #convert it to log 10 becuse of the dilution sequence
            valid_x.append(np.log10(xi))
            valid_y.append(yi)
   
    if len(valid_x) > 1:
        #getting all the statistics
        slope, intercept, r_value, p_value, std_err = stats.linregress(valid_x, valid_y)
        r_squared = r_value ** 2
        m, b = np.polyfit(valid_x, valid_y, 1)
        y_cut = b
        x_cut = 10 ** (-b / m)
        x_at_y50 = 10 ** ((50 - b) / m)
        formula = f"y = {m:.2f} * log10(x) + {b:.2f}"
       
        #return as a dictionary since it very nice to call values from
        return {
            'slope': m,
            'intercept': b,
            'r_squared': r_squared,
            'formula': formula,
            'y_cut': y_cut,
            'x_cut': x_cut,
            'x_at_y50': x_at_y50,
            'label': label,
            'color': color  # Add the color to the statistics dictionary
        }
   
    return None


# d8888b. d8888b. d88888b 
# 88  `8D 88  `8D 88'     
# 88oodD' 88   88 88ooo   
# 88~~~   88   88 88~~~   
# 88      88  .8D 88      
# 88      Y8888D' YP      

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def cv2_to_pil(cv2_img, convertColour = True):
    if cv2_img is None:
        return None
    if len(cv2_img.shape) == 2: #2 channels = greyscale
        return Image.fromarray(cv2_img)
    elif len(cv2_img.shape) == 3 and convertColour:  #3 channels = color
        return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))
    else:
        return Image.fromarray(cv2_img) 

#determining which proportion the image is contrained by and using that ration to keep everything the same proportion
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


def add_info_page(plate_info, story, logo, title_style, body_style):
    """Helper function to add plate information page"""  
    # Add title with plate name + Log
    story.append(Spacer(1, 10))
    title_text = f"\n{plate_info['filename']} Log"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 10))
    
    max_width = 280
    max_height = 160
    def create_image_with_caption(img_key, caption, max_width=max_width, max_height=max_height):
        """
        Creates an image and caption for the PDF report using ReportLab components.
        Handles both OpenCV images and base64-encoded preview images.
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
            
                # Resize image maintaining aspect ratio
                img_width, img_height = get_image_size(pil_img, max_width, max_height)
            
                # Save to bytes buffer
                img_data = BytesIO()
                pil_img.save(img_data, format='JPEG', quality=40)
                img_data.seek(0)
            
                # Create ReportLab image without border
                img = ImageR(img_data, width=img_width, height=img_height)
                
                # Create bold and italic caption style
                caption_style = ParagraphStyle(
                    'CaptionStyle',
                    parent=body_style,
                    fontWeight='bold',
                    fontStyle='italic'
                )
                
                return [img, Paragraph(caption, caption_style)]

        except Exception as e:
            print(f"Error creating image with caption: {e}")
            return []


    def create_info_text(plate_info):
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
        [create_image_with_caption('IMGPreview', "Preview Image"),
            create_info_text(plate_info)]
    ]
    row1_table = Table(row1_data, colWidths=[max_width, max_width])
    
    # Row 2: Binary Images
    row2_data = [
        # [create_image_with_caption('IMGToolUsage', "Tool Usage: Red(+) Blue(-))"),
        [create_image_with_caption('IMGbinary', "Tool Usage: Red(+) Blue(-))"),
        create_image_with_caption('IMGbinary', "Binary Image")]
    ]
    row2_table = Table(row2_data, colWidths=[max_width, max_width])
    # Row 3: Grid and Contours
    row3_data = [
        [create_image_with_caption('IMGgrid', "Grid Image"),
            create_image_with_caption('IMGcontours', "Contours Image")]
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
        story.append(Spacer(1, 20))
    story.append(PageBreak())    
    






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
    logo_path = relative_to_assets("LogoHorizontalDark.png")
    logo = ImageR(logo_path, width=1170/4, height=407/4)




    def add_final_info_page():
        story.append(logo)
        story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

        current_date = datetime.now().strftime("%Y-%m-%d")
        
        
        info_text = f"""
        This report was generated by <b>Spotplotter</b> version <b>1.0</b> on <b>{current_date}</b>

        Spotplotter was created by <b>Holly Lewis</b> with supervision from <b>R Verrinder</b> and <b>Dr. M Mason</b> as BSc (Eng) final year project submitted in partial fulfilment of the requirements for the degree of Bachelor of Science in Electrical and Computer Engineering in the Department of Electrical Engineering at the University of Cape Town.

        To read the full report please see: <i>GITHUB LINK</i>


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



    
    # Add plate info pages
    for plate_info in all_plate_info:
        add_info_page(plate_info, story, logo, title_style, body_style)
    
    def create_stats_table(stats_subset):
            """Create a statistics table for a subset of stats (max 4 entries)"""
            # Define fixed column widths (in points)
            col_widths = [1.2*inch]  # First column (row labels)
            col_widths.extend([1.5*inch] * len(stats_subset))  # Data columns
            
            table_data = [[''] + [stat['label'] for stat in stats_subset]]
            for row_label in ['Formula', 'Slope', 'Intercept', 'R-squared', 'y-cut', 'x-cut', 'x_at_y50']:
                row = [row_label]
                for stat in stats_subset:
                    if row_label == 'Formula':
                        value = stat['formula']
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
                # Add word wrapping
                ('WORDWRAP', (0, 0), (-1, -1), True),
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
            # Add logo before each graph
            story.append(logo)
            
            # Add figure
            img_data = BytesIO()
            fig.savefig(img_data, format='png', dpi=150, bbox_inches='tight')
            img_data.seek(0)

            # Calculate aspect ratio
            with Image.open(img_data) as img:
                width, height = img.size
                aspect_ratio = width / height

            # Desired width while maintaining aspect ratio
            desired_width = 7 * inch
            desired_height = desired_width / aspect_ratio

            # Reset img_data pointer
            img_data.seek(0)

            # Add image to the story
            story.append(ImageR(img_data, width=desired_width, height=desired_height))
            story.append(Spacer(1, 20))
            
            # Split stats into groups of 4 and create multiple tables if needed
            for i in range(0, len(stats), 4):
                stats_subset = stats[i:i+4]
                table = create_stats_table(stats_subset)
                story.append(table)
                story.append(Spacer(1, 10))

            
            # Add page break after each strain except the last one
            if strain_name != all_strain_data[-1][0]:
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
    logo_path = relative_to_assets("LogoHorizontalDark.png")
    logo = ImageR(logo_path, width=1170/4, height=407/4)

    def add_final_info_page():
        story.append(logo)
        story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

        current_date = datetime.now().strftime("%Y-%m-%d")
        
        
        info_text = f"""
        This report was generated by <b>Spotplotter</b> version <b>1.0</b> on <b>{current_date}</b>

        Spotplotter was created by <b>Holly Lewis</b> with supervision from <b>R Verrinder</b> and <b>Dr. M Mason</b> as BSc (Eng) final year project submitted in partial fulfilment of the requirements for the degree of Bachelor of Science in Electrical and Computer Engineering in the Department of Electrical Engineering at the University of Cape Town.

        To read the full report please see: <i>GITHUB LINK</i>
        """

        for paragraph in info_text.split('\n\n'):
            story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 6))
    add_final_info_page()
    story.append(PageBreak())
    
    def save_figure_for_pdf(fig, width=7.5*inch, height=3*inch):
        """Save matplotlib figure to bytes buffer and return as ReportLab image"""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        return ImageR(buf, width=width, height=height)
    
    
        # Add logo
    logo_path = relative_to_assets("LogoHorizontalDark.png")
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
    story.append(PageBreak())


    # Add final info page

    
    # Build the PDF with footer
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)


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




















