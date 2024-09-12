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

def combine_masks(circles_mask, gridlines_mask, yellow_areas_mask, counts_mask, lines_mask):
    """Combine black and white masks into a single colored image."""
    # Convert black and white masks to color (BGR)
    circles_mask_color = cv2.cvtColor(circles_mask, cv2.COLOR_GRAY2BGR)
    gridlines_mask_color = cv2.cvtColor(gridlines_mask, cv2.COLOR_GRAY2BGR)
    yellow_areas_mask_color = cv2.cvtColor(yellow_areas_mask, cv2.COLOR_GRAY2BGR)
    counts_mask_color = cv2.cvtColor(counts_mask, cv2.COLOR_GRAY2BGR)
    lines_mask_color = cv2.cvtColor(lines_mask, cv2.COLOR_GRAY2BGR)
    
    # Set colors
    circles_mask_color[:, :] = [0, 255, 0]  # Green for circles
    gridlines_mask_color[:, :] = [255, 0, 0]  # Red for gridlines
    yellow_areas_mask_color[:, :] = [0, 255, 255]  # Yellow for yellow areas
    line_mask_color[:, :] = [0, 255, 255]  # Yellow for yellow areas
    # Initialize the combined mask
    combined_mask = np.zeros_like(circles_mask_color)

    # Combine masks
    combined_mask = cv2.addWeighted(combined_mask, 1.0, circles_mask_color, 1.0, 0)
    combined_mask = cv2.addWeighted(combined_mask, 1.0, gridlines_mask_color, 1.0, 0)
    combined_mask = cv2.addWeighted(combined_mask, 1.0, yellow_areas_mask_color, 1.0, 0)
    combined_mask = cv2.addWeighted(combined_mask, 1.0, counts_mask_color, 1.0, 0)
    combined_mask = cv2.addWeighted(combined_mask, 1.0, line_mask_color, 1.0, 0)
    return combined_mask


#  .o88b. d888888b d8888b.  .o88b. db      d88888b .d8888. 
# d8P  Y8   `88'   88  `8D d8P  Y8 88      88'     88'  YP 
# 8P         88    88oobY' 8P      88      88ooooo `8bo.   
# 8b         88    88`8b   8b      88      88~~~~~   `Y8b. 
# Y8b  d8   .88.   88 `88. Y8b  d8 88booo. 88.     db   8D 
#  `Y88P' Y888888P 88   YD  `Y88P' Y88888P Y88888P `8888Y' 
                                                         

def findBlobs(binary_image, min_area, max_area, thickness=2):
    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a color image to draw on
    result_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
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
                    
                    # Draw a red X at the center
                    cv2.drawMarker(result_image, (cX, cY), (0, 0, 255), 
                                   cv2.MARKER_TILTED_CROSS, thickness=thickness)
                    # print(cX)
                    x_coords.append(cX)
                    y_coords.append(cY)
                    # print(x_coords)
    return x_coords,y_coords,result_image

def detect_and_draw_circles(binary_image, gray_image, min_radius=50, max_radius=160, param1 =50, param2 =28):
    """Detect circles in the image and draw grid, yellow areas, and counts."""
    circles = cv2.HoughCircles(
        gray_image,
        cv2.HOUGH_GRADIENT,
        dp=0.9, #higher for stricter
        minDist=200, #distance between circles
        param1 = param1,
        param2 = param2, #The smaller it is, the more false circles may be detected
        minRadius=min_radius,
        maxRadius=max_radius
    )
    counts = np.zeros((8, 12))

    if circles is None:
        print("No circles detected")
        return None, None
    elif( len(circles[0]) <8):
        print("would do blobs")
        x_coords, y_coords,result_image = findBlobs(binary_image, 1500,20000)
        marked_image = result_image
    elif circles is not None:
        circles = np.round(circles[0, :]).astype(int)
        #marked_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
       # height, width = gray_image.shape

        x_coords = circles[:, 0]
        y_coords = circles[:, 1]
        marked_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    height, width = gray_image.shape
    try:
        grid_start_x, grid_start_y, cell_size, slant_angle = calculate_grid(x_coords, y_coords, width, height, debug=False)

        # Detect multi-block areas first
        colored_image, multi_block_mask = detect_multi_block_areas(binary_image, grid_start_x, grid_start_y, cell_size)
        
        # Combine the colored_image (with yellow areas) and the marked_image
        marked_image = colored_image

        # Draw grid lines
        for i in range(13):
            x = int(grid_start_x + i * cell_size)
            cv2.line(marked_image, (x, 0), (x, height), (255, 0, 0), 3)
        
        for i in range(9):
            y = int(grid_start_y + i * cell_size)
            cv2.line(marked_image, (0, y), (width, y), (255, 0, 0), 3)

        # Quantify grid and draw counts
        counts = np.zeros((8, 12), dtype=int)
        for row in range(8):
            for col in range(12):
                x1 = int(grid_start_x + col * cell_size)
                y1 = int(grid_start_y + row * cell_size)
                x2 = int(x1 + cell_size)
                y2 = int(y1 + cell_size)
                
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                cell = binary_image[y1:y2, x1:x2]
                cell_mask = multi_block_mask[y1:y2, x1:x2]
                
                # Count white pixels only in areas not marked as multi-block
                white_pixels = np.sum((cell == 255) & (cell_mask == 0))
                counts[row, col] = white_pixels
                
                text_x = int(x1 + cell_size / 2)
                text_y = int(y1 + cell_size / 2)
                
                cv2.putText(marked_image, str(white_pixels), (text_x - 20, text_y + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Draw circles last to ensure they're visible
        for (x, y, r) in circles:
            cv2.circle(marked_image, (x, y), r, (0, 0, 255), 2)
            cv2.circle(marked_image, (x, y), 2, (0, 0, 255), 3)

    except ValueError:
        print("Not enough valid clusters found to calculate grid. Circles will be detected without drawing a grid.")
        # Draw circles if grid calculation fails
        if len(circles[0]) >7:
            for (x, y, r) in circles:
                cv2.circle(marked_image, (x, y), r, (0, 0, 255), 2)
                cv2.circle(marked_image, (x, y), 2, (0, 0, 255), 3)

    return counts, marked_image

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
    gray_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    #gray_image = cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY)

    if show_images:
        cv2.imshow('stretched', resize_for_display(stretched))
        cv2.imshow('blurred', resize_for_display(blurred))
        cv2.imshow('gray', resize_for_display(gray_image))
    return stretched, blurred, gray_image


def binarize(gray_image, original_image, contrast = 20,excludeSmallDots = 1000, show_images=False):
    """Binarize the grayscale image and perform contour detection."""
   
    block_size, divisor_c = 151, 15
    c = max(-50, min(int(-contrast), -1))
    binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, block_size, c)
    contour_img = original_image.copy()
    final_binary = np.zeros_like(binary_image)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    areas = [cv2.contourArea(cntr) for cntr in contours]
    median_area = np.median(areas) if areas else 0
    
    for cntr in contours:
        area = cv2.contourArea(cntr)
        if area > excludeSmallDots:
            cv2.drawContours(contour_img, [cntr], 0, (0,255,255), 2)
            cv2.drawContours(final_binary, [cntr], 0, 255, -1)



    if show_images:
        cv2.imshow('threshold', resize_for_display(binary_image))
        cv2.imshow('contours', resize_for_display(contour_img))
        cv2.imshow('final_binary', resize_for_display(final_binary))

    return binary_image, contour_img, final_binary,block_size



# d888b  d8888b. d888888b d8888b. 
# 88' Y8b 88  `8D   `88'   88  `8D 
# 88      88oobY'    88    88   88 
# 88  ooo 88`8b      88    88   88 
# 88. ~8~ 88 `88.   .88.   88  .8D 
#  Y888P  88   YD Y888888P Y8888D' 
def calculate_grid(x_coords, y_coords, width, height, debug=False):
    """Calculate grid parameters based on detected circle coordinates."""
    
    def find_clusters(coords, min_count=2):
        sorted_coords = np.sort(coords)
        diffs = np.diff(sorted_coords)
        median_diff = np.median(diffs)
        threshold = median_diff * 2  # Adjust this factor if needed
        
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

    x_clusters = find_clusters(x_coords)
    y_clusters = find_clusters(y_coords)
    
    if len(x_clusters) < 2 or len(y_clusters) < 2:
        raise ValueError("Not enough valid clusters found to calculate grid")
    
    x_diffs = np.diff(x_clusters)
    y_diffs = np.diff(y_clusters)
    avg_x_diff = np.mean(x_diffs)
    avg_y_diff = np.mean(y_diffs)
    cell_size = min(avg_x_diff, avg_y_diff)
    
    # Calculate horizontal slant
    slope, _ = np.polyfit(x_coords, y_coords, 1)
    angle = np.arctan(slope)
    max_angle = np.radians(8)
    slant_angle = np.clip(angle, -max_angle, max_angle)
    
    grid_start_x = x_clusters[0] - cell_size / 2
    grid_start_y = y_clusters[0] - cell_size / 2
    
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
    Quantify the grid by counting white pixels in each cell, excluding multi-block areas.
    """
    height, width = binary_image.shape
    rows, cols = 8, 12  # 8x12 grid
    
    # Detect multi-block areas
    colored_image, multi_block_mask = detect_multi_block_areas(binary_image, grid_start_x, grid_start_y, cell_size)
    
    # Combine the colored_image (with yellow areas) and the marked_image
    marked_image = cv2.addWeighted(marked_image, 1, colored_image, 0.5, 0)
    
    counts = np.zeros((rows, cols), dtype=int)
    
    for row in range(rows):
        for col in range(cols):
            x1 = int(grid_start_x + col * cell_size)
            y1 = int(grid_start_y + row * cell_size)
            x2 = int(x1 + cell_size)
            y2 = int(y1 + cell_size)
            
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)
            
            cell = binary_image[y1:y2, x1:x2]
            cell_mask = multi_block_mask[y1:y2, x1:x2]
            
            # Count white pixels only in areas not marked as multi-block
            white_pixels = np.sum((cell == 255) & (cell_mask == 0))
            counts[row, col] = white_pixels
            
            text_x = int(x1 + cell_size / 2)
            text_y = int(y1 + cell_size / 2)
            
            cv2.putText(marked_image, str(white_pixels), (text_x - 20, text_y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    
    return counts, marked_image

def detect_multi_block_areas(binary_image, grid_start_x, grid_start_y, cell_size):
    """
    Detect areas spanning multiple grid blocks and color them yellow if at least 20% is outside the primary block.
    """
    height, width = binary_image.shape
    rows, cols = 8, 12  # 8x12 grid
   
    # Create a colored image from the binary image
    colored_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
   
    # Create a mask for multi-block areas
    multi_block_mask = np.zeros_like(binary_image)
   
    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   
    for contour in contours:
        # Get bounding box of the contour
        x, y, w, h = cv2.boundingRect(contour)
        contour_area = cv2.contourArea(contour)
       
        # Determine the primary grid cell
        primary_col = int((x + w/2 - grid_start_x) / cell_size)
        primary_row = int((y + h/2 - grid_start_y) / cell_size)
       
        # Calculate area of contour inside primary cell
        cell_x1 = int(grid_start_x + primary_col * cell_size)
        cell_y1 = int(grid_start_y + primary_row * cell_size)
        cell_x2 = int(cell_x1 + cell_size)
        cell_y2 = int(cell_y1 + cell_size)
       
        cell_mask = np.zeros_like(binary_image)
        cv2.rectangle(cell_mask, (cell_x1, cell_y1), (cell_x2, cell_y2), 255, -1)
        
        contour_mask = np.zeros_like(binary_image)
        cv2.drawContours(contour_mask, [contour], 0, 255, -1)
        
        area_inside_primary = np.sum((contour_mask > 0) & (cell_mask > 0))
        
        # Check if at least 20% of the contour is outside the primary cell
        if contour_area >0:
            if area_inside_primary / contour_area <= 0.8:
                # Color the area yellow
                cv2.drawContours(colored_image, [contour], 0, (0, 255, 255), -1)
                cv2.drawContours(multi_block_mask, [contour], 0, 255, -1)
   
    return colored_image, multi_block_mask


# d8888b. d88888b d8888b. .d8888. d8888b. d88888b  .o88b. d888888b d888888b db    db d88888b 
# 88  `8D 88'     88  `8D 88'  YP 88  `8D 88'     d8P  Y8 `~~88~~'   `88'   88    88 88'     
# 88oodD' 88ooooo 88oobY' `8bo.   88oodD' 88ooooo 8P         88       88    Y8    8P 88ooooo 
# 88~~~   88~~~~~ 88`8b     `Y8b. 88~~~   88~~~~~ 8b         88       88    `8b  d8' 88~~~~~ 
# 88      88.     88 `88. db   8D 88      88.     Y8b  d8    88      .88.    `8bd8'  88.     
# 88      Y88888P 88   YD `8888Y' 88      Y88888P  `Y88P'    YP    Y888888P    YP    Y88888P

def detect_lines(image):
    stretched, blurred, gray_image = stretch_and_gray(image, 90, 150)
    binary_image, contour_img, final_binary, block_size = binarize(gray_image, image)
    gray_image = (binary_image * 255).astype(np.uint8) 
    lines = cv2.HoughLinesP(gray_image, 1, np.pi/180, threshold=50, minLineLength=1000, maxLineGap=10)
    return lines

def draw_lines_and_measure(image, vertical_lines):
    marked_image = image.copy()
    if vertical_lines is not None:
        for i, line in enumerate(vertical_lines):
            x1, y1, x2, y2 = line
            color = (0, 255, 0) if i in [1, 2] else (0, 0, 255)  # Green for inner lines, Red for outer
            cv2.line(marked_image, (x1, y1), (x2, y2), color, 2)
    
    # Measure distance between inner vertical lines
    if len(vertical_lines) >= 4:
        left_inner = vertical_lines[1]
        right_inner = vertical_lines[2]
        distance = abs(left_inner[0] - right_inner[0])  # Using x-coordinate of the start point
        
        # Draw measurement line
        mid_y = image.shape[0] // 2
        cv2.line(marked_image, (left_inner[0], mid_y), (right_inner[0], mid_y), (255, 255, 0), 2)
        cv2.putText(marked_image, f"{distance} pixels", 
                    (left_inner[0] + 10, mid_y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    return marked_image
def classify_lines(lines, image_shape):
    vertical_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            if abs(angle) > 80:  # More strict angle for vertical lines
                if length > image_shape[0] * 0.5:  # Longer lines
                    vertical_lines.append((x1, y1, x2, y2))
    
    # Sort vertical lines from left to right
    vertical_lines.sort(key=lambda line: min(line[0], line[2]))
    
    return vertical_lines

def correct_perspective(image, vertical_lines):
    h, w = image.shape[:2]
    
    if len(vertical_lines) < 2:
        print("Not enough vertical lines detected for perspective correction.")
        return image
    
    # Use the leftmost and rightmost vertical lines for perspective correction
    left_line = vertical_lines[0]
    right_line = vertical_lines[-1]
    
    # Calculate the angles of the lines
    left_angle = np.arctan2(left_line[3] - left_line[1], left_line[2] - left_line[0])
    right_angle = np.arctan2(right_line[3] - right_line[1], right_line[2] - right_line[0])
    
    # Calculate the average angle to determine the tilt
    avg_angle = (left_angle + right_angle) / 2
    
    # Calculate the shift at the top of the image
    left_shift = int(h * np.tan(avg_angle))
    right_shift = int(h * np.tan(avg_angle))
    
    # Define source points (top-left, top-right, bottom-right, bottom-left)
    src_pts = np.float32([
        [left_line[0] + left_shift, 0],
        [right_line[0] + right_shift, 0],
        [right_line[2], h - 1],
        [left_line[2], h - 1]
    ])
    
    # Define destination points
    dst_pts = np.float32([
        [left_line[2], 0],
        [right_line[2], 0],
        [right_line[2], h - 1],
        [left_line[2], h - 1]
    ])
    
    # Get the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    
    # Apply the perspective transform
    result = cv2.warpPerspective(image, matrix, (w, h))
    
    return result

def correct_perspective_pipeline(original_image):
    # Process the binarized image
    lines = detect_lines(original_image)
    if lines is None:
        print("No lines detected in the binarized image.")
        return original_image
    
    vertical_lines = classify_lines(lines, original_image.shape)
    
    if len(vertical_lines) < 2:
        print("Not enough vertical lines detected for perspective correction.")
        return original_image
    
    corrected_original_image = correct_perspective(original_image, vertical_lines)

    return corrected_original_image



#  d888b  d8888b.  .d8b.  d8888b. db   db 
# 88' Y8b 88  `8D d8' `8b 88  `8D 88   88 
# 88      88oobY' 88ooo88 88oodD' 88ooo88 
# 88  ooo 88`8b   88~~~88 88~~~   88~~~88 
# 88. ~8~ 88 `88. 88   88 88      88   88 
#  Y888P  88   YD YP   YP 88      YP   YP 

def process_2d_array(array_2d):
  """
  Processes a 2D array with 12 columns and 8 rows into a 1D array according to the specified pattern.

  Args:
    array_2d: A 2D array with 12 columns and 8 rows.

  Returns:
    A 1D array containing the values from the 2D array in the specified order.
  """

  result = []
  for i in range(4):
    for j in range(4):
      result.append(array_2d[j][i])
      result.append(array_2d[j + 4][i + 4])
  return result


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
