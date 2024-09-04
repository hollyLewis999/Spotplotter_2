import cv2
import numpy as np

def resize_for_display(image, max_width=1280, max_height=720):
    """Resize image for display while maintaining aspect ratio."""
    h, w = image.shape[:2]
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image

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

def find_intersection_point(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None
    px = ((x1*y2 - y1*x2) * (x3 - x4) - (x1 - x2) * (x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2) * (y3 - y4) - (y1 - y2) * (x3*y4 - y3*x4)) / denom
    return int(px), int(py)

def correct_perspective(image, vertical_lines):
    h, w = image.shape[:2]
    
    if len(vertical_lines) < 2:
        print("Not enough vertical lines detected for perspective correction.")
        return image
    
    # Use the leftmost and rightmost vertical lines
    left_line = vertical_lines[0]
    right_line = vertical_lines[-1]
    
    # Calculate the angles of these lines
    left_angle = np.arctan2(left_line[3] - left_line[1], left_line[2] - left_line[0])
    right_angle = np.arctan2(right_line[3] - right_line[1], right_line[2] - right_line[0])
    
    # Average angle for correction
    correction_angle = (left_angle + right_angle) / 2
    
    # Create rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D((w/2, h/2), np.degrees(correction_angle), 1)
    
    # Apply rotation
    rotated = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR)
    
    # Now correct for any remaining keystone effect
    pts1 = np.float32([[left_line[0], 0], [right_line[0], 0], [left_line[0], h], [right_line[0], h]])
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(rotated, matrix, (w, h))
    
    return result

def draw_lines(image, vertical_lines, horizontal_lines):
    marked_image = image.copy()
    if vertical_lines is not None:
        for line in vertical_lines:
            x1, y1, x2, y2 = line
            cv2.line(marked_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    if horizontal_lines is not None:
        for line in horizontal_lines:
            x1, y1, x2, y2 = line
            cv2.line(marked_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
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
    
    # Use the leftmost and rightmost vertical lines
    left_line = vertical_lines[0]
    right_line = vertical_lines[-1]
    
    # Calculate the angles of these lines
    left_angle = np.arctan2(left_line[3] - left_line[1], left_line[2] - left_line[0])
    right_angle = np.arctan2(right_line[3] - right_line[1], right_line[2] - right_line[0])
    
    # Average angle for correction
    correction_angle = (left_angle + right_angle) / 2
    
    # Create rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D((w/2, h/2), np.degrees(correction_angle), 1)
    
    # Apply rotation
    rotated = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR)
    
    # Now correct for any remaining keystone effect
    pts1 = np.float32([[left_line[0], 0], [right_line[0], 0], [left_line[0], h], [right_line[0], h]])
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(rotated, matrix, (w, h))
    
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

def process_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Unable to read the image. Please check the file path.")
    
    lines = detect_lines(image)
    if lines is None:
        print("No lines detected in the image.")
        return
    
    vertical_lines = classify_lines(lines, image.shape)
    
    if len(vertical_lines) < 2:
        print("Not enough vertical lines detected for perspective correction.")
        return
    
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