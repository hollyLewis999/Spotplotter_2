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
            custom_label = f"{series['label']}\n R² = {stats['r_squared']:.3f}\n{stats['formula']}"
            
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
                custom_label_avg = f"{additive}\nR² = {stats['r_squared']:.3f}\n{stats['formula']}"
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


# def calculate_statistics(x, y, color, label, additive):
#     valid_x = []
#     valid_y = []
#     excluded_points = []
    

    
#     # Track points excluded from calculations
#     for xi, yi in zip(x, y):
#         if xi > 0 and yi > 10:
#             # Convert to log 10 because of the dilution sequence
#             valid_x.append(np.log10(xi))
#             valid_y.append(yi)

    

#     if len(valid_x) > 1:
#         # Getting statistics for filtered data
#         slope, intercept, r_value, p_value, std_err = stats.linregress(valid_x, valid_y)
#         r_squared = r_value ** 2
#         m, b = np.polyfit(valid_x, valid_y, 1)
#         y_cut = b
#         x_cut = 10 ** (-b / m)
#         x_at_y50 = 10 ** ((50 - b) / m)
#         formula = f"y = {m:.2f} * log10(x) + {b:.2f}"
    
    
#         # Return as a dictionary since it's nice to call values from
#         return {
#             'slope': m,
#             'intercept': b,
#             'r_squared': r_squared,
#             'formula': formula,
#             'y_cut': y_cut,
#             'x_cut': x_cut,
#             'x_at_y50': x_at_y50,
#             'label': label,
#             'additive':additive,
#             'color': color,  # Add the color to the statistics dictionary
#             'full_line_formula': formula # Include full line formula
#         }
    
#     return None

#  d888b  d8888b.  .d8b.  d8888b. db   db .d8888.       .d8888b.
# 88' Y8b 88  `8D d8' `8b 88  `8D 88   88 88'  YP       88   `8D 
# 88      88oobY' 88ooo88 88oodD' 88ooo88 `8bo.         88ooooY'
# 88  ooo 88`8b   88~~~88 88~~~   88~~~88   `Y8b.       88~~~~b.
# 88. ~8~ 88 `88. 88   88 88      88   88 db   8D       88    8D
#  Y888P  88   YD YP   YP 88      YP   YP `8888Y'       Y88888P'




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
                    if i > 0 and i % 2 == 0:
                        story.append(PageBreak())
                        i = 0
                    table = create_stats_table(stats_subset)
                    story.append(table)
                    story.append(Spacer(1, 10))
                    i += 1

            # Add page break after each strain except the last one
            story.append(PageBreak())
        
    
    # Build the PDF with footer
    story.append(add_final_info_page())
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)






















