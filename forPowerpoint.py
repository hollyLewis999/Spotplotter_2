import cv2
import numpy as np
import skimage.exposure
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os
import io
from PIL import Image
from reportlab.lib.utils import ImageReader
from scipy.stats import linregress
import matplotlib.pyplot as plt
import math
from scipy import ndimage

COLOUMS = 12



# d8888b. d888888b .d8888. d8888b. db       .d8b.  db    db 
# 88  `8D   `88'   88'  YP 88  `8D 88      d8' `8b `8b  d8' 
# 88   88    88    `8bo.   88oodD' 88      88ooo88  `8bd8'  
# 88   88    88      `Y8b. 88~~~   88      88~~~88    88    
# 88  .8D   .88.   db   8D 88      88booo. 88   88    88    
# Y8888D' Y888888P `8888Y' 88      Y88888P YP   YP    YP 


def resize_for_display(image, max_width=1280, max_height=720):
    h, w = image.shape[:2]
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image

def analyze_tonal_range(image):
    inner_image = get_inner_image(image)
    brightness = calculate_brightness(inner_image)
    lower, upper = get_99_percent_range(brightness)
    
    return lower, upper

def stretch_and_gray(original_image, show_images=True):
    # Define save path for the images
    save_path = r"C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/powerpoint"
    
    # Analyze the original tonal range
    lower_bound, upper_bound = analyze_tonal_range(original_image)
    
    # Perform the linear stretch within the specified range
    linear_stretched = skimage.exposure.rescale_intensity(
        original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)
    ).astype(np.uint8)
    
    # Perform histogram equalization within the same range to maintain shape
    masked_image = np.clip(original_image, lower_bound, upper_bound)  # Clip to range
    equalized = skimage.exposure.equalize_hist(masked_image) * 255  # Apply histogram equalization
    equalized = equalized.astype(np.uint8)  # Convert to uint8 for image saving
    
    # Calculate ideal contrast based on the original stretch range
    idealContrast = int(-0.1813 * (upper_bound - lower_bound) + 25.113)
    idealContrast = max(idealContrast, 2)
    idealContrast = min(idealContrast, 20)
    
    # Apply Gaussian blur and convert to grayscale for the linearly stretched image
    blurred = cv2.GaussianBlur(linear_stretched, (0, 0), sigmaX=5, sigmaY=5)
    gray_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    
    # # Save both images to the specified folder
    # io.imsave(f"{save_path}\\linear_stretched_image.png", linear_stretched)
    # io.imsave(f"{save_path}\\histogram_equalized_image.png", equalized)
    
    # Optionally display the images if show_images is True
    if show_images:
        cv2.imshow("Linear Stretched Image", resize_for_display(linear_stretched))
        cv2.imshow("Histogram Equalized Image", resize_for_display(equalized))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return linear_stretched, equalized, blurred, gray_image, idealContrast

def get_inner_image(image):
    height, width = image.shape[:2]
    start_y = int(height * 0.2) #take off more from the bottom becuse of plate edge
    end_y = int(height * 0.9)
    start_x = int(width * 0.1)
    end_x = int(width * 0.9)
    return image[start_y:end_y, start_x:end_x]

def get_99_percent_range(brightness):
    #using a cumalitive histogramdisstogram
    hist, bin_edges = np.histogram(brightness.ravel(), bins=256, range=(0, 255))
    cumulative = np.cumsum(hist)
    total_pixels = cumulative[-1]
    lower = np.searchsorted(cumulative, 0.005 * total_pixels)
    upper = np.searchsorted(cumulative, 0.995 * total_pixels)
    return int(lower), int(upper)

def calculate_brightness(img_array):
    #get the different channels, this colour is in BGR not RGB
    blue_channel = img_array[:, :, 0]
    green_channel = img_array[:, :, 1]
    red_channel = img_array[:, :, 2]
    
    #weighted changels based on fomula
    red_weighted = 0.299 * red_channel
    green_weighted = 0.587 * green_channel
    blue_weighted = 0.114 * blue_channel
    brightness = red_weighted + green_weighted + blue_weighted
    
    return brightness
image_path1 = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/0.jpg"
image_path1="C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/AlternateDataSet/P3211769 Cropped.jpg"
original_image = cv2.imread(image_path1 )
stretched, blurred, gray_image, idealContrast = stretch_and_gray(original_image)


cv2.imshow("stretch_and_gray", resize_for_display(stretched))
cv2.waitKey(0)
cv2.destroyAllWindows()