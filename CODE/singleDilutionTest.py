import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import string
from matplotlib.patches import Patch

# Define constants
FONT = "Microsoft New Tai Lue"
FOREGROUND_COLOR = '#46A2A2'
CONTROL_COLOR = 'gray'
FACE_COLOR = '#F5F5F5'
TEXT_COLOR = 'black'

def generate_plate_labels(rows, cols):

    col_labels = list(string.ascii_uppercase[:cols])
    return [f"{col}{row+1}" for row in range(rows) for col in col_labels]


def analyze_plate_data(all_plate_info):
    """
    Analyze plate data from window.all_plate_info
    
    Parameters:
    all_plate_info (list): List of plate information dictionaries
    
    Returns:
    pandas.DataFrame: Processed plate data
    matplotlib.figure.Figure: Visualization of quantifications
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
    
    # Get first control and treatment plate
    control_plate = control_plates[0]
    treatment_plate = treatment_plates[0]
    
    # Get quantifications
    control_quants = control_plate['unorderedquantifications']
    treatment_quants = treatment_plate['unorderedquantifications']
    
    # Generate labels
    rows, cols = treatment_quants.shape
    labels = generate_plate_labels(rows, cols)
    
    # Flatten arrays
    control_values = control_quants.flatten()
    treatment_values = treatment_quants.flatten()
    
    # Prepare DataFrame
    df = pd.DataFrame({
        'Position': labels,
        'Control Value': control_values,
        'Treatment Value': treatment_values
    })
    
    # Calculate knockdown (treatment/control), setting to NA for zero cases
    df['Knockdown'] = np.where(
        (df['Control Value'] == 0) | (df['Treatment Value'] == 0),
        np.nan,
        df['Treatment Value'] / df['Control Value']
    )
    
    # Create categorical column for sorting
    df['Category'] = 'both_nonzero'
    df.loc[df['Treatment Value'] == 0, 'Category'] = 'treatment_zero'
    df.loc[df['Control Value'] == 0, 'Category'] = 'control_zero'
    df.loc[(df['Control Value'] == 0) & (df['Treatment Value'] == 0), 'Category'] = 'both_zero'
    
    # Remove only pairs where both values are zero
    df = df[df['Category'] != 'both_zero']
    
    # Sort the DataFrame:
    # 1. Treatment zeros first (sorted by control value, descending)
    # 2. Non-zero pairs (sorted by knockdown, descending)
    # 3. Control zeros last (sorted by treatment value, descending)
    df_treatment_zeros = df[df['Category'] == 'treatment_zero'].sort_values('Control Value', ascending=False)
    df_nonzeros = df[df['Category'] == 'both_nonzero'].sort_values('Knockdown', ascending=False)
    df_control_zeros = df[df['Category'] == 'control_zero'].sort_values('Treatment Value', ascending=False)
    
    # Concatenate the sorted sections
    df = pd.concat([df_treatment_zeros, df_nonzeros, df_control_zeros])
    
    # Reset index for plotting
    df = df.reset_index(drop=True)
    
    # Set the style
    plt.style.use('default')
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor(FACE_COLOR)
    
    # Create bar plots with black edges
    # Control bars
    sns.barplot(x='Position', y='Control Value', data=df, 
                color=CONTROL_COLOR, alpha=0.5, 
                ax=ax,
                edgecolor='black', 
                linewidth=1)
    
    # Treatment bars
    sns.barplot(x='Position', y='Treatment Value', data=df, 
                color=FOREGROUND_COLOR, alpha=0.7, 
                ax=ax,
                edgecolor='black', 
                linewidth=1)
    
    # Create legend
    legend_elements = [
        Patch(facecolor=CONTROL_COLOR, alpha=0.5, edgecolor='black', 
              label=f'Control (No additive)', linewidth=1),
        Patch(facecolor=FOREGROUND_COLOR, alpha=0.7, edgecolor='black', 
              label=f'Treatment ({treatment_plate["additive"]})', linewidth=1)
    ]
    ax.legend(handles=legend_elements, loc='upper right', 
             fontsize=8, frameon=True, facecolor='white')
    
    # Style the plot
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    
    # Add horizontal marking lines only (solid)
    ax.yaxis.grid(True, linestyle='-', alpha=0.7, color='gray')
    ax.xaxis.grid(False)
    
    # Ensure grid is behind the bars
    ax.set_axisbelow(True)
    
    # Style spines
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(1.5)
    
    # Add knockdown labels at the top of the highest bar
    for i, row in df.iterrows():
        max_height = max(row['Control Value'], row['Treatment Value'])
        label_text = f"{row['Knockdown']:.2f}" if not np.isnan(row['Knockdown']) else "NA"
        plt.text(i, max_height, label_text,
                 horizontalalignment='center', 
                 verticalalignment='bottom',
                 color=TEXT_COLOR,
                 fontsize=8,
                 fontweight='bold')
    
    # Set labels and title
    strain_name = control_plate.get('strain', 'Unknown Strain')
    additive_name = treatment_plate.get('additive', 'Unknown Additive')
    
    plt.title(f'Knockdown for {strain_name} with additive {additive_name}',
             color=TEXT_COLOR,
             pad=20,
             fontsize=12,
             fontweight='bold')
    
    plt.xlabel('Position', 
              color=TEXT_COLOR,
              fontsize=10,
              fontweight='bold')
    
    plt.ylabel('Quantification Value',
              color=TEXT_COLOR,
              fontsize=10,
              fontweight='bold')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Adjust layout
    plt.tight_layout()
    
    return df, fig

# Example usage
# df, fig = analyze_plate_data(all_plate_info)
# plt.show()


def plot_knockdown(df):
    """
    Create a plot showing knockdown values, excluding positions with NA values.
    
    Parameters:
    df (pandas.DataFrame): Processed plate data containing knockdown values
    
    Returns:
    matplotlib.figure.Figure: Visualization of knockdown values
    """
    # Filter out NA knockdown values
    df_filtered = df.dropna(subset=['Knockdown']).copy()
    
    # Sort by knockdown value for better visualization
    df_filtered = df_filtered.sort_values('Knockdown', ascending=False)
    
    # Set the style
    plt.style.use('default')
    plt.rcParams['font.family'] = "Microsoft New Tai Lue"
    plt.rcParams['font.weight'] = 'bold'
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#F5F5F5')
    
    # Create bar plot for knockdown values
    bars = sns.barplot(x='Position', y='Knockdown', data=df_filtered, 
                      color='#46A2A2', alpha=0.7,
                      ax=ax,
                      edgecolor='black',
                      linewidth=1)
    
    # Add value labels on top of bars
    for i, row in df_filtered.iterrows():
        plt.text(df_filtered.index.get_loc(i), row['Knockdown'],
                f"{row['Knockdown']:.2f}",
                horizontalalignment='center',
                verticalalignment='bottom',
                color='black',
                fontsize=8,
                fontweight='bold')
    
    # Add horizontal marking lines (solid)
    ax.yaxis.grid(True, linestyle='-', alpha=0.7, color='gray')
    ax.xaxis.grid(False)
    
    # Ensure grid is behind the bars
    ax.set_axisbelow(True)
    
    # Style spines
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(1.5)
    
    # Add a horizontal line at y=1 to show baseline
    ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, linewidth=1)
    
    # Set labels and title
    plt.title('Knockdown Values by Position (Excluding Zero Values)',
             color='black',
             pad=20,
             fontsize=12,
             fontweight='bold')
    
    plt.xlabel('Position',
              color='black',
              fontsize=10,
              fontweight='bold')
    
    plt.ylabel('Knockdown (Treatment/Control)',
              color='black',
              fontsize=10,
              fontweight='bold')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Add count information to title
    excluded_count = len(df) - len(df_filtered)
    plt.title(f'Knockdown Values by Position\n{len(df_filtered)} positions shown ({excluded_count} positions with zero values excluded)',
             color='black',
             pad=20,
             fontsize=12,
             fontweight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

# Example usage:
# knockdown_fig = plot_knockdown(df)
# plt.show()

# Example usage:
# knockdown_fig = plot_knockdown(df)
# plt.show()