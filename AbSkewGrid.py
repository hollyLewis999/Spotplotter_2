import cv2
import numpy as np

path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/"
image_path = path + "1.jpg"
image = cv2.imread(image_path)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply edge detection
edges = cv2.Canny(gray, 50, 150, apertureSize=3)

# Detect lines using Hough Line Transform
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

# Copy the original image to mark up
marked_image = image.copy()

# Draw the lines on the image
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(marked_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

# Function to find the intersection of two lines
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return None  # Lines don't intersect

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return int(x), int(y)

def resize_for_display(image, max_width=1280, max_height=720):
    """Resize image for display while maintaining aspect ratio."""
    h, w = image.shape[:2]
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image

# Find and draw the intersections (corners)
corners = []

if lines is not None:
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            line1 = [(lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3])]
            line2 = [(lines[j][0][0], lines[j][0][1]), (lines[j][0][2], lines[j][0][3])]
            intersection = line_intersection(line1, line2)
            if intersection:
                corners.append(intersection)
                cv2.circle(marked_image, intersection, 5, (0, 0, 255), -1)

# Display the marked-up image with lines and corners
cv2.imshow('Detected Lines and Corners', resize_for_display(marked_image))
cv2.waitKey(0)
cv2.destroyAllWindows()
