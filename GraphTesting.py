import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import seaborn as sns

FONT = "Microsoft New Tai Lue"
plt.rcParams['font.family'] = FONT

sns.set_style("whitegrid")

def normalize_array(arr, nomValue):
    return [100 * val / nomValue for val in arr]

def calculate_statistics(x, y, color, label):
    valid_x = []
    valid_y = []
    for xi, yi in zip(x, y):
        if xi > 0 and yi > 5:
            valid_x.append(np.log10(xi))
            valid_y.append(yi)
    
    if len(valid_x) > 1:
        slope, intercept, r_value, p_value, std_err = stats.linregress(valid_x, valid_y)
        r_squared = r_value ** 2
        m, b = np.polyfit(valid_x, valid_y, 1)
        y_cut = b
        x_cut = 10 ** (-b / m)
        x_at_y50 = 10 ** ((50 - b) / m)
        formula = f"y = {m:.2f} * log10(x) + {b:.2f}"
        
        return {
            'slope': m,
            'intercept': b,
            'r_squared': r_squared,
            'formula': formula,
            'y_cut': y_cut,
            'x_cut': x_cut,
            'x_at_y50': x_at_y50,
            'label': label
        }
    
    return None

def plot_logarithmic_graph(y1, y2, y3, y4, title, key1, key2, key3, key4):
    dilutionSeries = [1, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
    normValue = (y1[0] + y2[0]) / 2
    y_data = [normalize_array(y, normValue) for y in [y1, y2, y3, y4]]
    
    colors = ['#073B3A', '#0F8660', '#D3784A', '#D24C4A']
    markers = ['o', 's', '^', 'D']
    labels = [key1, key2, key3, key4]
    
    plt.figure(figsize=(12, 8))
    sns.set_context("notebook", font_scale=1.2)
    
    plt.xscale('log')
    ax = plt.gca()
    ax.set_facecolor('#F5F5F5')
    ATcs = "-ATc", "-ATc", "+ATc", "+ATc"
    
    statistics = []  # List to hold the statistics for each dataset

    for y, color, marker, label, ATc in zip(y_data, colors, markers, labels, ATcs):
        stats = calculate_statistics(dilutionSeries, y, color, label)
        if stats is not None:
            statistics.append(stats)
            label = ATc + " (" + label + " )"
            sns.scatterplot(x=dilutionSeries, y=y, color=color, marker=marker, label=label, s=80)
            
            x_fit = np.logspace(np.log10(min(dilutionSeries)), np.log10(max(dilutionSeries)), num=100)
            y_fit = stats['slope'] * np.log10(x_fit) + stats['intercept']
            plt.plot(x_fit, y_fit, color=color, linestyle='--', label=("R² =" + str(round(stats['r_squared'], 3)) + "\n" + stats['formula'] + "\n"))
    
    plt.title(title, fontsize=20, fontweight='bold', pad=20)
    plt.ylim(0, 120)
    plt.xlabel('Dilution Series', fontsize=16, fontweight='bold')
    plt.ylabel('Relative Growth (%)', fontsize=16, fontweight='bold')

    plt.legend(fontsize=10, loc='upper right', bbox_to_anchor=(0.98, 0.98),
               ncol=1, frameon=True, facecolor='white', edgecolor='none', framealpha=0.7)

    plt.tick_params(axis='both', which='major', labelsize=14)
    
    plt.tight_layout()
    
    # Return the figure and the collected statistics
    return plt.gcf(), statistics

# dilutionSeries = [1, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
# y1 = [32104, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0]
# y2= [35381, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0]
# y3= [18909, 16152, 13604, 12738, 12577, 8611, 14617, 6462, 3661, 1967, 3733, 990, 1650, 590, 662, 0, 203, 0, 161, 0, 0, 0, 0, 0, 0, 165, 0, 0, 0, 0, 0, 0]
# y4=[20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
# plot_logarithmic_graph(
#     y1, y2, y3, y4,
#     "StrainNAME",
#     "P4272701", "P4272705", "P4272703", "P4272707"
# )