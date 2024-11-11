import cv2
import numpy as np
import skimage.exposure
import os
from scipy import ndimage
from streachRange import analyze_tonal_range

def ensure_output_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def stretch_and_gray(original_image):
    lower_bound, upper_bound = analyze_tonal_range(original_image)
    stretched = skimage.exposure.rescale_intensity(original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)).astype(np.uint8)
    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=5, sigmaY=5)
    gray_image = cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY)
    return gray_image


def process_image(image_file, folder_path, output_folder):
    ensure_output_folder(output_folder)
    
    image_path = os.path.join(folder_path, image_file)
    if not os.path.exists(image_path):
        print(f"Error: File not found - {image_path}")
        return
    
    original_image = cv2.imread(image_path)
    if original_image is None:
        print(f"Error: Unable to read image {image_path}")
        return

    original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    gray_image = stretch_and_gray(original_image_rgb)

    # Apply thresholding (block size 151, contrast 16, method 'mean')

    contrast_value = 16
    binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                   cv2.THRESH_BINARY, 501, -20)
    
    # Find contours and create the overlay
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = original_image_rgb.copy()
    cv2.drawContours(contour_img, contours, -1, (255, 105, 65), 6)  # Drawing in red

    # Save the contour image (segmentation results)
    contour_output_path = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}_segmentation_result.jpg")
    contour_img_bgr = cv2.cvtColor(contour_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(contour_output_path, contour_img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 50])

    # Save the binary image
    binary_output_path = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}_binary.jpg")
    cv2.imwrite(binary_output_path, binary_image, [cv2.IMWRITE_JPEG_QUALITY, 50])

    print(f"Saved segmentation result and binary image for {image_file} to {output_folder}")

def process_image_list(folder_path, output_folder):
    image_files = ["P4292776_1.JPG", "P4292778.JPG","P5022787.JPG","P4272703.JPG", "P4272712.JPG","P4292771.JPG"]

    for image_file in image_files:
        process_image(image_file, folder_path, output_folder)

if __name__ == "__main__":
    folder_path = r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\Image Segmentation\testerdataset"
    output_folder = r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\Image Segmentation\testerdataset\binaryResults"
    process_image_list(folder_path, output_folder)
