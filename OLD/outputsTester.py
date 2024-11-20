import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as scipy_stats

# Color definitions
GREENCOLOURS = ["#073B3A", "#0B614D", "#0F8660", "#7DB46F"]
REDCOLOURS = ["#D24C4A", "#D3784A", "#DFA24F", "#EBCB53"]
BLUECOLOURS = ["#0C546B", "#0F7D87", "#46A2A2", "#7CC7BC"]
PURPLESCOLOURS = ["#591C5F", "#81377E", "#A9599C", "#D07BB9"]

def normalize_array(values, norm_value):
    """Normalize array values relative to a normalization value"""
    return [100 * v / norm_value for v in values]

def calculate_statistics(x_values, y_values, label, log_base):
    """Calculate regression statistics for the data series"""
    valid_points = [(x, y) for x, y in zip(x_values, y_values) if x > 0 and y > 0]
    if len(valid_points) < 2:
        return None
        
    x_vals, y_vals = zip(*valid_points)
    log_x = np.log(x_vals) / np.log(log_base)
    
    slope, intercept, r_value, _, _ = scipy_stats.linregress(log_x, y_vals)
    r_squared = r_value ** 2
    
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
    """
    Plot two graphs: individual series and averaged comparisons for multiple additives
    Parameters:
    - data_series: list of dictionaries containing:
        - y_values: list of measurements
        - additive: string ('none', 'ATC', or other additives)
        - label: string (series label)
        - marker: optional marker style
    - dilution_series: list of x-axis values
    - title: string
    - log_base: logarithm base for x-axis
    """
    # Find normalization value from 'none' additive series
    none_series = [series['y_values'][0] for series in data_series 
                  if series['additive'].lower() == 'none']
    if not none_series:
        raise ValueError("Must have at least one series with additive='none' for normalization")
    norm_value = sum(none_series) / len(none_series)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 8))
    sns.set_context("notebook", font_scale=1.2)
    
    # Set log scale and style
    for ax in [ax1, ax2]:
        ax.set_xscale('log', base=log_base)
        ax.set_facecolor('#F5F5F5')
    
    # Get unique additives and assign colors
    additives = sorted(set(series['additive'] for series in data_series))
    color_map = {}
    for additive in additives:
        if additive.lower() == 'none':
            color_map[additive] = BLUECOLOURS
        elif additive.lower() == 'atc':
            color_map[additive] = GREENCOLOURS
        elif len(color_map) % 2 == 0:
            color_map[additive] = REDCOLOURS
        else:
            color_map[additive] = PURPLESCOLOURS
    
    # Initialize data collection for averaging
    averaged_data = {additive: {x: [] for x in dilution_series} for additive in additives}
    
    # Plot individual series and collect data for averaging
    series_statistics = []
    additive_counts = {additive: 0 for additive in additives}
    default_markers = ['o', 's', '^', 'D']
    
    for idx, series in enumerate(data_series):
        y_norm = normalize_array(series['y_values'], norm_value)
        additive = series['additive']
        
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
        ax.set_ylim(0, 120)
        ax.set_xlabel('Dilution Series', fontsize=16, fontweight='bold')
        ax.set_ylabel('Relative Growth (%)', fontsize=16, fontweight='bold')
        ax.legend(fontsize=14, loc='upper right', bbox_to_anchor=(0.98, 0.98),
                 ncol=1, frameon=True, facecolor='white', edgecolor='none',
                 framealpha=0.7)
        ax.tick_params(axis='both', which='major', labelsize=14)
    
    ax1.set_title(f"Individual Growth Curves for {title}",
                 fontsize=20, fontweight='bold', pad=20)
    ax2.set_title(f"Average Growth Curves for {title}",
                 fontsize=20, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.show()
    
    return fig, series_statistics

# Example data
dilution_series = [0.001, 0.01, 0.1, 1, 10, 100]

data_series = [
    # Control series (no additive)
    {
        'y_values': [100, 90, 80, 70, 60, 50],
        'additive': 'none',
        'label': 'Control 1'
    },
    {
        'y_values': [98, 88, 78, 68, 58, 48],
        'additive': 'none',
        'label': 'Control 2'
    },
    # ATC series
    {
        'y_values': [95, 80, 65, 50, 35, 20],
        'additive': 'ATC',
        'label': 'ATC 1'
    },
    {
        'y_values': [93, 78, 63, 48, 33, 18],
        'additive': 'ATC',
        'label': 'ATC 2'
    },
    # Alternative additive series
    {
        'y_values': [97, 85, 70, 55, 40, 25],
        'additive': 'Drug X',
        'label': 'Drug X 1'
    },
    {
        'y_values': [96, 84, 69, 54, 39, 24],
        'additive': 'Drug X',
        'label': 'Drug X 2'
    }
]

# Example usage
fig, stats = plot_multiadditive_graph(data_series, dilution_series, "Multiple Additives Test")