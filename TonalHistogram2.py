import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.font_manager as fm
import matplotlib as mpl
blue_hex  = 'ef476f'  # Hex for ORIGIONAL
green_hex= 'ffd166'  # Hex for NEW
red_hex = 'f18701'  # Hex for OVERLAP


DARK = '#0B4D5A'
LIGHT = '#0F8660'
ACCENT = "#4169E1"
OVERLAP = "#D3784A"  # Dark magenta for overlap

DARK = '#ef476f'
LIGHT = '#ffd166'


colors = ['#073B3A', '#0F8660', '#D3784A', '#D24C4A']
ALPHA = 0.6
def calculate_luminance(img_array):
    # Calculate luminance (perceived brightness)
    # Using the formula: L = 0.299*R + 0.587*G + 0.114*B
    return 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]

def create_comparative_tonal_histogram(image_path1, image_path2):
    # Set the font to Computer Modern Roman
    mpl.rcParams['text.usetex'] = False
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['DejaVu Serif']
   
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
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [5, 1]})
   
    # Plot histograms of luminance values
    bins = 256
    hist1, bins1, _ = ax1.hist(luminance1.ravel(), bins=bins, color=DARK, alpha=ALPHA, label='Tonal Value of Image From Original Dataset')
    hist2, bins2, _ = ax1.hist(luminance2.ravel(), bins=bins, color=LIGHT, alpha=ALPHA, label='Tonal Values of Image From Unseen Dataset')
   
    # # Calculate and plot the overlap
    # overlap = np.minimum(hist1, hist2)
    # ax1.fill_between(bins1[:-1], overlap, step="post", alpha=1, color=OVERLAP, label='Overlap')
   
    ax1.set_title('Comparative Histograms of Tonal Values of the Entire Image, vs the Region of Interest')
    ax1.set_xlabel('Tonal Value')
    ax1.set_ylabel('Frequency (Pixels)')
    ax1.legend(prop={'weight':'normal'})
    ax1.set_xlim([0, 255])
   
    # Create a visual representation of tonal values
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax2.imshow(np.vstack((gradient,)), aspect='auto', cmap='gray')
    ax2.set_yticks([])
    ax2.set_xlabel('Tonal Value Representation')
   
    # Calculate and indicate the range where 90% of pixels lie for both images
    def get_90_percent_range(luminance):
        hist, bin_edges = np.histogram(luminance.ravel(), bins=256, range=(0, 255))
        cumulative = np.cumsum(hist)
        total_pixels = cumulative[-1]
        lower = np.searchsorted(cumulative, 0.005 * total_pixels)
        upper = np.searchsorted(cumulative, 0.995 * total_pixels)
        return lower, upper

    range1 = get_90_percent_range(luminance1)
    range2 = get_90_percent_range(luminance2)

    ax2.axvline(x=range1[0], color=DARK, linestyle='--')
    ax2.axvline(x=range1[1], color=DARK, linestyle='--')
    # Adjusting the y-coordinate to slightly below the first label
    ax2.text(255 / 2, -0.2, f'{range1[0]}-{range1[1]}', 
            color="#FFFFFF", ha='center', va='top', 
            bbox=dict(facecolor=DARK, edgecolor='none', alpha=0.7))

    ax2.axvline(x=range2[0], color=LIGHT, linestyle='--')
    ax2.axvline(x=range2[1], color=LIGHT, linestyle='--')
    # Adjusting the y-coordinate of the second label to be below the first one
    ax2.text((255/2), +0.1, f'{range2[0]}-{range2[1]}', 
            color="#FFFFFF", ha='center', va='top', 
            bbox=dict(facecolor=LIGHT, edgecolor='none', alpha=0.7))

    # ax2.axvline(x=90, color=LIGHT, linestyle='--')
    # ax2.axvline(x=180, color=DARK, linestyle='--')
    # ax2.text(135, 0, '90-180', color=DARK, ha='center', va='center',
    #          bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
   
    plt.tight_layout()
    plt.show()
# image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0.jpg"
# image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0C.jpg"

image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0C.jpg"
image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/MiddletonalUnseen.jpg"
create_comparative_tonal_histogram(image_path1, image_path2)