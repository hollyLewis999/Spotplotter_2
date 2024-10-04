import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.font_manager as fm
import matplotlib as mpl

DARK = "#092934"
LIGHT = "#C1D6EC"
ACCENT = "#4169E1"

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
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios': [5, 1]})
   
    # Plot histograms of luminance values
    ax1.hist(luminance1.ravel(), bins=256, color=DARK, alpha=1, label='Tonal Value of Entire Plate')
    ax1.hist(luminance2.ravel(), bins=256, color=LIGHT, alpha=1, label='Tonal Values of Center Region')
   
    ax1.set_title('Comparative Histograms of Tonal Values of the Entire Image, vs the Region of Interest')
    ax1.set_xlabel('Tonal Value')
    ax1.set_ylabel('Frequency (Pixels)')
    ax1.legend(prop={'weight':'normal'})
    ax1.set_xlim([0, 255])
    
    # Create a visual representation of tonal values
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax2.imshow(np.vstack((gradient,)), aspect='auto', cmap='gray')
    ax2.set_yticks([])
    ax2.set_xlabel('Tonal Value Representaion')
    
    # Indicate the range 90-180
    ax2.axvline(x=90, color=LIGHT, linestyle='--')
    ax2.axvline(x=180, color=DARK, linestyle='--')
    ax2.text(135, 0, '90-180', color=DARK, ha='center', va='center',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
    
    plt.tight_layout()
    plt.show()

image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0.jpg"
image_path2 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0C.jpg"
create_comparative_tonal_histogram(image_path1, image_path2)