import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set the style
FONT = "Microsoft New Tai Lue"
plt.rcParams['font.family'] = FONT
sns.set_style("whitegrid")

# Data
widths = [4800, 2400, 1200, 600, 300]
avg_values = [1364.3333, 1364.8333, 1365.0833, 1365.0312, 1361.1771]
upper_bounds = [1365, 1366, 1371, 1378, 1400]
lower_bounds = [1364, 1364, 1362, 1353, 1333]
real_values = [1364, 1364, 1364, 1364, 1364]

# Create the plot
plt.figure(figsize=(12, 8))
sns.set_context("notebook", font_scale=1.2)

# Set background color
ax = plt.gca()
ax.set_facecolor('#F5F5F5')

# Calculate error bars (ensuring positive values)
yerr_lower = []
yerr_upper = []
for avg, low, up in zip(avg_values, lower_bounds, upper_bounds):
    yerr_lower.append(abs(avg - low))
    yerr_upper.append(abs(up - avg))
yerr = [yerr_lower, yerr_upper]


plt.plot(widths, real_values, '--', color='#0F8660', linewidth=1.5,
         label='True Value')
# Plot points without label
plt.scatter(widths, avg_values, color='#073B3A', s=64, label='Average Value')

# Plot error bars with separate label
plt.errorbar(widths, avg_values, yerr=yerr, fmt='none', color='#073B3A',
             capsize=5, capthick=2, elinewidth=2,
             label='Range of Values')

# Add connecting line between points


# Customize the plot
plt.title('Image Width vs Average Value', fontsize=20, fontweight='bold', pad=20)
plt.xlabel('Width (pixels)', fontsize=16, fontweight='bold')
plt.ylabel('Average Value', fontsize=16, fontweight='bold')

# Customize legend
plt.legend(fontsize=14, loc='upper right', bbox_to_anchor=(0.98, 0.98),
          ncol=1, frameon=True, facecolor='white', edgecolor='none', framealpha=0.7)

# Customize tick labels
plt.tick_params(axis='both', which='major', labelsize=14)

# Add grid
plt.grid(True, which="both", ls="-", alpha=0.2)

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()