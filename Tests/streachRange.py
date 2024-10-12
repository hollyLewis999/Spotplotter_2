import numpy as np
import cv2

def calculate_luminance(img_array):
    # Calculate luminance (perceived brightness)
    # Using the formula: L = 0.299*R + 0.587*G + 0.114*B
    return 0.299 * img_array[:,:,2] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,0]

def get_inner_80_percent(image):
    height, width = image.shape[:2]
    start_y = int(height * 0.2) #take off more from the bottom becuse of plate edge
    end_y = int(height * 0.9)
    start_x = int(width * 0.1)
    end_x = int(width * 0.9)
    return image[start_y:end_y, start_x:end_x]

def get_99_percent_range(luminance):
    hist, bin_edges = np.histogram(luminance.ravel(), bins=256, range=(0, 255))
    cumulative = np.cumsum(hist)
    total_pixels = cumulative[-1]
    lower = np.searchsorted(cumulative, 0.005 * total_pixels)
    upper = np.searchsorted(cumulative, 0.995 * total_pixels)
    return int(lower), int(upper)

def analyze_tonal_range(image):
    # Get the inner 80% of the image
    inner_image = get_inner_80_percent(image)
    
    # Calculate luminance for the inner image
    luminance = calculate_luminance(inner_image)
    
    # Get the range where 99% of the pixels lie
    lower, upper = get_99_percent_range(luminance)
    
    return lower, upper