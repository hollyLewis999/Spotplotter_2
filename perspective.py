import cv2
import numpy as np
import matplotlib.pyplot as plt


def correct_perspective(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding to create a binary image
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Perform morphological operations to enhance thick lines
    kernel = np.ones((5,5), np.uint8)
    morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # Use probabilistic Hough Line Transform to detect long lines
    lines = cv2.HoughLinesP(morph, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
    
    if lines is None:
        print("No lines detected. Returning original image.")
        return image

    # Separate lines into left, right, and bottom
    left_lines = []
    right_lines = []
    bottom_lines = []
    
    height, width = image.shape[:2]
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(x2 - x1) < abs(y2 - y1):  # Vertical line
            if x1 < width / 3:  # Left third of the image
                left_lines.append(line)
            elif x1 > 2 * width / 3:  # Right third of the image
                right_lines.append(line)
        else:  # Horizontal line
            if y1 > 2 * height / 3:  # Bottom third of the image
                bottom_lines.append(line)
    
    # Function to calculate line length
    def line_length(line):
        x1, y1, x2, y2 = line[0]
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Get the longest lines
    left_line = max(left_lines, key=line_length) if left_lines else None
    right_line = max(right_lines, key=line_length) if right_lines else None
    bottom_line = max(bottom_lines, key=line_length) if bottom_lines else None
    
    # Check if we have all three required lines
    if left_line is None or right_line is None or bottom_line is None:
        print("Could not detect all required lines. Returning original image.")
        return image
    
    # Calculate intersection points
    def line_intersection(line1, line2):
        x1, y1, x2, y2 = line1[0]
        x3, y3, x4, y4 = line2[0]
        denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
        if denom == 0:
            return None
        x = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
        y = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom
        return int(x), int(y)

    # Find corners
    bottom_left = line_intersection(left_line, bottom_line)
    bottom_right = line_intersection(right_line, bottom_line)
    
    if bottom_left is None or bottom_right is None:
        print("Could not find valid intersections. Returning original image.")
        return image

    # For top corners, extend vertical lines to the top of the image
    def extend_line_to_top(line):
        x1, y1, x2, y2 = line[0]
        if y1 < y2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        m = (x2 - x1) / (y2 - y1) if y2 != y1 else 0
        x_top = int(x1 + m * (0 - y1))
        return x_top, 0

    top_left = extend_line_to_top(left_line)
    top_right = extend_line_to_top(right_line)
    
    corners = [top_left, top_right, bottom_right, bottom_left]
    
    # Define destination points for perspective transform
    width = max(np.linalg.norm(np.array(top_right) - np.array(top_left)),
                np.linalg.norm(np.array(bottom_right) - np.array(bottom_left)))
    height = max(np.linalg.norm(np.array(bottom_left) - np.array(top_left)),
                 np.linalg.norm(np.array(bottom_right) - np.array(top_right)))
    dst_points = np.array([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]], dtype="float32")
   
    # Apply perspective transform
    matrix = cv2.getPerspectiveTransform(np.array(corners, dtype="float32"), dst_points)
    corrected = cv2.warpPerspective(image, matrix, (int(width), int(height)))
   
    # Visualize results
    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    
    # Original image with detected lines and corners
    axs[0, 0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    for line in [left_line, right_line, bottom_line]:
        x1, y1, x2, y2 = line[0]
        axs[0, 0].plot([x1, x2], [y1, y2], 'r-', linewidth=2)
    for corner in corners:
        axs[0, 0].plot(corner[0], corner[1], 'go', markersize=10)
    axs[0, 0].set_title('Detected Lines and Corners')
    
    # Binary image after morphological operations
    axs[0, 1].imshow(morph, cmap='gray')
    axs[0, 1].set_title('Binary Image after Morphological Operations')
    
    # Hough lines
    hough_lines = image.copy()
    for line in [left_line, right_line, bottom_line]:
        x1, y1, x2, y2 = line[0]
        cv2.line(hough_lines, (x1, y1), (x2, y2), (0, 255, 0), 2)
    axs[1, 0].imshow(cv2.cvtColor(hough_lines, cv2.COLOR_BGR2RGB))
    axs[1, 0].set_title('Detected Longest Lines')
    
    # Corrected image
    axs[1, 1].imshow(cv2.cvtColor(corrected, cv2.COLOR_BGR2RGB))
    axs[1, 1].set_title('Corrected Image')
    
    plt.tight_layout()
    plt.show()
   
    return corrected


image = cv2.imread("C:/Users/ThinkPad/Downloads/P4272710(2).JPG")
corrected_image = correct_perspective(image)