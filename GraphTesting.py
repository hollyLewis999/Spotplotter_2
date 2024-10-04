import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
FONT = "Microsoft New Tai Lue"
plt.rcParams['font.family'] = FONT




def normalize_array(arr, nomValue):
    for i in range(len(arr)):
        arr[i] = 100 * arr[i] / nomValue
  
    return arr

def calculate_statistics(x, y, color, label):
    valid_x = []
    valid_y = []
    for xi, yi in zip(x, y):
        if xi >0 and yi > 5:
            valid_x.append(np.log10(xi))
            valid_y.append(yi)
        # else:
        #     print("invalid", yi)
    if len(valid_x) > 1:
        slope, intercept, r_value, p_value, std_err = stats.linregress(valid_x, valid_y)
        r_squared = r_value ** 2
        m, b = np.polyfit(valid_x, valid_y, 1)
        y_cut = b
        x_cut = 10 ** (-b / m)
        x_at_y50 = 10 ** ((50 - b) / m)
        formula = f"y = {m:.2f} * log10(x) + {b:.2f}"
        print(f"\nStatistics for {label} (color: {color}):")
        print(f"Line formula: y = {m:.2f} * log10(x) + {b:.2f}")
        print(f"Y-intercept (y-cut): {y_cut:.2f}")
        print(f"X-intercept (x-cut): {x_cut:.2f}")
        print(f"X value when y = 50: {x_at_y50:.2f}")
        print(f"Slope (from linregress): {slope:.4f}")
        print(f"Intercept (from linregress): {intercept:.4f}")
        print(f"R-squared: {r_squared:.4f}")
        print(f"P-value: {p_value:.4e}")
        print(f"Standard error: {std_err:.4f}")
        
        return m, b, r_squared, formula
    return None, None

def plot_logarithmic_graph(y1, y2, y3, y4, title, key1, key2, key3, key4):
    dilutionSeries = [1, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
    normValue = (y1[0] +y2[0])/2
    print(normValue)
    print(y1)
    y_data = [normalize_array(y, normValue) for y in [y1, y2, y3, y4]]
    # y_data =  [y1, y2, y3, y4]
    colors = ['red', 'yellow', 'blue', 'green']
    markers = ['s', 'o', '^', '*']
    labels = [key1, key2, key3, key4]

    plt.figure(figsize=(12, 8))
    plt.xscale('log')
    
    for y, color, marker, label in zip(y_data, colors, markers, labels):
        print(y)
        m, b, r_squared, formula = calculate_statistics(dilutionSeries, y, color, label)
        label = label + " (R² =" + str(round(r_squared, 3)) + ")"
        plt.scatter(dilutionSeries, y, color=color, marker=marker, label=label)
        x_fit = np.logspace(np.log10(min(dilutionSeries)), np.log10(max(dilutionSeries)), num=100)
        y_fit = m * np.log10(x_fit) + b
        plt.plot(x_fit, y_fit, color=color, linestyle='--', label = formula)

    plt.title(title, fontsize=16, fontweight='bold')
    plt.ylim(0, 120)
    plt.xlabel('Dilution Series', fontsize=14,fontweight='bold')
    plt.ylabel('Relative Growth', fontsize=14, fontweight='bold')
    plt.legend(fontsize=12)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tick_params(axis='both', which='major', labelsize=12)

    plt.show()


dilutionSeries = [1, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
y1 = [32104, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0]
y2= [35381, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0]
y3= [18909, 16152, 13604, 12738, 12577, 8611, 14617, 6462, 3661, 1967, 3733, 990, 1650, 590, 662, 0, 203, 0, 161, 0, 0, 0, 0, 0, 0, 165, 0, 0, 0, 0, 0, 0]
y4=[20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
plot_logarithmic_graph(
    y1, y2, y3, y4,
    "StrainNAME",
    "P4272701", "P4272705", "P4272703", "P4272707"
)