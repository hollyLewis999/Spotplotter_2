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

# d8888b. d8888b. d88888b d8888b. d8888b.  .d88b.   .o88b. 
# 88  `8D 88  `8D 88'     88  `8D 88  `8D .8P  Y8. d8P  Y8 
# 88oodD' 88oobY' 88ooooo 88oodD' 88oobY' 88    88 8P      
# 88~~~   88`8b   88~~~~~ 88~~~   88`8b   88    88 8b      
# 88      88 `88. 88.     88      88 `88. `8b  d8' Y8b  d8 
# 88      88   YD Y88888P 88      88   YD  `Y88P'   `Y88P' 


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

def analyze_tonal_range(image):
    inner_image = get_inner_image(image)
    brightness = calculate_brightness(inner_image)
    lower, upper = get_99_percent_range(brightness)
    
    return lower, upper


def stretch_and_gray(original_image, show_images=False):

    lower_bound, upper_bound = analyze_tonal_range(original_image)
    stretched = skimage.exposure.rescale_intensity(original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)).astype(np.uint8)
    #setting contrast as a function of the streach
    idealContrast = int(-0.1813*(upper_bound -lower_bound)+25.113)
    idealContrast = max(idealContrast,2)
    idealContrast = min(idealContrast,20)


    # blurredEdges = cv2.bilateralFilter(stretched, d=9, sigmaColor=75, sigmaSpace=75)
    # blurred = cv2.fastNlMeansDenoising(stretched, h=10, templateWindowSize=7, searchWindowSize=21)
    # blurredEdges3 = cv2.edgePreservingFilter(stretched, flags=1, sigma_s=60, sigma_r=0.4)
    # blurredEdges4 = cv2.medianBlur(stretched, ksize=5)
    # gray_image_notBlurred = cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY)
    #gray_image = cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('stretched', resize_for_display(stretched))


    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=5, sigmaY=5)
    gray_image= cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    #if show_images:
        #cv2.imshow('original_image', resize_for_display(original_image))
        #cv2.imshow('stretched', resize_for_display(stretched))
        # cv2.imshow('GaussianBlur', resize_for_display(blurred))
        # cv2.imshow('bilateralFilter', resize_for_display(blurredEdges))
        # cv2.imshow('fastNlMeansDenoising', resize_for_display(blurredEdges2))
        # cv2.imshow('edgePreservingFilter', resize_for_display(blurredEdges3))
        # cv2.imshow('medianBlur', resize_for_display(blurredEdges4))
        #cv2.imshow('grayBlur', resize_for_display(gray_image))
        #cv2.imshow('gray', resize_for_display(gray_image_notBlurred))
    return stretched, blurred, gray_image, idealContrast
    
 

def binarize(gray_image, original_image, contrast = 20,excludeSmallDots = 15, show_images=False):
    
    block_size, divisor_c = 151, 15
    c = max(-50, min(int(-contrast), -1))
    binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, block_size, c)   
    
    ############################################################################
    #CHANGE BACK LATER ONLY FOR TESTING GROUND TRUTH
    ############################################################################
        # gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        # binary_image = cv2.threshold(gray_image, 175, 255, cv2.THRESH_BINARY)[1]
    ############################################################################

    contour_img = original_image.copy()
    final_binary = np.zeros_like(binary_image)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    height, width = binary_image.shape
    #scale the exclude small dots 
    excludeSmallDots = int((width*(excludeSmallDots/5000))**2)

    areas = [cv2.contourArea(cntr) for cntr in contours]
    median_area = np.median(areas) if areas else 0
    excludeSmallDots

    #check if the area is big enough before drawing
    for cntr in contours:
        area = cv2.contourArea(cntr)
        if area > excludeSmallDots:
            cv2.drawContours(contour_img, [cntr], 0, (0,255,255), 2)
            cv2.drawContours(final_binary, [cntr], 0, 255, -1)


    return binary_image, contour_img, final_binary,block_size



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

    height, width = binary_image.shape
    rows, cols = 8, 12  #8x12 grid

    #https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.label.html
    #checks how many spots there are, takes into account the touching white pixels are one area
    labeled_image, num_features = ndimage.label(binary_image) 
    counts = np.zeros((rows, cols), dtype=int) #place holder to quantifications


    #needs to be in colour to add markings
    if len(marked_image.shape) == 2:  
        marked_image = cv2.cvtColor(marked_image, cv2.COLOR_GRAY2BGR)

    #turn everything  dark grey to show that its not counted
    white_areas = (marked_image[:, :, 0] == 255) & (marked_image[:, :, 1] == 255) & (marked_image[:, :, 2] == 255)
    marked_image[white_areas] = [64, 64, 64]
    
    #loops though each spot
    for label in range(1, num_features + 1):
        component = (labeled_image == label) #the labeled_images labels the connected areas all 1 and then all 2 etc
        coords = np.column_stack(np.where(component)) #store location
        
        #calcuating the gird and ensuring it is within hte image bounds
        min_row = max(0, int((np.min(coords[:, 0]) - grid_start_y) // cell_size))
        max_row = min(rows - 1, int((np.max(coords[:, 0]) - grid_start_y) // cell_size))
        min_col = max(0, int((np.min(coords[:, 1]) - grid_start_x) // cell_size))
        max_col = min(cols - 1, int((np.max(coords[:, 1]) - grid_start_x) // cell_size))
        
        main_cell = None
        max_overlap = 0
        #counts the total pixels f the blob
        total_area = np.sum(component)
        
        #finding the main block
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                #boundaries of current cell
                x1 = int(grid_start_x + col * cell_size)
                y1 = int(grid_start_y + row * cell_size)
                x2 = int(x1 + cell_size)
                y2 = int(y1 + cell_size)
                #must be within image
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                #this is how much of the CURRENT blob is within the cell
                cell = component[y1:y2, x1:x2]
                overlap = np.sum(cell)
                
                #this sets the current cell to the main cell if it is the most amount of overlap
                if overlap > max_overlap:
                    max_overlap = overlap
                    main_cell = (row, col)

        #has a main cell - this will always happen but checking anyway
        if main_cell is not None:
            main_row, main_col = main_cell
            #mac_overlap is the area within the main cell
            main_area = max_overlap
            outside_area = total_area - main_area
            
            #checking to see if its 0.4% within its main cell
            if outside_area <= 0.4 * total_area:
                #add to counts based on its main cell and colour the area white to show its sucessfully counted
                counts[main_row, main_col] += total_area
                marked_image[component] = [255, 255, 255]
     #scale counts to the width of the image
    counts = (np.round((counts / ((width-1)**2)) * 1000000)).astype(int)
    
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




#  .d8b.  d8888b. d8888b.  .d8b.  db    db 
# d8' `8b 88  `8D 88  `8D d8' `8b `8b  d8' 
# 88ooo88 88oobY' 88oobY' 88ooo88  `8bd8'  
# 88~~~88 88`8b   88`8b   88~~~88    88    
# 88   88 88 `88. 88 `88. 88   88    88    
# YP   YP 88   YD 88   YD YP   YP    YP  


def split_and_process(array):
    #three 8x4 arrays
    strain1 = [row[:4] for row in array]
    strain2 = [row[4:8] for row in array]
    strain3 = [row[8:] for row in array]

    #dictionary
    processed_data = {
        "Strain 1": process_strain(strain1),
        "Strain 2": process_strain(strain2),
        "Strain 3": process_strain(strain3)
    }

    return processed_data

def process_strain(strain):
    #this is based on the dilutions
    order = [
        (1,1), (1,2), (1,3), (1,4), (2,1), (1,5), (2,2), (1,6), (2,3), (1,7), (2,4), (3,1),
        (1,8), (2,5), (3,2), (2,6), (3,3), (2,7), (3,4), (4,1), (2,8), (3,5), (4,2), (3,6),
        (4,3), (3,7), (4,4), (3,8), (4,5), (4,6), (4,7), (4,8)
    ]

    processed_list = []
    #getting co-ordinate from speficic part of the array
    for col, row in order:
        if row <= 8 and col <= 4:
            processed_list.append(strain[row-1][col-1])

    return processed_list






