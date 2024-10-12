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
from streachRange import *

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

def detect_and_draw_circles(binary_image, gray_image, noClusters, min_radius=50, max_radius=140, param1=50, param2=28):
    height, width = binary_image.shape
    max_radius = int(width/24) #the biggest that a "good" circle would be is if all 12 in a line where fullly gorwn to te width of the image
    min_radius = int(max_radius/3)
    max_area = max_radius**2*(math.pi)
    min_area = min_radius**2*(math.pi)

    counts = np.zeros((8, 12))

    x_coords, y_coords, marked_image = findBlobs(binary_image, min_area, max_area)
    grid_calculated = False


    #keep trying to get the grid -TODO need to add a stop condition here
    while not grid_calculated:
        try:
            grid_start_x, grid_start_y, cell_size = calculate_grid(x_coords, y_coords, width, height, binary_image, gray_image, debug=False)
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



    counts, marked_image, ordered_counts = quantify_grid(binary_image, marked_image, grid_start_x, grid_start_y, cell_size)
    return counts, marked_image,ordered_counts


# d888b  d8888b. d888888b d8888b. 
# 88' Y8b 88  `8D   `88'   88  `8D 
# 88      88oobY'    88    88   88 
# 88  ooo 88`8b      88    88   88 
# 88. ~8~ 88 `88.   .88.   88  .8D 
#  Y888P  88   YD Y888888P Y8888D' 
# 

def calculate_grid(x_coords, y_coords, width, height, binarized_image, gray_image, debug=False):

    def find_clusters(coords, min_count=2):

        sorted_coords = np.sort(coords)
        diffs = np.diff(sorted_coords)
        median_diff = np.median(diffs) #this is the difference between cluster = cell size
        #need to fiddle with the median_diffs, using median not mean becuse some differences will be double becuse there is an empty row/coloumn
        threshold = max(median_diff *1.5,10) #otherwise if its perfect it threshold will be zero, this is taking out ones that are unrealistic

        clusters = []
        current_cluster = [sorted_coords[0]]
        
        #it loops though each co-ordinate and loops to see if it belongs in that cluster based on the threshold
        for i in range(1, len(sorted_coords)):
            if diffs[i-1] < threshold: #is part of cluster
                current_cluster.append(sorted_coords[i])
            else: #checks to see if there are enough co-ords in a cluster before adding it (to avoid a bunch of clusters with 1 co-ordnate)
                if len(current_cluster) >= min_count:
                    clusters.append(current_cluster)
                #goes to next cluster using the first co-ornate that was too big    
                current_cluster = [sorted_coords[i]]
        
        #FOR THE LAST CLUSTER (previously wasnt adding becuse the loop skips it) 
        # checks to see if there are enough co-ords in a cluster before adding it (to avoid a bunch of clusters with 1 co-ordnate)
        if len(current_cluster) >= min_count:
            clusters.append(current_cluster)
        
        cluster_means = [np.mean(cluster) for cluster in clusters]
        

        #Debug generated with chatGBT
        if debug:
            plt.figure(figsize=(10, 5))
            plt.scatter(coords, [0] * len(coords), c='blue', label='Original points')
            for mean in cluster_means:
                plt.axvline(x=mean, color='red', linestyle='--')
            plt.title(f'Clusters')
            plt.legend()
            plt.show()
        
        return cluster_means



    #print(x_coords)
    x_clusters = find_clusters(x_coords)
    y_clusters = find_clusters(y_coords)

    



    if len(x_clusters) < 2 or len(y_clusters) < 2:
        raise ValueError("Not enough valid clusters found to calculate grid")
    
    #distance between clusters to try get  cell size
    x_diffs = np.diff(x_clusters)
    y_diffs = np.diff(y_clusters)
    #take out the ones that are most likley differences within the same cluster or between non neighbouring clusters
    lowerBound = width/30
    upperBound = width/10
    filtered_x_diffs = [x for x in x_diffs if lowerBound <= x <= upperBound]
    filtered_y_diffs = [y for y in y_diffs if lowerBound <= y <= upperBound]

    #no valid differences
    if not filtered_x_diffs and not filtered_y_diffs: 
        raise ValueError("No valid differences found within bounds")



    #mediaun to avoid differences within the same cluster or between non neighbouring clusters
    #dealing this if there are no x, no y or none of wither
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
    elif median_x_diff is None:
        cell_size = median_y_diff
    elif median_y_diff is None:
        cell_size = median_x_diff
    else:
        cell_size = max(median_x_diff, median_y_diff)


    
    grid_start_x = min(x_clusters) - cell_size / 2
    grid_start_y = min(y_clusters) - cell_size / 2
    
    grid_width = cell_size * 12
    grid_height = cell_size * 8
    
    #making sure its startin within the bounds
    if grid_start_x + grid_width > width:
        grid_start_x = width - grid_width
    if grid_start_y + grid_height > height:
        grid_start_y = height - grid_height
    
    return grid_start_x, grid_start_y, cell_size 

def quantify_grid(binary_image, marked_image, grid_start_x, grid_start_y, cell_size):
    """
    Quantify the grid by counting white pixels in each cell, including blobs
    slightly overlapping (up to 20%) with neighboring blocks. All white areas 
    in the binary image are colored dark grey.
    """
    height, width = binary_image.shape
    rows, cols = 8, 12  # 8x12 grid
    
    # Label connected components
    labeled_image, num_features = ndimage.label(binary_image)
    
    counts = np.zeros((rows, cols), dtype=int)


    if len(marked_image.shape) == 2:  
        marked_image = cv2.cvtColor(marked_image, cv2.COLOR_GRAY2BGR)

    white_areas = (marked_image[:, :, 0] == 255) & (marked_image[:, :, 1] == 255) & (marked_image[:, :, 2] == 255)

    marked_image[white_areas] = [64, 64, 64]
    
    for label in range(1, num_features + 1):
        component = (labeled_image == label)
        coords = np.column_stack(np.where(component))
        
        min_row = max(0, int((np.min(coords[:, 0]) - grid_start_y) // cell_size))
        max_row = min(rows - 1, int((np.max(coords[:, 0]) - grid_start_y) // cell_size))
        min_col = max(0, int((np.min(coords[:, 1]) - grid_start_x) // cell_size))
        max_col = min(cols - 1, int((np.max(coords[:, 1]) - grid_start_x) // cell_size))
        
        main_cell = None
        max_overlap = 0
        total_area = np.sum(component)
        
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                x1 = int(grid_start_x + col * cell_size)
                y1 = int(grid_start_y + row * cell_size)
                x2 = int(x1 + cell_size)
                y2 = int(y1 + cell_size)
                
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                cell = component[y1:y2, x1:x2]
                overlap = np.sum(cell)
                
                if overlap > max_overlap:
                    max_overlap = overlap
                    main_cell = (row, col)
        
        if main_cell is not None:
            main_row, main_col = main_cell
            main_area = max_overlap
            outside_area = total_area - main_area
            
            if outside_area <= 0.4 * total_area:
                # Count the entire blob in the main cell and color it light grey
                counts[main_row, main_col] += total_area
                marked_image[component] = [255, 255, 255]  # Light grey
            else:

                pass
    print ("COUNT 00" + str(counts[0,0]))
    print("WIDTH: " + str(width))        
    counts = (np.round((counts / ((width-1)**2)) * 1000000)).astype(int)
    print ("hopefully After scaling" + str(counts[0,0]))
    #drawing the grid and adding the counts
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = width/1200
    thickness = int(width**(0.125)) #scaling the thickness so that it looks normal on smaller images

    for row in range(rows):
        for col in range(cols):
            x1 = int(grid_start_x + col * cell_size)
            y1 = int(grid_start_y + row * cell_size)
            x2 = int(x1 + cell_size)
            y2 = int(y1 + cell_size)
            thickness = 3
            #rectangle
            cv2.rectangle(marked_image, (x1, y1), (x2, y2), (255, 105, 65), thickness)
            
            #text
            text = str(counts[row, col])
            
            #getting the length of the text so that it will be in the middle of the block
            #print(thickness)
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            
            #put it in the midpoint
            text_x = int(x1 + (cell_size - text_size[0]) // 2)
            text_y = int(y1 + (cell_size + text_size[1]) // 2)
            
            #place text
            cv2.putText(marked_image, text, (text_x, text_y), font, font_scale, (255, 105, 65), thickness)
     
    ordered_counts = split_and_process(counts)
    return counts, marked_image, ordered_counts


def stretch_and_gray(original_image, lower_bound, upper_bound, show_images=False):
    """Stretch image intensity and convert to grayscale.
    
    :param lower_bound: Lower bound for intensity stretching
    :param upper_bound: Upper bound for intensity stretching"""
    # stretchedBAD = skimage.exposure.rescale_intensity(original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)).astype(np.uint8)
    # blurredBAD = cv2.GaussianBlur(stretchedBAD, (0, 0), sigmaX=5, sigmaY=5)
    # gray_imageBAD= cv2.cvtColor(blurredBAD, cv2.COLOR_BGR2GRAY)
    lower_bound, upper_bound = analyze_tonal_range(original_image)

    # print("Lower and upper bounds" + str(lower_bound) +"       "+  str(upper_bound))
    stretched = skimage.exposure.rescale_intensity(original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)).astype(np.uint8)
    idealContrast = int(-0.1813*(upper_bound -lower_bound)+25.113)
    idealContrast = max(idealContrast,2)
    idealContrast = min(idealContrast,20)
    #stretched = skimage.exposure.rescale_intensity(original_image, in_range=(72, 216), out_range=(0, 255)).astype(np.uint8)
    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=5, sigmaY=5)
    # blurredEdges = cv2.bilateralFilter(stretched, d=9, sigmaColor=75, sigmaSpace=75)
    # blurred = cv2.fastNlMeansDenoising(stretched, h=10, templateWindowSize=7, searchWindowSize=21)
    # blurredEdges3 = cv2.edgePreservingFilter(stretched, flags=1, sigma_s=60, sigma_r=0.4)
    # blurredEdges4 = cv2.medianBlur(stretched, ksize=5)
    # gray_image_notBlurred = cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY)
    gray_image= cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    #gray_image = cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('stretched', resize_for_display(stretched))
    if show_images:
        cv2.imshow('original_image', resize_for_display(original_image))
        #cv2.imshow('stretched', resize_for_display(stretched))
        # cv2.imshow('GaussianBlur', resize_for_display(blurred))
        # cv2.imshow('bilateralFilter', resize_for_display(blurredEdges))
        # cv2.imshow('fastNlMeansDenoising', resize_for_display(blurredEdges2))
        # cv2.imshow('edgePreservingFilter', resize_for_display(blurredEdges3))
        # cv2.imshow('medianBlur', resize_for_display(blurredEdges4))

        #cv2.imshow('grayBlur', resize_for_display(gray_image))
        #cv2.imshow('gray', resize_for_display(gray_image_notBlurred))
    return stretched, blurred, gray_image, idealContrast
    
def binarize_and_overlay(gray_image, gray_imageBAD, original_image, contrastBAD,contrast=20, exclude_small_dots=15, show_images=False):
    """Binarize the grayscale image using Gaussian and mean thresholding, perform contour detection, and overlay results."""
    
    height, width = gray_image.shape
    block_size, divisor_c = 151, 15
    c = max(-50, min(int(-contrast), -1))

    
    # Mean thresholding
    mean_binary = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                        cv2.THRESH_BINARY, block_size, -18)
    mean_binaryBAD = cv2.adaptiveThreshold(gray_imageBAD, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                        cv2.THRESH_BINARY, block_size, contrastBAD)                                    
    
    # Function to process contours
    def process_contours(binary_image):
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        exclude_small_dots_area = int((width * (exclude_small_dots / 5000)) ** 2)
        processed_contours = []
        for cntr in contours:
            area = cv2.contourArea(cntr)
            if area > exclude_small_dots_area:
                processed_contours.append(cntr)
        return processed_contours

    # Process contours for both thresholding methods

    mean_contours = process_contours(mean_binary)
    mean_contoursBAD = process_contours(mean_binaryBAD)
    # Create masks for each set of contours

    mean_mask = np.zeros(gray_image.shape, dtype=np.uint8)
    mean_maskBAD = np.zeros(gray_image.shape, dtype=np.uint8)
    cv2.drawContours(mean_maskBAD, mean_contoursBAD, -1, 255, -1)
    cv2.drawContours(mean_mask, mean_contours, -1, 255, -1)

    # Find overlapping regions
    overlap_mask = cv2.bitwise_and(mean_maskBAD, mean_mask)

    # Create overlay image
    overlay_img = original_image.copy()

    # Draw contours with different colors
    cv2.drawContours(overlay_img, mean_contoursBAD, -1, (0, 255, 0), 2)  # Green for Gaussian
    cv2.drawContours(overlay_img, mean_contours, -1, (255, 0, 0), 2)  # Blue for Mean

    # Draw overlapping contours in red
    overlap_contours, _ = cv2.findContours(overlap_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay_img, overlap_contours, -1, (0, 0, 255), 2)  # Red for overlap

    # Create legend
    legend_img = np.ones((100, width, 3), dtype=np.uint8) * 255
    cv2.putText(legend_img, "Adaptive Strech and Contrast", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(legend_img, "Constant Strech and Contrast", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(legend_img, "Overlapping Regions", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Combine overlay and legend
    result_img = np.vstack((overlay_img, legend_img))

    if show_images:
        plt.figure(figsize=(12, 8))
        plt.imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
        plt.title("Thresholding Results Overlay")
        plt.axis('off')
        plt.show()

    return gaussian_binary, mean_binary, overlay_img, result_img

    

def binarize(gray_image, original_image, contrast = 20,excludeSmallDots = 15, show_images=False):
    """Binarize the grayscale image and perform contour detection."""
    
    block_size, divisor_c = 151, 15
    c = max(-50, min(int(-contrast), -1))
    ####CHANGE BACK LATER

    binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, block_size, c)   
    
    ############################################################################
    #CHANGE BACK LATER ONLY FOR TESTING GROUND TRUTH
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
        # gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        # binary_image = cv2.threshold(gray_image, 175, 255, cv2.THRESH_BINARY)[1]
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    ############################################################################
    contour_img = original_image.copy()
    final_binary = np.zeros_like(binary_image)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    height, width = binary_image.shape
    excludeSmallDots = int((width*(excludeSmallDots/5000))**2)
    #print(width)
    #print(excludeSmallDots)

    areas = [cv2.contourArea(cntr) for cntr in contours]
    median_area = np.median(areas) if areas else 0
    excludeSmallDots
    for cntr in contours:
        area = cv2.contourArea(cntr)
        if area > excludeSmallDots:
            cv2.drawContours(contour_img, [cntr], 0, (0,255,255), 2)
            cv2.drawContours(final_binary, [cntr], 0, 255, -1)



    if show_images:
        cv2.imshow('threshold', resize_for_display(binary_image))
        cv2.imshow('contours', resize_for_display(contour_img))
        cv2.imshow('final_binary', resize_for_display(final_binary))
        # cv2.imshow('threshold',(binary_image))
        # cv2.imshow('contours', (contour_img))
        # cv2.imshow('final_binary',(final_binary))

    return binary_image, contour_img, final_binary,block_size



#  d888b  d8888b.  .d8b.  d8888b. db   db 
# 88' Y8b 88  `8D d8' `8b 88  `8D 88   88 
# 88      88oobY' 88ooo88 88oodD' 88ooo88 
# 88  ooo 88`8b   88~~~88 88~~~   88~~~88 
# 88. ~8~ 88 `88. 88   88 88      88   88 
#  Y888P  88   YD YP   YP 88      YP   YP 

def split_and_process(array):
    # Split the array into three 8x4 arrays
    strain1 = [row[:4] for row in array]
    strain2 = [row[4:8] for row in array]
    strain3 = [row[8:] for row in array]

    # Dictionary to store processed strains
    processed_data = {
        "Strain 1": process_strain(strain1),
        "Strain 2": process_strain(strain2),
        "Strain 3": process_strain(strain3)
    }

    return processed_data

def process_strain(strain):
    order = [
        (1,1), (1,2), (1,3), (1,4), (2,1), (1,5), (2,2), (1,6), (2,3), (1,7), (2,4), (3,1),
        (1,8), (2,5), (3,2), (2,6), (3,3), (2,7), (3,4), (4,1), (2,8), (3,5), (4,2), (3,6),
        (4,3), (3,7), (4,4), (3,8), (4,5), (4,6), (4,7), (4,8)
    ]

    processed_list = []

    for col, row in order:
        if row <= 8 and col <= 4:
            processed_list.append(strain[row-1][col-1])

    return processed_list






