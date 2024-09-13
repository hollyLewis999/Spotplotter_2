import cv2
import numpy as np

# Resize image for display while maintaining aspect ratio and return the scaling factor
def resize_for_display(image, max_width=1280, max_height=720):
    """Resize image for display while maintaining aspect ratio."""
    h, w = image.shape[:2]
    scale = 1
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA), scale
    return image, scale

# Initialize the cropping variables
cropping = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0
scale_factor = 1

# Mouse callback function to record start and end points of the drag
def mouse_crop(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end, cropping, image_copy, image_resized

    # Start cropping when left mouse button is clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        x_start, y_start, x_end, y_end = x, y, x, y
        cropping = True

    # Update the end point while dragging the mouse and display the selection rectangle
    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping:
            x_end, y_end = x, y
            image_copy = image_resized.copy()  # Reset the image copy to redraw rectangle
            cv2.rectangle(image_copy, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
            cv2.imshow("Image", image_copy)

    # Finish cropping when left mouse button is released
    elif event == cv2.EVENT_LBUTTONUP:
        x_end, y_end = x, y
        cropping = False

        # Draw the final rectangle on the resized image
        image_copy = image_resized.copy()
        cv2.rectangle(image_copy, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
        cv2.imshow("Image", image_copy)

# Load the image
image = cv2.imread('C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/1.jpg')

# Resize the image for display and get the scaling factor
image_resized, scale_factor = resize_for_display(image)

image_copy = image_resized.copy()

cv2.namedWindow("Image")
cv2.setMouseCallback("Image", mouse_crop)

while True:
    # Display the resized image
    cv2.imshow("Image", image_copy)
    key = cv2.waitKey(1)

    # Crop the selected area and display it
    if key == ord("c"):
        if not cropping:
            # Convert the selected coordinates from the resized image to the original image coordinates
            x_start_original = int(x_start / scale_factor)
            y_start_original = int(y_start / scale_factor)
            x_end_original = int(x_end / scale_factor)
            y_end_original = int(y_end / scale_factor)

            # Ensure the selected area is valid
            if x_start_original != x_end_original and y_start_original != y_end_original:
                roi = image[y_start_original:y_end_original, x_start_original:x_end_original]
                if roi.size != 0:
                    cv2.imshow("Cropped", resize_for_display(roi)[0])
                    cv2.imwrite('cropped_image.jpg', roi)

    # Exit when 'q' is pressed
    elif key == ord("q"):
        break

cv2.destroyAllWindows()
