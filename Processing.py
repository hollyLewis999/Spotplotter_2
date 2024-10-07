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
######################################For scaling
COLOUMS = 12

#max radius = width/(dots across*2) 






# d8888b. d888888b .d8888. d8888b. db       .d8b.  db    db 
# 88  `8D   `88'   88'  YP 88  `8D 88      d8' `8b `8b  d8' 
# 88   88    88    `8bo.   88oodD' 88      88ooo88  `8bd8'  
# 88   88    88      `Y8b. 88~~~   88      88~~~88    88    
# 88  .8D   .88.   db   8D 88      88booo. 88   88    88    
# Y8888D' Y888888P `8888Y' 88      Y88888P YP   YP    YP 

def save_images_to_pdf(image_steps, output_path,dpi, num_images_to_save=None):
    """
    Save processed images to a PDF file with higher quality.
    
    :param image_steps: List of dictionaries containing processed images
    :param output_path: Path to save the PDF
    :param num_images_to_save: Number of images to save (None for all)
    :param dpi: DPI for image quality (default 300)
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    for i, step_images in enumerate(image_steps):
        y_offset = height - 0.5*inch
        x_offset = inch

        # Limit the number of images if specified
        images_to_save = list(step_images.items())[:num_images_to_save] if num_images_to_save else step_images.items()

        for j, (label, image) in enumerate(images_to_save):
            if j % 2 == 0 and j > 0:
                y_offset -= 2.25 * inch  # Reduced vertical gap
                x_offset = inch
            
            # Convert OpenCV image to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Calculate new size based on DPI
            width_pixels = int(2.5 * dpi)
            height_pixels = int(2 * dpi)
            
            # Resize image while maintaining aspect ratio
            pil_image.thumbnail((width_pixels, height_pixels), Image.LANCZOS)
            
            # Save image to memory buffer
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='PNG', dpi=(dpi, dpi))
            img_buffer.seek(0)
            
            # Draw the label above the image
            c.drawString(x_offset, y_offset, label)
            
            # Draw the image below the label
            c.drawImage(ImageReader(img_buffer), x_offset, y_offset - 2*inch, width=2.5*inch, height=2*inch)
            
            if j % 2 == 0:
                x_offset += 4 * inch

        c.showPage()

    c.save()

def resize_for_display(image, max_width=1280, max_height=720):
    """Resize image for display while maintaining aspect ratio."""
    h, w = image.shape[:2]
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image

# def combine_masks(circles_mask, gridlines_mask, yellow_areas_mask, counts_mask, lines_mask):
#     """Combine black and white masks into a single colored image."""
#     # Convert black and white masks to color (BGR)
#     circles_mask_color = cv2.cvtColor(circles_mask, cv2.COLOR_GRAY2BGR)
#     gridlines_mask_color = cv2.cvtColor(gridlines_mask, cv2.COLOR_GRAY2BGR)
#     yellow_areas_mask_color = cv2.cvtColor(yellow_areas_mask, cv2.COLOR_GRAY2BGR)
#     counts_mask_color = cv2.cvtColor(counts_mask, cv2.COLOR_GRAY2BGR)
#     lines_mask_color = cv2.cvtColor(lines_mask, cv2.COLOR_GRAY2BGR)
    
#     # Set colors
#     circles_mask_color[:, :] = [0, 255, 0]  # Green for circles
#     gridlines_mask_color[:, :] = [255, 0, 0]  # Red for gridlines
#     yellow_areas_mask_color[:, :] = [0, 255, 255]  # Yellow for yellow areas
#     line_mask_color[:, :] = [0, 255, 255]  # Yellow for yellow areas
#     # Initialize the combined mask
#     combined_mask = np.zeros_like(circles_mask_color)

#     # Combine masks
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, circles_mask_color, 1.0, 0)
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, gridlines_mask_color, 1.0, 0)
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, yellow_areas_mask_color, 1.0, 0)
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, counts_mask_color, 1.0, 0)
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, line_mask_color, 1.0, 0)
#     return combined_mask


#  .o88b. d888888b d8888b.  .o88b. db      d88888b .d8888. 
# d8P  Y8   `88'   88  `8D d8P  Y8 88      88'     88'  YP 
# 8P         88    88oobY' 8P      88      88ooooo `8bo.   
# 8b         88    88`8b   8b      88      88~~~~~   `Y8b. 
# Y8b  d8   .88.   88 `88. Y8b  d8 88booo. 88.     db   8D 
#  `Y88P' Y888888P 88   YD  `Y88P' Y88888P Y88888P `8888Y' 
                                                         
#max area of the blocks = pi*maxr^2
def findBlobs(binary_image, min_area, max_area, thickness=2):
    #what is the max area?

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a color image to draw on
    result_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    # cv2.imshow('contours', resize_for_display(result_image))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    x_coords =[]
    y_coords=[]
    for contour in contours:
        # Calculate area of the contour
        area = cv2.contourArea(contour)
  
        if min_area <= area <= max_area:
            # Calculate circularity
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter)

            # Check if shape is roughly square or circular
            if circularity > 0.30:  # Adjust this threshold as needed
                # Find the center of the contour
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    
                    # # Draw a red X at the center
                    # cv2.drawMarker(result_image, (cX, cY), (0, 0, 255), 
                    #                cv2.MARKER_TILTED_CROSS, thickness=thickness)
                    # print(cX)
                    x_coords.append(cX)
                    y_coords.append(cY)
                    # print(x_coords)
    return x_coords,y_coords,result_image


def detect_and_draw_circles_origional(binary_image, gray_image, noClusters, min_radius=50, max_radius=140, param1=50, param2=28):
    """Detect circles in the image and draw grid, yellow areas, and counts."""
    height, width = binary_image.shape
    max_radius = int(width/24)
    min_radius = int(max_radius/3)
    max_area = max_radius**2*(math.pi)
    min_area = min_radius**2*(math.pi)
    # print("radiuses")
    # print(max_radius)
    # print(min_radius)
    minDist = min_radius*2
    circles = cv2.HoughCircles(
        gray_image,
        cv2.HOUGH_GRADIENT,
        dp=0.9,
        minDist=minDist,
        param1=param1,
        param2=param2,
        minRadius=min_radius,
        maxRadius=max_radius
    )
    counts = np.zeros((8, 12))

    if circles is None:
        print("No circles detected")
        noClusters = True

    if noClusters:
        print("Using blob detection")
        x_coords, y_coords, marked_image = findBlobs(binary_image, min_area, max_area)
    elif circles is not None:
        circles = np.round(circles[0, :]).astype(int)
        x_coords = circles[:, 0]
        y_coords = circles[:, 1]
        marked_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    
    grid_calculated = False
    while not grid_calculated:
        try:
            grid_start_x, grid_start_y, cell_size, slant_angle = calculate_grid(x_coords, y_coords, width, height, binary_image, gray_image, debug=False)
            grid_calculated = True
        except ValueError as e:
            print(f"Error in grid calculation: {e}")
            print("Attempting blob detection with looser parameters")
            x_coords, y_coords, marked_image = findBlobs(binary_image,min_area/1.5, max_area*1.5)  # Looser parametersf
            if len(x_coords) < 2 or len(y_coords) < 2:
                raise ValueError("Unable to detect sufficient blobs for grid calculation")

    # # Draw grid lines
    # for i in range(13):
    #     x = int(grid_start_x + i * cell_size)
    #     cv2.line(marked_image, (x, 0), (x, height), (255, 0, 0), 3)
    
    # for i in range(9):
    #     y = int(grid_start_y + i * cell_size)
    #     cv2.line(marked_image, (0, y), (width, y), (255, 0, 0), 3)

    counts, marked_image, ordered_counts = quantify_grid(binary_image, marked_image, grid_start_x, grid_start_y, cell_size)
    
    # if not noClusters and circles is not None:
    #     for (x, y, r) in circles:
    #         cv2.circle(marked_image, (x, y), r, (0, 0, 255), 2)
    #         cv2.circle(marked_image, (x, y), 2, (0, 0, 255), 3)
    
    # cv2.imshow("marked_image", resize_for_display(marked_image)) 
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # x_coords, y_coords, marked_image = findBlobs(binary_image, min_area, max_area)
    # cv2.imshow ("marked_image", resize_for_display(marked_image)) 
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return counts, marked_image,ordered_counts

def detect_and_draw_circles(binary_image, gray_image, noClusters, min_radius=50, max_radius=140, param1=50, param2=28):
    height, width = binary_image.shape
    max_radius = int(width/24)
    min_radius = int(max_radius/3)
    max_area = max_radius**2*(math.pi)
    min_area = min_radius**2*(math.pi)
    # print("radiuses")
    # print(max_radius)
    # print(min_radius)
    counts = np.zeros((8, 12))

    x_coords, y_coords, marked_image = findBlobs(binary_image, min_area, max_area)
    grid_calculated = False
    while not grid_calculated:
        try:
            grid_start_x, grid_start_y, cell_size, slant_angle = calculate_grid(x_coords, y_coords, width, height, binary_image, gray_image, debug=False)
            grid_calculated = True
        except ValueError as e:
            print(f"Error in grid calculation: {e}")
            print("Attempting blob detection with looser parameters")
            min_area = min_area/1.2
            max_area = max_area*1.2
            x_coords, y_coords, marked_image = findBlobs(binary_image,min_area, max_area)  # Looser parameters
            if len(x_coords) < 2 or len(y_coords) < 2:
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
    """Calculate grid parameters based on detected circle or blob coordinates."""
    
    def find_clusters(coords, min_count=2):
        sorted_coords = np.sort(coords)
        diffs = np.diff(sorted_coords)
        median_diff = np.median(diffs)
        threshold = max(median_diff *2,10) # Adjust this factor if needed
        print(threshold)
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
    
    x_diffs = np.diff(x_clusters)
    y_diffs = np.diff(y_clusters)
    # print("DIFFERECES")
    # print(x_diffs)
    # lowerBound = 200
    # upperBound = 320
    #######CHANGES HERE
    lowerBound = width/30
    upperBound = width/10
    filtered_x_diffs = [x for x in x_diffs if lowerBound <= x <= upperBound]
    filtered_y_diffs = [y for y in y_diffs if lowerBound <= y <= upperBound]
    if not filtered_x_diffs and not filtered_y_diffs:
        raise ValueError("No valid differences found within bounds")
    
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

    # Calculate horizontal slant
    slope, _ = np.polyfit(x_coords, y_coords, 1)
    angle = np.arctan(slope)
    max_angle = np.radians(8)
    slant_angle = np.clip(angle, -max_angle, max_angle)
    
    grid_start_x = min(x_clusters) - cell_size / 2
    grid_start_y = min(y_clusters) - cell_size / 2
    
    grid_width = cell_size * 12
    grid_height = cell_size * 8
    
    if grid_start_x + grid_width > width:
        grid_start_x = width - grid_width
    if grid_start_y + grid_height > height:
        grid_start_y = height - grid_height
    
    if debug:
        plt.figure(figsize=(10, 10))
        plt.scatter(x_coords, y_coords, c='blue', label='Original points')
        for i in range(13):  # Draw vertical lines
            x = grid_start_x + i * cell_size
            plt.plot([x, x + np.tan(slant_angle) * grid_height], 
                     [grid_start_y, grid_start_y + grid_height], 
                     'r-', alpha=0.5)
        for j in range(9):  # Draw horizontal lines
            y = grid_start_y + j * cell_size
            plt.plot([grid_start_x, grid_start_x + grid_width],
                     [y, y + np.tan(slant_angle) * grid_width],
                     'r-', alpha=0.5)
        plt.title('Grid Overlay')
        plt.legend()
        plt.show()
    
    return grid_start_x, grid_start_y, cell_size, slant_angle

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
            
            if outside_area <= 0.2 * total_area:
                # Count the entire blob in the main cell and color it light grey
                counts[main_row, main_col] += total_area
                marked_image[component] = [255, 255, 255]  # Light grey
            else:

                pass
    for count in counts:
        count = count/(width**2)
    # Draw grid and add count text
    for row in range(rows):
        for col in range(cols):
            x1 = int(grid_start_x + col * cell_size)
            y1 = int(grid_start_y + row * cell_size)
            x2 = int(x1 + cell_size)
            y2 = int(y1 + cell_size)
            
            # Draw rectangle for the grid cell
            cv2.rectangle(marked_image, (x1, y1), (x2, y2), (255, 105, 65), 2)
            
            # The text to be displayed
            text = str(counts[row, col])
            
            # Get the text size to calculate the center position
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            thickness = 3
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            
            # Calculate the centered position for the text and cast to int
            text_x = int(x1 + (cell_size - text_size[0]) // 2)
            text_y = int(y1 + (cell_size + text_size[1]) // 2)
            
            # Draw the text in the center of the block
            cv2.putText(marked_image, text, (text_x, text_y), font, font_scale, (255, 105, 65), thickness)

    ordered_counts = split_and_process(counts)
    return counts, marked_image, ordered_counts






# d8888b. d888888b d8b   db  .d8b.  d8888b. d888888b d88888D d88888b 
# 88  `8D   `88'   888o  88 d8' `8b 88  `8D   `88'   YP  d8' 88'     
# 88oooY'    88    88V8o 88 88ooo88 88oobY'    88       d8'  88ooooo 
# 88~~~b.    88    88 V8o88 88~~~88 88`8b      88      d8'   88~~~~~ 
# 88   8D   .88.   88  V888 88   88 88 `88.   .88.    d8' db 88.     
# Y8888P' Y888888P VP   V8P YP   YP 88   YD Y888888P d88888P Y88888P 

def stretch_and_gray(original_image, lower_bound, upper_bound, show_images=False):
    """Stretch image intensity and convert to grayscale.
    
    :param lower_bound: Lower bound for intensity stretching
    :param upper_bound: Upper bound for intensity stretching"""
    stretched = skimage.exposure.rescale_intensity(original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)).astype(np.uint8)
    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=5, sigmaY=5)
    # blurredEdges = cv2.bilateralFilter(stretched, d=9, sigmaColor=75, sigmaSpace=75)
    # blurred = cv2.fastNlMeansDenoising(stretched, h=10, templateWindowSize=7, searchWindowSize=21)
    # blurredEdges3 = cv2.edgePreservingFilter(stretched, flags=1, sigma_s=60, sigma_r=0.4)
    # blurredEdges4 = cv2.medianBlur(stretched, ksize=5)
    # gray_image_notBlurred = cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY)
    gray_image= cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    #gray_image = cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY)

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
    return stretched, blurred, gray_image
    
def binarize_and_overlay(gray_image, original_image, contrast=20, exclude_small_dots=15, show_images=False):
    """Binarize the grayscale image using Gaussian and mean thresholding, perform contour detection, and overlay results."""
    
    height, width = gray_image.shape
    block_size, divisor_c = 151, 15
    c = max(-50, min(int(-contrast), -1))
    
    # Gaussian thresholding
    gaussian_binary = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, block_size, -11)
    
    # Mean thresholding
    mean_binary = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                        cv2.THRESH_BINARY, block_size, -20)
    
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
    gaussian_contours = process_contours(gaussian_binary)
    mean_contours = process_contours(mean_binary)

    # Create masks for each set of contours
    gaussian_mask = np.zeros(gray_image.shape, dtype=np.uint8)
    mean_mask = np.zeros(gray_image.shape, dtype=np.uint8)

    cv2.drawContours(gaussian_mask, gaussian_contours, -1, 255, -1)
    cv2.drawContours(mean_mask, mean_contours, -1, 255, -1)

    # Find overlapping regions
    overlap_mask = cv2.bitwise_and(gaussian_mask, mean_mask)

    # Create overlay image
    overlay_img = original_image.copy()

    # Draw contours with different colors
    cv2.drawContours(overlay_img, gaussian_contours, -1, (0, 255, 0), 2)  # Green for Gaussian
    cv2.drawContours(overlay_img, mean_contours, -1, (255, 0, 0), 2)  # Blue for Mean

    # Draw overlapping contours in red
    overlap_contours, _ = cv2.findContours(overlap_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay_img, overlap_contours, -1, (0, 0, 255), 2)  # Red for overlap

    # Create legend
    legend_img = np.ones((100, width, 3), dtype=np.uint8) * 255
    cv2.putText(legend_img, "Gaussian Thresholding", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(legend_img, "Mean Thresholding", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
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
    # gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    # binary_image = cv2.threshold(gray_image, 175, 255, cv2.THRESH_BINARY)[1]

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


def plotScatter(counts):
  dilutionSeries = [0, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
  
  plt.figure(figsize=(10, 6))
  
  # Logarithmic scale for x-axis only
  plt.semilogx( dilutionSeries,counts, 'x', color='blue', markersize=8)
  
  # Grid for better readability
  plt.grid(True, which="both", linestyle='--', alpha=0.5)
  
  # Axis labels and title
  plt.ylabel('Counts', fontsize=12)
  plt.xlabel('Dilution Series', fontsize=12)
  plt.title('Scatter Plot with Logarithmic X-Axis', fontsize=14)  # Update title
  
  # Adjust plot margins
  plt.tight_layout()
  
  plt.show()






# d888888b d88888b .d8888. d888888b d888888b d8b   db  d888b  
# `~~88~~' 88'     88'  YP `~~88~~'   `88'   888o  88 88' Y8b 
#    88    88ooooo `8bo.      88       88    88V8o 88 88      
#    88    88~~~~~   `Y8b.    88       88    88 V8o88 88  ooo 
#    88    88.     db   8D    88      .88.   88  V888 88. ~8~ 
#    YP    Y88888P `8888Y'    YP    Y888888P VP   V8P  Y888P  


# #testing Prespective

# path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/GroundTruth.png"
# original_image = cv2.imread(path)
# binary_image = cv2.threshold(original_image, 127, 255, cv2.THRESH_BINARY) 
# origional_perspective,gray_image_perspective, binary_perspective,marked_image_1 = correct_perspective_pipeline(original_image,binary_image, binary_image)
# result_grid, marked_image = detect_and_draw_circles(binary_perspective, gray_image_perspective)

# # image_steps.append({
# #     "Original Image": original_image,
# #     # "Stretched Image": stretched,
# #     # "Blurred Image": blurred,
# #     # "Grayscale Image": gray_image,
# #     #"Binary Image": binary_image,
# #     "Contour Image": contour_img,
# #     "Final Binary Image": final_binary,
# #     "Marked Image with All Elements": marked_image
# # })
# cv2.imshow("original_image", resize_for_display(original_image))
# cv2.imshow("origional_perspective", resize_for_display(origional_perspective))
# cv2.imshow("binary_perspective", resize_for_display(binary_perspective ))
# cv2.imshow("marked_image_1", resize_for_display(marked_image_1))
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# print(f"Completed image {i}")





# image_steps = []
# print("Starting Analysis")
# for i in range(7):
#     path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/"
#     image_path = path + str(i) + ".jpg"
#     original_image = cv2.imread(image_path)
#     origional_perspective= correct_perspective_pipeline(original_image)
#     stretched, blurred, gray_image = stretch_and_gray(origional_perspective, 90, 150)
#     binary_image, contour_img, final_binary, block_size = binarize(gray_image, origional_perspective)
    
#     result_grid, marked_image = detect_and_draw_circles(binary, gray_image)
    
#     # image_steps.append({
#     #     "Original Image": original_image,
#     #     # "Stretched Image": stretched,
#     #     # "Blurred Image": blurred,
#     #     # "Grayscale Image": gray_image,
#     #     #"Binary Image": binary_image,
#     #     "Contour Image": contour_img,
#     #     "Final Binary Image": final_binary,
#     #     "Marked Image with All Elements": marked_image
#     # })
#     cv2.imshow("original_image", resize_for_display(original_image))
#     cv2.imshow("origional_perspective", resize_for_display(origional_perspective))
#     cv2.imshow("binary_perspective", resize_for_display(binary))
#     cv2.imshow("marked_image_1", resize_for_display(marked_image_1))
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#     print(f"Completed image {i}")

# Save images to PDF
# pdf_output_path = os.path.join(path, "FullDataSetSkewVaiableThreshold.pdf")
# print("Saving Images")
# save_images_to_pdf(image_steps, pdf_output_path, 300, num_images_to_save=4) 
# print(f"All images saved to: {pdf_output_path}")



# print("Starting Analysis")
# for i in range(1):
#     path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/"
#     image_path = path + str(i) + ".jpg"
#     original_image = cv2.imread(image_path)

#     stretched, blurred, gray_image = stretch_and_gray(original_image, 90, 150)
#     binary_image, contour_img, final_binary = binarize(gray_image, original_image)
#     result_grid, marked_image = detect_and_draw_circles(final_binary, gray_image)
    
#     # Save the images
#     cv2.imwrite(path + 'low_original_image.png', original_image)
#     cv2.imwrite(path + 'BADstretched.png', stretched)
#     cv2.imwrite(path + 'blurred.png', blurred)
#     cv2.imwrite(path + 'gray_image.png', gray_image)
#     cv2.imwrite(path + 'contour_img.png', contour_img)
#     cv2.imwrite(path + 'final_binary.png', final_binary)
#     cv2.imwrite(path + 'marked_image.png', marked_image)

# print("done")
