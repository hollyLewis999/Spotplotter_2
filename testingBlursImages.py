import cv2
import skimage.exposure
import numpy as np
import os

def resize_image(image, width=800, height=600):
    width=int(4000/5)
    height=int(2265/5)
    """Resize image to specified dimensions."""
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

def get_zoomed_top_right(image, zoom_factor=0.5):
    """Extract the top right portion of the image."""
    h, w = image.shape[:2]
    top = 0
    right = w
    new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
    left = right - new_w
    bottom = top + new_h
    return image[top:bottom, left:right]

path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/"
image_path = path + "0.jpg"
original_image = cv2.imread(image_path)
stretched = skimage.exposure.rescale_intensity(original_image, in_range=(90, 180), out_range=(0, 255)).astype(np.uint8)

# Define filters with optimized parameters
filters = {
    # "GaussianBlur": (cv2.GaussianBlur, {"ksize": (5, 5), "sigmaX": 0}),
    # "bilateralFilter": (cv2.bilateralFilter, {"d": 9, "sigmaColor": 75, "sigmaSpace": 75}),
    # "fastNlMeansDenoising": (cv2.fastNlMeansDenoising, {"h": 10, "templateWindowSize": 7, "searchWindowSize": 21}),
    # "edgePreservingFilter": (cv2.edgePreservingFilter, {"flags": cv2.RECURS_FILTER, "sigma_s": 60, "sigma_r": 0.4}),
    # "medianBlur": (cv2.medianBlur, {"ksize": 5}),
}

# Create output directory
output_dir = os.path.join(path, "filtered_images")
os.makedirs(output_dir, exist_ok=True)

resized_image = resize_image(stretched)

# Get zoomed top right
zoomed_image = get_zoomed_top_right(stretched)

# Save resized image
output_path = os.path.join(output_dir, "origional_800x600.jpg")
cv2.imwrite(output_path, resized_image)
print(f"Saved resized origioanal result to {output_path}")
zoom_output_path = os.path.join(output_dir, "origional _zoomed.jpg")
cv2.imwrite(zoom_output_path, zoomed_image)




# Apply each filter and save the result
for filter_name, (filter_func, filter_args) in filters.items():
    filtered_image = filter_func(stretched, **filter_args)
    
    # Resize to 800x600
    resized_image = resize_image(filtered_image)
    
    # Get zoomed top right
    zoomed_image = get_zoomed_top_right(filtered_image)
    
    # Save resized image
    output_path = os.path.join(output_dir, f"{filter_name}_800x600.jpg")
    cv2.imwrite(output_path, resized_image)
    print(f"Saved resized {filter_name} result to {output_path}")
    
    # Save zoomed image
    zoom_output_path = os.path.join(output_dir, f"{filter_name}_zoomed.jpg")
    cv2.imwrite(zoom_output_path, zoomed_image)
    print(f"Saved zoomed {filter_name} result to {zoom_output_path}")

print("All filters applied and results saved.")

# Explanations for each filter
filter_explanations = {
    "GaussianBlur": """
    Function: Applies a Gaussian blur to the image.
    Parameters: ksize=(5, 5), sigmaX=0
    Expected results:
    - Denoising: Effective at reducing Gaussian noise.
    - Edges: Blurs edges, reducing their sharpness.
    Reason: It averages pixel values with a Gaussian distribution, smoothing out noise but also blurring edges.
    """,
    
    "bilateralFilter": """
    Function: Applies bilateral filtering to the image.
    Parameters: d=9, sigmaColor=75, sigmaSpace=75
    Expected results:
    - Denoising: Very effective at reducing noise while preserving edges.
    - Edges: Maintains edges better than Gaussian blur.
    Reason: It considers both spatial proximity and intensity similarity, allowing it to smooth regions while preserving strong edges.
    """,
    
    "fastNlMeansDenoising": """
    Function: Applies non-local means denoising.
    Parameters: h=10, templateWindowSize=7, searchWindowSize=21
    Expected results:
    - Denoising: Highly effective at reducing various types of noise.
    - Edges: Preserves edges and fine details better than simple blurring methods.
    Reason: It averages similar patches in the image, effectively reducing noise while maintaining structure.
    """,
    
    "edgePreservingFilter": """
    Function: Applies edge-preserving smoothing.
    Parameters: flags=cv2.RECURS_FILTER, sigma_s=60, sigma_r=0.4
    Expected results:
    - Denoising: Effective at reducing noise in flat areas.
    - Edges: Excellent at preserving edges and overall image structure.
    Reason: It uses a recursive filtering approach that smooths the image while respecting strong intensity gradients (edges).
    """,
    
    "medianBlur": """
    Function: Applies median blurring to the image.
    Parameters: ksize=5
    Expected results:
    - Denoising: Very effective at reducing salt-and-pepper noise.
    - Edges: Preserves edges better than Gaussian blur, but can round off corners.
    Reason: It replaces each pixel with the median of neighboring pixels, effectively removing outlier values (noise) while maintaining edges.
    """
}

# Print explanations
for filter_name, explanation in filter_explanations.items():
    print(f"\n{filter_name}:")
    print(explanation)