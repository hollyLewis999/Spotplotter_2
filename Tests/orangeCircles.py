import cv2
import numpy as np

def detect_and_analyze_red_circles(image_path, min_radius=10, max_radius=100, 
                                   min_circularity=0.5):
    """
    Detect circular regions, analyze their average red value, 
    and create a heatmap-style visualization.
   
    Parameters:
    - image_path: Path to the input image
    - min_radius: Minimum radius of circles to detect
    - max_radius: Maximum radius of circles to detect
    - min_circularity: Minimum circularity threshold (0.0-1.0)
   
    Returns:
    List of detected circles with their average red values and annotated image
    """
    # Read the image
    img = cv2.imread(image_path)
    
    # Create a copy for annotation
    annotated_img = img.copy()
    
    # Create a heatmap overlay (semi-transparent)
    heatmap_overlay = np.zeros_like(img, dtype=np.uint8)
    
    # Split the image into color channels
    blue, green, red = cv2.split(img)
    
    # Convert to grayscale for contour detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    # List to store detected circles with red values
    detected_circles = []
    
    # Track min and max red values for color scaling
    min_red_value = float('inf')
    max_red_value = 0
    
    # First pass: detect circles and find min/max red values
    circle_data = []
    for contour in contours:
        # Calculate area and perimeter
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Skip if contour is too small or perimeter is zero
        if perimeter == 0:
            continue
        
        # Calculate circularity
        circularity = 4 * np.pi * area / (perimeter ** 2)
        
        # Fit a circle to the contour
        (x, y), radius = cv2.minEnclosingCircle(contour)
        radius = int(radius)
        
        # Check circularity and radius constraints
        if (circularity >= min_circularity and
            min_radius <= radius <= max_radius):
            
            # Create a mask for the current contour
            contour_mask = np.zeros(img.shape[:2], dtype=np.uint8)
            cv2.drawContours(contour_mask, [contour], -1, 255, -1)
            
            # Calculate average red value within the circle
            masked_red = cv2.bitwise_and(red, red, mask=contour_mask)
            avg_red_value = cv2.mean(masked_red, mask=contour_mask)[0]
            
            # Update min and max values
            min_red_value = min(min_red_value, avg_red_value)
            max_red_value = max(max_red_value, avg_red_value)
            
            # Store circle data
            circle_data.append({
                'center': (int(x), int(y)),
                'radius': radius,
                'avg_red_value': avg_red_value,
                'contour': contour
            })
    
    # Normalize color mapping
    for circle in circle_data:
        # Normalize red value to 0-255 range
        norm_red = int(255 * (circle['avg_red_value'] - min_red_value) / 
                       (max_red_value - min_red_value + 1e-10))
        
        # Create color gradient from blue (low) to red (high)
        color = (255 - norm_red, 0, norm_red)
        
        # Draw filled circle on heatmap overlay
        cv2.drawContours(heatmap_overlay, [circle['contour']], -1, color, -1)
        
        # Draw circle outline on annotated image
        cv2.drawContours(annotated_img, [circle['contour']], -1, (0, 255, 0), 2)
        
        # Add circle center dot
        center = circle['center']
        cv2.circle(annotated_img, center, 2, (0, 0, 255), 3)
        
        # Add text with average red value
        text = f'{circle["avg_red_value"]:.1f}'
        cv2.putText(annotated_img, text, 
                    (center[0], center[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        detected_circles.append(circle)
    
    # Blend heatmap with original image
    alpha = 0.5  # Transparency factor
    annotated_img = cv2.addWeighted(annotated_img, 1, heatmap_overlay, alpha, 0)
    
    return detected_circles, annotated_img

def resize_for_display(image, max_width=1280, max_height=720):
    h, w = image.shape[:2]
    if h > max_height or w > max_width:
        scale = min(max_height/h, max_width/w)
        new_size = (int(w*scale), int(h*scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image

# Example usage
if __name__ == '__main__':
    image_path = "C:/Users/ThinkPad/Downloads/MSM1Spots.jpeg"
    
    # Detect circles and get annotated image
    circles, annotated_img = detect_and_analyze_red_circles(image_path)
   
    # Print circle information
    print(f"Found {len(circles)} circles:")
    for circle in circles:
        print(f"Center: {circle['center']}, "
              f"Radius: {circle['radius']}, "
              f"Avg Red Value: {circle['avg_red_value']:.1f}")
   
    # Display the annotated image
    cv2.imshow('Detected Circles with Red Heatmap', resize_for_display(annotated_img))
    cv2.waitKey(0)
    cv2.destroyAllWindows()