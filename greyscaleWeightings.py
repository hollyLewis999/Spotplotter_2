import cv2
import numpy as np
import skimage.exposure as exposure

# Path and image loading
path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/"
image_path = path + "0.jpg"
original_image = cv2.imread(image_path)

# Stretch the intensity of the original image
stretched = exposure.rescale_intensity(original_image, in_range=(90, 180), out_range=(0, 255)).astype(np.uint8)

# Method 1: Convert to grayscale using equal weightings for RGB
def grayscale_equal_weighting(image):
    # Average the R, G, B values equally
    return np.mean(image, axis=2).astype(np.uint8)

# Method 2: Convert to grayscale using correct weightings (luminosity method)
def grayscale_correct_weighting(image):
    # Use the standard RGB weightings: 0.299 for Red, 0.587 for Green, and 0.114 for Blue
    return (0.299 * image[:, :, 2] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 0]).astype(np.uint8)

# Apply both methods
gray_equal = grayscale_equal_weighting(stretched)
gray_correct = grayscale_correct_weighting(stretched)

# Save or display the grayscale images
cv2.imwrite(path + "gray_equal_weighting.jpg", gray_equal)
cv2.imwrite(path + "gray_correct_weighting.jpg", gray_correct)
cv2.imwrite(path + "stretched.jpg", stretched)

# To display using OpenCV (optional)
# cv2.imshow('Equal Weight Grayscale', gray_equal)
# cv2.imshow('Correct Weight Grayscale', gray_correct)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
