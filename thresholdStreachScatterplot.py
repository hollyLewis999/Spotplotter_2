import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import seaborn as sns

# Set the style
FONT = "Microsoft New Tai Lue"
plt.rcParams['font.family'] = FONT
sns.set_style("whitegrid")

# Data
stretch_range = [117, 100, 99, 114, 117, 115, 110, 116, 175, 73, 84, 56, 57, 73, 80, 107, 75, 76, 114, 53, 61, 50, 60]
ideal_threshold = [12, 11, 18, 15, 10, 15, 14, 11, 10, 21, 15, 23, 21, 16, 17, 11, 12, 18, 7, 18, 17, 23, 26]

# Separate the outlier point (175, 10)
x_without_outlier = [x for x in stretch_range if x != 175]
y_without_outlier = [y for x, y in zip(stretch_range, ideal_threshold) if x != 175]

# Calculate linear regression (excluding the outlier)
slope, intercept, r_value, p_value, std_err = stats.linregress(x_without_outlier, y_without_outlier)
r_squared = r_value ** 2

# Create the plot
plt.figure(figsize=(12, 8))
sns.set_context("notebook", font_scale=1.2)

# Set background color
ax = plt.gca()
ax.set_facecolor('#F5F5F5')

# Plot all points including outlier
sns.scatterplot(x=stretch_range, y=ideal_threshold, color='#073B3A', marker='o', s=80)

# Plot regression line
x_fit = np.linspace(min(stretch_range), max(stretch_range), 100)
y_fit = slope * x_fit + intercept
plt.plot(x_fit, y_fit, color='#0F8660', linestyle='--', 
         label=f'Linear Regression\nR² = {r_squared:.3f}\ny = {slope:.2f}x + {intercept:.2f}')

# Customize the plot
plt.title('Stretch Range vs Approximate Ideal Threshold', fontsize=20, fontweight='bold', pad=20)
plt.xlabel('Stretch Range', fontsize=16, fontweight='bold')
plt.ylabel('Approximate Ideal Threshold', fontsize=16, fontweight='bold')

# Customize legend
plt.legend(fontsize=14, loc='upper right', bbox_to_anchor=(0.98, 0.98),
          ncol=1, frameon=True, facecolor='white', edgecolor='none', framealpha=0.7  )

# Customize tick labels
plt.tick_params(axis='both', which='major', labelsize=14)

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()