import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.font_manager as fm
import matplotlib as mpl
import seaborn as sns
DARK = "#343a40"
LIGHT = "#e9ecef"
ACCENT = "#4169E1"
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image

FONT = "Microsoft New Tai Lue"
FONT_SIZE = 14  # Increased font size
TITLE_SIZE = 18  # Larger size for titles


def create_rgb_histogram_with_image(image_path):
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = FONT_SIZE
    sns.set_style("whitegrid")
   
    # Open the image
    img = Image.open(image_path)
   
    # Convert image to numpy array
    img_array = np.array(img)
   
    # Get the middle row of pixels
    middle_row = img_array[img_array.shape[0] // 2, :, :]
   
    # Create figure with 2 subplots (top plot and bottom plot)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7),
                                   gridspec_kw={'height_ratios': [1.8, 0.4]},
                                   sharex=True)
   
    # Plot RGB values of the middle row
    ax1.plot(middle_row[:, 0], color='red', alpha=0.7)
    ax1.plot(middle_row[:, 1], color='green', alpha=0.7)
    ax1.plot(middle_row[:, 2], color='blue', alpha=0.7)
   
    ax1.set_title('RGB Values of Middle Row (indicated with dotted yellow line)', fontsize=TITLE_SIZE, fontweight='bold')
    ax1.set_ylabel('RGB Value', fontsize=FONT_SIZE, fontweight='bold')
    ax1.set_ylim(0, 300)
    ax1.set_facecolor('#F5F5F5')  # very light grey
   
    # Add labels directly to ax1 using `annotate` or `text`
    ax1.text(120, -10, 'F', fontsize=25, fontweight='bold', ha='center', va='top')
    ax1.text(150, -10, 'G', fontsize=25, fontweight='bold', ha='center', va='top')
    ax1.text(370, -10, 'H', fontsize=25, fontweight='bold', ha='center', va='top')
    ax1.text(400, -10, 'I', fontsize=25, fontweight='bold', ha='center', va='top')
   
    # ax1.text(120, -10, 'A', fontsize=25, fontweight='bold', ha='center', va='top')
    # ax1.text(150, -10, 'B', fontsize=25, fontweight='bold', ha='center', va='top')
    # ax1.text(370, -10, 'C', fontsize=25, fontweight='bold', ha='center', va='top')
    # ax1.text(430, -10, 'D', fontsize=25, fontweight='bold', ha='center', va='top')
    # ax1.text(680, -10, 'E', fontsize=25, fontweight='bold', ha='center', va='top')
    # Display the image
    ax2.imshow(img)
    ax2.set_ylabel('Image', fontsize=FONT_SIZE, fontweight='bold')
    ax2.set_xlabel('Column Index', fontsize=FONT_SIZE, fontweight='bold')
   
    # Remove y-axis ticks from the image
    ax2.set_yticks([])
   
    # Add a horizontal line to show which row is being analyzed
    ax2.axhline(y=img_array.shape[0] // 2, color='yellow', linestyle='--', linewidth=1)
   
    # Adjust spacing between subplots
    plt.subplots_adjust(hspace=-0.4)  # Smaller value for closer plots

    plt.tight_layout()
    plt.show()

image_path = "C:/Users/ThinkPad/Downloads/streachedColorscropped2.png"
create_rgb_histogram_with_image(image_path)
