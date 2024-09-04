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
    horizontal_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            if abs(angle) > 70:
                if length > image_shape[0] * 0.2:
                    vertical_lines.append((x1, y1, x2, y2))
            elif abs(angle) < 20:
                if length > image_shape[1] * 0.2:
                    horizontal_lines.append((x1, y1, x2, y2))
    return vertical_lines, horizontal_lines

def find_intersection_point(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None
    px = ((x1*y2 - y1*x2) * (x3 - x4) - (x1 - x2) * (x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2) * (y3 - y4) - (y1 - y2) * (x3*y4 - y3*x4)) / denom
    return int(px), int(py)

def correct_perspective(image, vertical_lines, horizontal_lines):
    h, w = image.shape[:2]
    
    if len(vertical_lines) < 2 or len(horizontal_lines) < 2:
        print("Not enough lines detected for perspective correction.")
        return image
    
    left_line = min(vertical_lines, key=lambda l: l[0])
    right_line = max(vertical_lines, key=lambda l: l[0])
    top_line = min(horizontal_lines, key=lambda l: l[1])
    bottom_line = max(horizontal_lines, key=lambda l: l[1])
    
    top_left = find_intersection_point(left_line, top_line)
    top_right = find_intersection_point(right_line, top_line)
    bottom_left = find_intersection_point(left_line, bottom_line)
    bottom_right = find_intersection_point(right_line, bottom_line)
    
    if None in [top_left, top_right, bottom_left, bottom_right]:
        print("Failed to find all intersection points.")
        return image
    
    src_pts = np.float32([top_left, top_right, bottom_right, bottom_left])
    dst_pts = np.float32([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]])
    
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    result = cv2.warpPerspective(image, matrix, (w, h))
    
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

def process_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Unable to read the image. Please check the file path.")
    
    lines = detect_lines(image)
    if lines is None:
        print("No lines detected in the image.")
        return
    
    vertical_lines, horizontal_lines = classify_lines(lines, image.shape)
    
    if len(vertical_lines) < 2 or len(horizontal_lines) < 2:
        print("Not enough lines detected for perspective correction.")
        return
    
    marked_image = draw_lines(image, vertical_lines, horizontal_lines)
    corrected_image = correct_perspective(image, vertical_lines, horizontal_lines)
    
    cv2.imshow('Original Image with Detected Lines',resize_for_display( marked_image))
    cv2.imshow('Corrected Image', resize_for_display(corrected_image))
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Usage
image_path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/low_contrast_contours_filled.png"
process_image(image_path)