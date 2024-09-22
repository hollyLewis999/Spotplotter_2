import cv2
import numpy as np
from Processing import *
def binarizeTest(original_image, contrast=20, excludeSmallDots=10000, show_images=False):
    """Binarize the color image using global thresholding and perform contour detection."""
    
    # Convert the color image to grayscale
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # Create binary image using global thresholding
    _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)  # You can adjust 127 for different threshold levels
    cv2.imshow('BINARYIMAGE', resize_for_display(binary_image))
    contour_img = original_image.copy()
    final_binary = np.zeros_like(binary_image)
    
    # Find contours
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
    
    return binary_image, contour_img, final_binary


def findBlobsTest(binary_image, min_area, max_area, thickness=2):
    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a color image to draw on
    result_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    x_coords =[]
    y_coords=[]
    for contour in contours:
        # Calculate area of the contour
        area = cv2.contourArea(contour)
  
        #if min_area <= area <= max_area:
        if True:   
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
def detect_and_draw_circles_Test(binary_image, gray_image, noClusters, min_radius=50, max_radius=140, param1=50, param2=28):
    """Detect circles in the image and draw grid, yellow areas, and counts."""
    x_coords, y_coords, marked_image = findBlobsTest(final_binary, 1, 2000000)
    cv2.imshow("marked_image", resize_for_display(marked_image))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    height, width = binary_image.shape
    grid_calculated = False
    while not grid_calculated:
        try:
            grid_start_x, grid_start_y, cell_size, slant_angle = calculate_grid(x_coords, y_coords, width, height, binary_image, gray_image, debug=False)
            grid_calculated = True
        except ValueError as e:
            print(f"Error in grid calculation: {e}")
            print("Attempting blob detection with looser parameters")
            x_coords, y_coords, marked_image = findBlobsTest(final_binary, 1000, 25000)  # Looser parameters
            if len(x_coords) < 2 or len(y_coords) < 2:
                raise ValueError("Unable to detect sufficient blobs for grid calculation")

    # Draw grid lines
    for i in range(13):
        x = int(grid_start_x + i * cell_size)
        cv2.line(marked_image, (x, 0), (x, height), (255, 0, 0), 3)
    
    for i in range(9):
        y = int(grid_start_y + i * cell_size)
        cv2.line(marked_image, (0, y), (width, y), (255, 0, 0), 3)

    counts, marked_image = quantify_grid(binary_image, marked_image, grid_start_x, grid_start_y, cell_size)
    
    return counts, marked_image
# List of image filenames
image_filenames = [
    "Normal.png", 
    "overgrown.png", 
    "random.png", 
    "size.png", 
    "skewHorozontal.png", 
    "skewVerticle.png", 
    "sparse.png", 
    "VeryRandom.png"
]


image_steps = []
print("Starting Analysis")

path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/GroundTuth/1x/"
for image_filename in image_filenames:
    image_path = path + image_filename
    original_image = cv2.imread(image_path)
    # Print the path to check if it's correct
    print(f"Loading image: {image_path}")
    
    # Load the image
    original_image = cv2.imread(image_path)

    binary_image, contour_img, final_binary = binarizeTest(original_image)
    cv2.imshow("original_image", resize_for_display(original_image))
    cv2.imshow("binary", resize_for_display(binary_image))
    cv2.imshow("binary", resize_for_display(contour_img))
    cv2.imshow("binary", resize_for_display(final_binary))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    result_grid, marked_image = detect_and_draw_circles_Test(binary_image, binary_image, True)
    
    # image_steps.append({
    #     "Original Image": original_image,
    #     # "Stretched Image": stretched,
    #     # "Blurred Image": blurred,
    #     # "Grayscale Image": gray_image,
    #     #"Binary Image": binary_image,
    #     "Contour Image": contour_img,
    #     "Final Binary Image": final_binary,
    #     "Marked Image with All Elements": marked_image
    # })
    cv2.imshow("original_image", resize_for_display(original_image))
    cv2.imshow("binary", resize_for_display(binary_image))
    cv2.imshow("marked_image", resize_for_display(marked_image))

    print(f"Completed image {i}")

# Save images to PDF
# pdf_output_path = os.path.join(path, "FullDataSetSkewVaiableThreshold.pdf")
# print("Saving Images")
# save_images_to_pdf(image_steps, pdf_output_path, 300, num_images_to_save=4) 
# print(f"All images saved to: {pdf_output_path}")
