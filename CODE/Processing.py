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
from scipy import stats
import time
import seaborn as sns


import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed


# d8888b. d888888b .d8888. d8888b. db       .d8b.  db    db 
# 88  `8D   `88'   88'  YP 88  `8D 88      d8' `8b `8b  d8' 
# 88   88    88    `8bo.   88oodD' 88      88ooo88  `8bd8'  
# 88   88    88      `Y8b. 88~~~   88      88~~~88    88    
# 88  .8D   .88.   db   8D 88      88booo. 88   88    88    
# Y8888D' Y888888P `8888Y' 88      Y88888P YP   YP    YP 


def resize_for_display(image, max_width=1280, max_height=720):

    # Purpose: Resize images for display while maintaining aspect ratio
    # Scales down images exceeding specified maximum dimensions
    # Uses area interpolation for high-quality resizing
    # Preserves image quality during visualization

    h, w = image.shape[:2]
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image

# d8888b. d8888b. d88888b d8888b. d8888b.  .d88b.   .o88b. 
# 88  `8D 88  `8D 88'     88  `8D 88  `8D .8P  Y8. d8P  Y8 
# 88oodD' 88oobY' 88ooooo 88oodD' 88oobY' 88    88 8P      
# 88~~~   88`8b   88~~~~~ 88~~~   88`8b   88    88 8b      
# 88      88 `88. 88.     88      88 `88. `8b  d8' Y8b  d8 
# 88      88   YD Y88888P 88      88   YD  `Y88P'   `Y88P' 


def calculate_brightness(img_array):

    #Purpose: Calculate image brightness using weighted color channels
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

    
def get_inner_image(image):
    #Purpose: Get just the inner part of the image for histogram analysis
    height, width = image.shape[:2]
    start_y = int(height * 0.1) #take off more from the bottom becuse of plate edge
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

def analyze_tonal_range(image):
    #get the total range that 99% of pixels fall into
    inner_image = get_inner_image(image)
    brightness = calculate_brightness(inner_image)
    lower, upper = get_99_percent_range(brightness)
    
    return lower, upper

def stretch_and_gray(original_image, show_images=False):
    #streach the contrast differnet and make the image into greyscale
    lower_bound, upper_bound = analyze_tonal_range(original_image)
    stretched = skimage.exposure.rescale_intensity(original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)).astype(np.uint8)
    #setting contrast as a function of the streach
    idealContrast = int(-0.1813*(upper_bound -lower_bound)+27.113)
    print("Streach range diff: " + str(upper_bound - lower_bound))

    
    idealContrast = max(idealContrast,2)
    idealContrast = min(idealContrast,20)


    height, width = original_image.shape[:2]
    print(f"HEIGHT {height}, WIDTH {width}")
    # Define a scaling factor for sigma, e.g., 1% of the image dimensions
    sigma_scale = 0.0015  # Adjust this as needed

    # Compute sigmaX and sigmaY as a function of the image size
    sigmaX = sigma_scale * width
    sigmaY = sigma_scale * height

    # Apply Gaussian blur with calculated sigma values
    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=sigmaX, sigmaY=sigmaX)
    # blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=5, sigmaY=5)
    gray_image= cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    print(sigmaX, sigmaY)

        #CONTOURS HERE FOR TESTING
    # cv2.imshow('stretched', resize_for_display(stretched))
    # cv2.imshow('blurred', resize_for_display(blurred))
    # cv2.imshow('gray_image', resize_for_display(gray_image))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    return stretched, blurred, gray_image, idealContrast
    
 
def binarize(gray_image, original_image, contrast=20, excludeSmallDots=15, block_size=301, show_images=False):
    #make it into a binart image using adaptive thresholding  
    c = max(-50, min(int(-contrast), -1))-5
    binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, block_size, c)  
   
    contour_img = original_image.copy()
    final_binary = np.zeros_like(binary_image)
    
    # Use RETR_LIST to find all contours without hierarchical relationships
    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
   
    height, width = binary_image.shape
    image_area = height * width
    
    # Scale the exclude small dots
    excludeSmallDots = int((width*(excludeSmallDots/5000))**2)
    
    # Filter and draw inner contours
    for i, cntr in enumerate(contours):
        area = cv2.contourArea(cntr)
        
        # Skip very small contours
        if area <= excludeSmallDots:
            continue
        
        # Skip contours that are too large
        if area > 0.5 * image_area:
            continue
        
        # Draw the contour
        cv2.drawContours(contour_img, [cntr], 0, (255, 105, 65), 2)
        cv2.drawContours(final_binary, [cntr], 0, 255, -1)
    
    return binary_image, contour_img, final_binary, block_size





#  .o88b. d888888b d8888b.  .o88b. db      d88888b .d8888. 
# d8P  Y8   `88'   88  `8D d8P  Y8 88      88'     88'  YP 
# 8P         88    88oobY' 8P      88      88ooooo `8bo.   
# 8b         88    88`8b   8b      88      88~~~~~   `Y8b. 
# Y8b  d8   .88.   88 `88. Y8b  d8 88booo. 88.     db   8D 
#  `Y88P' Y888888P 88   YD  `Y88P' Y88888P Y88888P `8888Y' 
                                                         
#adpated method from:
####https://learnopencv.com/blob-detection-using-opencv-python-c/
def findBlobs(binary_image, min_area, max_area, thickness=2):

    #find contours to look for blobs in
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #needs to be convered to colour so that it can be drawn on
    result_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)

    #CONTOURS HERE FOR TESTING
    # cv2.imshow('contours', resize_for_display(result_image))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    x_coords =[]
    y_coords=[]
    for contour in contours:

        area = cv2.contourArea(contour)
        if min_area <= area <= max_area:
            #circuarity
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter)

            if circularity > 0.30:
                #find center using moments
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    #if it meets the criteria then add the centerpoint
                    x_coords.append(cX)
                    y_coords.append(cY)
    return x_coords,y_coords,result_image

def detect_and_draw_circles(binary_image, gray_image, noClusters, min_radius=50, max_radius=140, param1=50, param2=28, columns = 12, rows=8, square_grid = False):
    
    height, width = binary_image.shape
    max_radius = int(width/(columns*2)) #the biggest that a "good" circle would be is if all 12 in a line where fullly gorwn to te width of the image
    min_radius = int(max_radius/3)
    max_area = max_radius**2*(math.pi)
    min_area = min_radius**2*(math.pi)

    counts = np.zeros((rows, columns))

    x_coords, y_coords, marked_image = findBlobs(binary_image, min_area, max_area)
    grid_calculated = False


    #keep trying to get the grid -TODO need to add a stop condition here
    while not grid_calculated:
        try:
                                                                    
            grid_start_x, grid_start_y, cell_width, cell_height = calculate_grid(x_coords, y_coords, width, height, binary_image, gray_image, columns, rows, square_grid = False, debug=False)
            grid_calculated = True
        except ValueError as e:
            print(f"Error in grid calculation: {e}")
            print("Attempting blob detection with looser parameters")
            #try looser parameters
            min_area = min_area/1.2
            max_area = max_area*1.2
            x_coords, y_coords, marked_image = findBlobs(binary_image,min_area, max_area)
            
            if len(x_coords) < 2 or len(y_coords) < 2: #this will trigger looser parameters
                raise ValueError("Unable to detect sufficient blobs for grid calculation")



    counts, marked_image = quantify_grid(binary_image, marked_image, grid_start_x, grid_start_y, cell_width, cell_height, columns, rows)
    return counts, marked_image


# d888b  d8888b. d888888b d8888b. 
# 88' Y8b 88  `8D   `88'   88  `8D 
# 88      88oobY'    88    88   88 
# 88  ooo 88`8b      88    88   88 
# 88. ~8~ 88 `88.   .88.   88  .8D 
#  Y888P  88   YD Y888888P Y8888D' 
# 

def calculate_grid(x_coords, y_coords, width, height, binarized_image, gray_image, columns, rows, square_grid=True, debug=False):
    start_time = time.time()
    def find_clusters(coords, min_count=2):
        # [Previous find_clusters implementation remains unchanged]
        FONT = "Microsoft New Tai Lue"
        plt.rcParams['font.family'] = FONT
        sns.set_style("whitegrid")
        sorted_coords = np.sort(coords)
        diffs = np.diff(sorted_coords)
        filtered_diff = diffs[(diffs > 0) & (diffs < 50)]
        median_diff = np.median(filtered_diff)
        
        if (math.isnan(median_diff)):
            threshold = 2
        else:    
            threshold = max(median_diff * 3, 12)
            threshold = min(threshold, 50)
            
        clusters = []
        current_cluster = [sorted_coords[0]]
        
        for i in range(1, len(sorted_coords)):
            if diffs[i-1] < threshold:
                current_cluster.append(sorted_coords[i])
            else:
                if len(current_cluster) >= min_count:
                    clusters.append(current_cluster)
                current_cluster = [sorted_coords[i]]
        
        if len(current_cluster) >= min_count:
            clusters.append(current_cluster)

        cluster_means = [np.mean(cluster) for cluster in clusters]
    
        mean_diffs = np.diff(cluster_means)
        if len(mean_diffs) > 0:
            kde = stats.gaussian_kde(mean_diffs)
            x_range = np.linspace(mean_diffs.min(), mean_diffs.max(), 100)
            modal_diff = x_range[np.argmax(kde(x_range))]
        else:
            modal_diff = threshold

        if True:    
            combined_clusters = []
            combined_indices = []
            i = 0
            while i < len(clusters):
                current_combined = clusters[i]
                combined_group = [i]
                while i + 1 < len(clusters) and cluster_means[i+1] - cluster_means[i] < modal_diff / 2:
                    current_combined.extend(clusters[i+1])
                    combined_group.append(i+1)
                    i += 1
                combined_clusters.append(current_combined)
                if len(combined_group) > 1:
                    combined_indices.append(combined_group)
                i += 1
            final_cluster_means = [np.mean(cluster) for cluster in combined_clusters]
            return final_cluster_means
        else:
            return cluster_means

    x_clusters = find_clusters(x_coords)
    y_clusters = find_clusters(y_coords)

    if len(x_clusters) < 2 or len(y_clusters) < 2:
        raise ValueError("Not enough valid clusters found to calculate grid")
    
    x_diffs = np.diff(x_clusters)
    y_diffs = np.diff(y_clusters)
    
    # Calculate bounds separately for x and y
    x_lowerBound = width/(columns*2)
    x_upperBound = width/(columns*0.5)
    y_lowerBound = height/(rows*2)
    y_upperBound = height/(rows*0.5)
    
    filtered_x_diffs = [x for x in x_diffs if x_lowerBound <= x <= x_upperBound]
    filtered_y_diffs = [y for y in y_diffs if y_lowerBound <= y <= y_upperBound]

    if not filtered_x_diffs and not filtered_y_diffs:
        filtered_x_diffs = [x for x in x_diffs]
        filtered_y_diffs = [y for y in y_diffs]

    if filtered_x_diffs:
        median_x_diff = np.median(filtered_x_diffs)
    else:
        median_x_diff = None

    if filtered_y_diffs:
        median_y_diff = np.median(filtered_y_diffs)
    else:
        median_y_diff = None

    if median_x_diff is None and median_y_diff is None:
        raise ValueError("Both x and y differences are invalid")
    
    if square_grid:
        # Original behavior for square cells
        if median_x_diff is None:
            cell_size = median_y_diff
        elif median_y_diff is None:
            cell_size = median_x_diff
        else:
            cell_size = max(median_x_diff, median_y_diff)
        cell_width = cell_size
        cell_height = cell_size
    else:
        # Handle rectangular cells
        if median_x_diff is None:
            cell_width = width / columns  # fallback to even distribution
        else:
            cell_width = median_x_diff
            
        if median_y_diff is None:
            cell_height = height / rows  # fallback to even distribution
        else:
            cell_height = median_y_diff
    
    grid_start_x = min(x_clusters) - cell_width / 2
    grid_start_y = min(y_clusters) - cell_height / 2
    
    grid_width = cell_width * columns
    grid_height = cell_height * rows
    
    if grid_start_x + grid_width > width:
        grid_start_x = width - grid_width
    if grid_start_y + grid_height > height:
        grid_start_y = height - grid_height
        
    end_time = time.time()
    print(f"calculate_grid total execution time: {end_time - start_time:.4f} seconds")
    
    if square_grid:
        return grid_start_x, grid_start_y, cell_width, cell_width # maintains backward compatibility
    else:
        return grid_start_x, grid_start_y, cell_width, cell_height

# def process_label(args):
#     """
#     Process a single label (spot) in the image
    
#     Parameters:
#     - args: Tuple containing:
#         - labeled_image: Labeled image from ndimage.label
#         - label: Current label to process
#         - grid_start_x: Starting x coordinate of the grid
#         - grid_start_y: Starting y coordinate of the grid
#         - cell_size: Size of each grid cell
#         - rows: Number of rows in the grid
#         - columns: Number of columns in the grid
#         - width: Image width
#         - height: Image height
    
#     Returns:
#     - Tuple of (row, col, total_area) if the spot is successfully counted
#     - None if the spot is not counted
#     """
#     (labeled_image, label, grid_start_x, grid_start_y, cell_size, 
#      rows, columns, width, height) = args
    
#     component = (labeled_image == label)
#     coords = np.column_stack(np.where(component))
    
#     # Calculate grid bounds
#     min_row = max(0, int((np.min(coords[:, 0]) - grid_start_y) // cell_size))
#     max_row = min(rows - 1, int((np.max(coords[:, 0]) - grid_start_y) // cell_size))
#     min_col = max(0, int((np.min(coords[:, 1]) - grid_start_x) // cell_size))
#     max_col = min(columns - 1, int((np.max(coords[:, 1]) - grid_start_x) // cell_size))
    
#     main_cell = None
#     max_overlap = 0
#     total_area = np.sum(component)
    
#     # Find the main cell with maximum overlap
#     for row in range(min_row, max_row + 1):
#         for col in range(min_col, max_col + 1):
#             x1 = int(grid_start_x + col * cell_size)
#             y1 = int(grid_start_y + row * cell_size)
#             x2 = int(x1 + cell_size)
#             y2 = int(y1 + cell_size)
            
#             x1, y1 = max(0, x1), max(0, y1)
#             x2, y2 = min(width, x2), min(height, y2)
            
#             cell = component[y1:y2, x1:x2]
#             overlap = np.sum(cell)
            
#             if overlap > max_overlap:
#                 max_overlap = overlap
#                 main_cell = (row, col)
    
#     # Check if the spot should be counted
#     if main_cell is not None:
#         main_row, main_col = main_cell
#         outside_area = total_area - max_overlap
        
#         if outside_area <= 0.4 * total_area:
#             return (main_row, main_col, total_area)
    
#     return None



# def process_label(labeled_image, label, grid_start_x, grid_start_y, cell_size, 
#                   rows, columns, width, height):
#     """
#     Process a single label (spot) in the image
    
#     Returns:
#     - Tuple of (row, col, total_area) if the spot is successfully counted
#     - None if the spot is not counted
#     """
#     component = (labeled_image == label)
#     coords = np.column_stack(np.where(component))
    
#     # Calculate grid bounds
#     min_row = max(0, int((np.min(coords[:, 0]) - grid_start_y) // cell_size))
#     max_row = min(rows - 1, int((np.max(coords[:, 0]) - grid_start_y) // cell_size))
#     min_col = max(0, int((np.min(coords[:, 1]) - grid_start_x) // cell_size))
#     max_col = min(columns - 1, int((np.max(coords[:, 1]) - grid_start_x) // cell_size))
    
#     main_cell = None
#     max_overlap = 0
#     total_area = np.sum(component)
    
#     # Find the main cell with maximum overlap
#     for row in range(min_row, max_row + 1):
#         for col in range(min_col, max_col + 1):
#             x1 = int(grid_start_x + col * cell_size)
#             y1 = int(grid_start_y + row * cell_size)
#             x2 = int(x1 + cell_size)
#             y2 = int(y1 + cell_size)
            
#             x1, y1 = max(0, x1), max(0, y1)
#             x2, y2 = min(width, x2), min(height, y2)
            
#             cell = component[y1:y2, x1:x2]
#             overlap = np.sum(cell)
            
#             if overlap > max_overlap:
#                 max_overlap = overlap
#                 main_cell = (row, col)
    
#     # Check if the spot should be counted
#     if main_cell is not None:
#         main_row, main_col = main_cell
#         outside_area = total_area - max_overlap
        
#         if outside_area <= 0.4 * total_area:
#             return (main_row, main_col, total_area, component)
    
#     return None

# def quantify_grid(binary_image, marked_image, grid_start_x, grid_start_y, cell_size, columns, rows):
#     start_time = time.time()
#     height, width = binary_image.shape

#     # Label the image
#     labeled_image, num_features = ndimage.label(binary_image) 
#     counts = np.zeros((rows, columns), dtype=int)

#     # Convert to color image if grayscale
#     if len(marked_image.shape) == 2:  
#         marked_image = cv2.cvtColor(marked_image, cv2.COLOR_GRAY2BGR)

#     # Mark non-counted areas dark grey
#     white_areas = (marked_image[:, :, 0] == 255) & (marked_image[:, :, 1] == 255) & (marked_image[:, :, 2] == 255)
#     marked_image[white_areas] = [64, 64, 64]
    
#     # Process labels with ThreadPoolExecutor
#     with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() + 1)) as executor:
#         # Submit all label processing tasks
#         future_to_label = {
#             executor.submit(process_label, labeled_image, label, grid_start_x, grid_start_y, 
#                             cell_size, rows, columns, width, height): label 
#             for label in range(1, num_features + 1)
#         }
        
#         # Process results as they complete
#         for future in as_completed(future_to_label):
#             result = future.result()
#             if result is not None:
#                 row, col, total_area, component = result
#                 counts[row, col] += total_area
#                 marked_image[component] = [255, 255, 255]
    
#     print("COUNTS")
#     print(counts)
#     # Scale counts
#     counts = (np.round((counts / ((width-1)**2)) * 1000000)).astype(int)
    
#     # Draw grid and add counts (same as original function)
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     font_scale = width *0.0008
#     thickness = int(width *0.002)
#     print("FONT SCALE AND THICKNESS")
#     print (font_scale)
#     print (thickness)

#     for row in range(rows):
#         for col in range(columns):
#             x1 = int(grid_start_x + col * cell_size)
#             y1 = int(grid_start_y + row * cell_size)
#             x2 = int(x1 + cell_size)
#             y2 = int(y1 + cell_size)
            
#             cv2.rectangle(marked_image, (x1, y1), (x2, y2), (255, 105, 65), thickness)
            
#             text = str(counts[row, col])
#             text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            
#             text_x = int(x1 + (cell_size - text_size[0]) // 2)
#             text_y = int(y1 + (cell_size + text_size[1]) // 2)
            
#             cv2.putText(marked_image, text, (text_x, text_y), font, font_scale, (255, 105, 65), thickness)

#     end_time = time.time()
#     print(f"quantify_grid total execution time: {end_time - start_time:.4f} seconds")
    
#     return counts, marked_image



def process_label(labeled_image, label, grid_start_x, grid_start_y, cell_width, cell_height, 
                  rows, columns, width, height):
    """
    Process a single label (spot) in the image
    
    Args:
    - labeled_image: Image with labeled components
    - label: Current label to process
    - grid_start_x: Starting x coordinate of the grid
    - grid_start_y: Starting y coordinate of the grid
    - cell_width: Width of each grid cell
    - cell_height: Height of each grid cell
    - rows: Number of grid rows
    - columns: Number of grid columns
    - width: Image width
    - height: Image height
    
    Returns:
    - Tuple of (row, col, total_area, component) if the spot is successfully counted
    - None if the spot is not counted
    """
    component = (labeled_image == label)
    coords = np.column_stack(np.where(component))
    
    # Calculate grid bounds using separate cell dimensions
    min_row = max(0, int((np.min(coords[:, 0]) - grid_start_y) // cell_height))
    max_row = min(rows - 1, int((np.max(coords[:, 0]) - grid_start_y) // cell_height))
    min_col = max(0, int((np.min(coords[:, 1]) - grid_start_x) // cell_width))
    max_col = min(columns - 1, int((np.max(coords[:, 1]) - grid_start_x) // cell_width))
    
    main_cell = None
    max_overlap = 0
    total_area = np.sum(component)
    
    # Find the main cell with maximum overlap
    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            x1 = int(grid_start_x + col * cell_width)
            y1 = int(grid_start_y + row * cell_height)
            x2 = int(x1 + cell_width)
            y2 = int(y1 + cell_height)
            
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)
            
            cell = component[y1:y2, x1:x2]
            overlap = np.sum(cell)
            
            if overlap > max_overlap:
                max_overlap = overlap
                main_cell = (row, col)
    
    # Check if the spot should be counted
    if main_cell is not None:
        main_row, main_col = main_cell
        outside_area = total_area - max_overlap
        
        if outside_area <= 0.4 * total_area:
            return (main_row, main_col, total_area, component)
    
    return None

def quantify_grid(binary_image, marked_image, grid_start_x, grid_start_y, cell_width, cell_height, columns, rows):
    print(cell_width)
    print(cell_height)
    """
    Quantify spots in a grid and visualize results
    
    Args:
    - binary_image: Binary image with spots
    - marked_image: Image to draw results on
    - grid_start_x: Starting x coordinate of the grid
    - grid_start_y: Starting y coordinate of the grid
    - cell_size: Cell size (if square_grid=True) or tuple of (cell_width, cell_height)
    - columns: Number of grid columns
    - rows: Number of grid rows
    - square_grid: If True, cells are square and cell_size is a single value
                  If False, cell_size should be a tuple of (cell_width, cell_height)
    """
    start_time = time.time()
    height, width = binary_image.shape


    # Label the image
    labeled_image, num_features = ndimage.label(binary_image) 
    counts = np.zeros((rows, columns), dtype=int)

    # Convert to color image if grayscale
    if len(marked_image.shape) == 2:  
        marked_image = cv2.cvtColor(marked_image, cv2.COLOR_GRAY2BGR)

    # Mark non-counted areas dark grey
    white_areas = (marked_image[:, :, 0] == 255) & (marked_image[:, :, 1] == 255) & (marked_image[:, :, 2] == 255)
    marked_image[white_areas] = [64, 64, 64]
    
    # Process labels with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() + 1)) as executor:
        # Submit all label processing tasks
        future_to_label = {
            executor.submit(process_label, labeled_image, label, grid_start_x, grid_start_y, 
                          cell_width, cell_height, rows, columns, width, height): label 
            for label in range(1, num_features + 1)
        }
        
        # Process results as they complete
        for future in as_completed(future_to_label):
            result = future.result()
            if result is not None:
                row, col, total_area, component = result
                counts[row, col] += total_area
                marked_image[component] = [255, 255, 255]
    
    print("COUNTS")
    print(counts)
    # Scale counts
    counts = (np.round((counts / ((width-1)**2)) * 1000000)).astype(int)
    
    # Draw grid and add counts
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = width * 0.0008
    thickness = int(width * 0.002)
    print("FONT SCALE AND THICKNESS")
    print(font_scale)
    print(thickness)

    for row in range(rows):
        for col in range(columns):
            x1 = int(grid_start_x + col * cell_width)
            y1 = int(grid_start_y + row * cell_height)
            x2 = int(x1 + cell_width)
            y2 = int(y1 + cell_height)
            
            cv2.rectangle(marked_image, (x1, y1), (x2, y2), (255, 105, 65), thickness)
            
            text = str(counts[row, col])
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            
            # Center text in potentially rectangular cell
            text_x = int(x1 + (cell_width - text_size[0]) // 2)
            text_y = int(y1 + (cell_height + text_size[1]) // 2)
            
            cv2.putText(marked_image, text, (text_x, text_y), font, font_scale, (255, 105, 65), thickness)

    end_time = time.time()
    print(f"quantify_grid total execution time: {end_time - start_time:.4f} seconds")
    
    return counts, marked_image