import numpy as np
import cv2

# Define the width and height of the image
width, height = 1000, 100  # Adjust width and height as needed

# Create an empty image array with all zeros (black) and single channel for grayscale
image = np.zeros((height, width), dtype=np.uint8)

# Create a linear gradient from 50 to 100
for i in range(width):
    # Calculate the grayscale value for the current column
    gray_value = int(90 + (i / (width - 1)) * (180 - 90))
    
    # Set this value to all rows in the column
    image[:, i] = gray_value

# Save and display the image
cv2.imwrite('linear_gradient.png', image)
cv2.imshow('Grayscale Gradient', image)
cv2.waitKey(0)
cv2.destroyAllWindows()