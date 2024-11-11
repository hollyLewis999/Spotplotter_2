import cv2
import numpy as np
import skimage.exposure
import os
from scipy import ndimage
from streachRange import analyze_tonal_range

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def ensure_output_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def stretch_and_gray(original_image):
    lower_bound, upper_bound = analyze_tonal_range(original_image)
    stretched = skimage.exposure.rescale_intensity(original_image, in_range=(lower_bound, upper_bound), out_range=(0, 255)).astype(np.uint8)
    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=5, sigmaY=5)
    gray_image = cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY)
    return gray_image

def add_legend(image, labels, colors):
    height, width = image.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.7  # Significantly increased font scale
    thickness = 12
    padding = 40  # Increased padding
    circle_radius = 40  # Larger circles
    text_offset = 20
    item_gap = 120  # Gap between legend items

    # Calculate the width of all legend items
    total_width = padding
    for label in labels:
        (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
        total_width += circle_radius * 2 + text_offset + text_width + item_gap

    # Create a white image for the legend
    legend_height = int(text_height * 3.5)  # Increased legend height
    legend_image = np.ones((legend_height, width, 3), dtype=np.uint8) * 255

    # Draw legend items
    x = padding
    for label, color in zip(labels, colors):
        # Draw circle
        cv2.circle(legend_image, (x + circle_radius, legend_height // 2), circle_radius, color, -1)
        x += circle_radius * 2 + text_offset

        # Draw text
        (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
        cv2.putText(legend_image, label, (x, legend_height // 2 + text_height // 2), font, font_scale, color, thickness)
        x += text_width + item_gap  # Add gap after each item

    # Combine the original image with the legend
    combined_image = np.vstack((image, legend_image))
    return combined_image

def binarize_and_overlay(gray_image, original_image, contrasts, block_sizes, thresholding_methods):
    height, width = gray_image.shape
    overlay_images = []
    color_hex = ['#ef476f', '#ffd166', '#06d6a0', '#118ab2']
    colors = [hex_to_rgb(c) for c in color_hex]

    params_list = [contrasts, block_sizes, thresholding_methods]
    labels_list = [
        [f"Threshold {c}" for c in contrasts],
        [f"Block Size {b}" for b in block_sizes],
        thresholding_methods
    ]

    for params, labels in zip(params_list, labels_list):
        overlay_img = original_image.copy()

        for i, param in enumerate(params):
            if isinstance(param, int):
                if param in contrasts:
                    binary = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                   cv2.THRESH_BINARY, 501, -param)
                elif param in block_sizes:
                    binary = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                   cv2.THRESH_BINARY, param, -16)
            elif isinstance(param, str):
                if param == 'gaussian':
                    binary = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                   cv2.THRESH_BINARY, 501, -16)
                else:
                    binary = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                   cv2.THRESH_BINARY, 501, -16)

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay_img, contours, -1, colors[i], 2)

        overlay_img_with_legend = add_legend(overlay_img, labels, colors[:len(labels)])
        overlay_images.append(overlay_img_with_legend)

    return overlay_images

def save_image_low_quality(image, file_path, quality=50):
    file_path = os.path.splitext(file_path)[0] + '.jpg'
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(file_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])

def resize_image(image, width=2000):
    height = int(image.shape[0] * (width / image.shape[1]))
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

def process_image_list(folder_path, output_folder):
    image_files = ["P4292776_1.JPG", "P4292778.JPG","P5022787.JPG","P4272703.JPG", "P4272712.JPG","P4292771.JPG"]
    ensure_output_folder(output_folder)

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        if not os.path.exists(image_path):
            print(f"Error: File not found - {image_path}")
            continue

        original_image = cv2.imread(image_path)
        if original_image is None:
            print(f"Error: Unable to read image {image_path}")
            continue

        original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        gray_image = stretch_and_gray(original_image_rgb)

        contrasts = [10, 16, 22,28]
        block_sizes = [301, 501, 701, 901]
        thresholding_methods = ['gaussian', 'mean']

        overlay_images = binarize_and_overlay(gray_image, original_image_rgb, contrasts, block_sizes, thresholding_methods)

        descriptive_names = [
            "threshold_comparison2",
            "block_size_comparison2",
            "thresholding_method_comparison2"
        ]

        for overlay, name in zip(overlay_images, descriptive_names):
            resized_overlay = resize_image(overlay, width=2000)
            output_path = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}_{name}.jpg")
            save_image_low_quality(resized_overlay, output_path, quality=50)

        print(f"Saved processed images for {image_file} to {output_folder}")

if __name__ == "__main__":
    folder_path = r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\Image Segmentation\testerdataset"
    output_folder = r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\Image Segmentation\testerdataset\fullresults"
    process_image_list(folder_path, output_folder)