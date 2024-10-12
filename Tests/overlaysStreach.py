import cv2
import numpy as np
import skimage.exposure
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os
import io
from PIL import Image
from reportlab.lib.utils import ImageReader
from scipy.stats import linregress
import matplotlib.pyplot as plt
import math
from scipy import ndimage
from streachRange import analyze_tonal_range

colors = ['#073B3A', '#0F8660', '#D3784A', '#D24C4A']
blue_hex  = 'ef476f'  # Hex for ORIGIONAL
green_hex= 'ffd166'  # Hex for NEW
red_hex = 'f18701'  # Hex for OVERLAP


def ensure_output_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Helper function to convert hex color to RGB tuple
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def stretch_and_grayOriginal(original_image, lower_bound, upper_bound):
    stretched = skimage.exposure.rescale_intensity(original_image, in_range=(90, 180), out_range=(0, 255)).astype(np.uint8)
    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=5, sigmaY=5)
    gray_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    idealContrast = 16
    return stretched, blurred, gray_image, idealContrast

def stretch_and_grayNew(original_image):
    lower_bound, upper_bound = analyze_tonal_range(original_image)
    print(f"Lower and upper bounds: {lower_bound}, {upper_bound}")
    stretched = skimage.exposure.rescale_intensity(original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)).astype(np.uint8)
    idealContrast = int(-0.1813 * (upper_bound - lower_bound) + 25.113)
    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=5, sigmaY=5)
    gray_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    return stretched, blurred, gray_image, idealContrast
def binarize_and_overlay(gray_imageOG, gray_imageNEW, original_image, contrastNEW, contrastOG=20, exclude_small_dots=5):
    height, width = gray_imageOG.shape
    block_size = 151

    # Mean thresholding
    mean_binaryOG = cv2.adaptiveThreshold(gray_imageOG, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, block_size, -contrastOG)
    mean_binaryNEW = cv2.adaptiveThreshold(gray_imageNEW, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                           cv2.THRESH_BINARY, block_size, -contrastNEW)

    def process_contours(binary_image):
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        exclude_small_dots_area = int((width * (exclude_small_dots / 5000)) ** 2)
        return [cntr for cntr in contours if cv2.contourArea(cntr) > exclude_small_dots_area]

    mean_contoursOG = process_contours(mean_binaryOG)
    mean_contoursNEW = process_contours(mean_binaryNEW)

    # Create separate images for each contour set and the overlap
    overlay_imgOG = original_image.copy()
    overlay_imgNEW = original_image.copy()
    overlay_img_combined = original_image.copy()

    # Create blank images to draw contours
    contour_imgOG = np.zeros((height, width), dtype=np.uint8)
    contour_imgNEW = np.zeros((height, width), dtype=np.uint8)

    # Increase contour thickness
    contour_thickness = 5

    # Draw contours on blank images with increased thickness
    cv2.drawContours(contour_imgOG, mean_contoursOG, -1, 255, contour_thickness)
    cv2.drawContours(contour_imgNEW, mean_contoursNEW, -1, 255, contour_thickness)

    # Find true contour overlap
    overlap_contours = cv2.bitwise_and(contour_imgOG, contour_imgNEW)

    # Define contour colors using hexadecimal values
    blue_rgb = hex_to_rgb(blue_hex)
    green_rgb = hex_to_rgb(green_hex)
    red_rgb = hex_to_rgb(red_hex)

    # Draw contours on overlay images with increased thickness
    cv2.drawContours(overlay_imgOG, mean_contoursOG, -1, blue_rgb, contour_thickness)
    cv2.drawContours(overlay_imgNEW, mean_contoursNEW, -1, green_rgb, contour_thickness)

    # Draw both contour sets on the combined image with increased thickness
    cv2.drawContours(overlay_img_combined, mean_contoursOG, -1, blue_rgb, contour_thickness)
    cv2.drawContours(overlay_img_combined, mean_contoursNEW, -1, green_rgb, contour_thickness)

    # Draw overlapping contours in red with increased visibility
    overlap_coords = np.column_stack(np.where(overlap_contours > 0))
    for coord in overlap_coords:
        cv2.circle(overlay_img_combined, (coord[1], coord[0]), 2, red_rgb, -1)  # Increased circle size

    return overlay_imgOG, overlay_imgNEW, overlay_img_combined

def save_image_low_quality(image, file_path, quality=50):
    """
    Save an image in JPEG format with specified quality, handling color conversion correctly.
    
    :param image: numpy array of the image (assumed to be in RGB format)
    :param file_path: path to save the image
    :param quality: JPEG quality (0-100), lower means more compression
    """
    # Ensure the file extension is .jpg
    file_path = os.path.splitext(file_path)[0] + '.jpg'
    
    # Convert RGB to BGR (OpenCV uses BGR)
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Save the image with specified quality
    cv2.imwrite(file_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])

def process_image_list(folder_path, output_folder):
    image_files = [
        "P3211769.JPG"
        # "P3211709(1).JPG",
        # "P3211711(1).JPG",
        # "P3211773(1).JPG",
        # "P3211775(1).JPG",
        # "P4292771.JPG",
        # "P4292776_1.JPG",
        # "P5022788.JPG",
        # "P5022809.JPG"
    ]

    ensure_output_folder(output_folder)

    for idx, image_file in enumerate(image_files):
        image_path = os.path.join(folder_path, image_file)
        if not os.path.exists(image_path):
            print(f"Error: File not found - {image_path}")
            continue

        # Read image in BGR format
        original_image = cv2.imread(image_path)
        if original_image is None:
            print(f"Error: Unable to read image {image_path}")
            continue

        # Convert to RGB for processing
        original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        # Process with original method
        stretched_OG, _, gray_imageOG, contrastOG = stretch_and_grayOriginal(original_image_rgb, 0, 255)

        # Process with new method
        stretched_NEW, _, gray_imageNEW, contrastNEW = stretch_and_grayNew(original_image_rgb)

        # Binarize and overlay
        overlay_imgOG, overlay_imgNEW, overlay_img_combined = binarize_and_overlay(
            gray_imageOG, gray_imageNEW, original_image_rgb, contrastNEW, contrastOG, exclude_small_dots=5
        )

        # Save results to output folder with lower quality
        output_OG_path = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}_original.jpg")
        output_NEW_path = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}_new.jpg")
        output_combined_path = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}_combined.jpg")

        save_image_low_quality(overlay_imgOG, output_OG_path, quality=50)
        save_image_low_quality(overlay_imgNEW, output_NEW_path, quality=50)
        save_image_low_quality(overlay_img_combined, output_combined_path, quality=50)

        print(f"Saved processed images for {image_file} to {output_folder}")

# Example usage
if __name__ == "__main__":
    folder_path = r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\Image Segmentation\FullDataSet\TestingRange\More"
    output_folder = r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\Image Segmentation\FullDataSet\TestingRange\ProcessedImages"
    process_image_list(folder_path, output_folder)