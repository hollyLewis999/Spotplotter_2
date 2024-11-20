#Acknolgements: 
#Tkinter Designer by Parth Jadhav
#https://github.com/ParthJadhav/Tkinter-Designer


from pathlib import Path
import os
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage,filedialog,font, Y, X, Frame, Scrollbar, BOTTOM, Label,messagebox, Scale, HORIZONTAL,BooleanVar, Checkbutton, CENTER,  DoubleVar, ROUND, LEFT, RIGHT
from tkinter import ttk
import tkinter as tk
import cv2
import numpy as np
from scipy.spatial import distance
from PIL import Image, ImageTk, ImageDraw
import copy
from functools import partial
import time
import math 
import sys
import json
import os
from datetime import datetime
from collections import defaultdict
import pickle


from Processing import *
from outputs import *
from metadataMaker import *
from Style import *
sys.path.append(r'C:\Users\ThinkPad\AppData\Roaming\Python\Python312\site-packages')
COLORS = ["#3B82F6", "#10B981", "#F97316", "#EF4444", "#8B5CF6", "#D53F8C", "#6B7280", "#4B5563"]
import openpyxl



DARK = "#092934"
LIGHT = "#FFFFFF"
# DARK = "#FFFFFF"
# LIGHT = "#092934"
GRAY = "#B0B0B0"
ACCENT = "#4169E1"
FONT = "Microsoft New Tai Lue"
TITLEHEIGHT = 130
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\GUI\assets\frame0")
buttonPosX = 1200
buttonPosY = 885
backToEdit2 = False
PROGRESSX = 1180
PROGRESSY = 36


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)






# .88b  d88. d88888b d888888b  .d8b.  d8888b.  .d8b.  d888888b  .d8b.  
# 88'YbdP`88 88'     `~~88~~' d8' `8b 88  `8D d8' `8b `~~88~~' d8' `8b 
# 88  88  88 88ooooo    88    88ooo88 88   88 88ooo88    88    88ooo88 
# 88  88  88 88~~~~~    88    88~~~88 88   88 88~~~88    88    88~~~88 
# 88  88  88 88.        88    88   88 88  .8D 88   88    88    88   88 
# YP  YP  YP Y88888P    YP    YP   YP Y8888D' YP   YP    YP    YP   YP 





def create_plate_designer(window):
    # Clear window
    for widget in window.winfo_children():
        widget.destroy()
        
    # Initialize window properties
    # window.title("Plate Layout Designer")
    # window.geometry("1440x1024")
    # window.configure(bg=LIGHT)
    
    # Initialize plate layout attributes
    window.plate_layout = {
        'rows': tk.IntVar(value=8),
        'columns': tk.IntVar(value=12),
        'strains': tk.IntVar(value=2),
        'x_dilution': tk.IntVar(value=10),
        'y_dilution': tk.IntVar(value=2),
        'gap_between_strains': tk.BooleanVar(value=False),
        'removed_positions': set(),
        'strain_positions': {}
    }

    
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

    image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
    canvas.image_image_1 = image_image_1  # Keeping a reference to prevent garbage collection
    image_1 = canvas.create_image(719.0, 57.0, image=image_image_1)
    # Main dark rectangles
    round_rectangle(canvas, 17.0, 168.0, 1100.0, 826.0, fill=DARK, outline="")
    round_rectangle(canvas, 1120.0, 168.0, 1422.0, 826.0, fill=DARK, outline="")
    
    # Create frames
    plate_frame = Frame(window, bg=DARK)
    plate_frame.place(x=27, y=178, width=1070, height=638)
    
    control_frame = Frame(window, bg=DARK)
    control_frame.place(x=1130, y=178, width=282, height=638)

    create_controls(control_frame, window)
    create_plate_display(plate_frame, window)
    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: go_to_assignment_screen(window),
        x=buttonPosX,
        y=buttonPosY
    )

    create_rounded_button(
        canvas=canvas,
        text="Back",
        command=lambda: create_titleFrame(window),
        x=17.0,
        y=buttonPosY
    )




















######  ########  ########    ###    ######## ########     ######   ######  ########  ######## ######## ##    ##  ######  
##    ## ##     ## ##         ## ##      ##    ##          ##    ## ##    ## ##     ## ##       ##       ###   ## ##    ## 
##       ##     ## ##        ##   ##     ##    ##          ##       ##       ##     ## ##       ##       ####  ## ##       
##       ########  ######   ##     ##    ##    ######       ######  ##       ########  ######   ######   ## ## ##  ######  
##       ##   ##   ##       #########    ##    ##                ## ##       ##   ##   ##       ##       ##  ####       ## 
##    ## ##    ##  ##       ##     ##    ##    ##          ##    ## ##    ## ##    ##  ##       ##       ##   ### ##    ## 
 ######  ##     ## ######## ##     ##    ##    ########     ######   ######  ##     ## ######## ######## ##    ##  ######  


def create_titleFrame(window):
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
   
    ###LOGO IMAGE
    image_path_10 = relative_to_assets("image_10.png")
    img_logobig = Image.open(image_path_10)
    img_logobig_resized = img_logobig.resize((img_logobig.width // 2, img_logobig.height //2), Image.LANCZOS) #this resizing method maintains the quality

    #has to be a photoimage for Tkinkter, 
    image_image_10 = ImageTk.PhotoImage(img_logobig_resized)
    canvas.image_image_10 = image_image_10
    canvas.create_image(720.0, 420.0, image=image_image_10)


    create_rounded_button(
        canvas=canvas,
        text="Upload Assays",
        command=lambda: upload_images(window),
        x=730.0,
        y=670.0, )

    create_rounded_button(
        canvas=canvas,
        text="Upload MetaData",
        command=lambda: upload_txt_file(window),
        x=510.0,
        y=670.0,)

    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: validate_and_proceed(window),
        x=buttonPosX,
        y=buttonPosY )

        

    create_rounded_button(
    canvas=canvas,
    text="Create Metadata",
    command=lambda: create_plate_designer(window),
    x=290.0,
    y=670.0)    

    create_rounded_button(
    canvas=canvas,
    text="Upload MetaData NEW",
    command=lambda: upload_metadata_handler(window),
    x=950.0,
    y=670.0)


    return canvas


def display_results(window):

    for widget in window.winfo_children():
        widget.destroy()

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
    #logo
    image_path_10 = relative_to_assets("image_10.png")
    img_logobig = Image.open(image_path_10)
    img_logobig_resized = img_logobig.resize((img_logobig.width // 2, img_logobig.height //2), Image.LANCZOS)

    image_image_10 = ImageTk.PhotoImage(img_logobig_resized)
    canvas.image_image_10 = image_image_10 
    canvas.create_image(720.0, 420.0, image=image_image_10)


    canvas.create_text(
        720,  
        750.0,
        text="Results Downloading......",
        fill=DARK,
        font=(FONT, 12, "bold"),
        anchor="center" 
    )

    #this makes sure that the screen doesnt freeze on the previous screen. It loads up will here, generates the results and then displays the finish button
    window.update()


    #generates the PDF, the excel and the images 
    generate_all_outputs(window)
    #this will only display once the results are generated
    create_rounded_button(
        canvas=canvas,
        text="Finish",
        command=lambda: window.quit(),#will exit the program
        x=720 - (200 // 2),  
        y=buttonPosY-100,
        button_tag="Finish"
    )



    

def display_final_image(window, override =False):
    cv2.imshow("EDITwindow.all_plate_info[0]['IMGbinaryAutomatic']", resize_for_display(window.all_plate_info[0]['IMGbinaryAutomatic']))
    add_to_history(window) #incase the user goes back

    for widget in window.winfo_children():
        widget.destroy()

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


    create_rounded_button(
        canvas=canvas,
        text="Redo Edit",
        command=lambda: create_editFrame(window),
        x=720-225,
        y=buttonPosY,
        button_tag = "back_button_edit" )


    create_rounded_button(
        canvas=canvas,
        text="Override Grid",
        command=lambda: open_grid_override(window),
        x=720+25,
        y=buttonPosY,
        button_tag = "override_button" )

    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: next_image(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag = "DisplayNext" )




    #frame where result will be displayed
    frame = Frame(window, bg=LIGHT)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    if (override):#ie if the user has over ridden the grid
        marked_image = window.marked_image
        result_grid = window.result_grid
        window.all_plate_info[window.current_image_index]['unorderedquantifications'] = result_grid
        # print(f"Debug: CURRENT INDEX {window.current_image_index}")
        # print(f"Debug: Current image info: {window.current_info}")
        # print(f"Debug: 345434 ALL INFO : {window.image_info}" )
    else:   
        gray_image = window.gray_image  
        columns = window.all_plate_info[window.current_image_index]['layout']['columns']
        rows = window.all_plate_info[window.current_image_index]['layout']['rows']
        result_grid, marked_image = detect_and_draw_circles(window.binarized_image, gray_image, False,columns = columns, rows = rows )
        window.all_plate_info[window.current_image_index]['unorderedquantifications'] = result_grid
        #print(window.all_plate_info)
        # #comment out later, for testing and report
        # path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Tests/GroundTuth/TESTS/Cropped/RESULTS/"
        # cv2.imwrite(path +window.current_info['filename']+ '_result.png', marked_image)   
        # # # cv2.imshow("marked", resize_for_display(marked_image))

        # #checking to see if the window has current into to avoid cracshing
        # if hasattr(window, 'current_info'):
        #     window.current_info['QuantificationA'] = ordered_counts["Strain 1"]
        #     window.current_info['QuantificationB'] = ordered_counts["Strain 2"]
        #     window.current_info['QuantificationC'] = ordered_counts["Strain 3"]

        #     window.image_info[window.current_image_index] = window.current_info
        #     # print(f"Debug: CURRENT INDEX {window.current_image_index}")
        # #     # print(f"Debug: Current image info: {window.current_info}")
        # #     # print(f"Debug:098765 ALL INFO : {window.image_info}" )
        # else:
        #     print("Error: current_info not initialized")

        # # print("TESTER INFORMATION:") 
        # # print("_______________________________________________________________________")
        # # print(window.current_info['filename'])
        # print(ordered_counts["Strain 1"])    
        # print(ordered_counts["Strain 2"])   
        # print(ordered_counts["Strain 3"])   

    #make sure its the correct type
    if isinstance(marked_image, Image.Image):
        marked_image = np.array(marked_image)
        # print("yes is instance")

    #this is also taking into account that the one uses RGB and the other uses BGR    
    marked_image = cv2.cvtColor(marked_image, cv2.COLOR_RGB2BGR)   


    #resizing the image to fit
    max_width, max_height = 1200, 700
    h, w = marked_image.shape[:2]
    scale = min(max_width / w, max_height / h)
    new_size = (int(w * scale), int(h * scale))


    #saving what values and images to be used in the PDF reort
    window.all_plate_info [window.current_image_index]["threshold"] = window.contrast_value
    window.all_plate_info [window.current_image_index]["smallArea"] = window.excludeSmallDots
    window.all_plate_info [window.current_image_index]["blocksize"] = window.block_size
    window.all_plate_info [window.current_image_index]["IMGgrid"] = marked_image
    window.all_plate_info [window.current_image_index]["IMGbinary"] = window.binarized_image
    
    
    ###HERE ABC
    # window.image_info[window.current_image_index]["IMGgrid"] = marked_image
    # cv2.imshow("marked", resize_for_display(marked_image))
    # # cv2.imshow("contours", resize_for_display(window.marked_image))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()




    #Has to be PIL image for tkinkter, resizing and displaying
    resized_image = cv2.resize(marked_image, new_size, interpolation=cv2.INTER_AREA)
    img = Image.fromarray(resized_image)
    photo = ImageTk.PhotoImage(img)
    x_position = (1440 - new_size[0]) // 2
    y_position = (974 - new_size[1]) // 2
    canvas.create_image(x_position, y_position, anchor="nw", image=photo)
    canvas.image = photo





    #progress bar was created with help from Chat GBT
    window.progress_frame = Frame(window, bg=LIGHT)
    window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)
    window.progress_bar = ttk.Progressbar(window.progress_frame, style="styled.Horizontal.TProgressbar", orient="horizontal",
                                        length=150, mode="determinate", maximum=100, value=0)
    window.progress_bar.pack(side="left", padx=(0, 10))
    window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    window.progress_label.pack(side="left")
    
    update_progress_bar(window)

def create_slidersFrame(window):
    # Create main canvas
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

    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: create_editFrame(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag = "slidersNext" )

    # Main dark rectangle for image area
    round_rectangle(canvas,
        17.0,
        168.0,
        1100.0,
        826.0,
        fill=DARK,
        outline="")

    # Control panel rectangle
    round_rectangle(canvas,
        1120.0,
        168.0,
        1422.0,
        826.0,
        fill=DARK,
        outline="")

    # Create frame for image canvas
    main_frame = Frame(window, bg=DARK)
    main_frame.place(x=27, y=178, width=1070, height=638)

    # Create single canvas for image display
    window.image_canvas = Canvas(
        main_frame,
        width=1050,
        height=580,
        bg=DARK,
        highlightthickness=0
    )
    window.image_canvas.pack(expand=True, fill='both')

    # Control panel
    control_frame = Frame(window, bg=DARK)
    control_frame.place(x=1130, y=178, width=282, height=638)

    # Sliders setup
    y_offset = 20
    spacing = 100

    # Threshold Slider
    threshold_label = Label(control_frame, text="Threshold", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    threshold_label.place(x=20, y=y_offset)
    create_circular_slider(
        control_frame, 
        min_val=0, 
        max_val=40,
        position=(40, y_offset + 30),
        command=lambda v: on_contrast_change(window, v, False),
        initial_value=window.contrast_value
    )

    # Size Slider
    size_label = Label(control_frame, text="Size", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    size_label.place(x=20, y=y_offset + spacing)
    create_circular_slider(
        control_frame, 
        min_val=1, 
        max_val=100,
        position=(40, y_offset + spacing + 30),
        command=lambda v: on_excludeSmallDots(window, v, False),
        initial_value=window.excludeSmallDots
    )

    # Block Size Slider
    block_label = Label(control_frame, text="Block Size", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    block_label.place(x=20, y=y_offset + spacing * 2)
    create_circular_slider(
        control_frame, 
        min_val=51, 
        max_val=1001,
        position=(40, y_offset + spacing * 2 + 30),
        command=lambda v: on_block_size_change(window, v, False),
        initial_value=window.block_size if hasattr(window, 'block_size') else 301
    )

    # Toggle Original/Processed Image
    create_rounded_button(
        canvas=canvas,
        text="Toggle View",
        command=lambda: toggle_image(window),
        x=1130,
        y=y_offset + spacing * 3 + 30,
        button_tag="Toggle",
        width=140,
        height=40,
        fill=LIGHT,
        accent=DARK
    )

    # # Next button
    # create_rounded_button(
    #     canvas=canvas,
    #     text="Next",
    #     command=lambda: switch_to_edit_screen(window),
    #     x=1130,
    #     y=750,
    #     button_tag="adjustmentNext"
    # )

    # Progress bar
    window.progress_frame = Frame(window, bg=LIGHT)
    window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)
    window.progress_bar = ttk.Progressbar(
        window.progress_frame, 
        style="styled.Horizontal.TProgressbar", 
        orient="horizontal",
        length=150, 
        mode="determinate", 
        maximum=100, 
        value=0
    )
    window.progress_bar.pack(side="left", padx=(0, 10))
    window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    window.progress_label.pack(side="left")
    update_progress_bar(window)

    display_image(window)
    return canvas

def on_contrast_change(window, value, backToEdit = False):
    global backToEdit2
    if (backToEdit2 == False):
        window.contrast_value = float(value)
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots, block_size = window.block_size)

        #save new iamges
        window.binarized_image = final_binary
        window.contour_img = contour_img
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        # window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] = final_binary
        # print("SAVED")
        #cannot use undo redo buttons to undo this
        display_image(window)
    else:
        backToEdit2 = False   


def on_excludeSmallDots(window, value, backToEdit = False):
    #print("on_excludeSmallDots")
    global backToEdit2

    if (backToEdit2 == False):
        window.excludeSmallDots = float(value)
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots,block_size = window.block_size)

        #save new images
        window.binarized_image = final_binary
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        # print("am i resetting here?")
        # window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] = final_binary
        display_image(window)
    else:
        backToEdit2 = False


def on_block_size_change(window, value, backToEdit = False):
    #print("on_excludeSmallDots")
    global backToEdit2

    if (backToEdit2 == False):
        if int(value)%2 ==0:
            window.block_size = int(value)+1
        else:   
            window.block_size = int(value) 
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots, block_size = window.block_size)
        # window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] = final_binary
        #save new images
        window.binarized_image = final_binary
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        display_image(window)
    else:
        backToEdit2 = False


def display_image(window):
    try:
        # Get original image dimensions
        original_width = window.debug_image.shape[1]
        original_height = window.debug_image.shape[0]
        
        # Calculate available space
        canvas_width = 1050  # Fixed canvas width
        canvas_height = 580  # Fixed canvas height
        
        # Calculate scaling factors
        width_scale = canvas_width / original_width
        height_scale = canvas_height / original_height
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Calculate centering offsets
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2


        img_np = window.debug_image
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        contours, _ = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        contour_img = cv2.cvtColor(window.current_image, cv2.COLOR_BGR2RGB).copy()
        cv2.drawContours(contour_img, contours, -1, (0, 0, 255), 3)
        
        window.all_plate_info[window.current_image_index]["IMGcontours"] = contour_img
        window.current_info["IMGcontours"] = contour_img
        display_img = contour_img

        # Convert to PIL Image and resize
        img_pil = Image.fromarray(display_img)
        img_pil = img_pil.resize((new_width, new_height), Image.LANCZOS)
        window.photo_image = ImageTk.PhotoImage(img_pil)
        
        # Clear canvas and display new image
        window.image_canvas.delete("all")
        window.image_canvas.create_image(
            x_offset,
            y_offset,
            anchor="nw",
            image=window.photo_image
        )

    except Exception as e:
        print(f"Error in display_image: {e}")

def on_excludeSmallDots(window, value, backToEdit = False):
    #print("on_excludeSmallDots")
    global backToEdit2

    if (backToEdit2 == False):
        window.excludeSmallDots = float(value)
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots,block_size = window.block_size)

        #save new images
        window.binarized_image = final_binary
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        # print("am i resetting here?")
        #reset history, cannot use undo redo buttons to undo this
        display_image(window)
    else:
        backToEdit2 = False


def on_block_size_change(window, value, backToEdit = False):
    #print("on_excludeSmallDots")
    global backToEdit2

    if (backToEdit2 == False):
        if int(value)%2 ==0:
            window.block_size = int(value)+1
        else:   
            window.block_size = int(value) 
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots, block_size = window.block_size)

        #save new images
        window.binarized_image = final_binary
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        # print("am i resetting here?")
        #reset history, cannot use undo redo buttons to undo this
        display_image(window)
    else:
        backToEdit2 = False

def create_editFrame(window, backToEdit = False):

    global backToEdit2 #have to put this here if i want to edit it within this function
    if backToEdit == False:
        # Only set if not already set, or force overwrite is needed
        if window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] is None:
            window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] = window.binarized_image.copy()
            print("IMGbinaryAutomatic updated")
        cv2.imshow("window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic']", resize_for_display(window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic']))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

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

    window.show_original = False 

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

    # #displaying metadata fro mthe textfile, checking if current_info is initilised
    # #TODO HERE
    # if hasattr(window, 'current_info'):
    #     current_info = window.current_info
    #     metadata_text = f"Filename: {current_info['filename']}\n"
    #     metadata_text += f"StrainA: {current_info['strainA']}\n"
    #     metadata_text += f"StrainB: {current_info['strainB']}\n"
    #     metadata_text += f"StrainC: {current_info['strainC']}"
    # else:
    #     metadata_text = "No metadata available1"

    # #fixing issue of only metadata displaying
    # if hasattr(window, 'metadata_label'):
    #     window.metadata_label.destroy()  # Destroy the old label

    # window.metadata_label = Label(window, text=metadata_text, font=(FONT, 16 * -1, 'bold'), bg=LIGHT, fg=DARK, justify=LEFT)
    # window.metadata_label.place(x=50, y=850)


    canvas.create_text(
        1391.0,
        400.0,
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
    img_thinPen = Image.open(image_path_2) 
    #resizing image, using the othermethod made it super pixelated
    img_thinPen_resized = img_thinPen.resize((img_thinPen.width // 11, img_thinPen.height // 11), Image.LANCZOS)


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
    
    button_thin_pen.place(x=1377.0, y=420.0)


    # image_path_3 = relative_to_assets("image_3.png")
    # img_adder = Image.open(image_path_3) 
    # img_adder_resized = img_adder.resize((img_adder.width // 11, img_adder.height // 11), Image.LANCZOS)
    # image_image_3 = ImageTk.PhotoImage(img_adder_resized)    
    # window.edit_images.append(image_image_3)
    # magic_adder_button = Button(
    #     window,
    #     image=image_image_3,
    #     borderwidth=0,
    #     highlightthickness=0,
    #     command=lambda: print("adder"),
    #     relief="flat",
    #     bg = DARK
    # )
    # magic_adder_button.place(x=1376,y=402)


    #big eraser
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
    img_thickPen = Image.open(image_path_5) 
    img_thickPen_resized = img_thickPen.resize((img_thickPen.width // 11, img_thickPen.height // 11), Image.LANCZOS)


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
    big_pen_button.place(x=1377, y=460)


    image_path_6 = relative_to_assets("image_6.png")
    img_flood = Image.open(image_path_6) 
    img_flood_resized = img_flood.resize((img_flood.width // 11, img_flood.height // 11), Image.LANCZOS)


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
    img_redo = Image.open(image_path_7)
    img_redo_resized = img_redo.resize((img_redo.width // 11, img_redo.height // 11), Image.LANCZOS)

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


    #undo
    image_path_8 = relative_to_assets("image_8.png")
    img_undo = Image.open(image_path_8) 
    img_undo_resized = img_undo.resize((img_undo.width // 11, img_undo.height // 11), Image.LANCZOS)
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


    # thin eraser
    image_path_9 = relative_to_assets("image_9.png")
    img_thinEraser = Image.open(image_path_9)
    img_thinEraser_resized = img_thinEraser.resize((img_thinEraser.width // 11, img_thinEraser.height // 11), Image.LANCZOS)
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
    total_height = 783 - 203 - 100
    img_width = total_width // 2
    img_height = total_height

    # Create frames to hold canvas and scrollbars
    left_frame = Frame(window, bg=DARK)
    right_frame = Frame(window, bg=DARK)
    
    # Create canvases with scrollbars
    window.left_canvas = Canvas(
        left_frame,
        width=img_width,
        height=img_height,
        bg=DARK,
        highlightthickness=0
    )
    left_scroll_y = Scrollbar(left_frame, orient="vertical", command=window.left_canvas.yview)
    left_scroll_x = Scrollbar(left_frame, orient="horizontal", command=window.left_canvas.xview)


    window.right_canvas = Canvas(
        right_frame,
        width=img_width,
        height=img_height,
        bg=DARK,
        highlightthickness=0
    )
    right_scroll_y = Scrollbar(right_frame, orient="vertical", command=window.right_canvas.yview)
    right_scroll_x = Scrollbar(right_frame, orient="horizontal", command=window.right_canvas.xview)

    cv2.imshow("TEST4window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic']", resize_for_display(window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic']))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Synchronization functions
    def sync_scroll_y_left(*args):
        window.right_canvas.yview_moveto(args[0])

    def sync_scroll_y_right(*args):
        window.left_canvas.yview_moveto(args[0])

    def sync_scroll_x_left(*args):
        window.right_canvas.xview_moveto(args[0])

    def sync_scroll_x_right(*args):
        window.left_canvas.xview_moveto(args[0])

    # Configure scrollbar synchronization
    window.left_canvas.configure(
        xscrollcommand=lambda *args: (left_scroll_x.set(*args), sync_scroll_x_left(*args)),
        yscrollcommand=lambda *args: (left_scroll_y.set(*args), sync_scroll_y_left(*args))
    )

    window.right_canvas.configure(
        xscrollcommand=lambda *args: (right_scroll_x.set(*args), sync_scroll_x_right(*args)),
        yscrollcommand=lambda *args: (right_scroll_y.set(*args), sync_scroll_y_right(*args))
    )

    # Configure scrollbar commands to update both canvases
    left_scroll_y.configure(command=lambda *args: (window.left_canvas.yview(*args), window.right_canvas.yview(*args)))
    left_scroll_x.configure(command=lambda *args: (window.left_canvas.xview(*args), window.right_canvas.xview(*args)))
    right_scroll_y.configure(command=lambda *args: (window.right_canvas.yview(*args), window.left_canvas.yview(*args)))
    right_scroll_x.configure(command=lambda *args: (window.right_canvas.xview(*args), window.left_canvas.xview(*args)))

    # Grid layout for scrollbars
    window.left_canvas.grid(row=0, column=0, sticky="nsew")
    left_scroll_y.grid(row=0, column=1, sticky="ns")
    left_scroll_x.grid(row=1, column=0, sticky="ew")
        
    window.right_canvas.grid(row=0, column=0, sticky="nsew")
    right_scroll_y.grid(row=0, column=1, sticky="ns")
    right_scroll_x.grid(row=1, column=0, sticky="ew")

    # Configure grid weights
    left_frame.grid_rowconfigure(0, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)
    right_frame.grid_rowconfigure(0, weight=1)
    right_frame.grid_columnconfigure(0, weight=1)

    yposFrames= 300
    # Position the frames
    left_frame.place(x=30, y=yposFrames, width=img_width + 20, height=img_height + 20)
    right_frame.place(x=690, y=yposFrames, width=img_width + 20, height=img_height + 20)

    # Initialize zoom level
    window.zoom_level = 1.0
    
    # Set up zoom controls and bindings
    setup_zoom_controls(window)
    window.left_canvas.bind("<MouseWheel>", lambda e: mouse_zoom(window, e))
    window.right_canvas.bind("<MouseWheel>", lambda e: mouse_zoom(window, e))

    # Synchronize scrolling between canvases
    def on_left_scroll(*args):
        window.right_canvas.yview_moveto(args[1])
    
    def on_right_scroll(*args):
        window.left_canvas.yview_moveto(args[1])

    window.left_canvas.configure(yscrollcommand=lambda *args: (left_scroll_y.set(*args), on_left_scroll(*args)))
    window.right_canvas.configure(yscrollcommand=lambda *args: (right_scroll_y.set(*args), on_right_scroll(*args)))
    
    # Display images
    display_images(window)
    
    create_rounded_button(
        canvas=canvas,
        text="Toggle",
        command=lambda: toggle_image(window),
        x=1200,
        y=205,
        button_tag = "Toggle",
        width = 100, 
        height = 60,
        fill = LIGHT,
        accent = DARK)


    # #sliders
    # smallDots_label = Label(window, text="Size:", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    # smallDots_label.place(x=665, y=223)
    # smallDots_slider = create_circular_slider(
    #     window, min_val=1, max_val=100,
    #     position=(700, 190),
    #     command=lambda v: on_excludeSmallDots(window, v, False),
    #     initial_value=window.excludeSmallDots
    # )

    # contrast_label = Label(window, text="Threshold:", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    # contrast_label.place(x=220, y=223)
    # contrast_slider = create_circular_slider(
    #     window, min_val=0, max_val=40,
    #     position=(300, 190),
    #     command=lambda v: on_contrast_change(window, v, False),
    #     initial_value=window.contrast_value
    # )



    #bind mouse clicks to start the drawing mode, binding it like this allows the user to draw continiously until they let go of the click
    for canvas in [window.left_canvas, window.right_canvas]:
        canvas.bind("<ButtonPress-1>", lambda event: start_draw(window, event))
        canvas.bind("<B1-Motion>", lambda event: draw(window, event))
        canvas.bind("<ButtonRelease-1>", lambda event: stop_draw(window, event))
    #configuring buttonts to theit associated fucntions/modes
    button_thin_pen.config(command=lambda: set_mode(window, "small_brush"))
    big_pen_button.config(command=lambda: set_mode(window, "large_brush"))
    thin_eraser_button.config(command=lambda: set_mode(window, "small_eraser"))
    big_eraser_button.config(command=lambda: set_mode(window, "large_eraser"))
    flood_eraser_button.config(command=lambda: set_mode(window, "flood"))
    undo_button.config(command=lambda: undo(window))
    redo_button.config(command=lambda: redo(window))




    #progress bar (same code for all screens), created with help from chatGBT
    window.progress_frame = Frame(window, bg=LIGHT)
    window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)
    #making the position a global variable so if i move it i dont have to change it for all screens
    window.progress_bar = ttk.Progressbar(window.progress_frame, style="styled.Horizontal.TProgressbar", orient="horizontal",
                                        length=150, mode="determinate", maximum=100, value=0)
    window.progress_bar.pack(side="left", padx=(0, 10))
    window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    window.progress_label.pack(side="left")
    update_progress_bar(window)

    cv2.imshow("TEST5window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic']", resize_for_display(window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic']))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return canvas
def test_Next(window):
    cv2.imshow("EDITwindow.all_plate_info[0]['IMGbinaryAutomatic']", resize_for_display(window.all_plate_info[0]['IMGbinaryAutomatic']))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    
def update_zoomed_images(window):
    """Update both canvases with zoomed images, maintaining scrollable content"""
    window.left_canvas.delete("all")
    window.right_canvas.delete("all")
    
    left_img = window.current_image
    right_img = window.processed_image
    
    if left_img and right_img:
        # Calculate zoomed dimensions
        new_width = int(left_img.width * window.zoom_level)
        new_height = int(left_img.height * window.zoom_level)
        
        # Resize images
        left_img_zoomed = left_img.resize((new_width, new_height), Image.LANCZOS)
        right_img_zoomed = right_img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        window.left_photo = ImageTk.PhotoImage(left_img_zoomed)
        window.right_photo = ImageTk.PhotoImage(right_img_zoomed)
        
        # Set scroll region to the full size of the zoomed image
        window.left_canvas.config(scrollregion=(0, 0, new_width, new_height))
        window.right_canvas.config(scrollregion=(0, 0, new_width, new_height))
        
        # Display images at (0,0) - scrolling will handle visibility
        window.left_canvas.create_image(0, 0, anchor=NW, image=window.left_photo)
        window.right_canvas.create_image(0, 0, anchor=NW, image=window.right_photo)


def open_grid_override(window):
    for widget in window.winfo_children():
        widget.destroy()
   
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

    binary_image = window.binarized_image.copy()
    window.binary_image = binary_image

    rgb_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2RGB)
   
    #resizing as the dataset images are HUGE
    max_width, max_height = 1200, 700
    h, w = rgb_image.shape[:2]
    scale = min(max_width / w, max_height / h)
    new_size = (int(w * scale), int(h * scale))
    resized_image = cv2.resize(rgb_image, new_size, interpolation=cv2.INTER_AREA)
   
    img = Image.fromarray(resized_image)
    photo = ImageTk.PhotoImage(img)
    x_position = (1440 - new_size[0]) // 2
    y_position = (974 - new_size[1]) // 2
    canvas.create_image(x_position, y_position, anchor="nw", image=photo)
    canvas.image = photo
   
    #use scale factor for pen tools so it maps correcly on the image
    window.grid_override_scale = scale
    window.grid_override_offset = (x_position, y_position)
   
    #find the blobs so the centerpoints are displayed if the user tries to override the grid. Finding blobs is based on the size of the image incase the image is much bigger/smaller it cant be a set pixel size
    height, width = window.binary_image.shape
    coloums = window.all_plate_info[window.current_image_index]['layout']['columns']

    max_radius = int(width/(coloums*2))
    min_radius = int(max_radius/3)
    max_area = max_radius**2*(math.pi)
    min_area = min_radius**2*(math.pi)
    # cv2.imshow("marked image1244443", resize_for_display(marked_image))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    x_coords, y_coords, _ = findBlobs(binary_image, min_area, max_area)
    window.center_points = list(zip(x_coords, y_coords))

    window.blob_points = list(zip(x_coords, y_coords))
    print("window.blob_points")
    print(window.blob_points)
    window.clicked_points = []

    #allows the user to add points
    def draw_points():
        canvas.delete("point")
        for x, y in window.blob_points:
            scaled_x = x * scale + x_position
            scaled_y = y * scale + y_position
            canvas.create_line(scaled_x-5, scaled_y-5, scaled_x+5, scaled_y+5, fill=ACCENT, tags="point", width=4)
            canvas.create_line(scaled_x-5, scaled_y+5, scaled_x+5, scaled_y-5, fill=ACCENT, tags="point", width=4)
        for x, y in window.clicked_points:
            scaled_x = x * scale + x_position
            scaled_y = y * scale + y_position
            canvas.create_line(scaled_x-5, scaled_y-5, scaled_x+5, scaled_y+5, fill=ACCENT, tags="point", width=4)
            canvas.create_line(scaled_x-5, scaled_y+5, scaled_x+5, scaled_y-5, fill=ACCENT, tags="point", width=4)
    draw_points()

    #allows the user to remove points that they made OR points detected from find blobs
    def remove_point(event):
        x, y = (event.x - x_position) / scale, (event.y - y_position) / scale
        remove_radius = 50  #this allows the user to not be so exact with where they click
        blob_points = []

        #checking to see if point must be removed
        for point in window.blob_points:
            distance = ((point[0] - x)**2 + (point[1] - y)**2)**0.5
            if distance > remove_radius:
                blob_points.append(point)

        window.blob_points = blob_points
        #same thing for the clicked points
        clicked_points = []
        for point in window.clicked_points:
            distance = ((point[0] - x)**2 + (point[1] - y)**2)**0.5
            if distance > remove_radius:
                clicked_points.append(point)

        window.clicked_points = clicked_points
        #redraw everyhting
        draw_points()

    #if the user clicks
    def add_point(event):
        x, y = (event.x - x_position) / scale, (event.y - y_position) / scale
        #check if the point is within the image boundaries (otherwise it draws when you click on the add button)
        if (0 <= x < window.binary_image.shape[1] and 
            0 <= y < window.binary_image.shape[0]):
            window.clicked_points.append((int(x), int(y)))
            draw_points()

    #moves the crosshairs
    def on_mouse_move(event):
        canvas.delete("hover_line")
        x, y = event.x, event.y
        
        #checking how far they must expand so they are not outside the image boundaries
        left_boundary = x_position
        right_boundary = x_position + new_size[0]
        top_boundary = y_position
        bottom_boundary = y_position + new_size[1]

        #drawing them
        if top_boundary <= y <= bottom_boundary:
            canvas.create_line(left_boundary, y, right_boundary, y, fill=ACCENT, tags="hover_line")
        
        if left_boundary <= x <= right_boundary:
            canvas.create_line(x, top_boundary, x, bottom_boundary, fill=ACCENT, tags="hover_line")

    #this was the other option instead of the buttons, it binds to left and right mouse clicks
    canvas.bind("<Button-1>", add_point)
    canvas.bind("<Button-3>", remove_point)
    canvas.bind("<Motion>", on_mouse_move)

    #buttons
    create_rounded_button(
        canvas=canvas,
        text="Remove Points",
        command=lambda: canvas.bind("<Button-1>", remove_point),
        x=720+25,
        y=buttonPosY,
        button_tag = "Remove_Points" )


    create_rounded_button(
        canvas=canvas,
        text="Add Points",
        command=lambda: canvas.bind("<Button-1>", add_point),
        x=720-225,
        y=buttonPosY,
        button_tag = "Add_points" )

    create_rounded_button(
        canvas=canvas,
        text="Recalculate Grid",
        command=lambda: recalculate_grid(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag = "Recalculate" )


    window.mainloop()


def recalculate_grid(window):
    #user clicked and previously detected
    all_points = window.blob_points + window.clicked_points
    if len(all_points) < 12:
        messagebox.showwarning("Not enough points", "Please ensure there are at least 12 points before recalculating the grid.")
        return

    #convert to numpy array so its the same type as the senterpoints
    window.clicked_pointsx = [point[0] for point in all_points]
    window.clicked_pointsy = [point[1] for point in all_points]
    height, width = window.gray_image.shape
    #new grid using user clicked AND previously detected
    columns = window.all_plate_info[window.current_image_index]['layout']['columns']
    rows = window.all_plate_info[window.current_image_index]['layout']['rows']
    grid_start_x, grid_start_y, cell_size = calculate_grid(window.clicked_pointsx,window.clicked_pointsy, width, height, window.binary_image, window.gray_image, columns, rows)

    counts, marked_image= quantify_grid(window.binary_image, window.binary_image, grid_start_x, grid_start_y, cell_size,columns, rows)

    window.all_plate_info[window.current_image_index]['unorderedquantifications'] = counts
    # #SAVING INFO
    # if hasattr(window, 'current_info'):
    #     window.current_info['QuantificationA'] = ordered_counts["Strain 1"]
    #     window.current_info['QuantificationB'] = ordered_counts["Strain 2"]
    #     window.current_info['QuantificationC'] = ordered_counts["Strain 3"]
    #     # Update the window.image_info with the modified current_info
    #     window.image_info[window.current_image_index] = window.current_info.copy()
        
    #     # print("RECALCULATED:      TESTER INFORMATION:") 
    #     # print("_______________________________________________________________________")
    #     # print(ordered_counts["Strain 1"])    
    #     # print(ordered_counts["Strain 2"])   
    #     # print(ordered_counts["Strain 3"])   

    #     # print(f"Debug: CURRENT INDEX {window.current_image_index}")
    #     # print(f"Debug: Current image info: {window.current_info}")
    #     # print(f"Debug: in recalcgrid ALL INFO : {window.image_info}" )

    # else:
    #     print("Error: current_info not initialized")

    #update so the new override one is used
    window.result_grid= counts
    window.marked_image = marked_image
    display_final_image(window, True)


#progress bar update - help from chatGBT
def update_progress_bar(window):
    if hasattr(window, 'progress_bar') and window.progress_bar:
        progress = (window.current_image_index + 1) / len(window.image_paths) * 100
        window.progress_bar['value'] = progress
        window.progress_label.config(text=f"{window.current_image_index + 1}/{len(window.image_paths)}")

def validate_and_proceed(window):
    """
    Validates if the image paths and image info are properly initialized and match entries in window.all_plate_info.
    Proceeds to create the crop frame if valid, otherwise shows a warning.
    """
    # Ensure `window.image_paths`, `window.all_plate_info`, and `window.image_info` are initialized
    if (
        hasattr(window, 'image_paths') and window.image_paths
        and hasattr(window, 'all_plate_info') and window.all_plate_info
    ):
        # Check if all filenames in `window.image_info` exist in `window.all_plate_info`
        all_filenames = {info['filename'].lower() for info in window.all_plate_info}
        
        # Debugging: Print out expected filenames from the metadata
        # print("Expected filenames from metadata:")
        # for filename in all_filenames:
        #     print(f"- {filename}")
        
        # if unmatched:
        #     messagebox.showwarning(
        #         "Warning",
        #         f"The following filenames do not match metadata entries:\n{', '.join(unmatched)}"
        #     )
       # else:
        create_cropFrame(window)
    else:
        messagebox.showwarning("Warning", "Please upload both text file and images that match metadata entries.")


def process_image(window):
    stretched, blurred, gray_image, idealContrast = stretch_and_gray(window.current_image, False)
    window.contrast_value = idealContrast

    window.gray_image = gray_image
    binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.current_image, excludeSmallDots=window.excludeSmallDots, contrast=window.contrast_value, block_size = window.block_size)

    window.contour_img = contour_img
    window.binarized_image = final_binary
    window.debug_image = np.stack((final_binary,) * 3, axis=-1)
    
    # only initialize history if it's empty, othewise its adding doubles
    if not window.history:
        window.history = [window.binarized_image.copy()]
        window.redo_stack = []
    
    update_undo_redo_buttons(window)
    #create_editFrame(window)
    create_slidersFrame(window)


#  .o88b. d8888b.  .d88b.  d8888b. d8888b. d888888b d8b   db  d888b  
# d8P  Y8 88  `8D .8P  Y8. 88  `8D 88  `8D   `88'   888o  88 88' Y8b 
# 8P      88oobY' 88    88 88oodD' 88oodD'    88    88V8o 88 88      
# 8b      88`8b   88    88 88~~~   88~~~      88    88 V8o88 88  ooo 
# Y8b  d8 88 `88. `8b  d8' 88      88        .88.   88  V888 88. ~8~ 
#  `Y88P' 88   YD  `Y88P'  88      88      Y888888P VP   V8P  Y888P  


#makes sure that the crop takes into account the scale of the image, since its downsized
def resize_for_display_crop(image, max_width=1000, max_height=650):
    h, w = image.shape[:2]
    scale = min(max_width/w, max_height/h)
    new_size = (int(w*scale), int(h*scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA), scale


#get the co-ordnates of the click , where the crop starts
def start_crop(event, window):
    window.cropping = True
    window.x_start, window.y_start = event.x, event.y



def crop(event, window, canvas):

    #removes old rectangle and creates a new one
    if window.cropping:
        window.x_end, window.y_end = event.x, event.y
        canvas.delete("crop_rectangle")

        # Create the rectangle
        canvas.create_rectangle(
            window.x_start, window.y_start, window.x_end, window.y_end,
            outline=LIGHT,
            width=2,
            fill=LIGHT,
            stipple="gray50", #only had this option for low opacity
            tags="crop_rectangle"
        )

def end_crop(event, window, canvas):
    window.cropping = False

def apply_crop(window):
    if window.x_start != window.x_end and window.y_start != window.y_end:
        #dimensions of the original image
        original_height, original_width = window.original_image.shape[:2]
        
        #scaling factors
        scale_x = original_width / window.display_width
        scale_y = original_height / window.display_height
        
        #offset of the image on the canvas
        canvas_width = 1440  # From your create_cropFrame function
        canvas_height = 1024  # From your create_cropFrame function
        offset_x = (canvas_width - window.display_width) // 2 
        offset_y = (canvas_height - window.display_height) // 2
        
        #scaling to crop coordinates, accounting for the offset
        x_start = int((min(window.x_start, window.x_end) - offset_x) * scale_x)
        y_start = int((min(window.y_start, window.y_end) - offset_y) * scale_y)
        x_end = int((max(window.x_start, window.x_end) - offset_x) * scale_x)
        y_end = int((max(window.y_start, window.y_end) - offset_y) * scale_y)
        
        #check within image bounds, or map to beinging end of bounds
        x_start = max(0, x_start)
        y_start = max(0, y_start)
        x_end = min(x_end, original_width)
        y_end = min(y_end, original_height)
        
        #actual crop
        window.current_image = window.original_image[y_start:y_end, x_start:x_end]
        h, w = window.current_image.shape[:2]
        # print("width")
        # print(w)
        #cv2.imshow("Cropped", resize_for_display(window.current_image) )
        process_image(window)
    else:
        messagebox.showwarning("Warning", "Please select an area to crop.")


def create_cropFrame(window):
    for widget in window.winfo_children():
        widget.destroy()

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

    canvas.create_text(
        720,
        TITLEHEIGHT,
        text="Please crop image to exclude plate lable. Line up vertical sides with outer edges of the plate",
        fill=DARK,
        font=(FONT, 12, 
        "bold")
    )

    #resize image
    display_image, scale_factor = resize_for_display_crop(window.original_image)
    window.scale_factor = scale_factor

    #convert OpenCV to PhotoImage for Tkinkter to use
    image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    photo = ImageTk.PhotoImage(image=image)

    #place image on canvas
    canvas.create_image(720, 512, image=photo, anchor="center")
    canvas.image = photo

    #keep dimensions
    window.display_width = photo.width()
    window.display_height = photo.height()


    create_rounded_button(
        canvas=canvas,
        text="Crop",
        command=lambda: apply_crop(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag = "cropNext" )


    #default cropping variables
    window.cropping = False
    window.x_start, window.y_start, window.x_end, window.y_end = 0, 0, 0, 0

    #bind mouse events
    canvas.bind("<ButtonPress-1>", lambda event: start_crop(event, window))
    canvas.bind("<B1-Motion>", lambda event: crop(event, window, canvas))
    canvas.bind("<ButtonRelease-1>", lambda event: end_crop(event, window, canvas))

    #progress bar things - same as other screens
    window.progress_frame = Frame(window, bg=LIGHT)
    window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)
    window.progress_bar = ttk.Progressbar(window.progress_frame, style="styled.Horizontal.TProgressbar", orient="horizontal",length=150, mode="determinate", maximum=100, value=0)
    window.progress_bar.pack(side="left", padx=(0, 10))
    window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    window.progress_label.pack(side="left")
    update_progress_bar(window)


# db    db d8888b. db       .d88b.   .d8b.  d8888b. .d8888. 
# 88    88 88  `8D 88      .8P  Y8. d8' `8b 88  `8D 88'  YP 
# 88    88 88oodD' 88      88    88 88ooo88 88   88 `8bo.   
# 88    88 88~~~   88      88    88 88~~~88 88   88   `Y8b. 
# 88b  d88 88      88booo. `8b  d8' 88   88 88  .8D db   8D 
# ~Y8888P' 88      Y88888P  `Y88P'  YP   YP Y8888D' `8888Y' 

# def upload_txt_file(window):
#     file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
#     if file_path:

#         window.image_info = []
#         window.image_paths = []
#         skipped_lines = []#store which liens where skipped

#         with open(file_path, 'r') as file:
#             lines = file.readlines()
#             if len(lines) > 1:  #must be more than just header
#                 header = lines[0].strip().split(',') #split based on comma
#                 #print(f"Debug: Header: {header}")
#                 for i, line in enumerate(lines[1:], start=2):#start from second line (header in first)
#                     parts = line.strip().split(',')
#                     if len(parts) == 8:  # check correct number of parts
#                         info = {
#                             'filename': parts[0],
#                             'type': parts[1],
#                             'detergent': parts[2],
#                             'treatment': parts[3],
#                             'repeat': parts[4],
#                             'strainA': parts[5],
#                             'QuantificationA': None,
#                             'strainB': parts[6],
#                             'QuantificationB': None,
#                             'strainC': parts[7],
#                             'QuantificationC': None,
#                             'IMGcontours': None,  
#                             'IMGbinary': None,   
#                             'IMGgrid': None, 
#                             'threshold': 0,
#                             'smallArea': 0   
#                         }
#                         window.image_info.append(info) 
#                     else:
#                         skipped_lines.append(i)  #line number for skipped line
#         #display skipped lines
#         if skipped_lines:
#             messagebox.showwarning("Warning", f"Skipping {len(skipped_lines)} line(s) due to incorrect format.\nLine numbers: {', '.join(map(str, skipped_lines))} \nCorrect Format: FileName,Type,Detergent,Treatment,Repeat,StrainA_Name,StrainB_Name,StrainC_Name")
#          #initialize info
#         window.current_image_index = 0
#         if window.image_info:
#             window.current_info = window.image_info[0].copy() 
#         else:
#             window.current_info = None


# #For testing so i can upload anything
# def upload_images(window):
#     file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])

#     if file_paths:
#         window.image_paths = list(file_paths)
#         window.current_image_index = 0
#         load_current_image(window)
#     else:
#         messagebox.showwarning("Warning", "No images were selected.")
def upload_images(window):
    """
    Allow the user to upload image files, but only those that match filenames in window.all_plate_info.
    """
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
   
    # Ensure file_paths are selected and window.all_plate_info is initialized
    if file_paths and hasattr(window, 'all_plate_info'):
        window.image_paths = []
        unmatched_filenames = []  # Collect unmatched filenames

        # Get the list of filenames from window.all_plate_info
        valid_filenames = {info['filename'].lower() for info in window.all_plate_info}
        
        # Debugging: Print out expected filenames from the metadata
        print("Expected filenames from metadata:")
        for filename in valid_filenames:
            print(f"- {filename}")

        # Check the selected files for matches
        for path in file_paths:
            filename = os.path.basename(path).lower()
            if filename in valid_filenames:
                window.image_paths.append(path)
            else:
                unmatched_filenames.append(filename)

        # Handle matching and unmatched files
        if window.image_paths:
            window.current_image_index = 0
            load_current_image(window)  # Load the first matching image
            # if unmatched_filenames:
            #     messagebox.showwarning(
            #         "Warning",
            #         f"No matching entries found for {len(unmatched_filenames)} file(s):\n{', '.join(unmatched_filenames)}"
            #     )
        else:
            messagebox.showwarning(
                "Warning",
                "No matching images found for any entries in the metadata."
            )
    else:
        messagebox.showwarning(
            "Warning",
            "No files selected or metadata not initialized."
        )

def load_current_image(window):
    #within correct bounds
    if 0 <= window.current_image_index < len(window.image_paths):
        window.image_path = window.image_paths[window.current_image_index]
        window.original_image = cv2.imread(window.image_path)
        if window.original_image is None:
            messagebox.showerror("Error", f"Failed to load image: {window.image_path}")
            return
        window.current_image = window.original_image.copy()
       
        # # Update the current image info
        # print("IS IT HERE??????")

        # print("AFTER")

        #TODO NEED TO FIX HERE TO LOAD THE INFO
        window.current_info = window.all_plate_info[window.current_image_index].copy()
        # print(f"Debug: Loading image {window.current_image_index}")
        # print(f"Debug: Current image info: {window.current_info}")
    else:
        messagebox.showerror("Error", "No image to load")

def next_image(window):
    if window.current_image_index < len(window.image_paths) - 1:
        window.current_image_index += 1
        load_current_image(window)
        create_cropFrame(window)
        update_progress_bar(window)
        # print(f"Debug: CURRENT INDEX {window.current_image_index}")
        # print(f"Debug: Current image info: {window.current_info}")
        # print(f"Debug: ALL INFO : {window.image_info}" )
    else:
        save_window_state(window, 'window_state_IntermediaryImages.pkl')
        print("saved")
        # processResults(window)

import cv2
import numpy as np

def process_tool_usage(window):
    """
    Process binary images to create a color-coded visualization of tool usage.
    
    Args:
        window: Window object containing all_plate_info with binary images
    """
    print(window.all_plate_info)
    for plate_info in window.all_plate_info:
        # Skip if either image is None
        if plate_info['IMGbinary'] is None or plate_info['IMGbinaryAutomatic'] is None:
            print("IS NONE")
            continue
            
        # Get the binary images
        manual_binary = plate_info['IMGbinary']
        auto_binary = plate_info['IMGbinaryAutomatic']
        
        # Ensure both images are binary (0 or 255)
        _, manual_binary = cv2.threshold(manual_binary, 127, 255, cv2.THRESH_BINARY)
        _, auto_binary = cv2.threshold(auto_binary, 127, 255, cv2.THRESH_BINARY)
        
        # Create blank RGB image
        height, width = manual_binary.shape
        tool_usage = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Where both are white (255)
        both_white = cv2.bitwise_and(manual_binary, auto_binary)
        tool_usage[both_white == 255] = [255, 255, 255]  # White
        
        # Where only manual is white
        only_manual = cv2.bitwise_and(manual_binary, cv2.bitwise_not(auto_binary))
        tool_usage[only_manual == 255] = [0, 0, 255]  # Red
        
        # Where only automatic is white
        only_auto = cv2.bitwise_and(auto_binary, cv2.bitwise_not(manual_binary))
        tool_usage[only_auto == 255] = [255, 0, 0]  # Blue
        cv2.imshow("debug image", resize_for_display(tool_usage))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # Save the result back to the plate info
        plate_info['IMGToolUsage'] = tool_usage

def processResults(window):
    # restore_window_state(window, 'window_state_multipulAdditives.pkl')
    cv2.imshow("window.all_plate_info[0]['IMGbinaryAutomatic']", resize_for_display(window.all_plate_info[0]['IMGbinaryAutomatic']))
    cv2.imshow("window.all_plate_info[1]['IMGbinaryAutomatic']", resize_for_display(window.all_plate_info[1]['IMGbinaryAutomatic']))
    process_tool_usage(window)
    process_split_order_quantifications(window)
    strain_data, dilution_series = generate_data_series(window)


    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Collect all strain data
    all_strain_data = []
    
    for strain, series in strain_data.items():
        # Get all figures and statistics for this strain
        figures_and_stats = plot_multiadditive_graphs(series, dilution_series, strain)
        all_strain_data.append((strain, figures_and_stats))
    
    # Generate single PDF report with all strains
    output_filename = "growth_analysis_report_Test.pdf"
    generate_pdf_report(window.all_plate_info, all_strain_data, output_filename)
    
    # Clean up matplotlib figures
    for _, figures_and_stats in all_strain_data:
        for fig, _, _ in figures_and_stats:
            plt.close(fig)
    #display_results(window)

def save_window_state(window, filename):
    # Extract the all_plate_info from the window object
    all_plate_info = window.all_plate_info
    
    # Serialize and save it to a file using pickle
    with open(filename, 'wb') as file:
        pickle.dump(all_plate_info, file)

def restore_window_state(window, filename):
    # Deserialize the state from the pickle file
    with open(filename, 'rb') as file:
        all_plate_info = pickle.load(file)
    
    # Restore the all_plate_info attribute in the window object
    window.all_plate_info = all_plate_info

def process_split_order_quantifications(window):
    """
    Processes all_plate_info by calculating dilution series, splitting unordered quantifications
    into split_quantifications based on strain_positions, and saving ordered quantifications.

    Parameters:
    window (object): The window object containing all_plate_info
    """
    for plate in window.all_plate_info:
        # Extract plate layout and dilution factors
        rows = plate['layout']['rows']
        cols = len(plate['column_indexes'])
        x_dilution_factor = plate['layout']['x_dilution'] #see how many coloums each strain takes up
        y_dilution_factor = plate['layout']['y_dilution']
        
        # Calculate the dilution series
        dilution_array = calculate_dilution_series(rows, cols, x_dilution_factor, y_dilution_factor)
        plate['dilutions'] = dilution_array 
        # Get sorted positions based on dilution series
        sorted_positions = get_sorted_positions(dilution_array)
        
        # Split unorderedquantifications into split_quantifications
        unordered_quantifications = np.array(plate['unorderedquantifications'])
        strain_positions = plate['strain_positions']
        
        split_quantifications = []
        for strain, pos_range in strain_positions.items():
            start, end = pos_range
            split_quantifications.append(unordered_quantifications[:, start:end + 1])
        
        # Save split_quantifications to the plate
        plate['split_quantifications'] = split_quantifications
        
        # Create ordered_quantifications based on sorted positions
        ordered_quantifications = []
        for strain_data in split_quantifications:
            ordered_strain_values = extract_values_at_positions(strain_data, sorted_positions)
            ordered_quantifications.append(ordered_strain_values)
        
        # Save ordered_quantifications to the plate
        plate['ordered_quantifications'] = ordered_quantifications


def generate_data_series(window):
    # Dictionary to store data series for each strain
    strain_data = defaultdict(list)
    dilution_series = window.all_plate_info[0]['dilutions']
   
    # Iterate over all plates
    for plate in window.all_plate_info:
        
        additive = plate.get('additive', 'Control') or 'Control'

        filename = plate.get('filename', 'Unnamed Plate')
        strains = plate['strains']
        column_indexes = plate['column_indexes']
        ordered_quantifications = plate['ordered_quantifications']
        
        # Ensure ordered_quantifications and column_indexes match strain count
        if len(ordered_quantifications) != len(strains):
            raise ValueError("Mismatch between strains and ordered_quantifications length in plate.")
        
        # For each strain in the plate
        for strain_idx, strain in enumerate(strains):
            # Extract y_values for this strain
            y_values = ordered_quantifications[strain_idx]
            column_indexes_for_strain = column_indexes[strain_idx]
    
            # Calculate the range of column indexes
            start_col = min(column_indexes_for_strain)
            end_col = max(column_indexes_for_strain)
            
            # Generate a label for this series
            label = f"{additive if additive != 'none' else 'Control'} ({filename} {start_col}-{end_col})"
            
            print(label)  # Optional: Debugging to check the labels
            # Generate a label for this series

            # Append data series to the strain's list
            strain_data[strain].append({
                'y_values': y_values,
                'additive': additive,
                'label': label,
                'strain': strain,
                'filename': filename,
                'column_indexes':column_indexes_for_strain
            })
    
    # Convert strain_data to a list of series if needed
    data_series = []
    for strain, series in strain_data.items():
        data_series.extend(series)
    
    return strain_data, dilution_series


# Example usage





##     ##  #######  ########  ########  ######  
###   ### ##     ## ##     ## ##       ##    ## 
#### #### ##     ## ##     ## ##       ##       
## ### ## ##     ## ##     ## ######    ######  
##     ## ##     ## ##     ## ##             ## s
##     ## ##     ## ##     ## ##       ##    ## 
##     ##  #######  ########  ########  ###### 

# def on_contrast_change(window, value, backToEdit = False):
#     global backToEdit2
#     if (backToEdit2 == False):
#         window.contrast_value = float(value)
#         binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots, block_size =window.block_size )

#         #save new iamges
#         window.binarized_image = final_binary
#         window.contour_img = contour_img
#         window.debug_image = np.stack((final_binary,) * 3, axis=-1)

#         #cannot use undo redo buttons to undo this
#         clear_history(window)
#         display_image(window)
#     else:
#         backToEdit2 = False   
 
# def on_excludeSmallDots(window, value, backToEdit = False):
#     #print("on_excludeSmallDots")
#     global backToEdit2

#     if (backToEdit2 == False):
#         window.excludeSmallDots = float(value)
#         binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots, block_size =window.block_size)

#         #save new images
#         window.binarized_image = final_binary
#         window.debug_image = np.stack((final_binary,) * 3, axis=-1)
#         # print("am i resetting here?")
#         #reset history, cannot use undo redo buttons to undo this
#         clear_history(window)
#         display_image(window)
#     else:
#         backToEdit2 = False

def set_mode(window, mode):
    window.mode = mode
    if mode == "small_brush" or mode == "small_eraser":
        window.brush_size = 40
    elif mode == "large_brush" or mode == "large_eraser":
        window.brush_size = 120

def toggle_image(window):
    window.show_original = not window.show_original
    display_images(window)

# def display_images(window):

#     try:
#         #right image = editing image
#         # cv2.imshow("debug image", resize_for_display(window.debug_image))
#         # cv2.waitKey(0)
#         # cv2.destroyAllWindows()
#         img_editing = Image.fromarray(window.debug_image)
#         img_editing.thumbnail((window.winfo_width()//2 - 60, window.winfo_height() - 200))
#         window.photo_editing = ImageTk.PhotoImage(img_editing)
#         window.right_canvas.config(width=window.photo_editing.width(), height=window.photo_editing.height())
#         window.right_canvas.create_image(0, 0, anchor="nw", image=window.photo_editing)
#         window.display_width = window.photo_editing.width()
#         window.display_height = window.photo_editing.height()

#         #toggleable left image
#         if window.show_original:
#             img_left = Image.fromarray(cv2.cvtColor(window.current_image, cv2.COLOR_BGR2RGB))
#         else:
#             img_np = window.current_image
#             img_editing_resized = cv2.resize(np.array(img_editing), (img_np.shape[1], img_np.shape[0]))
#             img_gray = cv2.cvtColor(img_editing_resized, cv2.COLOR_RGB2GRAY)
#             contours, _ = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             contour_img = img_np.copy()
#             for cntr in contours:
#                 cv2.drawContours(contour_img, [cntr], 0, (0, 255, 255), 3)
#             window.image_info[window.current_image_index]["IMGcontours"] = contour_img    
#             window.current_info["IMGcontours"] = contour_img 
#             # cv2.imshow("contours2345", resize_for_display(contour_img))
#             # # # cv2.imshow("contours", resize_for_display(window.marked_image))
#             # cv2.waitKey(0)
#             # cv2.destroyAllWindows()
#             img_left = Image.fromarray(cv2.cvtColor(contour_img, cv2.COLOR_BGR2RGB))
#         img_left.thumbnail((window.winfo_width()//2 - 60, window.winfo_height() - 200))
#         window.photo_left = ImageTk.PhotoImage(img_left)
#         window.left_canvas.config(width=window.photo_left.width(), height=window.photo_left.height())
#         window.left_canvas.create_image(0, 0, anchor="nw", image=window.photo_left)


#     except Exception as e:
#         print(f"Error in display_images: {e}")


def setup_zoom_controls(window):
    """Set up zoom controls and initialize zoom-related variables"""
    window.zoom_level = 1.0
    window.zoom_min = 0.5
    window.zoom_max = 5.0
    
    # Create zoom frame
    zoom_frame = Frame(window, bg=DARK)
    zoom_frame.place(x=1376, y=300)
    
    # Zoom in button
    zoom_in_btn = Button(
        zoom_frame,
        text="+",
        command=lambda: adjust_zoom(window, 1.2),
        font=(FONT, 12, 'bold'),
        bg=DARK,
        fg=LIGHT,
        width=2
    )
    zoom_in_btn.pack(pady=2)
    
    # Zoom out button
    zoom_out_btn = Button(
        zoom_frame,
        text="-",
        command=lambda: adjust_zoom(window, 0.8),
        font=(FONT, 12, 'bold'),
        bg=DARK,
        fg=LIGHT,
        width=2
    )
    zoom_out_btn.pack(pady=2)
    
    # Add scrollbars for both canvases
    # add_scrollbars(window)

# def add_scrollbars(window):
#     """Add scrollbars to both canvases"""
#     # Left canvas scrollbars
#     left_frame = Frame(window)
#     left_frame.place(x=30, y=303)
    
#     left_scrollbar_y = Scrollbar(left_frame)
#     left_scrollbar_y.pack(side=RIGHT, fill=Y)
    
#     left_scrollbar_x = Scrollbar(left_frame, orient=HORIZONTAL)
#     left_scrollbar_x.pack(side=BOTTOM, fill=X)
    
#     window.left_canvas.config(
#         xscrollcommand=left_scrollbar_x.set,
#         yscrollcommand=left_scrollbar_y.set
#     )
#     left_scrollbar_x.config(command=window.left_canvas.xview)
#     left_scrollbar_y.config(command=window.left_canvas.yview)
    
#     # Right canvas scrollbars
#     right_frame = Frame(window)
#     right_frame.place(x=690, y=303)
    
#     right_scrollbar_y = Scrollbar(right_frame)
#     right_scrollbar_y.pack(side=RIGHT, fill=Y)
    
#     right_scrollbar_x = Scrollbar(right_frame, orient=HORIZONTAL)
#     right_scrollbar_x.pack(side=BOTTOM, fill=X)
    
#     window.right_canvas.config(
#         xscrollcommand=right_scrollbar_x.set,
#         yscrollcommand=right_scrollbar_y.set
#     )
#     right_scrollbar_x.config(command=window.right_canvas.xview)
#     right_scrollbar_y.config(command=window.right_canvas.yview)

def adjust_zoom(window, factor):
    """Adjust zoom level and trigger display update"""
    new_zoom = window.zoom_level * factor
    if window.zoom_min <= new_zoom <= window.zoom_max:
        window.zoom_level = new_zoom
        display_images(window)

def display_images(window):
    """Display images while maintaining original aspect ratio with zoom support"""
    try:
        # Get original image dimensions
        original_width = window.debug_image.shape[1]
        original_height = window.debug_image.shape[0]
        
        # Calculate available space
        max_width = int((window.winfo_width()//2 - 60) * window.zoom_level)
        max_height = int((window.winfo_height() - 200) * window.zoom_level)
        
        # Calculate scaling factors for both dimensions
        width_scale = max_width / original_width
        height_scale = max_height / original_height
        
        # Use the smaller scaling factor to maintain aspect ratio
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        zoomed_width = int(original_width * scale)
        zoomed_height = int(original_height * scale)
        
        # Right image (editing image)
        img_editing = Image.fromarray(window.debug_image)
        img_editing = img_editing.resize((zoomed_width, zoomed_height), Image.LANCZOS)
        window.photo_editing = ImageTk.PhotoImage(img_editing)
        
        # Configure right canvas
        window.right_canvas.config(
            width=window.photo_editing.width(),
            height=window.photo_editing.height(),
            scrollregion=(0, 0, zoomed_width, zoomed_height)
        )
        window.right_canvas.create_image(0, 0, anchor="nw", image=window.photo_editing)
        
        # Store display dimensions
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
                cv2.drawContours(contour_img, [cntr], 0, (0, 0, 255), 3)
            window.all_plate_info[window.current_image_index]["IMGcontours"] = contour_img    
            window.current_info["IMGcontours"] = contour_img
            img_left = Image.fromarray(cv2.cvtColor(contour_img, cv2.COLOR_BGR2RGB))
            
        # Resize left image with zoom while maintaining aspect ratio
        img_left = img_left.resize((zoomed_width, zoomed_height), Image.LANCZOS)
        window.photo_left = ImageTk.PhotoImage(img_left)
        
        # Configure left canvas
        window.left_canvas.config(
            width=window.photo_left.width(),
            height=window.photo_left.height(),
            scrollregion=(0, 0, zoomed_width, zoomed_height)
        )
        window.left_canvas.create_image(0, 0, anchor="nw", image=window.photo_left)
    except Exception as e:
        print(f"Error in display_images: {e}")

# Update the draw functions to work with zoom
def start_draw(window, event):
    window.is_drawing = True
    window.last_x = event.widget.canvasx(event.x)
    window.last_y = event.widget.canvasy(event.y)
    window.active_canvas = event.widget
    draw(window, event)

def draw(window, event):
    if window.is_drawing:
        # Get current canvas coordinates considering scroll
        x = window.active_canvas.canvasx(event.x)
        y = window.active_canvas.canvasy(event.y)
        
        # Get actual image dimensions
        img_height, img_width = window.binarized_image.shape[:2]
        
        # Calculate scaling factors considering zoom
        scale_x = img_width / (window.display_width / window.zoom_level)
        scale_y = img_height / (window.display_height / window.zoom_level)
        
        # Convert coordinates
        x_img = int(x / window.zoom_level * scale_x)
        y_img = int(y / window.zoom_level * scale_y)
        last_x_img = int(window.last_x / window.zoom_level * scale_x)
        last_y_img = int(window.last_y / window.zoom_level * scale_y)
        
        # Apply drawing operation
        if window.mode == "flood":
            flood_erase(window, x_img, y_img)
        else:
            # Scale brush size with zoom
            original_brush_size = window.brush_size
            window.brush_size = max(1, int(window.brush_size / window.zoom_level))
            brush_draw(window, last_x_img, last_y_img, x_img, y_img)
            window.brush_size = original_brush_size
        
        window.last_x = x
        window.last_y = y
        display_images(window)


def mouse_zoom(window, event):
    """Handle mouse wheel zoom"""
    if event.delta > 0:
        adjust_zoom(window, 1.1)
    else:
        adjust_zoom(window, 0.9)


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
        color = 255  #white drawing
    else:
        color = 0  #black erasing
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

def clear_history(window): 
    window.history.clear()
    window.redo_stack.clear()

    current_state = window.binarized_image.copy()
    window.history.append(current_state)

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


#used for both eraser and pen, 
def brush_draw(window, x1, y1, x2, y2):
    if window.mode in ["small_brush", "large_brush"]:
        color = 255  #white if drawing
    else:
        color = 0  #black if erasing
    cv2.line(window.binarized_image, (x1, y1), (x2, y2), color, window.brush_size)
    window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)
    cv2.line(window.debug_image, (x1, y1), (x2, y2), (0, 0, 255), 2)


def initialize_window_attributes(window):
    #progress bar style
    s = ttk.Style()
    s.theme_use('clam')
    s.configure("styled.Horizontal.TProgressbar", troughcolor=LIGHT,bordercolor=DARK, background=DARK, lightcolor=DARK, 
                darkcolor=DARK)
    style = ttk.Style()

    #slider style
    style.configure("TScale",
                    background=DARK,
                    troughcolor=LIGHT,
                    sliderthickness=15,
                    sliderlength=25)  # Adjust size of the knob to be rounder            

    #default parameters
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
    window.block_size = 301
    window.image_paths = []
    window.current_image_index = 0
    window.next_button = None
    window.progress_bar = None
    window.progress_label = None
    window.current_image = None 


#creating the frame with title and icon
window = Tk()
window.geometry("1440x1000")
window.configure(bg=LIGHT)
window.title("SpotPlotter")
window.iconbitmap(r'C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\GUI\ICONS\ICON.ico')

# initialize_window_attributes(window)
# title_frame_widgets = create_titleFrame(window)

# window.resizable(False, False)
# window.mainloop()

restore_window_state(window, 'window_state_IntermediaryImages.pkl')

processResults(window)







#Different saved states:

#window_state.pkl   - real test its testing these images where https://www.dropbox.com/scl/fo/55v2k6p7hfb4hws18diod/AK-1lWdCixipX0rCeqPYjYc?rlkey=4uou81nqbu13wig1f8vwbx4ie&e=1&st=4vqqji7x&dl=0 
#1 additive and 4 repeats for each

#'window_state_multipulAdditives.pkl   4 attitives with 2 repeats for each

#window_state_IntermediaryImages.pkl checking to see if the binary images and preview are saving correctyl



