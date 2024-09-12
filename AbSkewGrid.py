import cv2
import numpy as np
from ImageProcessing import *

def detect_lines(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lines = cv2.HoughLinesP(gray, 1, np.pi/180, threshold=50, minLineLength=1000, maxLineGap=10)
    return lines

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

def draw_debug_perspective(image, src_pts, dst_pts):
    debug_image = image.copy()
    
    # Draw source points
    for pt in src_pts:
        cv2.circle(debug_image, tuple(pt.astype(int)), 5, (0, 0, 255), -1)
    
    # Draw lines connecting source points
    cv2.line(debug_image, tuple(src_pts[0].astype(int)), tuple(src_pts[1].astype(int)), (0, 255, 0), 2)
    cv2.line(debug_image, tuple(src_pts[1].astype(int)), tuple(src_pts[2].astype(int)), (0, 255, 0), 2)
    cv2.line(debug_image, tuple(src_pts[2].astype(int)), tuple(src_pts[3].astype(int)), (0, 255, 0), 2)
    cv2.line(debug_image, tuple(src_pts[3].astype(int)), tuple(src_pts[0].astype(int)), (0, 255, 0), 2)
    
    cv2.imwrite("debug_perspective.png", resize_for_display(debug_image))
    cv2.imshow("Perspective Correction", resize_for_display(debug_image))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def process_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Unable to read the image. Please check the file path.")
    
    # Detect lines
    lines = detect_lines(image)
    if lines is None:
        print("No lines detected in the image.")
        return
    
    vertical_lines = classify_lines(lines, image.shape)
    
    if len(vertical_lines) < 2:
        print("Not enough vertical lines detected for perspective correction.")
        return
    
    # Debug: Draw detected lines
    debug_image = image.copy()
    for line in vertical_lines:
        x1, y1, x2, y2 = line
        cv2.line(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow('Detected Vertical Lines', resize_for_display(debug_image))
    cv2.waitKey(0)
    
    # Debug: Show perspective correction points
    h, w = image.shape[:2]
    left_line = vertical_lines[0]
    right_line = vertical_lines[-1]
    left_shift = int(h * np.tan(np.arctan2(left_line[3] - left_line[1], left_line[2] - left_line[0])))
    right_shift = int(h * np.tan(np.arctan2(right_line[3] - right_line[1], right_line[2] - right_line[0])))
    src_pts = np.float32([
        [left_line[0] + left_shift, 0],
        [right_line[0] + right_shift, 0],
        [right_line[2], h - 1],
        [left_line[2], h - 1]
    ])
    dst_pts = np.float32([
        [left_line[2], 0],
        [right_line[2], 0],
        [right_line[2], h - 1],
        [left_line[2], h - 1]
    ])
    draw_debug_perspective(image, src_pts, dst_pts)
    
    corrected_image = correct_perspective(image, vertical_lines)
    
    # Detect lines again on the corrected image
    corrected_lines = detect_lines(corrected_image)
    corrected_vertical_lines = classify_lines(corrected_lines, corrected_image.shape)
    
    marked_image = draw_lines_and_measure(corrected_image, corrected_vertical_lines)
    
    cv2.imshow('Original Image', resize_for_display(image))
    cv2.imshow('Corrected Image with Measurements', resize_for_display(marked_image))
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Usage
image_path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/low_contrast_contours_filled.png"
process_image(image_path)