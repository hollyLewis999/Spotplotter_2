#Acknolgements: 
#Tkinter Designer by Parth Jadhav
#https://github.com/ParthJadhav/Tkinter-Designer


from pathlib import Path
import os
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage,filedialog,font, Frame, Label,messagebox, Scale, HORIZONTAL,BooleanVar, Checkbutton, CENTER,  DoubleVar, ROUND, LEFT
from tkinter import ttk
import cv2
import numpy as np
from scipy.spatial import distance
from PIL import Image, ImageTk, ImageDraw
import copy
from functools import partial
import time
import math 
import sys

from Processing import *
from outputs import *

sys.path.append(r'C:\Users\ThinkPad\AppData\Roaming\Python\Python312\site-packages')

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

# .d8888. d888888b db    db db      d88888b 
# 88'  YP `~~88~~' `8b  d8' 88      88'     
# `8bo.      88     `8bd8'  88      88ooooo 
#   `Y8b.    88       88    88      88~~~~~ 
# db   8D    88       88    88booo. 88.     
# `8888Y'    YP       YP    Y88888P Y88888P 


#################################################################
# The functions create_circular_slider, create_round_button and round_rectabgle were created by Chatgbt, Tkinter did not have very asthetic sliders or buttons
#                                       
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
        window.image_info[window.current_image_index] = window.current_info.copy()
        # print(f"Debug: CURRENT INDEX {window.current_image_index}")
        # print(f"Debug: Current image info: {window.current_info}")
        # print(f"Debug: 345434 ALL INFO : {window.image_info}" )
    else:   
        gray_image = window.gray_image  
        result_grid, marked_image, ordered_counts = detect_and_draw_circles(window.binarized_image, gray_image, False)

        #comment out later, for testing and report
        # path = "C:/Users/ThinkPad/Documents/AA ACADEMIC 2024/Thesis/Tests/GroundTuth/TESTS/Cropped/RESULTS/"
        # cv2.imwrite(path +window.current_info['filename']+ '_result.png', marked_image)   
        # # cv2.imshow("marked", resize_for_display(marked_image))

        #checking to see if the window has current into to avoid cracshing
        if hasattr(window, 'current_info'):
            window.current_info['QuantificationA'] = ordered_counts["Strain 1"]
            window.current_info['QuantificationB'] = ordered_counts["Strain 2"]
            window.current_info['QuantificationC'] = ordered_counts["Strain 3"]

            window.image_info[window.current_image_index] = window.current_info
            # print(f"Debug: CURRENT INDEX {window.current_image_index}")
            # print(f"Debug: Current image info: {window.current_info}")
            # print(f"Debug:098765 ALL INFO : {window.image_info}" )
        else:
            print("Error: current_info not initialized")

        # print("TESTER INFORMATION:") 
        # print("_______________________________________________________________________")
        # print(window.current_info['filename'])
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
    window.image_info[window.current_image_index]["threshold"] = window.contrast_value
    window.image_info[window.current_image_index]["smallArea"] = window.excludeSmallDots
    window.image_info[window.current_image_index]["IMGgrid"] = marked_image
    window.image_info[window.current_image_index]["IMGbinary"] = window.binarized_image
    
    
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
    
def create_editFrame(window, backToEdit = False):
    global backToEdit2 #have to put this here if i want to edit it within this function

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

    #displaying metadata fro mthe textfile, checking if current_info is initilised
    if hasattr(window, 'current_info'):
        current_info = window.current_info
        metadata_text = f"Filename: {current_info['filename']}\n"
        metadata_text += f"StrainA: {current_info['strainA']}\n"
        metadata_text += f"StrainB: {current_info['strainB']}\n"
        metadata_text += f"StrainC: {current_info['strainC']}"
    else:
        metadata_text = "No metadata available1"

    #fixing issue of only metadata displaying
    if hasattr(window, 'metadata_label'):
        window.metadata_label.destroy()  # Destroy the old label

    window.metadata_label = Label(window, text=metadata_text, font=(FONT, 16 * -1, 'bold'), bg=LIGHT, fg=DARK, justify=LEFT)
    window.metadata_label.place(x=50, y=850)


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
    total_height = 783 - 203
    img_width = total_width // 2 -50 #each must be half the width
    img_height = total_height

    window.left_canvas = Canvas(window, width=img_width, height=img_height, bg=DARK, highlightthickness=0)
    window.left_canvas.place(x=30, y=303)
    window.right_canvas = Canvas(window, width=img_width, height=img_height, bg=DARK, highlightthickness=0)
    window.right_canvas.place(x=690, y=303)


    display_images(window)
    
    create_rounded_button(
        canvas=canvas,
        text="Toggle",
        command=lambda: toggle_image(window),
        x=40,
        y=205,
        button_tag = "Toggle",
        width = 140, 
        height = 60,
        fill = LIGHT,
        accent = DARK)


    #sliders
    smallDots_label = Label(window, text="Size:", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    smallDots_label.place(x=665, y=223)
    smallDots_slider = create_circular_slider(
        window, min_val=1, max_val=100,
        position=(700, 190),
        command=lambda v: on_excludeSmallDots(window, v, False),
        initial_value=window.excludeSmallDots
    )

    contrast_label = Label(window, text="Threshold:", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    contrast_label.place(x=220, y=223)
    contrast_slider = create_circular_slider(
        window, min_val=0, max_val=40,
        position=(300, 190),
        command=lambda v: on_contrast_change(window, v, False),
        initial_value=window.contrast_value
    )



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

   
    return canvas



#if the grid is not detectecd correctly then the user can ovverride it 
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
    max_radius = int(width/24)
    min_radius = int(max_radius/3)
    max_area = max_radius**2*(math.pi)
    min_area = min_radius**2*(math.pi)
    x_coords, y_coords, marked_image = findBlobs(binary_image, min_area, max_area)
    # cv2.imshow("marked image1244443", resize_for_display(marked_image))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    x_coords, y_coords, _ = findBlobs(binary_image, min_area, max_area)
    window.center_points = list(zip(x_coords, y_coords))

    window.blob_points = list(zip(x_coords, y_coords))
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
    grid_start_x, grid_start_y, cell_size = calculate_grid(window.clicked_pointsx,window.clicked_pointsy, width, height, window.binary_image, window.gray_image)
    counts, marked_image, ordered_counts= quantify_grid(window.binary_image, window.binary_image, grid_start_x, grid_start_y, cell_size)

    
    #SAVING INFO
    if hasattr(window, 'current_info'):
        window.current_info['QuantificationA'] = ordered_counts["Strain 1"]
        window.current_info['QuantificationB'] = ordered_counts["Strain 2"]
        window.current_info['QuantificationC'] = ordered_counts["Strain 3"]
        # Update the window.image_info with the modified current_info
        window.image_info[window.current_image_index] = window.current_info.copy()
        
        # print("RECALCULATED:      TESTER INFORMATION:") 
        # print("_______________________________________________________________________")
        # print(ordered_counts["Strain 1"])    
        # print(ordered_counts["Strain 2"])   
        # print(ordered_counts["Strain 3"])   

        # print(f"Debug: CURRENT INDEX {window.current_image_index}")
        # print(f"Debug: Current image info: {window.current_info}")
        # print(f"Debug: in recalcgrid ALL INFO : {window.image_info}" )

    else:
        print("Error: current_info not initialized")

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
    #first checks if there is attribute and there are valiv paths and there is image info and image info it proergated
    if hasattr(window, 'image_paths') and window.image_paths and hasattr(window, 'image_info') and window.image_info:
        create_cropFrame(window)
    else:
        messagebox.showwarning("Warning", "Please upload both text file and images")


def process_image(window):
    stretched, blurred, gray_image, idealContrast = stretch_and_gray(window.current_image, False)
    window.contrast_value = idealContrast

    #For testing 
    # cv2.imshow("origional", resize_for_display(window.current_image))
    # cv2.imshow("streached", resize_for_display(stretched))
    # cv2.imshow("blurred", resize_for_display(blurred))
    # cv2.imshow("gray_image", resize_for_display(gray_image))

    # stretch_values = [60, 70, 80, 90, 100, 110]
    # blur_values = [110, 120, 130, 140, 150]

    # for stretch in stretch_values:
    #     for blur in blur_values:
    #         stretched, blurred, gray_image = stretch_and_gray(window.current_image, stretch, blur)
    #         window_name = f"Stretch {stretch} Blur {blur}"
    #         cv2.imshow(window_name, resize_for_display(stretched))

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    window.gray_image = gray_image
    binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.current_image, excludeSmallDots=window.excludeSmallDots, contrast=window.contrast_value)

    window.contour_img = contour_img
    window.binarized_image = final_binary
    window.debug_image = np.stack((final_binary,) * 3, axis=-1)
    
    # only initialize history if it's empty, othewise its adding doubles
    if not window.history:
        window.history = [window.binarized_image.copy()]
        window.redo_stack = []
    
    update_undo_redo_buttons(window)
    create_editFrame(window)



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

def upload_txt_file(window):
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:

        window.image_info = []
        window.image_paths = []
        skipped_lines = []#store which liens where skipped

        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) > 1:  #must be more than just header
                header = lines[0].strip().split(',') #split based on comma
                #print(f"Debug: Header: {header}")
                for i, line in enumerate(lines[1:], start=2):#start from second line (header in first)
                    parts = line.strip().split(',')
                    if len(parts) == 8:  # check correct number of parts
                        info = {
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
                            'QuantificationC': None,
                            'IMGcontours': None,  
                            'IMGbinary': None,   
                            'IMGgrid': None, 
                            'threshold': 0,
                            'smallArea': 0   
                        }
                        window.image_info.append(info) 
                    else:
                        skipped_lines.append(i)  #line number for skipped line
        #display skipped lines
        if skipped_lines:
            messagebox.showwarning("Warning", f"Skipping {len(skipped_lines)} line(s) due to incorrect format.\nLine numbers: {', '.join(map(str, skipped_lines))} \nCorrect Format: FileName,Type,Detergent,Treatment,Repeat,StrainA_Name,StrainB_Name,StrainC_Name")
         #initialize info
        window.current_image_index = 0
        if window.image_info:
            window.current_info = window.image_info[0].copy() 
        else:
            window.current_info = None



def upload_images(window):
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
   
   #check that there are filepaths and that everything is initilised
    if file_paths and hasattr(window, 'image_info'):
        window.image_paths = []
        unmatched_filenames = []  # Collect unmatched filenames

        #this is looking at the seleted files and seeing if the names match the textfile
        for info in window.image_info:
            filename = info['filename'].lower()
            matching_path = None 
            for path in file_paths:
                if os.path.basename(path).lower() == filename:
                    matching_path = path
                    break  # exit if match is found
            if matching_path:
                window.image_paths.append(matching_path)
            else:
                unmatched_filenames.append(info['filename']) 
                
        if window.image_paths:
            window.current_image_index = 0
            load_current_image(window)
            if unmatched_filenames:
                messagebox.showwarning("Warning", f"No matching images found for {len(unmatched_filenames)} file(s):\n{', '.join(unmatched_filenames)}")
        else:
            messagebox.showwarning("Warning", "No matching images found for all entries")

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
        window.current_info = window.image_info[window.current_image_index].copy()
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
        display_results(window)




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

        #save new iamges
        window.binarized_image = final_binary
        window.contour_img = contour_img
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)

        #cannot use undo redo buttons to undo this
        clear_history(window)
        display_images(window)
    else:
        backToEdit2 = False   
 
def on_excludeSmallDots(window, value, backToEdit = False):
    #print("on_excludeSmallDots")
    global backToEdit2

    if (backToEdit2 == False):
        window.excludeSmallDots = float(value)
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots)

        #save new images
        window.binarized_image = final_binary
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        # print("am i resetting here?")
        #reset history, cannot use undo redo buttons to undo this
        clear_history(window)
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
        #right image = editing image
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

        #toggleable left image
        if window.show_original:
            img_left = Image.fromarray(cv2.cvtColor(window.current_image, cv2.COLOR_BGR2RGB))
        else:
            img_np = window.current_image
            img_editing_resized = cv2.resize(np.array(img_editing), (img_np.shape[1], img_np.shape[0]))
            img_gray = cv2.cvtColor(img_editing_resized, cv2.COLOR_RGB2GRAY)
            contours, _ = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour_img = img_np.copy()
            for cntr in contours:
                cv2.drawContours(contour_img, [cntr], 0, (0, 0, 255), 2)
            window.image_info[window.current_image_index]["IMGcontours"] = contour_img    
            window.current_info["IMGcontours"] = contour_img 
            # cv2.imshow("contours2345", resize_for_display(contour_img))
            # # # cv2.imshow("contours", resize_for_display(window.marked_image))
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
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
    window.image_paths = []
    window.current_image_index = 0
    window.next_button = None
    window.progress_bar = None
    window.progress_label = None
    window.current_image = None 


#creating the frame with title and icon
window = Tk()
window.geometry("1440x1024")
window.configure(bg=LIGHT)
window.title("SpotPlotter")
window.iconbitmap(r'C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\GUI\ICONS\ICON.ico')

initialize_window_attributes(window)
title_frame_widgets = create_titleFrame(window)

window.resizable(False, False)
window.mainloop()














