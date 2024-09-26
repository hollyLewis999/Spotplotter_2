
from pathlib import Path
import os
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage,filedialog,font, Frame, Label,messagebox, Scale, HORIZONTAL,BooleanVar, Checkbutton, CENTER,  DoubleVar, ROUND, LEFT
from tkinter import ttk
import cv2
import numpy as np
from scipy.spatial import distance
from PIL import Image, ImageTk, ImageDraw
import copy
from Processing import *
from functools import partial
import time
import math 

DARK = "#092934"
LIGHT = "#FFFFFF"
GRAY = "#B0B0B0"
FONT = "Microsoft New Tai Lue"
TITLEHEIGHT = 130
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\GUI\assets\frame0")
buttonPosX = 1200
buttonPosY = 910
backToEdit2 = False
PROGRESSX = 1180
PROGRESSY = 36

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)



# .d8888. d888888b db    db db      d88888b 
# 88'  YP `~~88~~' `8b  d8' 88      88'     
# `8bo.      88     `8bd8'  88      88ooooo 
#   `Y8b.    88       88    88      88~~~~~ 
# db   8D    88       88    88booo. 88.     
# `8888Y'    YP       YP    Y88888P Y88888P 
                                          
                                          
def create_circular_slider(master, min_val, max_val, position, command=None, initial_value=None):
    frame = Frame(master, width=300, height=70, bg=DARK)
    frame.place(x=position[0], y=position[1])
    canvas = Canvas(frame, width=300, height=70, bg=DARK, highlightthickness=0)
    canvas.pack()
    
    current_value = DoubleVar(value=min_val if initial_value is None else initial_value)
    last_update_time = 0
    update_interval = 100  # Update interval in milliseconds

    def draw_slider(update_label=False):
        canvas.delete("all")
        filled_x = value_to_position(current_value.get())
        canvas.create_line(10, 45, 290, 45, fill=GRAY, width=10, capstyle=ROUND)
        canvas.create_line(10, 45, filled_x, 45, fill=LIGHT, width=10, capstyle=ROUND)
        
        knob_x = value_to_position(current_value.get())
        canvas.create_oval(knob_x-10, 35, knob_x+10, 55, fill=LIGHT, outline=DARK, tags="knob")
        
        if update_label:
            canvas.delete("value_text")
            label_x = max(10, min(knob_x, 270))
            canvas.create_text(label_x, 20, text=str(int(current_value.get())), 
                               font=(FONT, 10, "bold"), fill=LIGHT, tags="value_text")

    def value_to_position(value):
        return (value - min_val) / (max_val - min_val) * 280 + 10

    def position_to_value(x):
        return (x - 10) / 280 * (max_val - min_val) + min_val

    def on_drag(event):
        nonlocal last_update_time
        current_time = event.time
        if 35 <= event.y <= 55:
            new_value = position_to_value(event.x)
            current_value.set(max(min_val, min(max_val, new_value)))
            
            if current_time - last_update_time >= update_interval:
                draw_slider(update_label=True)
                last_update_time = current_time
            else:
                draw_slider(update_label=False)
            
            if command:
                command(int(current_value.get()))

    def on_release(event):
        draw_slider(update_label=True)
        if command:
            command(int(current_value.get()))

    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    def set_value(value):
        current_value.set(max(min_val, min(max_val, value)))
        draw_slider(update_label=True)

    draw_slider(update_label=True)
    frame.set = set_value
    frame.get = lambda: int(current_value.get())
    return frame
        
def create_rounded_button(canvas, text, command, x, y, width=200, height=70, cornerradius=12, padding=2, button_tag=None, fill = DARK, accent = LIGHT):
    # Calculate radius
    rad = 2 * cornerradius

    # Ensure each button has a unique tag if not provided
    if button_tag is None:
        button_tag = f"button_{x}_{y}"  # Unique tag based on position

    # Draw the rounded rectangle shape at (x, y) position and give it a tag
    canvas.create_polygon(
        (x + padding, y + height - cornerradius - padding,
         x + padding, y + cornerradius + padding,
         x + padding + cornerradius, y + padding,
         x + width - padding - cornerradius, y + padding,
         x + width - padding, y + cornerradius + padding,
         x + width - padding, y + height - cornerradius - padding,
         x + width - padding - cornerradius, y + height - padding,
         x + padding + cornerradius, y + height - padding),
        fill=fill, outline=fill, tags=button_tag
    )

    # Draw rounded corners using arcs and add the same tag
    canvas.create_arc(
        (x + padding, y + padding + rad, x + padding + rad, y + padding),
        start=90, extent=90, fill=fill, outline=fill, tags=button_tag
    )
    canvas.create_arc(
        (x + width - padding - rad, y + padding, x + width - padding, y + padding + rad),
        start=0, extent=90, fill=fill, outline=fill, tags=button_tag
    )
    canvas.create_arc(
        (x + width - padding, y + height - rad - padding, x + width - padding - rad, y + height - padding),
        start=270, extent=90, fill=fill, outline=fill, tags=button_tag
    )
    canvas.create_arc(
        (x + padding, y + height - padding - rad, x + padding + rad, y + height - padding),
        start=180, extent=90, fill=fill, outline=fill, tags=button_tag
    )

    # Add text in the middle of the button and tag it
    canvas.create_text(x + width / 2, y + height / 2, text=text, fill=accent, font=(FONT, 12, "bold"), tags=button_tag)

    # Bind the click event to the entire button with the unique tag
    canvas.tag_bind(button_tag, "<Button-1>", lambda event: command()) 


def round_rectangle(canvas,x1, y1, x2, y2, radius=35, **kwargs):
        
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]

    return canvas.create_polygon(points, **kwargs, smooth=True)

######  ########  ########    ###    ######## ########     ######   ######  ########  ######## ######## ##    ##  ######  
##    ## ##     ## ##         ## ##      ##    ##          ##    ## ##    ## ##     ## ##       ##       ###   ## ##    ## 
##       ##     ## ##        ##   ##     ##    ##          ##       ##       ##     ## ##       ##       ####  ## ##       
##       ########  ######   ##     ##    ##    ######       ######  ##       ########  ######   ######   ## ## ##  ######  
##       ##   ##   ##       #########    ##    ##                ## ##       ##   ##   ##       ##       ##  ####       ## 
##    ## ##    ##  ##       ##     ##    ##    ##          ##    ## ##    ## ##    ##  ##       ##       ##   ### ##    ## 
 ######  ##     ## ######## ##     ##    ##    ########     ######   ######  ##     ## ######## ######## ##    ##  ######  




def create_titleFrame(window):
    # Create the canvas
    canvas = Canvas(
        window,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)
   
    # Load the image
    image_path_10 = relative_to_assets("image_10.png")

    img_logobig = Image.open(image_path_10)  # Open image using Pillow

    # Resize the image while keeping better quality
    img_logobig_resized = img_logobig.resize((img_logobig.width // 2, img_logobig.height //2), Image.LANCZOS)

    # Convert to PhotoImage for Tkinter
    image_image_10 = ImageTk.PhotoImage(img_logobig_resized)
    canvas.image_image_10 = image_image_10  # Keep a reference to avoid garbage collection
    canvas.create_image(720.0, 400.0, image=image_image_10)


    create_rounded_button(
        canvas=canvas,
        text="Upload Assays",
        command=lambda: upload_images(window),
        x=620.0,
        y=650.0, )

    create_rounded_button(
        canvas=canvas,
        text="Upload MetaData",
        command=lambda: upload_txt_file(window),
        x=400.0,
        y=650.0,)

    create_rounded_button(
        canvas=canvas,
        text="Upload Plate Data",
        command=lambda: upload_txt_file(window),
        x=840.0,
        y=650.0,)

    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: validate_and_proceed(window),
        x=buttonPosX,
        y=buttonPosY )

    return canvas


def display_results(window):
    # Clear the window
    for widget in window.winfo_children():
        widget.destroy()
        # Right image (editing image)
    # cv2.imshow("debug image", resize_for_display(window.debug_image))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # Create a new canvas for results
    canvas = Canvas(
        window,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)

    image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
    window.edit_images.append(image_image_1)
    image_1 = canvas.create_image(
        719.0,
        57.0,
        image=image_image_1
    )

    # Add a title
    canvas.create_text(
        720,
        TITLEHEIGHT,
        text="Downloading Reults",
        fill=DARK,
        font=(FONT, 12, 
        "bold")
    )

    write_image_info_to_file(window)
    finish_button = Button(
        window,
        text="Finish",
        command=window.quit,
        font=(FONT, 14),
        bg=DARK,
        fg=LIGHT,
        padx=20,
        pady=10
    )
    finish_button.place(relx=0.5, rely=0.9, anchor="center")
    
def display_final_image(window, override =False):
    #cv2.imshow("contours", resize_for_display(window.contour_img))
    add_to_history(window)
    # Clear the window
    for widget in window.winfo_children():
        widget.destroy()

    # Create a new canvas
    canvas = Canvas(
        window,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)

    image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
    window.edit_images.append(image_image_1)
    image_1 = canvas.create_image(
        719.0,
        57.0,
        image=image_image_1
    )

    next_button = Button(
        window,
        text= "Next",
        command=lambda: next_image(window),
        font=(FONT, 14),
        bg=DARK,
        fg=LIGHT,
        padx=20,
        pady=10
    )
    next_button.place(x=1192.0, y=935.0, width=207.0, height=61.0)
    

    override_button = Button(
        window,
        text="Override Grid",
        command=lambda: open_grid_override(window),
        font=(FONT, 14),
        bg=DARK,
        fg=LIGHT,
        padx=20,
        pady=10
    )
    override_button.place(relx=0.3, rely=0.9, anchor="center")


    # Create a frame to center the image
    frame = Frame(window, bg=LIGHT)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    if (override):
        marked_image = window.marked_image
        result_grid = window.result_grid
    else:   
        # Convert the NumPy array to PIL Image
        gray_image = window.gray_image  # Make sure this is set earlier in the processs
        result_grid, marked_image, ordered_counts = detect_and_draw_circles(window.binarized_image, gray_image, False)
        #SAVING INFO
        window.current_info['QuantificationA'] = ordered_counts["Strain 1"]
        window.current_info['QuantificationB'] = ordered_counts["Strain 2"]
        window.current_info['QuantificationC'] = ordered_counts["Strain 3"]

    # Update the window.image_info with the modified current_info
        window.image_info[window.current_image_index] = window.current_info

    # Ensure marked_image is a PIL Image
    if isinstance(marked_image, np.ndarray):
        marked_image = Image.fromarray(marked_image)

    # Convert to "RGB" mode if not already
    if marked_image.mode not in ["RGB", "RGBA"]:
        marked_image = marked_image.convert("RGB")

    # Resize the image to fit the window (adjust as needed)
    max_size = (1000, 800)  # Maximum width and height
    marked_image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Convert to PhotoImage
    photo = ImageTk.PhotoImage(marked_image)

    # Create a label to display the image
    image_label = Label(frame, image=photo, bg=LIGHT)
    image_label.image = photo  # Keep a reference
    image_label.pack()


    # Add a "Back to Editing" button
    back_button = Button(
        window,
        text="Back to Editing",
        command=lambda: create_editFrame(window),
        font=(FONT, 14),
        bg=DARK,
        fg=LIGHT,
        padx=20,
        pady=10
    )
    back_button.place(relx=0.5, rely=0.9, anchor="center")




    # Create a frame for the progress bar
    window.progress_frame = Frame(window, bg=LIGHT)
    window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)

    # Create and pack the progress bar with the custom style
    window.progress_bar = ttk.Progressbar(window.progress_frame, style="styled.Horizontal.TProgressbar", orient="horizontal",
                                        length=150, mode="determinate", maximum=100, value=0)
    window.progress_bar.pack(side="left", padx=(0, 10))

    # Label next to the progress bar
    window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    window.progress_label.pack(side="left")
    
    update_progress_bar(window)
    
def create_editFrame(window, backToEdit = False):
    global backToEdit2

    canvas = Canvas(
        window,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)
    

    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    window.edit_images.append(image_image_1)
    image_1 = canvas.create_image(
        719.0,
        57.0,
        image=image_image_1
    )

    window.show_original = False  # Initialize with showing the original image

    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: display_final_image(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag = "editNext" )

    round_rectangle(canvas,
       1362.0,
        168.0,
        1422.0,
        826.0,
        fill=DARK,
        outline="")

    round_rectangle(canvas,
        17.0,
        168.0,
        1350.0,
        826.0,
        fill=DARK,
        outline="")


    if hasattr(window, 'current_image_info'):
        current_info = window.current_image_info
        metadata_text = f"Filename: {current_info['filename']}\n"
        metadata_text += f"StrainA: {current_info['strainA']}\n"
        metadata_text += f"StrainB: {current_info['strainB']}\n"
        metadata_text += f"StrainC: {current_info['strainC']}"
    else:
        metadata_text = "No metadata available"

    # Always recreate the metadata label
    if hasattr(window, 'metadata_label'):
        window.metadata_label.destroy()  # Destroy the old label

    window.metadata_label = Label(window, text=metadata_text, font=(FONT, 16 * -1, 'bold'), bg=LIGHT, fg=DARK, justify=LEFT)
    window.metadata_label.place(x=50, y=850)


    canvas.create_text(
        1391.0,
        380.0,
        text="Add",
        fill=LIGHT,
        font=(FONT, 14 * -1,'bold')
    )

    canvas.create_text(
        1391.0,
        580.0,
        text="Delete",
        fill=LIGHT,
        font=(FONT, 14* -1,'bold')
    )



    image_path_2 = relative_to_assets("image_2.png")
    img_thinPen = Image.open(image_path_2)  # Open image using Pillow

    # Resize the image while keeping better quality
    img_thinPen_resized = img_thinPen.resize((img_thinPen.width // 11, img_thinPen.height // 11), Image.LANCZOS)

    # Convert to PhotoImage for Tkinter
    image_image_2 = ImageTk.PhotoImage(img_thinPen_resized)
    window.edit_images.append(image_image_2)
    button_thin_pen = Button(
        window,
        image=image_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: set_mode(window, "thin_brush"),
        bg= DARK
   
    )
    
    button_thin_pen.place(x=1377.0, y=480.0)


    image_path_3 = relative_to_assets("image_3.png")
    img_adder = Image.open(image_path_3)  # Open image using Pillow

    # Resize the image while keeping better quality
    img_adder_resized = img_adder.resize((img_adder.width // 11, img_adder.height // 11), Image.LANCZOS)

    # Convert to PhotoImage for Tkinter
    image_image_3 = ImageTk.PhotoImage(img_adder_resized)    
    window.edit_images.append(image_image_3)
    magic_adder_button = Button(
        window,
        image=image_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("adder"),
        relief="flat",
        bg = DARK
    )
    magic_adder_button.place(x=1376,y=402)


    # Big eraser
    image_image_4 = PhotoImage(file=relative_to_assets("image_4.png"))
    image_image_4 = image_image_4.subsample(11, 11) 
    window.edit_images.append(image_image_4)
    big_eraser_button = Button(
        window,
        image=image_image_4,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: set_mode(window, "large_brush"),
        relief="flat",
        bg = DARK
    )
    big_eraser_button.place(x=1377.0, y=655.0)

    image_path_5 = relative_to_assets("image_5.png")
    img_thickPen = Image.open(image_path_5)  # Open image using Pillow

    # Resize the image while keeping better quality
    img_thickPen_resized = img_thickPen.resize((img_thickPen.width // 11, img_thickPen.height // 11), Image.LANCZOS)

    # Convert to PhotoImage for Tkinter
    image_image_5 = ImageTk.PhotoImage(img_thickPen_resized)
    window.edit_images.append(image_image_5)
    big_pen_button = Button(
        window,
        image=image_image_5,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: set_mode(window, "large_brush"),
        relief="flat",
        bg = DARK
    )
    big_pen_button.place(x=1377, y=441)


    image_path_6 = relative_to_assets("image_6.png")
    img_flood = Image.open(image_path_6)  # Open image using Pillow

    # Resize the image while keeping better quality
    img_flood_resized = img_flood.resize((img_flood.width // 11, img_flood.height // 11), Image.LANCZOS)

    # Convert to PhotoImage for Tkinter
    image_image_6 = ImageTk.PhotoImage(img_flood_resized)
    window.edit_images.append(image_image_6)
    flood_eraser_button = Button(
        window,
        image=image_image_6,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: set_mode(window, "flood"),
        relief="flat",
        bg = DARK
    )
    flood_eraser_button.place(x=1376.0, y=616.0)

    image_path_7 = relative_to_assets("image_7.png")
    img_redo = Image.open(image_path_7)  # Open image using Pillow

    # Resize the image while keeping better quality
    img_redo_resized = img_redo.resize((img_redo.width // 11, img_redo.height // 11), Image.LANCZOS)

    # Convert to PhotoImage for Tkinter
    image_image_7 = ImageTk.PhotoImage(img_redo_resized)
    window.edit_images.append(image_image_7)
    redo_button = Button(
        window,
        image=image_image_7,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: redo(window),
        relief="flat",
        bg = DARK
    )
    redo_button.place(x=1376.0, y=251.0)


    # Undo Button
    image_path_8 = relative_to_assets("image_8.png")
    img_undo = Image.open(image_path_8)  # Open image using Pillow

    # Resize the image while keeping better quality
    img_undo_resized = img_undo.resize((img_undo.width // 11, img_undo.height // 11), Image.LANCZOS)

    # Convert to PhotoImage for Tkinter
    image_image_8 = ImageTk.PhotoImage(img_undo_resized)

    window.edit_images.append(image_image_8)
    undo_button = Button(
        window,
        image=image_image_8,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: undo(window),
        relief="flat",
        bg = DARK
    )
    undo_button.place(x=1376.0, y=212.0)


    # Thin eraser

    image_path_9 = relative_to_assets("image_9.png")
    img_thinEraser = Image.open(image_path_9)  # Open image using Pillow

    # Resize the image while keeping better quality
    img_thinEraser_resized = img_thinEraser.resize((img_thinEraser.width // 11, img_thinEraser.height // 11), Image.LANCZOS)

    # Convert to PhotoImage for Tkinter
    image_image_9 = ImageTk.PhotoImage(img_thinEraser_resized)
    window.edit_images.append(image_image_9)
    thin_eraser_button = Button(
        window,
        image=image_image_9,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: set_mode(window, "small_brush"),
        relief="flat",
        bg = DARK
    )
    thin_eraser_button.place(x=1376.0, y=693.0)

    window.undo_button = undo_button
    window.redo_button = redo_button

    total_width = 1295 - 34
    total_height = 783 - 203
    img_width = total_width // 2 -50 # Half of the total width for each image
    img_height = total_height

    window.left_canvas = Canvas(window, width=img_width, height=img_height, bg=DARK, highlightthickness=0)
    window.left_canvas.place(x=30, y=303)

    window.right_canvas = Canvas(window, width=img_width, height=img_height, bg=DARK, highlightthickness=0)
    window.right_canvas.place(x=690, y=303)

    # Display images
    display_images(window)
    
    create_rounded_button(
        canvas=canvas,
        text="Toggle",
        command=lambda: toggle_image(window),
        x=40,
        y=215,
        button_tag = "Toggle",
        width = 110, 
        height = 40,
        fill = LIGHT,
        accent = DARK)

    smallDots_label = Label(window, text="Size", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    smallDots_label.place(x=645, y=223)
    smallDots_slider = create_circular_slider(
        window, min_val=1, max_val=100,
        position=(700, 190),
        command=lambda v: on_excludeSmallDots(window, v, False),
        initial_value=window.excludeSmallDots
    )

    # Contrast Slider
    contrast_label = Label(window, text="Threshold:", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    contrast_label.place(x=200, y=223)
    contrast_slider = create_circular_slider(
        window, min_val=0, max_val=40,
        position=(300, 190),
        command=lambda v: on_contrast_change(window, v, False),
        initial_value=window.contrast_value
    )



    # Bind events for editing on both canvases
    for canvas in [window.left_canvas, window.right_canvas]:
        canvas.bind("<ButtonPress-1>", lambda event: start_draw(window, event))
        canvas.bind("<B1-Motion>", lambda event: draw(window, event))
        canvas.bind("<ButtonRelease-1>", lambda event: stop_draw(window, event))

    # Connect buttons to functions
    button_thin_pen.config(command=lambda: set_mode(window, "small_brush"))
    big_pen_button.config(command=lambda: set_mode(window, "large_brush"))
    thin_eraser_button.config(command=lambda: set_mode(window, "small_eraser"))
    big_eraser_button.config(command=lambda: set_mode(window, "large_eraser"))
    flood_eraser_button.config(command=lambda: set_mode(window, "flood"))
    undo_button.config(command=lambda: undo(window))
    redo_button.config(command=lambda: redo(window))




    # Create a frame for the progress bar
    window.progress_frame = Frame(window, bg=LIGHT)
    window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)

    # Create and pack the progress bar with the custom style
    window.progress_bar = ttk.Progressbar(window.progress_frame, style="styled.Horizontal.TProgressbar", orient="horizontal",
                                        length=150, mode="determinate", maximum=100, value=0)
    window.progress_bar.pack(side="left", padx=(0, 10))

    # Label next to the progress bar
    window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    window.progress_label.pack(side="left")
    
    update_progress_bar(window)

   
    return canvas
    
def open_grid_override(window):
    # Clear the window
    for widget in window.winfo_children():
        widget.destroy()
    
    # Create a new canvas for grid override
    canvas = Canvas(
        window,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)
    image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
    window.edit_images.append(image_image_1)
    image_1 = canvas.create_image(
        719.0,
        57.0,
        image=image_image_1
    )

    # Add a title
    canvas.create_text(
        720,
        TITLEHEIGHT,
        text="Please click centerpoints of dots, start from the top left and work across and down",
        fill=DARK,
        font=(FONT, 12, 
        "bold")
    )
    # Use the binarized image (which includes all edits)
    binary_image = window.binarized_image.copy()
    window.binary_image = binary_image
    # Convert to RGB for display
    rgb_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2RGB)
    
    # Resize the image to fit within the canvas
    max_width = 1200  # Adjust as needed
    max_height = 600  # Adjust as needed
    h, w = rgb_image.shape[:2]
    scale = min(max_width / w, max_height / h)
    new_size = (int(w * scale), int(h * scale))
    resized_image = cv2.resize(rgb_image, new_size, interpolation=cv2.INTER_AREA)
    
    # Convert to PhotoImage
    img = Image.fromarray(resized_image)
    photo = ImageTk.PhotoImage(img)
    
    # Calculate position to center the image
    x_position = (1440 - new_size[0]) // 2
    y_position = (1024 - new_size[1]) // 2
    
    # Display the image
    canvas.create_image(x_position, y_position, anchor="nw", image=photo)
    canvas.image = photo  # Keep a reference
    
    # Store the scale factor for later use
    window.grid_override_scale = scale
    window.grid_override_offset = (x_position, y_position)
    
    # Store clicked points
    window.clicked_pointsx = []
    window.clicked_pointsy = []
    # Bind click event
    canvas.bind("<Button-1>", lambda event: on_canvas_click(event, window, canvas))
    

    create_rounded_button(
        canvas=canvas,
        text="Recalculate Grid",
        command=lambda: recalculate_grid(window),
        x=buttonPosX,
        y=buttonPosY, 
        button_tag ="recalculate_grid")

def on_canvas_click(event, window, canvas):
    x, y = event.x, event.y
    
    # Adjust coordinates based on image position and scaling
    adjusted_x = (x - window.grid_override_offset[0]) / window.grid_override_scale
    adjusted_y = (y - window.grid_override_offset[1]) / window.grid_override_scale
    
    window.clicked_pointsx.append(adjusted_x)
    window.clicked_pointsy.append(adjusted_y)
    # Draw a red X at the clicked point
    canvas.create_line(x-5, y-5, x+5, y+5, fill=DARK, width=2)
    canvas.create_line(x-5, y+5, x+5, y-5, fill=DARK, width=2)

def recalculate_grid(window):
    if len(window.clicked_pointsx) < 12:
        messagebox.showerror("Error", "Please select at least 16 points")
        return
   
    # Convert clicked points to numpy array
    pointsx, pointsy = np.array(window.clicked_pointsx), np.array(window.clicked_pointsy)
    height, width = window.gray_image.shape
    # Calculate new grid parameters using user-provided points
    grid_start_x, grid_start_y, cell_size, slant_angle = calculate_grid(window.clicked_pointsx,window.clicked_pointsy, width, height, window.binary_image, window.gray_image)
    counts, marked_image, ordered_counts= quantify_grid(window.binary_image, window.binary_image, grid_start_x, grid_start_y, cell_size)
    #SAVING INFO
    current_info['QuantificationA'] = ordered_counts["Strain 1"]
    current_info['QuantificationB'] = ordered_counts["Strain 2"]
    current_info['QuantificationC'] = ordered_counts["Strain 3"]

# Update the window.image_info with the modified current_info
    window.image_info[window.current_image_index] = current_info
    # Create a color copy of the original image for marking
    # Update window attributes
    window.result_grid= counts
    window.marked_image = marked_image
    # Display the final image with the new grid
    display_final_image(window, True)

def update_progress_bar(window):
    if hasattr(window, 'progress_bar') and window.progress_bar:
        progress = (window.current_image_index + 1) / len(window.image_paths) * 100
        window.progress_bar['value'] = progress
        window.progress_label.config(text=f"{window.current_image_index + 1}/{len(window.image_paths)}")

def validate_and_proceed(window):
    if hasattr(window, 'image_paths') and window.image_paths and hasattr(window, 'image_info') and window.image_info:
        create_cropFrame(window)  # Proceed to the next frame
    else:
        messagebox.showwarning("Warning", "Please upload both text file and images")


def process_image(window):

    stretched, blurred, gray_image = stretch_and_gray(window.current_image, 90, 150)
    window.gray_image = gray_image
    binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.current_image, excludeSmallDots=window.excludeSmallDots, contrast=window.contrast_value)
    
    #############################FOR TESTING#######################


    #################################################################



    window.contour_img = contour_img
    window.binarized_image = final_binary
    window.debug_image = np.stack((final_binary,) * 3, axis=-1)
    
    # Only initialize history if it's empty
    if not window.history:
        window.history = [window.binarized_image.copy()]
        window.redo_stack = []
    
    update_undo_redo_buttons(window)
    create_editFrame(window)
    #
    # print("imagge is being reprocessed ")


#  .o88b. d8888b.  .d88b.  d8888b. d8888b. d888888b d8b   db  d888b  
# d8P  Y8 88  `8D .8P  Y8. 88  `8D 88  `8D   `88'   888o  88 88' Y8b 
# 8P      88oobY' 88    88 88oodD' 88oodD'    88    88V8o 88 88      
# 8b      88`8b   88    88 88~~~   88~~~      88    88 V8o88 88  ooo 
# Y8b  d8 88 `88. `8b  d8' 88      88        .88.   88  V888 88. ~8~ 
#  `Y88P' 88   YD  `Y88P'  88      88      Y888888P VP   V8P  Y888P  

def resize_for_display_crop(image, max_width=1000, max_height=650):
    """Resize image for display while maintaining aspect ratio."""
    h, w = image.shape[:2]
    scale = min(max_width/w, max_height/h)
    new_size = (int(w*scale), int(h*scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA), scale

def start_crop(event, window):
    window.cropping = True
    window.x_start, window.y_start = event.x, event.y

def crop(event, window, canvas):
    if window.cropping:
        window.x_end, window.y_end = event.x, event.y
        canvas.delete("crop_rectangle")
        
        
        # Create the rectangle
        canvas.create_rectangle(
            window.x_start, window.y_start, window.x_end, window.y_end,
            outline=LIGHT,
            width=2,
            fill=LIGHT,
            stipple="gray50",  # Use stipple pattern for opacity effect
            tags="crop_rectangle"
        )

def end_crop(event, window, canvas):
    window.cropping = False

def apply_crop(window):
    if window.x_start != window.x_end and window.y_start != window.y_end:
        # Calculate the dimensions of the original image
        original_height, original_width = window.original_image.shape[:2]
        
        # Calculate the scaling factors
        scale_x = original_width / window.display_width
        scale_y = original_height / window.display_height
        
        # Calculate the offset of the image on the canvas
        canvas_width = 1440  # From your create_cropFrame function
        canvas_height = 1024  # From your create_cropFrame function
        offset_x = (canvas_width - window.display_width) // 2 
        offset_y = (canvas_height - window.display_height) // 2
        
        # Apply scaling to crop coordinates, accounting for the offset
        x_start = int((min(window.x_start, window.x_end) - offset_x) * scale_x)
        y_start = int((min(window.y_start, window.y_end) - offset_y) * scale_y)
        x_end = int((max(window.x_start, window.x_end) - offset_x) * scale_x)
        y_end = int((max(window.y_start, window.y_end) - offset_y) * scale_y)
        
        # Ensure coordinates are within image bounds
        x_start = max(0, x_start)
        y_start = max(0, y_start)
        x_end = min(x_end, original_width)
        y_end = min(y_end, original_height)
        
        # Crop the image
        window.current_image = window.original_image[y_start:y_end, x_start:x_end]
        h, w = window.current_image.shape[:2]
        print("width")
        print(w)
        #cv2.imshow("Cropped", resize_for_display(window.current_image) )
        process_image(window)
    else:
        messagebox.showwarning("Warning", "Please select an area to crop.")


def create_cropFrame(window):
    # Clear the window
    for widget in window.winfo_children():
        widget.destroy()

    # Create a new canvas
    canvas = Canvas(
        window,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)
    window.edit_images = []

    image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
    window.edit_images.append(image_image_1)
    image_1 = canvas.create_image(
        719.0,
        57.0,
        image=image_image_1
    )
        # Add a title
    canvas.create_text(
        720,
        TITLEHEIGHT,
        text="Please crop image to exclude plate lable, line up vertical sides with inner edges of the plate",
        fill=DARK,
        font=(FONT, 12, 
        "bold")
    )

 # Resize image for display
    display_image, scale_factor = resize_for_display_crop(window.original_image)
    window.scale_factor = scale_factor

    # Convert OpenCV image to PhotoImage
    image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    photo = ImageTk.PhotoImage(image=image)

    # Create image on canvas
    canvas.create_image(720, 512, image=photo, anchor="center")
    canvas.image = photo

    # Store the display dimensions
    window.display_width = photo.width()
    window.display_height = photo.height()


    create_rounded_button(
        canvas=canvas,
        text="Crop",
        command=lambda: apply_crop(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag = "cropNext" )


    # Cropping variables
    window.cropping = False
    window.x_start, window.y_start, window.x_end, window.y_end = 0, 0, 0, 0

    # Bind mouse events
    canvas.bind("<ButtonPress-1>", lambda event: start_crop(event, window))
    canvas.bind("<B1-Motion>", lambda event: crop(event, window, canvas))
    canvas.bind("<ButtonRelease-1>", lambda event: end_crop(event, window, canvas))


    window.progress_frame = Frame(window, bg=LIGHT)
    window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)

    # Create and pack the progress bar with the custom style
    window.progress_bar = ttk.Progressbar(window.progress_frame, style="styled.Horizontal.TProgressbar", orient="horizontal",
                                        length=150, mode="determinate", maximum=100, value=0)
    window.progress_bar.pack(side="left", padx=(0, 10))

    # Label next to the progress bar
    window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    window.progress_label.pack(side="left")
    
    update_progress_bar(window)


# db    db d8888b. db       .d88b.   .d8b.  d8888b. .d8888. 
# 88    88 88  `8D 88      .8P  Y8. d8' `8b 88  `8D 88'  YP 
# 88    88 88oodD' 88      88    88 88ooo88 88   88 `8bo.   
# 88    88 88~~~   88      88    88 88~~~88 88   88   `Y8b. 
# 88b  d88 88      88booo. `8b  d8' 88   88 88  .8D db   8D 
# ~Y8888P' 88      Y88888P  `Y88P'  YP   YP Y8888D' `8888Y' 

def upload_txt_file(window):
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        window.image_info = []
        window.image_paths = []  # Initialize image_paths
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) > 1:  # Check if there's more than just the header
                header = lines[0].strip().split(',')
                print(f"Debug: Header: {header}")
                for line in lines[1:]:
                    parts = line.strip().split(',')

                    if len(parts) == 8:  # Adjusted for the new format
                        window.image_info.append({
                            'filename': parts[0],
                            'type': parts[1],
                            'detergent': parts[2],
                            'treatment': parts[3],
                            'repeat': parts[4],
                            'strainA': parts[5],
                            'QuantificationA': None,
                            'strainB': parts[6],
                            'QuantificationB': None,
                            'strainC': parts[7],
                            'QuantificationC': None
                        })
                    else:
                        print(f"Debug: Skipping line due to incorrect number of parts: {len(parts)}")
        window.current_image_index = 0

    


def upload_images(window):
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
    

    for info in window.image_info:
        print(f"  - {info['filename']}")
    

    for path in file_paths:
        print(f"  - {os.path.basename(path)}")
    
    if file_paths and hasattr(window, 'image_info'):
        window.image_paths = []
        for info in window.image_info:
            matching_path = next((path for path in file_paths if os.path.basename(path).lower() == info['filename'].lower()), None)
            if matching_path:
                window.image_paths.append(matching_path)
            else:
                print(f"Debug: No matching image found for {info['filename']}")
       
        if window.image_paths:
            window.current_image_index = 0
            load_current_image(window)
        else:
            print("Debug: No matching images found at all")
            messagebox.showwarning("Warning", "No matching images found")


def load_current_image(window):
    if 0 <= window.current_image_index < len(window.image_paths):
        window.image_path = window.image_paths[window.current_image_index]
        window.original_image = cv2.imread(window.image_path)
        if window.original_image is None:
            messagebox.showerror("Error", f"Failed to load image: {window.image_path}")
            return
        window.current_image = window.original_image.copy()
       
        # Update the current image info
        window.current_image_info = window.image_info[window.current_image_index]
    else:
        messagebox.showerror("Error", "No image to load")

def next_image(window):
    if window.current_image_index < len(window.image_paths) - 1:
        window.current_image_index += 1
        load_current_image(window)
        create_cropFrame(window)
        update_progress_bar(window)
    else:
        display_results(window)




# d8888b.  .d88b.  db   d8b   db d8b   db db       .d88b.   .d8b.  d8888b. .d8888. 
# 88  `8D .8P  Y8. 88   I8I   88 888o  88 88      .8P  Y8. d8' `8b 88  `8D 88'  YP 
# 88   88 88    88 88   I8I   88 88V8o 88 88      88    88 88ooo88 88   88 `8bo.   
# 88   88 88    88 Y8   I8I   88 88 V8o88 88      88    88 88~~~88 88   88   `Y8b. 
# 88  .8D `8b  d8' `8b d8'8b d8' 88  V888 88booo. `8b  d8' 88   88 88  .8D db   8D 
# Y8888D'  `Y88P'   `8b8' `8d8'  VP   V8P Y88888P  `Y88P'  YP   YP Y8888D' `8888Y' 
                                                                                



def write_image_info_to_file(window):
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx")])
    if filename:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Image Data"

        # Define dilution series
        dilutionSeries = [0, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]

        # Write header
        headers = ["filename", "type", "detergent", "treatment", "repeat", "strain", "Name", "quantification", "fold_dilution"]
        ws.append(headers)

        # Write data
        for info in window.image_info:
            base_row = [info['filename'], info['type'], info['detergent'], info['treatment'], info['repeat'], info['Name']]
            
            # Add rows for strain A
            if info['QuantificationA']:
                for quant, dilution in zip(info['QuantificationA'], dilutionSeries[:len(info['QuantificationA'])]):
                    row = base_row + [info['strainA'], quant, dilution]
                    ws.append(row)
            
            # Add rows for strain B
            if info['QuantificationB']:
                for quant, dilution in zip(info['QuantificationB'], dilutionSeries[:len(info['QuantificationB'])]):
                    row = base_row + [info['strainB'], quant, dilution]
                    ws.append(row)
            
            # Add rows for strain C
            if info['QuantificationC']:
                for quant, dilution in zip(info['QuantificationC'], dilutionSeries[:len(info['QuantificationC'])]):
                    row = base_row + [info['strainC'], quant, dilution]
                    ws.append(row)

        # Save the workbook
        wb.save(filename)













##     ##  #######  ########  ########  ######  
###   ### ##     ## ##     ## ##       ##    ## 
#### #### ##     ## ##     ## ##       ##       
## ### ## ##     ## ##     ## ######    ######  
##     ## ##     ## ##     ## ##             ## s
##     ## ##     ## ##     ## ##       ##    ## 
##     ##  #######  ########  ########  ###### 

def on_contrast_change(window, value, backToEdit = False):
    global backToEdit2
    if (backToEdit2 == False):
        window.contrast_value = float(value)
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots)
        # Update the binarized image and contour image
        window.binarized_image = final_binary
        window.contour_img = contour_img
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        # Update the history
        add_to_history(window)
        # Refresh the displayed images
        display_images(window)
    else:
        backToEdit2 = False   
 
def on_excludeSmallDots(window, value, backToEdit = False):
    #print("on_excludeSmallDots")
    global backToEdit2

    if (backToEdit2 == False):
        window.excludeSmallDots = float(value)
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots)
        # Update the binarized image
        window.binarized_image = final_binary
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        # print("am i resetting here?")
        # Update the history
        add_to_history(window)
        # Refresh the displayed images
        display_images(window)
    else:
        backToEdit2 = False

def set_mode(window, mode):
    window.mode = mode
    if mode == "small_brush" or mode == "small_eraser":
        window.brush_size = 40
    elif mode == "large_brush" or mode == "large_eraser":
        window.brush_size = 120

def toggle_image(window):
    window.show_original = not window.show_original
    display_images(window)

def display_images(window):

    try:
        # # Right image (editing image)
        # cv2.imshow("debug image", resize_for_display(window.debug_image))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        img_editing = Image.fromarray(window.debug_image)
        img_editing.thumbnail((window.winfo_width()//2 - 60, window.winfo_height() - 200))
        window.photo_editing = ImageTk.PhotoImage(img_editing)
        window.right_canvas.config(width=window.photo_editing.width(), height=window.photo_editing.height())
        window.right_canvas.create_image(0, 0, anchor="nw", image=window.photo_editing)
       
        window.display_width = window.photo_editing.width()
        window.display_height = window.photo_editing.height()

        # Left image (toggleable)
        if window.show_original:
            img_left = Image.fromarray(cv2.cvtColor(window.current_image, cv2.COLOR_BGR2RGB))
        else:
            img_np = window.current_image
            img_editing_resized = cv2.resize(np.array(img_editing), (img_np.shape[1], img_np.shape[0]))
            img_gray = cv2.cvtColor(img_editing_resized, cv2.COLOR_RGB2GRAY)
            contours, _ = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour_img = img_np.copy()
            for cntr in contours:
                cv2.drawContours(contour_img, [cntr], 0, (0, 255, 255), 2)
            img_left = Image.fromarray(cv2.cvtColor(contour_img, cv2.COLOR_BGR2RGB))

        img_left.thumbnail((window.winfo_width()//2 - 60, window.winfo_height() - 200))
        window.photo_left = ImageTk.PhotoImage(img_left)
        window.left_canvas.config(width=window.photo_left.width(), height=window.photo_left.height())
        window.left_canvas.create_image(0, 0, anchor="nw", image=window.photo_left)

    except Exception as e:
        print(f"Error in display_images: {e}")

def start_draw(window, event):
    window.is_drawing = True
    window.last_x = event.x
    window.last_y = event.y
    window.active_canvas = event.widget
    draw(window, event)

def draw(window, event):
    if window.is_drawing:
        x, y = event.x, event.y
        img_height, img_width = window.binarized_image.shape[:2]
        scale_x = img_width / window.display_width
        scale_y = img_height / window.display_height

        x_img = int(x * scale_x)
        y_img = int(y * scale_y)
        last_x_img = int(window.last_x * scale_x)
        last_y_img = int(window.last_y * scale_y)

        if window.mode == "flood":
            flood_erase(window, x_img, y_img)
        else:
            brush_draw(window, last_x_img, last_y_img, x_img, y_img)

        window.last_x = x
        window.last_y = y
        display_images(window)

def stop_draw(window, event):
    window.is_drawing = False
    current_state = window.binarized_image.copy()
    if len(window.history) == 0 or not np.array_equal(current_state, window.history[-1]):
        add_to_history(window)
    update_undo_redo_buttons(window)

def flood_erase(window, x, y):
    if window.binarized_image[y, x] == 255:  # If the clicked pixel is white
        cv2.floodFill(window.binarized_image, None, (x, y), 0)  # Fill with black
        window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)

def brush_draw(window, x1, y1, x2, y2):
    if window.mode in ["small_brush", "large_brush"]:
        color = 255  # White color for drawing
    else:
        color = 0  # Black color for erasing
    cv2.line(window.binarized_image, (x1, y1), (x2, y2), color, window.brush_size)
    window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)
    cv2.line(window.debug_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

def brush_erase(window, x1, y1, x2, y2):
    cv2.line(window.binarized_image, (x1, y1), (x2, y2), 0, window.brush_size * 2)
    window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)
    cv2.line(window.debug_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
def add_to_history(window):
    current_state = window.binarized_image.copy()
    if not window.history or not np.array_equal(current_state, window.history[-1]):
        window.history.append(current_state)
        window.redo_stack.clear()
        update_undo_redo_buttons(window)

def undo(window):
    if len(window.history) > 1:
        current_state = window.binarized_image.copy()
        window.redo_stack.append(current_state)
        window.binarized_image = window.history.pop().copy()
        window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)
        display_images(window)
    elif len(window.history) == 1:
        # If there's only one item in history, it's the original image
        current_state = window.binarized_image.copy()
        if not np.array_equal(current_state, window.history[0]):
            window.redo_stack.append(current_state)
            window.binarized_image = window.history[0].copy()
            window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)
            display_images(window)
    update_undo_redo_buttons(window)

def redo(window):
    if window.redo_stack:
        window.history.append(window.binarized_image.copy())
        window.binarized_image = window.redo_stack.pop().copy()
        window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)
        display_images(window)
        update_undo_redo_buttons(window)

def update_undo_redo_buttons(window):
    if hasattr(window, 'undo_btn') and window.undo_btn is not None:
        window.undo_btn['state'] = "normal" if len(window.history) > 1 else "disabled"
    if hasattr(window, 'redo_btn') and window.redo_btn is not None:
        window.redo_btn['state'] = "normal" if window.redo_stack else "disabled"

def brush_draw(window, x1, y1, x2, y2):
    if window.mode in ["small_brush", "large_brush"]:
        color = 255  # White color for drawing
    else:
        color = 0  # Black color for erasing
    cv2.line(window.binarized_image, (x1, y1), (x2, y2), color, window.brush_size)
    window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)
    cv2.line(window.debug_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

def initialize_window_attributes(window):
    # Style for the progress bar
    s = ttk.Style()
    s.theme_use('clam')
    s.configure("styled.Horizontal.TProgressbar", troughcolor=LIGHT,bordercolor=DARK, background=DARK, lightcolor=DARK, 
                darkcolor=DARK)
    style = ttk.Style()

    # Configure the scale slider appearance
    style.configure("TScale",
                    background=DARK,
                    troughcolor=LIGHT,
                    sliderthickness=15,
                    sliderlength=25)  # Adjust size of the knob to be rounder            

    window.window_width = 1440
    window.window_height = 1024
    window.history = []
    window.undo_btn = None
    window.redo_btn = None
    window.redo_stack = []
    window.mode = "small_brush"
    window.brush_size = 5
    window.is_drawing = False
    window.last_x = None
    window.last_y = None
    window.update_undo_redo_buttons = update_undo_redo_buttons
    window.display_images = display_images
    window.excludeSmallDots = 15
    window.contrast_value = 20
    window.image_paths = []
    window.current_image_index = 0
    window.next_button = None
    window.progress_bar = None
    window.progress_label = None
    window.current_image = None 

window = Tk()
window.geometry("1440x1024")
window.configure(bg=LIGHT)
window.title("SpotPlotter")
window.iconbitmap(r'C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\GUI\ICONS\ICON.ico')
#DFAULT VALUES

initialize_window_attributes(window)
# Create the title frame
title_frame_widgets = create_titleFrame(window)

window.resizable(False, False)
window.mainloop()
