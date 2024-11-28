import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import string
from matplotlib.patches import Patch

# Define constants
FONT = "Microsoft New Tai Lue"
FOREGROUND_COLOR = '#073b3a'  # Darker blue for better visibility
CONTROL_COLOR = '#C1CEBE'     # Orange for better contrast
FACE_COLOR = '#F5F5F5'
TEXT_COLOR = 'black'
ALPHA = 0.8
LIGHT_ALPHA = 0.2 

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

import pandas as pd
import numpy as np

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

# Example usage:
# df = export_plate_data_to_excel(all_plate_info, 'plate_analysis.xlsx')    