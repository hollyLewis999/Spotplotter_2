# Styling constants
FONT = 'Arial'
FONT_SIZE = 12
DARK = '#2F4F4F'
LIGHT = '#778899'

def visualize_brightness(brightness, filename):
    normalized = cv2.normalize(brightness, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    cv2.imwrite(filename, normalized)

def create_styled_histogram(image, lower, upper, filename, title="Tonal Distribution"):
    # Set style
    plt.rcParams['font.family'] = FONT
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['font.size'] = FONT_SIZE
    sns.set_style("whitegrid")
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), 
                                  gridspec_kw={'height_ratios': [5, 0.5]})
    
    # Set background color
    ax1.set_facecolor('#F5F5F5')
    
    # Calculate histogram
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    
    # Plot histogram with outline
    ax1.fill_between(range(256), hist.ravel(), color=DARK, alpha=0.7,
                     edgecolor='black', linewidth=0.5)
    
    # Add vertical lines for range
    ax1.axvline(x=lower, color='red', linestyle='--', linewidth=2)
    ax1.axvline(x=upper, color='green', linestyle='--', linewidth=2)
    
    # Add labels
    ax1.set_title(title, fontweight='bold', pad=20)
    ax1.set_xlabel('Tonal Value', fontweight='bold')
    ax1.set_ylabel('Frequency (Pixels)', fontweight='bold')
    ax1.set_xlim([0, 255])
    
    # Create gradient bar
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax2.imshow(np.vstack((gradient,)), aspect='auto', cmap='gray')
    ax2.set_yticks([])
    ax2.set_xticks([])
    ax2.set_xlabel('Tonal Range', fontweight='bold')
    
    # Add range annotation
    range_text = f'Range: {lower}-{upper}'
    ax2.text(128, 0, range_text, color=DARK, ha='center', va='center',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
             fontweight='bold', fontsize=FONT_SIZE)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def get_inner_image(image):
    height, width = image.shape[:2]
    start_y = int(height * 0.1)
    end_y = int(height * 0.9)
    start_x = int(width * 0.1)
    end_x = int(width * 0.9)
    
    # Draw rectangle with thicker red line
    vis_img = image.copy()
    cv2.rectangle(vis_img, (start_x, start_y), (end_x, end_y), 
                 (0, 0, 255), 4)  # Red color, thickness=4
    cv2.imwrite('08_crop_visualization.jpg', vis_img)
    
    cropped = image[start_y:end_y, start_x:end_x]
    cv2.imwrite('09_cropped_image.jpg', cropped)
    return cropped

def stretch_and_gray(original_image, show_images=False):
    lower_bound, upper_bound = analyze_tonal_range(original_image)
    
    cv2.imwrite('12_original_image.jpg', original_image)
    
    # Create before stretch histogram
    create_styled_histogram(cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY),
                          lower_bound, upper_bound, '12a_before_stretch_histogram.jpg',
                          "Original Tonal Distribution")
    
    # Stretch intensity
    stretched = skimage.exposure.rescale_intensity(
        original_image, 
        in_range=(lower_bound, upper_bound), 
        out_range=(0, 255)
    ).astype(np.uint8)
    
    # Create after stretch histogram
    create_styled_histogram(cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY),
                          0, 255, '13a_after_stretch_histogram.jpg',
                          "Stretched Tonal Distribution")
    
    # Create before/after comparison
    visualize_before_after_stretch(original_image, stretched, 
                                 lower_bound, upper_bound,
                                 '13b_stretch_comparison.jpg')
    
    cv2.imwrite('13_stretched_image.jpg', stretched)

    # Rest of the function remains the same
    idealContrast = int(-0.1813*(upper_bound - lower_bound) + 27.113)
    idealContrast = max(idealContrast, 2)
    idealContrast = min(idealContrast, 20)

    height, width = original_image.shape[:2]
    sigma_scale = 0.0015
    sigmaX = sigma_scale * width
    sigmaY = sigma_scale * height
    sigma = min(sigmaX, sigmaY)
    
    blurred = cv2.GaussianBlur(stretched, (0, 0), sigmaX=sigma, sigmaY=sigma)
    cv2.imwrite('14_blurred_image.jpg', blurred)

    gray_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('15_gray_image.jpg', gray_image)

    return stretched, blurred, gray_image, idealContrast


def calculate_brightness(img_array):
    # Purpose: Calculate image brightness using weighted color channels
    blue_channel = img_array[:, :, 0]
    green_channel = img_array[:, :, 1]
    red_channel = img_array[:, :, 2]
    
    # Save individual channels
    cv2.imwrite('01_blue_channel.jpg', blue_channel)
    cv2.imwrite('02_green_channel.jpg', green_channel)
    cv2.imwrite('03_red_channel.jpg', red_channel)
    
    # Weighted channels based on formula
    red_weighted = 0.299 * red_channel
    green_weighted = 0.587 * green_channel
    blue_weighted = 0.114 * blue_channel
    
    # Save weighted channels
    cv2.imwrite('04_red_weighted.jpg', red_weighted.astype(np.uint8))
    cv2.imwrite('05_green_weighted.jpg', green_weighted.astype(np.uint8))
    cv2.imwrite('06_blue_weighted.jpg', blue_weighted.astype(np.uint8))
    
    brightness = red_weighted + green_weighted + blue_weighted
    visualize_brightness(brightness, '07_combined_brightness.jpg')
    
    return brightness


def get_99_percent_range(brightness):
    hist, bin_edges = np.histogram(brightness.ravel(), bins=256, range=(0, 255))
    cumulative = np.cumsum(hist)
    total_pixels = cumulative[-1]
    lower = np.searchsorted(cumulative, 0.005 * total_pixels)
    upper = np.searchsorted(cumulative, 0.995 * total_pixels)
    
    # Visualize histogram with range
    
    return int(lower), int(upper)

def analyze_tonal_range(image):
    inner_image = get_inner_image(image)
    brightness = calculate_brightness(inner_image)
    lower, upper = get_99_percent_range(brightness)
    
    # Visualize the range on the original image
    vis_img = image.copy()
    cv2.putText(vis_img, f'Range: {lower}-{upper}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imwrite('11_tonal_range_visualization.jpg', vis_img)
    
    return lower, upper
def visualize_before_after_stretch(original, stretched, lower, upper, filename):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Get dimensions for inner rectangle
    height, width = original.shape[:2]
    start_y = int(height * 0.1)
    end_y = int(height * 0.9)
    start_x = int(width * 0.1)
    end_x = int(width * 0.9)
    
    # Original image with red rectangle
    rgb_original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    ax1.imshow(rgb_original)
    rect = plt.Rectangle((start_x, start_y), end_x - start_x, end_y - start_y,
                        fill=False, color='red', linewidth=2)
    ax1.add_patch(rect)
    ax1.set_title('Original Image\n(Red rectangle shows analyzed region)', fontweight='bold')
    ax1.axis('off')
    
    # Calculate histograms
    gray_orig = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    hist_orig = cv2.calcHist([gray_orig], [0], None, [256], [0, 256])
    y_max = np.max(hist_orig)  # Get max value for consistent y-axis
    
    # Original histogram
    ax2.fill_between(range(256), hist_orig.ravel(), color=DARK, alpha=0.7)
    ax2.set_title('Original Histogram', fontweight='bold')
    ax2.set_xlim([0, 255])
    ax2.set_ylim([0, y_max])  # Set consistent y-axis limit
    ax2.grid(True)
    
    # Stretched image
    ax3.imshow(cv2.cvtColor(stretched, cv2.COLOR_BGR2RGB))
    ax3.set_title('Stretched Image', fontweight='bold')
    ax3.axis('off')
    
    # Stretched histogram with same y-axis limit
    hist_stretch = cv2.calcHist([cv2.cvtColor(stretched, cv2.COLOR_BGR2GRAY)],
                               [0], None, [256], [0, 256])
    ax4.fill_between(range(256), hist_stretch.ravel(), color=DARK, alpha=0.7)
    ax4.set_title('Stretched Histogram', fontweight='bold')
    ax4.set_xlim([0, 255])
    ax4.set_ylim([0, y_max])  # Use same y-axis limit as original
    ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
def binarize(gray_image, original_image, contrast=20, excludeSmallDots=15, block_size=301, show_images=False):
    c = max(-50, min(int(-contrast), 0))
    
    print("Image shapes")
    print (gray_image.shape)
    print (original_image.shape)
    # Initial binary image
    binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, block_size, c)
    cv2.imwrite('16_initial_binary.jpg', binary_image)
    
    contour_img = gray_image.copy()
    final_binary = np.zeros_like(binary_image)
    print("Image shapes")
    print (gray_image.shape)
    print (original_image.shape)
    print (binary_image.shape)
    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    height, width = binary_image.shape
    image_area = height * width
    
    # Scale the exclude small dots
    excludeSmallDots = int((width*(excludeSmallDots/5000))**2)
    
    # Create visualization of filtered contours
    filtered_contour_img = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
    all_contours_img = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

    
    # Draw all contours first
    cv2.drawContours(all_contours_img, contours, -1, (255, 105, 65), 2)
    cv2.imwrite('17_all_contours.jpg', all_contours_img)
    
    for i, cntr in enumerate(contours):
        area = cv2.contourArea(cntr)
        
        if area <= excludeSmallDots or area > 0.5 * image_area:
            continue
            
        cv2.drawContours(filtered_contour_img, [cntr], 0, (255, 105, 65), 2)
        cv2.drawContours(final_binary, [cntr], 0, 255, -1)
    
    cv2.imwrite('18_filtered_contours.jpg', filtered_contour_img)
    cv2.imwrite('19_final_binary.jpg', final_binary)

    return binary_image, filtered_contour_img, final_binary, block_size

