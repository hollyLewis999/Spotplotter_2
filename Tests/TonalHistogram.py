# import numpy as np
# import matplotlib.pyplot as plt
# from PIL import Image
# import matplotlib.font_manager as fm
# import matplotlib as mpl

# DARK = "#343a40"
# LIGHT = "#e9ecef"
# ACCENT = "#4169E1"

# def calculate_luminance(img_array):
#     # Calculate luminance (perceived brightness)
#     # Using the formula: L = 0.299*R + 0.587*G + 0.114*B
#     return 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]

# def create_comparative_tonal_histogram(image_path1, image_path2):
#     # Set the font to Computer Modern Roman
#     # mpl.rcParams['text.usetex'] = False
#     # mpl.rcParams['font.family'] = 'serif'
#     # mpl.rcParams['font.serif'] = ['DejaVu Serif']
    
#     # Open the images
#     img1 = Image.open(image_path1)
#     img2 = Image.open(image_path2)
   
#     # Convert images to numpy arrays
#     img_array1 = np.array(img1)
#     img_array2 = np.array(img2)
   
#     # Calculate luminance for both images
#     luminance1 = calculate_luminance(img_array1)
#     luminance2 = calculate_luminance(img_array2)
   
#     # Create histogram
#     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios': [5, 1]})
   
#     # Plot histograms of luminance values
#     ax1.hist(luminance1.ravel(), bins=256, color=DARK, alpha=1, label='Tonal Value of Entire Plate')
#     ax1.hist(luminance2.ravel(), bins=256, color=LIGHT, alpha=1, label='Tonal Values of Center Region')
   
#     ax1.set_title('Comparative Histograms of Tonal Values of the Entire Image, vs the Region of Interest')
#     ax1.set_xlabel('Tonal Value')
#     ax1.set_ylabel('Frequency (Pixels)')
#     ax1.legend(prop={'weight':'normal'})
#     ax1.set_xlim([0, 255])

    
#     # Create a visual representation of tonal values
#     gradient = np.linspace(0, 1, 256).reshape(1, -1)
#     ax2.imshow(np.vstack((gradient,)), aspect='auto', cmap='gray')
#     ax2.set_yticks([])
#     ax2.set_xlabel('Tonal Value Representaion')
    
#     # Indicate the range 90-180
#     ax2.axvline(x=90, color=LIGHT, linestyle='--')
#     ax2.axvline(x=180, color=DARK, linestyle='--')
#     ax2.text(135, 0, '90-180', color=DARK, ha='center', va='center',
#              bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
    
#     plt.tight_layout()
#     plt.show()

# image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0.jpg"
# image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0C.jpg"

# # image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/tonalUnseen.jpg"
# # image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/MiddletonalUnseen.jpg"


# # image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Images for thesis/single Multi/og.png"
# # image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Images for thesis/single Multi/og.png"
# # image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/tonalUnseen.jpg"
# # image_path2 = "C:/Users/ThinkPad/Documents/hands.png"
# create_comparative_tonal_histogram(image_path1, image_path2)


import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.font_manager as fm
import matplotlib as mpl
import seaborn as sns

DARK = "#343a40"
LIGHT = "#e9ecef"
ACCENT = "#4169E1"
FONT = "Microsoft New Tai Lue"
FONT_SIZE = 12  # Increased font size

def calculate_luminance(img_array):
    # Calculate luminance (perceived brightness)
    # Using the formula: L = 0.299*R + 0.587*G + 0.114*B
    return 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]

def create_comparative_tonal_histogram(image_path1, image_path2):
    # Set the font and style
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'  # Make font bold
    plt.rcParams['font.size'] = FONT_SIZE  # Set font size
    sns.set_style("whitegrid")
    
    # Open the images
    img1 = Image.open(image_path1)
    img2 = Image.open(image_path2)
    
    # Convert images to numpy arrays
    img_array1 = np.array(img1)
    img_array2 = np.array(img2)
    
    # Calculate luminance for both images
    luminance1 = calculate_luminance(img_array1)
    luminance2 = calculate_luminance(img_array2)
    
    # Create histogram
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios': [5, 0.5]})
    
    # Set the background color
    ax1.set_facecolor('#F5F5F5')  # very light grey
    
    # Plot histograms of luminance values with outlines
    ax1.hist(luminance1.ravel(), bins=256, color=DARK, alpha=1, label='Tonal Value of Entire Plate', edgecolor='black', linewidth=0.5)
    ax1.hist(luminance2.ravel(), bins=256, color=LIGHT, alpha=1, label='Tonal Values of Center Region', edgecolor='black', linewidth=0.5)
    
    ax1.set_title('Comparative Histograms of Tonal Values of the Entire Image, vs the Region of Interest', fontweight='bold')
    ax1.set_xlabel('Tonal Value', fontweight='bold')
    ax1.set_ylabel('Frequency (Pixels)', fontweight='bold')
    ax1.legend(prop={'weight':'bold'})
    ax1.set_xlim([0, 255])
    
    # Create a visual representation of tonal values
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax2.imshow(np.vstack((gradient,)), aspect='auto', cmap='gray')
    ax2.set_yticks([])
    ax2.set_xticks([])  # Remove x-axis ticks
    ax2.set_xlabel('Tonal Value Representation', fontweight='bold')
    
    # Indicate the range 90-180
    ax2.axvline(x=90, color=LIGHT, linestyle='--')
    ax2.axvline(x=180, color=DARK, linestyle='--')
    ax2.text(135, 0, '90-180', color=DARK, ha='center', va='center',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
             fontweight='bold', fontsize=FONT_SIZE)
    
    plt.tight_layout()
    plt.show()

def create_single_tonal_histogram(image_path1):
    # Set the font and style
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'  # Make font bold
    plt.rcParams['font.size'] = FONT_SIZE  # Set font size
    sns.set_style("whitegrid")
    
    # Open the images
    img1 = Image.open(image_path1)

    
    # Convert images to numpy arrays
    img_array1 = np.array(img1)

    
    # Calculate luminance for both images
    luminance1 = calculate_luminance(img_array1)

    
    # Create histogram
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), gridspec_kw={'height_ratios': [5, 0.5]})
    
    # Set the background color
    ax1.set_facecolor('#F5F5F5')  # very light grey
    
    # Plot histograms of luminance values with outlines
    ax1.hist(luminance1.ravel(), bins=256, color=DARK, alpha=1, edgecolor='black', linewidth=0.5)

    
    ax1.set_title('Histograms of Image Tonal Values', fontweight='bold')
    ax1.set_xlabel('Tonal Value', fontweight='bold')
    ax1.set_ylabel('Frequency (Pixels)', fontweight='bold')
    ax1.legend(prop={'weight':'bold'})
    ax1.set_xlim([0, 255])

    
    # Create a visual representation of tonal values
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax2.imshow(np.vstack((gradient,)), aspect='auto', cmap='gray')
    ax2.set_yticks([])
    ax2.set_xticks([])  # Remove x-axis ticks
    ax2.set_xlabel('Tonal Value Representation', fontweight='bold')
    
    # # Indicate the range 90-180
    # ax2.axvline(x=90, color=LIGHT, linestyle='--')
    # ax2.axvline(x=180, color=DARK, linestyle='--')
    # ax2.text(135, 0, '90-180', color=DARK, ha='center', va='center',
    #          bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
    #          fontweight='bold', fontsize=FONT_SIZE)
    
    plt.tight_layout()
    plt.show()



def create_comparative_tonal_histogram_overlap(image_path1, image_path2):
    colour1 ="#088682"
    colour2="#69C78C"
    # colour2 ="#FFBD52"
    colour1="#055864"
    # Set the font and style
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = FONT_SIZE
    sns.set_style("whitegrid")
    
    # Open the images
    img1 = Image.open(image_path1)
    img2 = Image.open(image_path2)
    
    # Convert images to numpy arrays
    img_array1 = np.array(img1)
    img_array2 = np.array(img2)
    
    # Calculate luminance for both images
    luminance1 = calculate_luminance(img_array1)
    luminance2 = calculate_luminance(img_array2)
    
    # Create histogram
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios': [5, 0.5]})
    
    # Set the background color
    ax1.set_facecolor('#F5F5F5')
    
    # Plot histograms with modified transparency and zorder
    n1, bins1, patches1 = ax1.hist(luminance1.ravel(), bins=256, 
                                  color=colour1, alpha=1,
                                  label='Central Tonal Values of Orignal Dataset', 
                                  edgecolor='black', linewidth=0.5, zorder=1)
    
    n2, bins2, patches2 = ax1.hist(luminance2.ravel(), bins=256, 
                                  color=colour2, alpha=0.8,
                                  label='Central Tonal Values of Unseen Dataset', 
                                  edgecolor='black', linewidth=0.5, zorder=2)
    
    # Add histogram outlines using the same bin structure
    ax1.hist(luminance1.ravel(), bins=bins1, histtype='step',
             edgecolor='black', linewidth=1.0, zorder=3)
    ax1.hist(luminance2.ravel(), bins=bins2, histtype='step',
             edgecolor='black', linewidth=1.0, zorder=4)
    
    # Calculate and plot the intersection
    hist1, _ = np.histogram(luminance1.ravel(), bins=bins1)
    hist2, _ = np.histogram(luminance2.ravel(), bins=bins2)
    intersection = np.minimum(hist1, hist2)
    bin_centers = (bins1[:-1] + bins1[1:]) / 2
    
    # # Fill the intersection area
    # ax1.fill_between(bin_centers, intersection, 
    #                  color=overlap, alpha=0.3,
    #                  label='Overlap', zorder=5)
    
    ax1.set_title('Comparative Histograms of Tonal Values of the Entire Image, vs the Region of Interest', 
                  fontweight='bold')
    ax1.set_xlabel('Tonal Value', fontweight='bold')
    ax1.set_ylabel('Frequency (Pixels)', fontweight='bold')
    ax1.legend(prop={'weight':'bold'})
    ax1.set_xlim([0, 255])
    
    # Create a visual representation of tonal values
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax2.imshow(np.vstack((gradient,)), aspect='auto', cmap='gray')
    ax2.set_yticks([])
    ax2.set_xticks([])
    ax2.set_xlabel('Tonal Value Representation', fontweight='bold')
    
    # Indicate the range 90-180
    ax2.axvline(x=90, color=LIGHT, linestyle='--')
    ax2.axvline(x=180, color=DARK, linestyle='--')
    ax2.text(135, 0, '90-180', color=DARK, ha='center', va='center',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
             fontweight='bold', fontsize=FONT_SIZE)
    
    plt.tight_layout()
    plt.show()
colors = ['#073B3A', '#0F8660', '#0F8660', '#D24C4A']
image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0.jpg"
image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0C.jpg"
image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Images for thesis/single Multi/eg2.png"
image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Images for thesis/single Multi/og.png"
image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0C.jpg"
image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/MiddletonalUnseen.jpg"
image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/powerpoint/origional.jpg"
image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/powerpoint/streachedCropped.png"
create_single_tonal_histogram(image_path2)