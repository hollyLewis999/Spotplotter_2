import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import string
from matplotlib.patches import Patch

# Define constants
FONT = "Microsoft New Tai Lue"
FOREGROUND_COLOR = '#80AEB8'
CONTROL_COLOR = '#DFE6E8'
FACE_COLOR = '#F5F5F5'
TEXT_COLOR = 'black'
ALPHA = 1
def generate_plate_labels(rows, cols):

    col_labels = list(string.ascii_uppercase[:cols])
    return [f"{col}{row+1}" for row in range(rows) for col in col_labels]



def analyze_plate_data(all_plate_info):
    """
    Analyze plate data showing averaged bars with individual data points:
    - Bar height represents average quantification
    - Individual points shown for each measurement
    - Ordered by position (A1, A2, etc.)
    
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
    
    # Get all control and treatment quantifications
    control_quants_list = [plate['unorderedquantifications'].flatten() 
                          for plate in control_plates]
    treatment_quants_list = [plate['unorderedquantifications'].flatten() 
                            for plate in treatment_plates]
    
    # Convert to arrays for easier manipulation
    control_quants_array = np.array(control_quants_list)
    treatment_quants_array = np.array(treatment_quants_list)
    
    # Calculate averages
    control_means = np.mean(control_quants_array, axis=0)
    treatment_means = np.mean(treatment_quants_array, axis=0)
    
    # Generate labels based on first plate shape
    rows, cols = control_plates[0]['unorderedquantifications'].shape
    labels = generate_plate_labels(rows, cols)
    
    # Prepare DataFrame
    df = pd.DataFrame({
        'Position': labels,
        'Control Mean': control_means,
        'Treatment Mean': treatment_means
    })
    
    # Calculate knockdown using means
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
    
    # Remove only pairs where both values are zero
    df = df[df['Category'] != 'both_zero']
    
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
    
    # For each position, plot bars and individual points
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
        
        # Plot individual points for controls
        for control_values in control_quants_list:
            ax.scatter(i, control_values[i], color=CONTROL_COLOR, 
                      edgecolor='black', linewidth=1, s=30, zorder=3)
        
        # Plot individual points for treatments
        for treatment_values in treatment_quants_list:
            ax.scatter(i, treatment_values[i], color=FOREGROUND_COLOR,
                      edgecolor='black', linewidth=1, s=30, zorder=3)
    
    # Create legend
    legend_elements = [
        Patch(facecolor=CONTROL_COLOR, alpha=ALPHA, edgecolor='black', 
              label=f'Control Mean (No additive)', linewidth=1),
        Patch(facecolor=FOREGROUND_COLOR, alpha=ALPHA, edgecolor='black', 
              label=f'Treatment Mean ({treatment_plates[0]["additive"]})', linewidth=1),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=CONTROL_COLOR,
                  markeredgecolor='black', label='Individual Control Values', 
                  markersize=8, markeredgewidth=1),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=FOREGROUND_COLOR,
                  markeredgecolor='black', label='Individual Treatment Values', 
                  markersize=8, markeredgewidth=1)
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
        max_height = max(row['Control Mean'], row['Treatment Mean'])
        label_text = f"{row['Knockdown']:.2f}" if not np.isnan(row['Knockdown']) else "NA"
        plt.text(i, max_height+5, label_text,
                 horizontalalignment='center', 
                 verticalalignment='bottom',
                 color=TEXT_COLOR,
                 fontsize=6,
                 fontweight='bold')
    
    # Set labels and title
    strain_name = control_plates[0].get('strain', 'Unknown Strain')
    additive_name = treatment_plates[0].get('additive', 'Unknown Additive')
    
    plt.title(f'Knockdown for {strain_name} with additive {additive_name}',
             color=TEXT_COLOR,
             pad=20,
             fontsize=12,
             fontweight='bold')
    
    # Set x-axis labels to positions
    plt.xticks(range(len(df)), df['Position'])
    
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