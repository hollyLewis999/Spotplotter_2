import cv2
import skimage.exposure
import numpy as np
import time
from tabulate import tabulate

def resize_for_display(image, max_width=1280, max_height=720):
    """Resize image for display while maintaining aspect ratio."""
    h, w = image.shape[:2]
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image

def time_filter(filter_func, image, *args, **kwargs):
    times = []
    for _ in range(5):
        start_time = time.time()
        filter_func(image, *args, **kwargs)
        end_time = time.time()
        times.append(end_time - start_time)
    return times

path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/"
image_path = path + "0.jpg"
original_image = cv2.imread(image_path)
stretched = skimage.exposure.rescale_intensity(original_image, in_range=(90, 180), out_range=(0, 255)).astype(np.uint8)

# Define filters
filters = {
    "GaussianBlur": (cv2.GaussianBlur, {"ksize": (0, 0), "sigmaX": 5, "sigmaY": 5}),
    "bilateralFilter": (cv2.bilateralFilter, {"d": 9, "sigmaColor": 75, "sigmaSpace": 75}),
    "fastNlMeansDenoising": (cv2.fastNlMeansDenoising, {"h": 10, "templateWindowSize": 7, "searchWindowSize": 21}),
    "edgePreservingFilter": (cv2.edgePreservingFilter, {"flags": 1, "sigma_s": 60, "sigma_r": 0.2}),
    "medianBlur": (cv2.medianBlur, {"ksize": 5}),
}

print("starting...")
# Time each filter
results = []
for filter_name, (filter_func, filter_args) in filters.items():
    times = time_filter(filter_func, stretched, **filter_args)
    results.append([filter_name] + times + [sum(times) / len(times)])
    print("done 1")

# Create and print the table
headers = ["Filter"] + [f"Run {i+1}" for i in range(5)] + ["Average"]
print(tabulate(results, headers=headers, floatfmt=".6f"))