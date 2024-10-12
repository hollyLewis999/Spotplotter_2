
def save_images_to_pdf(image_steps, output_path,dpi, num_images_to_save=None):
    """
    Save processed images to a PDF file with higher quality.
    
    :param image_steps: List of dictionaries containing processed images
    :param output_path: Path to save the PDF
    :param num_images_to_save: Number of images to save (None for all)
    :param dpi: DPI for image quality (default 300)
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    for i, step_images in enumerate(image_steps):
        y_offset = height - 0.5*inch
        x_offset = inch

        # Limit the number of images if specified
        images_to_save = list(step_images.items())[:num_images_to_save] if num_images_to_save else step_images.items()

        for j, (label, image) in enumerate(images_to_save):
            if j % 2 == 0 and j > 0:
                y_offset -= 2.25 * inch  # Reduced vertical gap
                x_offset = inch
            
            # Convert OpenCV image to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Calculate new size based on DPI
            width_pixels = int(2.5 * dpi)
            height_pixels = int(2 * dpi)
            
            # Resize image while maintaining aspect ratio
            pil_image.thumbnail((width_pixels, height_pixels), Image.LANCZOS)
            
            # Save image to memory buffer
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='PNG', dpi=(dpi, dpi))
            img_buffer.seek(0)
            
            # Draw the label above the image
            c.drawString(x_offset, y_offset, label)
            
            # Draw the image below the label
            c.drawImage(ImageReader(img_buffer), x_offset, y_offset - 2*inch, width=2.5*inch, height=2*inch)
            
            if j % 2 == 0:
                x_offset += 4 * inch

        c.showPage()

    c.save()






# def combine_masks(circles_mask, gridlines_mask, yellow_areas_mask, counts_mask, lines_mask):
#     """Combine black and white masks into a single colored image."""
#     # Convert black and white masks to color (BGR)
#     circles_mask_color = cv2.cvtColor(circles_mask, cv2.COLOR_GRAY2BGR)
#     gridlines_mask_color = cv2.cvtColor(gridlines_mask, cv2.COLOR_GRAY2BGR)
#     yellow_areas_mask_color = cv2.cvtColor(yellow_areas_mask, cv2.COLOR_GRAY2BGR)
#     counts_mask_color = cv2.cvtColor(counts_mask, cv2.COLOR_GRAY2BGR)
#     lines_mask_color = cv2.cvtColor(lines_mask, cv2.COLOR_GRAY2BGR)
    
#     # Set colors
#     circles_mask_color[:, :] = [0, 255, 0]  # Green for circles
#     gridlines_mask_color[:, :] = [255, 0, 0]  # Red for gridlines
#     yellow_areas_mask_color[:, :] = [0, 255, 255]  # Yellow for yellow areas
#     line_mask_color[:, :] = [0, 255, 255]  # Yellow for yellow areas
#     # Initialize the combined mask
#     combined_mask = np.zeros_like(circles_mask_color)

#     # Combine masks
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, circles_mask_color, 1.0, 0)
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, gridlines_mask_color, 1.0, 0)
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, yellow_areas_mask_color, 1.0, 0)
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, counts_mask_color, 1.0, 0)
#     combined_mask = cv2.addWeighted(combined_mask, 1.0, line_mask_color, 1.0, 0)
#     return combined_mask




# d888888b d88888b .d8888. d888888b d888888b d8b   db  d888b  
# `~~88~~' 88'     88'  YP `~~88~~'   `88'   888o  88 88' Y8b 
#    88    88ooooo `8bo.      88       88    88V8o 88 88      
#    88    88~~~~~   `Y8b.    88       88    88 V8o88 88  ooo 
#    88    88.     db   8D    88      .88.   88  V888 88. ~8~ 
#    YP    Y88888P `8888Y'    YP    Y888888P VP   V8P  Y888P  


# #testing Prespective

# path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/GroundTruth.png"
# original_image = cv2.imread(path)
# binary_image = cv2.threshold(original_image, 127, 255, cv2.THRESH_BINARY) 
# origional_perspective,gray_image_perspective, binary_perspective,marked_image_1 = correct_perspective_pipeline(original_image,binary_image, binary_image)
# result_grid, marked_image = detect_and_draw_circles(binary_perspective, gray_image_perspective)

# # image_steps.append({
# #     "Original Image": original_image,
# #     # "Stretched Image": stretched,
# #     # "Blurred Image": blurred,
# #     # "Grayscale Image": gray_image,
# #     #"Binary Image": binary_image,
# #     "Contour Image": contour_img,
# #     "Final Binary Image": final_binary,
# #     "Marked Image with All Elements": marked_image
# # })
# cv2.imshow("original_image", resize_for_display(original_image))
# cv2.imshow("origional_perspective", resize_for_display(origional_perspective))
# cv2.imshow("binary_perspective", resize_for_display(binary_perspective ))
# cv2.imshow("marked_image_1", resize_for_display(marked_image_1))
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# print(f"Completed image {i}")





# image_steps = []
# print("Starting Analysis")
# for i in range(7):
#     path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/"
#     image_path = path + str(i) + ".jpg"
#     original_image = cv2.imread(image_path)
#     origional_perspective= correct_perspective_pipeline(original_image)
#     stretched, blurred, gray_image = stretch_and_gray(origional_perspective, 90, 150)
#     binary_image, contour_img, final_binary, block_size = binarize(gray_image, origional_perspective)
    
#     result_grid, marked_image = detect_and_draw_circles(binary, gray_image)
    
#     # image_steps.append({
#     #     "Original Image": original_image,
#     #     # "Stretched Image": stretched,
#     #     # "Blurred Image": blurred,
#     #     # "Grayscale Image": gray_image,
#     #     #"Binary Image": binary_image,
#     #     "Contour Image": contour_img,
#     #     "Final Binary Image": final_binary,
#     #     "Marked Image with All Elements": marked_image
#     # })
#     cv2.imshow("original_image", resize_for_display(original_image))
#     cv2.imshow("origional_perspective", resize_for_display(origional_perspective))
#     cv2.imshow("binary_perspective", resize_for_display(binary))
#     cv2.imshow("marked_image_1", resize_for_display(marked_image_1))
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#     print(f"Completed image {i}")

# Save images to PDF
# pdf_output_path = os.path.join(path, "FullDataSetSkewVaiableThreshold.pdf")
# print("Saving Images")
# save_images_to_pdf(image_steps, pdf_output_path, 300, num_images_to_save=4) 
# print(f"All images saved to: {pdf_output_path}")



# print("Starting Analysis")
# for i in range(1):
#     path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Image Segmentation/DATASET/"
#     image_path = path + str(i) + ".jpg"
#     original_image = cv2.imread(image_path)

#     stretched, blurred, gray_image = stretch_and_gray(original_image, 90, 150)
#     binary_image, contour_img, final_binary = binarize(gray_image, original_image)
#     result_grid, marked_image = detect_and_draw_circles(final_binary, gray_image)
    
#     # Save the images
#     cv2.imwrite(path + 'low_original_image.png', original_image)
#     cv2.imwrite(path + 'BADstretched.png', stretched)
#     cv2.imwrite(path + 'blurred.png', blurred)
#     cv2.imwrite(path + 'gray_image.png', gray_image)
#     cv2.imwrite(path + 'contour_img.png', contour_img)
#     cv2.imwrite(path + 'final_binary.png', final_binary)
#     cv2.imwrite(path + 'marked_image.png', marked_image)

# print("done")
