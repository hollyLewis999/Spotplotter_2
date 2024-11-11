import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.font_manager as fm
import matplotlib as mpl
from scipy.signal import find_peaks, peak_prominences

DARK = "#666666"
LIGHT = "#C1D6EC"
ACCENT = "#4169E1"

def calculate_luminance(img_array):
    return 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]

def find_threshold_points(hist):
    smoothed_hist = np.convolve(hist, np.ones(5)/5, mode='same')
    peaks, _ = find_peaks(-smoothed_hist)
    prominences = peak_prominences(-smoothed_hist, peaks)[0]
    sorted_peaks = peaks[np.argsort(-prominences)]
    multi_thresholds = sorted_peaks[:2]
    single_threshold = sorted_peaks[0]
    return multi_thresholds, single_threshold

def apply_single_threshold(image, threshold):
    return (image > 174).astype(np.uint8) * 255

def apply_multi_threshold(image, thresholds):
    result = np.zeros_like(image)
    for i, t in enumerate(sorted(thresholds)):
        result[image > t] = i + 1
    return (result * (255 // (len(thresholds) + 1))).astype(np.uint8)

def create_histogram_and_threshold(image_path):
    mpl.rcParams['text.usetex'] = False
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['DejaVu Serif']
   
    # Open and process the image
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img_array = np.array(img)
   
    # Create histogram
    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(15, 20))
    
    hist, bins = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
   
    # Find threshold points
    multi_thresholds, single_threshold = find_threshold_points(hist)
   
    # Plot original histogram
    ax1.hist(img_array.flatten(), bins=256, range=[0, 256], color=DARK, alpha=1)
    ax1.set_title('Original Histogram')
    ax1.set_xlim([0, 255])
    ax1.set_ylim([0, 5000])
    
    # # Plot thresholds on histogram
    # for threshold in multi_thresholds:
    #     ax1.axvline(x=bins[threshold], color=ACCENT, linestyle='--', label=f'Multi-level Threshold ({bins[threshold]:.0f})')
    # ax1.axvline(x=bins[single_threshold], color=LIGHT, linestyle='-', label=f'Single-level Threshold ({bins[single_threshold]:.0f})')
    # ax1.legend()

    # Display original image
    ax2.imshow(img_array, cmap='gray')
    ax2.set_title('Original Image')
    ax2.axis('off')

    # Apply and display single-level threshold
    single_threshold_img = apply_single_threshold(img_array, bins[single_threshold])
    ax3.hist(single_threshold_img.flatten(), bins=256, range=[0, 256], color=DARK, alpha=1)
    ax3.set_title('Single-level Threshold Histogram')
    ax3.set_xlim([0, 255])

    ax4.imshow(single_threshold_img, cmap='gray')
    ax4.set_title('Single-level Threshold Image')
    ax4.axis('off')

    # Apply and display multi-level threshold
    multi_threshold_img = apply_multi_threshold(img_array, bins[multi_thresholds])
    ax5.hist(multi_threshold_img.flatten(), bins=256, range=[0, 256], color=DARK, alpha=1)
    ax5.set_title('Multi-level Threshold Histogram')
    ax5.set_xlim([0, 255])

    ax6.imshow(multi_threshold_img, cmap='gray')
    ax6.set_title('Multi-level Threshold Image')
    ax6.axis('off')

    plt.tight_layout()
    plt.show()

# Use the same image for analysis
image_path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Images for thesis/single Multi/eg2.png"
create_histogram_and_threshold(image_path)