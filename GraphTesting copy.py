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
def plot_logarithmic_graph(y1, title, key1):
    dilutionSeries = [1, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
    normValue = (y1[0])
    y_data = [normalize_array(y, normValue) for y in [y1]]
    
    colors = ['#073B3A', '#0F8660', '#D3784A', '#D24C4A']
    markers = ['o', 's', '^', 'D']
    
    
    plt.figure(figsize=(12, 8))
    sns.set_context("notebook", font_scale=1.2)
    
    plt.xscale('log')
    ax = plt.gca()
    ax.set_facecolor('#F5F5F5')
    
    statistics = []  # List to hold the statistics for each dataset

    stats = calculate_statistics(dilutionSeries, y_data[0], '#073B3A', key1)
    if stats is not None:
        statistics.append(stats)
        label = "Strain 3"
        sns.scatterplot(x=dilutionSeries, y=y_data[0], color= '#073B3A', marker='o', label=label, s=80)
        
        x_fit = np.logspace(np.log10(min(dilutionSeries)), np.log10(max(dilutionSeries)), num=100)
        y_fit = stats['slope'] * np.log10(x_fit) + stats['intercept']
        plt.plot(x_fit, y_fit, color='#073B3A', linestyle='--', label=("R² =" + str(round(stats['r_squared'], 3)) + "\n" + stats['formula'] + "\n"))

    plt.title(f"Growth Curve for {title}", fontsize=20, fontweight='bold', pad=20)
    plt.ylim(0, 120)
    plt.xlabel('Dilution Series', fontsize=16, fontweight='bold')
    plt.ylabel('Relative Growth (%)', fontsize=16, fontweight='bold')

    # Increase fontsize for the legend
    plt.legend(fontsize=14, loc='upper right', bbox_to_anchor=(0.98, 0.98),
               ncol=1, frameon=True, facecolor='white', edgecolor='none', framealpha=0.7)

    plt.tick_params(axis='both', which='major', labelsize=14)
    
    plt.tight_layout()

    plt.show()
    # Return the figure and the collected statistics
    return plt.gcf(), statistics

# dilutionSeries = [1, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
# y1 = [32104, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0]
# y2= [35381, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0]
# y3= [18909, 16152, 13604, 12738, 12577, 8611, 14617, 6462, 3661, 1967, 3733, 990, 1650, 590, 662, 0, 203, 0, 161, 0, 0, 0, 0, 0, 0, 165, 0, 0, 0, 0, 0, 0]
# y4=[20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
y1 =[50616, 37339, 30041, 27021, 16966, 14982, 19105, 12030, 17760, 15553, 17760, 8717, 0, 15382, 12191, 4635, 6970, 8798, 0, 4020, 6, 738, 0, 508, 0, 1228, 419, 0, 0, 0, 1111, 649]
y1Attempt2 = [39509, 35242, 25733, 25601, 16599, 14848, 18275, 11938, 16896, 15405, 17606, 8469, 4553, 15167, 10841, 4228, 6048, 8361, 0, 6497, 3, 895, 3173, 456, 0, 1145, 5, 1, 1, 1, 3, 0]
plt , _ = plot_logarithmic_graph(
    y1Attempt2,
    "Cracked Plate",
    "Strain3"
)



y1= [34836, 19115, 18236, 17047, 17213, 9879, 19880, 9501, 10821, 11041, 9224, 9191, 1982, 4877, 8236, 3349, 7730, 3062, 989, 758, 9, 4668, 2812, 1315, 0, 1064, 405, 0, 507, 0, 0, 0]

y2= [25866, 27395, 7657, 16971, 4872, 3206, 10361, 6266, 4289, 2888, 8605, 2004, 0, 2367, 2000, 3302, 0, 0, 0, 0, 0, 0, 519, 0, 0, 0, 0, 0, 0, 623, 0, 0]
