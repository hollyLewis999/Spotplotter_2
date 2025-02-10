#Acknolgements: 
#Tkinter Designer by Parth Jadhav
#https://github.com/ParthJadhav/Tkinter-Designer

import base64
import copy
import io
import json
import math
import os
import pickle
import sys
import time
from collections import defaultdict
from datetime import datetime
from functools import partial
from pathlib import Path
from tkinter import BOTTOM,BooleanVar,Button,Canvas,CENTER,Checkbutton,DoubleVar,Entry,Frame,HORIZONTAL,Label,LEFT,Message,PhotoImage,RIGHT,ROUND,Scale,Scrollbar,Text,Toplevel,Tk,Y,X,filedialog,font,messagebox
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor
from tkinter import TclError
import cv2
import numpy as np
import openpyxl
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageTk
from scipy.spatial import distance
VERSION = "1.0.0"
from Processing import *
from Style import *
from outputs import *
# from help import *


DARK = "#092934"
LIGHT = "#FFFFFF"
COLORS = ["#D24C4A", "#D3784A", "#DFA24F", "#7DB46F", "#0F8660", "#46A2A2", "#7CC7BC", "#A9599C"] #https://coolors.co/d24c4a-d3784a-dfa24f-7db46f-0f8660-46a2a2-7cc7bc-a9599c
COLORS = ["#D24C4A", "#DFA24F", "#7DB46F", "#7CC7BC", "#46A2A2", "#0F8660", "#A9599C", "#D3784A", "#A9599C", "#D24C4A", "#DFA24F", "#7DB46F", "#7CC7BC", "#46A2A2", "#0F8660", "#A9599C", "#D3784A", "#A9599C"] #https://coolors.co/d24c4a-d3784a-dfa24f-7db46f-0f8660-46a2a2-7cc7bc-a9599c
CURRENTPLATEINDEX =-1
GRAY1 = "#F0F0F0"
GRAY2 = "#E0E0E0"
GRAY = "#B0B0B0"
ACCENT = "#4169E1"
FONT = "Microsoft New Tai Lue"

TITLEHEIGHT = 130
buttonPosX = 1440 -200 -17
buttonPosXleft = 17

buttonPosY = 728 +20
backToEdit2 = False
PROGRESSX = 1180
PROGRESSY = 36
base_y = 212.0
heading_y = 20
y_offset_edit  = 30




# d8888b. db       .d8b.  d888888b d88888b    .o88b. d8888b. d88888b  .d8b.  d888888b  .d88b.  d8888b. 
# 88  `8D 88      d8' `8b `~~88~~' 88'       d8P  Y8 88  `8D 88'     d8' `8b `~~88~~' .8P  Y8. 88  `8D 
# 88oodD' 88      88ooo88    88    88ooooo   8P      88oobY' 88ooooo 88ooo88    88    88    88 88oobY' 
# 88~~~   88      88~~~88    88    88~~~~~   8b      88`8b   88~~~~~ 88~~~88    88    88    88 88`8b   
# 88      88booo. 88   88    88    88.       Y8b  d8 88 `88. 88.     88   88    88    `8b  d8' 88 `88. 
# 88      Y88888P YP   YP    YP    Y88888P    `Y88P' 88   YD Y88888P YP   YP    YP     `Y88P'  88   YD 

def open_help_popup(parent, image_path, title="Help"):
    """
    Create a scrollable popup window with an image
    
    :param parent: Parent window
    :param image_path: Path to the image file
    :param title: Title of the popup window
    """
    # Create popup window
    help_window = Toplevel(parent)
    help_window.title(title)
    help_window.geometry("900x800")  # Adjust size as needed
    help_window.resizable(True, True)
    help_window.iconbitmap("Icons/ICON.ico")  # Allow vertical resizing

    # Create a frame to hold the canvas and scrollbar
    main_frame = Frame(help_window)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Create a canvas with scrollbar
    canvas = Canvas(main_frame)
    scrollbar = Scrollbar(main_frame, orient='vertical', command=canvas.yview)
    scrollable_frame = Frame(canvas)

    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Pack the scrollbar and canvas
    canvas.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # Create a window in the canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

    # Open and resize the image
    original_image = Image.open(image_path)
    
    # Resize image to fit the window width, maintaining aspect ratio
    window_width = 900  # Slightly less than popup width to account for padding
    width_ratio = window_width / original_image.width
    new_height = int(original_image.height * width_ratio)
    
    resized_image = original_image.resize((window_width, new_height), Image.LANCZOS)
    
    # Convert to PhotoImage
    tk_image = ImageTk.PhotoImage(resized_image)

    # Create a label with the image
    image_label = Label(scrollable_frame, image=tk_image)
    image_label.image = tk_image  # Keep a reference to prevent garbage collection
    image_label.pack(fill='both', expand=True)


def open_help_manual(window, page_number):
    """
    Open help popup for a specific page
    
    :param window: Parent window
    :param page_number: Page number to display
    """
    # Map page numbers to corresponding image paths
    help_images = {
        1: "help_images/AllHelpScreens_page-0001.jpg",  # Replace with your actual help image paths
        2: "help_images/AllHelpScreens_page-0002.jpg",
        3: "help_images/AllHelpScreens_page-0003.jpg",
        4: "help_images/AllHelpScreens_page-0004.jpg",
        5: "help_images/AllHelpScreens_page-0005.jpg",
        6: "help_images/AllHelpScreens_page-0006.jpg"
    }
    
    # Get the image path for the specified page
    image_path = help_images.get(page_number)
    
    if image_path:
        open_help_popup(window, image_path, f"Help - Page {page_number}")
    else:
        print(f"No help image found for page {page_number}")
                                                                                                     
def create_controls(control_frame, window, mode):
    y_offset = 100
    spacing = 70
    label_width = 100
    
    def create_input_row(label_text, variable, y_pos):
        label = Label(
            control_frame,
            text=label_text,
            font=(FONT, 12, 'bold'),
            fg=LIGHT,
            bg=DARK,
            width=10,
            anchor="e"
        )
        label.place(x=10, y=y_pos)
        
        entry_frame = RoundedEntry(control_frame, width=100, height=35)
        entry_frame.place(x=140, y=y_pos - 5)
        entry_frame.entry.config(textvariable=variable, font=(FONT, 11))
        
        return entry_frame.entry
    
    # Create input rows based on the mode
    create_input_row("Rows:", window.plate_layout['rows'], y_offset)
    create_input_row("Columns:", window.plate_layout['columns'], y_offset + spacing)


    
    if mode == "A":
        create_input_row("Strains:", window.plate_layout['strains'], y_offset + spacing * 2)
        create_input_row("X-Dilution:", window.plate_layout['x_dilution'], y_offset + spacing * 3)
        create_input_row("Y-Dilution:", window.plate_layout['y_dilution'], y_offset + spacing * 4)
    
                # Store checkbox widgets in window for proper cleanup
        window.checkboxes = []
        
        # Create checkbox for gap between strains with proper variable binding
        checkbox1 = RoundedCheckbox(
            control_frame,
            text="Gap Between Strains",
            variable=window.plate_layout['gap_between_strains'],
            command=lambda: update_plate_display_layout_designer(window)
        )
        checkbox1.place(x=20, y=y_offset + spacing * 4.8)
        checkbox1.label.place(x=50, y=y_offset + spacing * 4.8)
        window.checkboxes.append(checkbox1)

        checkbox2 = RoundedCheckbox(
            control_frame,
            text="Square Grid Cells",
            variable=window.plate_layout['square_grid'],
            command=lambda: update_plate_display_layout_designer(window)
        )
        checkbox2.place(x=20, y=y_offset + spacing * 5.6)
        checkbox2.label.place(x=50, y=y_offset + spacing * 5.6)
        window.checkboxes.append(checkbox2)

    # Bind all variables to update function
    for var_name in ['rows', 'columns', 'strains', 'x_dilution', 'y_dilution']:
        if isinstance(window.plate_layout[var_name], tk.Variable):  # Check if it's a tkinter variable
            window.plate_layout[var_name].trace_add(
                "write",
                lambda *args: update_plate_display_layout_designer(window)
            )
def create_mode_switcher(control_frame, window):
    def switch_mode(new_mode):
        window.current_mode = new_mode
        update_toggle_button()
        create_plate_designer(window, mode=new_mode)

    def update_toggle_button():
        # Clear existing buttons
        toggle_canvas.delete("dilutions_btn")
        toggle_canvas.delete("arrayed_btn")
        
        # Recreate buttons with updated colors
        create_rounded_button(
            canvas=toggle_canvas,
            text="Dilutions",
            command=lambda: switch_mode("A"),
            x=10,
            y=5,
            width=115,
            height=50,
            cornerradius=15,
            button_tag="dilutions_btn",
            fill=LIGHT if window.current_mode == "A" else DARK,
            accent=DARK if window.current_mode == "A" else LIGHT,
            font_size=12,
            bold=True
        )
        
        create_rounded_button(
            canvas=toggle_canvas,
            text="Arrayed",
            command=lambda: switch_mode("B"),
            x=125,
            y=5,
            width=115,
            height=50,
            cornerradius=15,
            button_tag="arrayed_btn",
            fill=LIGHT if window.current_mode == "B" else DARK,
            accent=DARK if window.current_mode == "B" else LIGHT,
            font_size=12,
            bold=True
        )

    def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, fill, outline):
        canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, 
                         start=90, extent=90, fill=fill, outline=outline)
        canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, 
                         start=0, extent=90, fill=fill, outline=outline)
        canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, 
                         start=180, extent=90, fill=fill, outline=outline)
        canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, 
                         start=270, extent=90, fill=fill, outline=outline)
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, 
                              fill=fill, outline=outline)
        canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, 
                              fill=fill, outline=outline)

    # Container for toggle buttons
    toggle_frame = Frame(control_frame, bg=DARK)
    toggle_frame.place(x=10, y=10, width=250, height=60)

    # Canvas for background and outline
    toggle_canvas = Canvas(toggle_frame, width=250, height=60, 
                         bg=DARK, highlightthickness=0)
    toggle_canvas.place(x=0, y=0)

    # Initial button creation
    create_rounded_button(
        canvas=toggle_canvas,
        text="Dilutions",
        command=lambda: switch_mode("A"),
        x=10,
        y=5,
        width=115,
        height=50,
        cornerradius=15,
        button_tag="dilutions_btn",
        fill=LIGHT if window.current_mode == "A" else DARK,
        accent=DARK if window.current_mode == "A" else LIGHT,
        font_size=12,
        bold=True
    )

    create_rounded_button(
        canvas=toggle_canvas,
        text="Arrayed",
        command=lambda: switch_mode("B"),
        x=125,
        y=5,
        width=115,
        height=50,
        cornerradius=15,
        button_tag="arrayed_btn",
        fill=LIGHT if window.current_mode == "B" else DARK,
        accent=DARK if window.current_mode == "B" else LIGHT,
        font_size=12,
        bold=True
    )


def create_plate_display(plate_frame, window):
    # Destroy existing plate canvas if it exists
    if hasattr(window, 'plate_canvas') and window.plate_canvas.winfo_exists():
        window.plate_canvas.destroy()
    
    # Create new plate canvas
    window.plate_canvas = tk.Canvas(
        plate_frame,
        bg=DARK,
        highlightthickness=0
    )
    window.plate_canvas.pack(expand=True, fill='both')
    update_plate_display_layout_designer(window)

def update_plate_display_layout_designer(window):
    try:
        # Check if plate canvas still exists
        if not hasattr(window, 'plate_canvas') or not window.plate_canvas.winfo_exists():
            return
            
        window.plate_canvas.delete('all')
        
        try:
            rows = min(max(0, window.plate_layout['rows'].get()),99)
            cols = min(max(0, window.plate_layout['columns'].get()),99)
            strains = max(1, window.plate_layout['strains'].get())
            x_dil = max(1, window.plate_layout['x_dilution'].get())
            y_dil = max(1, window.plate_layout['y_dilution'].get())
        except tk.TclError:
            # If variables are invalid or being destroyed, exit gracefully
            return
            
        width = window.plate_canvas.winfo_width()
        height = window.plate_canvas.winfo_height()
        if width <= 1 or height <= 1:
            # Schedule another update when the canvas has actual dimensions
            if window.plate_canvas.winfo_exists():
                window.plate_canvas.after(100, lambda: update_plate_display_layout_designer(window))
            return
            
        margin = margin_sides = 50
        grid_width = width - 2 * margin
        grid_height = height - 2 * margin
        cols_per_strain = cols // strains
        total_cols = cols
        
        try:
            if window.plate_layout['gap_between_strains'].get():
                total_gaps = strains - 1
                total_cols = cols + total_gaps
        except tk.TclError:
            # Handle case where variable is being destroyed
            return

        # Adjust cell dimensions based on the square grid setting

        cell_width = grid_width / total_cols
        cell_height = grid_height / rows


        try:
            if window.plate_layout['square_grid'].get():
                # Enforce square cells considering gaps
                total_width_with_gaps = total_cols
                cell_size = min(grid_width / total_width_with_gaps, grid_height / rows)
                cell_width = cell_height = cell_size
                margin_sides = (width - (cell_width * total_cols))/2
        except tk.TclError:
            # Handle case where variable is being destroyed
            return

        # Update strain positions
        current_col = 0
        window.plate_layout['strain_positions'] = {}
        
        for strain in range(strains):
            start_col = current_col
            end_col = start_col + cols_per_strain - 1
            window.plate_layout['strain_positions'][strain] = (start_col, end_col)
            current_col = end_col + 1
            if window.plate_layout['gap_between_strains'].get() and strain < strains - 1:
                current_col += 1

        draw_spots(window, strains, margin_sides, margin, cell_width, cell_height, x_dil, y_dil, rows)
        
    except tk.TclError as e:
        # Handle any other Tcl errors that might occur during update
        print(f"TclError during plate display update: {e}")
        return

def draw_spots(window, strains, margin_sides, margin, cell_width, cell_height, x_dil, y_dil, rows):
    try:
        if not window.plate_canvas.winfo_exists():
            return
            
        for strain in range(strains):
            start_col, end_col = window.plate_layout['strain_positions'][strain]
            for col_offset in range(end_col - start_col + 1):
                actual_col = start_col + col_offset
                x_value = x_dil ** col_offset
                x_pos = margin_sides + actual_col * cell_width + cell_width/2
                
                if window.current_mode == 'A':
                    window.plate_canvas.create_text(
                        x_pos,
                        margin - 20,
                        text=x_value,
                        fill=LIGHT,
                        font=(FONT, 8)
                    )
                
                for row in range(rows):
                    pos_key = f"{row}-{actual_col}"
                    x = margin_sides + actual_col * cell_width + cell_width/2
                    y = margin + row * cell_height + cell_height/2
                    color = COLORS[strain % len(COLORS)]
                    
                    window.plate_canvas.create_oval(
                        x-10, y-10, x+10, y+10,
                        fill=color,
                        outline=color,
                        tags=(pos_key, "spot", f"strain_{strain}")
                    )
                        
                # Add y-dilution labels (to the left of the rows)
                for row in range(rows):
                    y_value = y_dil ** row
                    y_pos = margin + row * cell_height + cell_height / 2
                    if window.current_mode == 'A' and strain == 0:
                        window.plate_canvas.create_text(
                            margin_sides - 20,
                            y_pos,
                            text=y_value,
                            fill=LIGHT,
                            font=(FONT, 8)
                        )
                        
    except tk.TclError as e:
        print(f"TclError during spot drawing: {e}")
        return



def go_to_assignment_screen(window):
    valid_positions = {}
    for strain, (start_col, end_col) in window.plate_layout['strain_positions'].items():
        strain_positions = []
        for row in range(window.plate_layout['rows'].get()):
            for col in range(start_col, end_col + 1):
                pos_key = f"{row}-{col}"
                strain_positions.append(pos_key)
        valid_positions[strain] = strain_positions

    layout_data = {
        'rows': window.plate_layout['rows'].get(),
        'columns': window.plate_layout['columns'].get(),
        'strains': window.plate_layout['strains'].get(),
        'x_dilution': window.plate_layout['x_dilution'].get(),
        'y_dilution': window.plate_layout['y_dilution'].get(),
        'gap_between_strains': window.plate_layout['gap_between_strains'].get(),
        'square_grid': window.plate_layout['square_grid'].get(),
        'strain_positions': window.plate_layout['strain_positions'],
        'valid_positions': valid_positions
    }


    window.layout_data = layout_data
    create_strain_designer(window)


def create_plate_designer(window, mode="A"):
    global CURRENTPLATEINDEX
    CURRENTPLATEINDEX = 0
    # Properly destroy existing widgets
    if hasattr(window, 'checkboxes'):
        for checkbox in window.checkboxes:
            checkbox.destroy()
    
    for widget in window.winfo_children():
        widget.destroy()
    
    # Initialize plate layout attributes with defaults if it doesn't already exist
    if not hasattr(window, 'plate_layout'):
        window.old_num_strains = tk.IntVar(value=3) 
        window.plate_layout = {
            'rows': tk.IntVar(value=8),
            'columns': tk.IntVar(value=12),
            'strains': tk.IntVar(value=1 if mode == "B" else 3),
            'x_dilution': tk.IntVar(value=-1 if mode == "B" else 10),
            'y_dilution': tk.IntVar(value=-1 if mode == "B" else 2),
            'gap_between_strains': tk.BooleanVar(value=False),
            'square_grid': tk.BooleanVar(value=True),
            'strain_positions': {}
        }
    else:
        # If switching to mode B, update only the necessary values while preserving variable types
        if mode == 'B':
            def safe_get(variable, default=0):
                try:
                    return int(variable.get())  # Ensure integer conversion
                except (ValueError, TclError):  # Handle empty string or invalid value
                    return default


            # Store current values
            current_rows = safe_get(window.plate_layout['rows'])
            current_cols = safe_get(window.plate_layout['columns'])
            current_gap = window.plate_layout['gap_between_strains'].get()
            current_square = window.plate_layout['square_grid'].get()
            
            # Update values while maintaining tkinter variable types
            window.old_num_strains.set(window.plate_layout['strains'].get())
            window.plate_layout['rows'].set(current_rows)
            window.plate_layout['columns'].set(current_cols)
            window.plate_layout['strains'].set(1)
            window.plate_layout['gap_between_strains'].set(current_gap)
            window.plate_layout['square_grid'].set(current_square)
            window.plate_layout['strain_positions'] = {}
        else:
            window.plate_layout['strains'].set(window.old_num_strains.get())


    # Store the current mode
    window.current_mode = mode

    # Create the rest of the UI
    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both")
    
    canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.pack(expand=True)
    
    # Add background images and frames
    image_image_1 = PhotoImage(file=("Icons/image_1.png"))
    canvas.image_image_1 = image_image_1
    image_1 = canvas.create_image(719.0, 57.0, image=image_image_1)
    round_rectangle(canvas, 17.0, 168.0-y_offset_edit, 1100.0, 730.0, fill=DARK, outline="")
    round_rectangle(canvas, 1120.0, 168.0-y_offset_edit, 1422.0, 730.0, fill=DARK, outline="")
    
    plate_frame = Frame(canvas, bg=DARK)
    plate_frame.place(x=27, y=178-y_offset_edit, width=1070, height=542+y_offset_edit)
    
    control_frame = Frame(canvas, bg=DARK)
    control_frame.place(x=1130, y=178-y_offset_edit, width=282, height=542+y_offset_edit)
    
    create_mode_switcher(control_frame, window)
    create_controls(control_frame, window, mode)
    create_plate_display(plate_frame, window)
    
    # Add navigation buttons
    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: go_to_assignment_screen(window),
        x=buttonPosX,
        y=buttonPosY
    )
    create_rounded_button(
        canvas=canvas,
        text="?",
        command=lambda: open_help_manual(window, 1),
        x=20,
        y=20,
        width=50,
        height=50,
        font_size=15
    )
    create_rounded_button(
        canvas=canvas,
        text="Back",
        command=lambda: create_titleFrame(window),
        x=buttonPosXleft,
        y=buttonPosY
    )


# .d8888. d888888b d8888b.  .d8b.  d888888b d8b   db .d8888. 
# 88'  YP `~~88~~' 88  `8D d8' `8b   `88'   888o  88 88'  YP 
# `8bo.      88    88oobY' 88ooo88    88    88V8o 88 `8bo.   
#   `Y8b.    88    88`8b   88~~~88    88    88 V8o88   `Y8b. 
# db   8D    88    88 `88. 88   88   .88.   88  V888 db   8D 
# `8888Y'    YP    88   YD YP   YP Y888888P VP   V8P `8888Y' 


def create_strain_designer(window):
    # Clear window
    for widget in window.winfo_children():
        widget.destroy()

    # Initialize window properties
    # Store all state as window attributes
    window.plates = []
    window.strains = []
    window.strain_colors = COLORS
    window.current_color_index = 0
    window.current_plate = 0
    window.strain_buttons = []
    window.position_labels = {i: chr(65 + i) for i in range(window.layout_data['strains'])}
    window.column_assignments = {}
    window.atc_var = tk.StringVar(value="") 
    window.plate_visible = True
    # Create main canvas

    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both")

    window.canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    window.canvas.pack(expand=True)

    # Load the image using PhotoImage (or Pillow for more formats)
    image_image_1 = PhotoImage(file="Icons/image_1.png")
    window.canvas.image_image_1 = image_image_1  # Keep a reference to prevent garbage collection

    # Place the image on the canvas
    image_1 = window.canvas.create_image(719.0, 57.0, image=image_image_1)

    # Main dark rectangles
    round_rectangle(window.canvas, 17.0, 168.0-y_offset_edit, 1100.0, 730.0, fill=DARK, outline="")
    round_rectangle(window.canvas, 1120.0, 168-y_offset_edit, 1422.0, 730.0, fill=DARK, outline="")

    # Create frames
    window.plate_frame = Frame(window.canvas, bg=DARK)
    window.plate_frame.place(x=27, y=178-y_offset_edit, width=1070, height=512)

    window.control_frame = Frame(window.canvas, bg=DARK)
    window.control_frame.place(x=1130, y=178-y_offset_edit, width=282, height=512)

    # Create subframes
    window.strains_frame = Frame(window.control_frame, bg=DARK)
    window.strains_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    window.bottom_frame = Frame(window.control_frame, bg=DARK)
    window.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    setup_frames(window)

    create_rounded_button(
        canvas=window.canvas,
        text="Previous Plate",
        command=lambda:prev_plate(window),
        x=191.5+17+100,
        y=buttonPosY
    )

    create_rounded_button(
        canvas=window.canvas,
        text="Next Plate",
        command=lambda:next_plate(window),
        x=191.5+17+250+250 +100,
        y=buttonPosY
    )

    create_rounded_button(
        canvas=window.canvas,
        text="?",
        command=lambda: open_help_manual(window, 2),
        x=20,
        y=20,
        width=50,
        height=50,
        font_size=15

    )


    create_rounded_button(
        canvas=window.canvas,
        text="Preview All",
        command=lambda:preview_all_plates(window),
        x=191.5+17+250 +100,
        y=buttonPosY
    )

    create_rounded_button(
        canvas=window.canvas,
        text="Next",
        command=lambda:export_data(window),
        x=buttonPosX,
        y=buttonPosY
    )

    create_rounded_button(
        canvas=window.canvas,
        text="Back",
        command=lambda: create_plate_designer(window),
        x=buttonPosXleft,
        y=buttonPosY
    )  


def draw_plate(window, canvas, margin_left, margin_top, grid_width, grid_height):
    if CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        return
        
    plate = window.plates[CURRENTPLATEINDEX]
    
    # Calculate cell dimensions
    cols_per_strain = window.layout_data['columns'] // window.layout_data['strains']
    total_gaps = window.layout_data['strains'] - 1 if window.layout_data['gap_between_strains'] else 0
    total_width = window.layout_data['columns'] + total_gaps
    cell_width = grid_width / total_width
    cell_height = grid_height / window.layout_data['rows']

    # Draw position labels and spots
    current_x = margin_left
    for position_idx in range(window.layout_data['strains']):
        start_col, end_col = window.plate_layout['strain_positions'][position_idx]
        position_width = (end_col - start_col + 1) * cell_width

        # Find if this position is assigned to a strain
        assigned_strain = None
        for pos_key, assignment in plate.get('assignments', {}).items():
            row, col = map(int, pos_key.split('-'))
            if start_col <= col <= end_col:
                assigned_strain = assignment
                break

        # Draw position label
        label_text = assigned_strain if assigned_strain else f"PosA {window.position_labels[position_idx]}"
        canvas.create_text(
            current_x + position_width/2,
            margin_top,
            text=label_text,
            font=(FONT, 16, 'bold'),
            fill=DARK
        )

        # Draw spots
        for col_offset in range(end_col - start_col + 1):
            col = start_col + col_offset
            x_pos = current_x + col_offset * cell_width + cell_width/2

            for row in range(window.layout_data['rows']):
                pos_key = f"{row}-{col}"

                y_pos = margin_top + row * cell_height + cell_height/2
                
                # Determine spot color
                spot_color = GRAY1
                if pos_key in plate['assignments']:
                    strain = plate['assignments'][pos_key]
                    strain_index = window.strains.index(strain)
                    spot_color = window.strain_colors[strain_index]
                # Draw spot
                canvas.create_oval(
                    x_pos-8, y_pos-8, x_pos+8, y_pos+8,
                    fill=spot_color,
                    outline=spot_color,
                    tags=(pos_key, "spot")
                )

        current_x += position_width

        if window.layout_data['gap_between_strains'] and position_idx < window.layout_data['strains'] - 1:
            current_x += cell_width

def update_plate_display(window):
    print(f"Total plates: {len(window.plates)}")
    
    if not window.plates:
        print("ERROR: No plates exist")
        return

    # Validate plate index
    if CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        print(f"ERROR: Invalid plate index {CURRENTPLATEINDEX}")
        return

    if not window.plate_visible:
        window.plate_canvas.delete('all')
        window.plate_canvas.create_text(
            window.plate_canvas.winfo_width() // 2,
            window.plate_canvas.winfo_height() // 2,
            text="Layout Complete\nCreate a new plate or navigate to view other plates",
            font=(FONT, 16, 'bold'),
            fill=LIGHT,
            justify='center'
        )
        return

    current_plate = window.plates[CURRENTPLATEINDEX]

    # Verify plate_canvas exists
    if not hasattr(window, 'plate_canvas'):
        print("ERROR: plate_canvas does not exist")
        return

    # Clear the canvas completely
    window.plate_canvas.delete('all')

    # Get canvas dimensions
    width = window.plate_canvas.winfo_width()
    height = window.plate_canvas.winfo_height()
    
    print(f"Canvas Dimensions: {width} x {height}")

    # If canvas is not properly sized, schedule a retry
    if width <= 1 or height <= 1:
        print("WARNING: Invalid canvas size, scheduling retry")
        window.plate_canvas.after(100, lambda: update_plate_display(window))
        return

    # Calculate dimensions
    margin_left = 30
    margin_right = 30
    margin_top = 70
    margin_bottom = 30

    grid_width = width - margin_left - margin_right
    grid_height = height - margin_top - margin_bottom

    # Print layout details for debugging
    print(f"Layout Details:")
    print(f"Rows: {window.layout_data['rows']}")
    print(f"Columns: {window.layout_data['columns']}")
    print(f"Strain Positions: {window.plate_layout['strain_positions']}")

    # Draw the plate
    try:
        draw_plate(window, window.plate_canvas, 
                   margin_left, margin_top, grid_width, grid_height)
    except Exception as e:
        print(f"ERROR in draw_plate: {e}")
        import traceback
        traceback.print_exc()

    # Update the plate display grid and header
    try:
        draw_plate_grid(window, width, height, margin_left, margin_right, margin_top, 
                        margin_bottom, grid_width, grid_height)
    except Exception as e:
        print(f"ERROR in draw_plate_grid: {e}")
        import traceback
        traceback.print_exc()

def draw_plate_grid(window, width, height, margin_left, margin_right, margin_top, 
                   margin_bottom, grid_width, grid_height):
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        return
        
    plate = window.plates[CURRENTPLATEINDEX]
    num_strains = window.layout_data['strains']

    # Draw plate header
    additive_display = f" (Additive: {plate['additive']})" if plate.get('additive') is not None else ''
    
    # Draw plate header with corrected syntax
    window.plate_canvas.create_text(
        width // 2,
        20,
        text=f"Current Plate: {CURRENTPLATEINDEX + 1} - {plate['name']}{additive_display}",
        fill=LIGHT,
        font=(FONT, 16, 'bold')
    )
    
    # Calculate cell dimensions
    cols_per_strain = window.layout_data['columns'] // num_strains
    total_gaps = num_strains - 1 if window.layout_data['gap_between_strains'] else 0
    total_width = window.layout_data['columns'] + total_gaps
    cell_width = grid_width / total_width
    cell_height = grid_height / window.layout_data['rows']
    
    draw_positions_and_spots(window, margin_left, margin_top, 
                           cell_width, cell_height, num_strains) 

def truncate_strain_name(strain_name, max_width, window):
    """
    Truncates strain name to fit within max_width and adds strain number
    Returns: (truncated_name, strain_number)
    """
    # Get or initialize the strain counter from window
    if not hasattr(window, 'strain_counter'):
        window.strain_counter = {}
    
    # Get or assign strain number
    if strain_name not in window.strain_counter:
        window.strain_counter[strain_name] = len(window.strain_counter) + 1
    strain_number = window.strain_counter[strain_name]
    
    # Format with strain number
    numbered_strain = f"#{strain_number} {strain_name}"
    
    # Check if full text fits
    text_width = window.plate_canvas.tk.call(
        'font', 'measure',
        '{Helvetica} 16 bold',
        numbered_strain
    )
    
    if float(text_width) <= float(max_width) * 0.85:
        return numbered_strain
        
    # If too long, truncate the strain name
    max_chars = len(strain_name)
    while max_chars > 0:
        truncated = f"#{strain_number} {strain_name[:max_chars]}..."
        text_width = window.plate_canvas.tk.call(
            'font', 'measure',
            '{Helvetica} 16 bold',
            truncated
        )
        if float(text_width) <= float(max_width) * 0.85:
            return truncated
        max_chars -= 1
        
    # If even minimal text doesn't fit, return just the number
    return f"#{strain_number}"

def draw_positions_and_spots(window, margin_left, margin_top,
                           cell_width, cell_height, num_strains):
    plate = window.plates[CURRENTPLATEINDEX]
    current_x = margin_left
    
    def calculate_max_width(width):
        # Account for minimum spacing and font characteristics
        # Assuming average character width of 10 pixels at font size 16
        return int(width*0.8 / 10) - 2  # -2 for some padding, minimum 5 chars
    
    def truncate_strain(strain, max_chars):
        if len(strain) > max_chars:
            return strain[:max_chars-3] + "..."
        return strain
    
    for position_idx in range(num_strains):
        start_col, end_col = window.plate_layout['strain_positions'][position_idx]
        position_width = (end_col - start_col + 1) * cell_width
        
        # Find assigned strain
        assigned_strain = None
        for pos_key in plate.get('assignments', {}):
            row, col = map(int, pos_key.split('-'))
            if start_col <= col <= end_col:
                assigned_strain = plate['assignments'][pos_key]
                break
        
        if window.current_mode == 'A':
            max_chars = calculate_max_width(position_width)
            if assigned_strain:
                # Get strain number based on its position in window.strains
                strain_number = window.strains.index(assigned_strain) + 1
                
                # Calculate max width and truncate strain name
                
                truncated_strain = truncate_strain(assigned_strain, max_chars)
                
                # Create numbered and truncated label
                label_text = f"{strain_number}. {truncated_strain}"
            else:
                if (max_chars >10):
                    label_text = f"Position: {window.position_labels[position_idx]}"
                elif (max_chars >5):
                    label_text = f"Pos: {window.position_labels[position_idx]}"  
                else:
                    label_text = f"{window.position_labels[position_idx]}"        
            
            window.plate_canvas.create_text(
                current_x + position_width/2,
                margin_top,
                text=label_text,
                font=(FONT, int(16), 'bold'),
                fill=LIGHT
            )
        
        current_x += position_width
        if window.layout_data['gap_between_strains'] and position_idx < num_strains - 1:
            current_x += cell_width

def create_strain_controls(window):
    if window.current_mode == 'A':
        # "Add a strain" header
        strain_header = tk.Label(
            window.control_frame,
            text="Add a Strain",
            font=(FONT, 14, 'bold'),
            fg=LIGHT,
            bg=DARK
        )
        strain_header.pack(pady=(10, 5))
       
        # Strain name entry frame
        strain_frame = tk.Frame(window.control_frame, bg=DARK)
        strain_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        # Strain entry field with RoundedEntry
        window.strain_entry = RoundedEntry(
            strain_frame,
            width=200,
            height=35
        )
        window.strain_entry.pack(side=tk.LEFT, expand=True, padx=(0, 5))
       
        # Canvas for the add strain button
        add_strain_canvas = tk.Canvas(strain_frame, bg=DARK, highlightthickness=0, width=35, height=35)
        add_strain_canvas.pack(side=tk.RIGHT, padx=(5, 0))
       
        create_rounded_button(
            add_strain_canvas,
            "+",
            lambda: add_strain(window),
            0, 0,
            width=35,
            height=35,
            cornerradius=6,
            fill=LIGHT,
            accent=DARK
        )
       
        # Create a frame to hold the canvas and scrollbar
        container_frame = tk.Frame(window.control_frame, bg=DARK)
        container_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 20))
    
        canvas = tk.Canvas(container_frame, bg=DARK, highlightthickness=0)
        window.strain_list_frame = tk.Frame(canvas, bg=DARK)
    
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas_window = canvas.create_window((0, 0), window=window.strain_list_frame, anchor="nw")
    
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_window_size(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        window.strain_list_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_window_size)
        
        # Smooth scrolling implementation
        def smooth_scroll(event):
            # Get current scroll position
            current_position = canvas.yview()[0]
            
            # Calculate target position (smoother scrolling)
            delta = -1 * (event.delta / 1200)  # Reduced scroll speed
            target_position = current_position + delta
            
            # Clamp target position between 0 and 1
            target_position = max(0, min(1, target_position))
            
            # Animate the scroll
            def animate_scroll(current, target, steps=10):
                if steps > 0:
                    next_position = current + (target - current) / steps
                    canvas.yview_moveto(next_position)
                    window.after(10, animate_scroll, next_position, target, steps - 1)
            
            animate_scroll(current_position, target_position)
        
        canvas.bind_all("<MouseWheel>", smooth_scroll)

def add_strain(window):
    strain = window.strain_entry.get().strip()
    def truncate_strain(strain):
        if len(strain) > 19:
            return strain[:17] + "..."
        return strain
    if strain and strain not in window.strains:
        if len(window.strains) >= 14:
            messagebox.showwarning("Warning", "Maximum number of strains reached")
            return
        
        window.strains.append(strain)
        window.strain_entry.delete(0, tk.END)
        
        # Create strain frame
        strain_frame = tk.Frame(window.strain_list_frame, bg=DARK)
        strain_frame.pack(fill=tk.X, pady=2)
        
        # Create circular color indicator
        color_indicator = tk.Label(
            strain_frame,
            bg=window.strain_colors[len(window.strains) - 1],
            width=2,
            height=1,
            relief="solid",
            borderwidth=1
        )
        color_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        # Strain label with number
        strain_number = len(window.strains)
        strain_label = tk.Label(
            strain_frame,
            text=f"{strain_number}. {truncate_strain(strain)}",
            font=(FONT, 8),
            fg=LIGHT,
            bg=DARK
        )
        strain_label.pack(side=tk.LEFT, expand=True, anchor='w')
        
        # Create a frame for buttons
        button_frame = tk.Frame(strain_frame, bg=DARK)
        button_frame.pack(side=tk.RIGHT, anchor='e')  # Ensure buttons are tight

             # Create a Canvas for the "X" delete button
        delete_canvas = tk.Canvas(button_frame, bg=DARK, highlightthickness=0, width=30, height=30)
        delete_canvas.pack(side=tk.RIGHT)  

        # Create a Canvas for the "Assign" button
        assign_canvas = tk.Canvas(button_frame, bg=DARK, highlightthickness=0, width=70, height=30)  # Slightly smaller width
        assign_canvas.pack(side=tk.RIGHT , padx=2)  # Use RIGHT for tight placement

   
        
        # Create the rounded "Assign" button
        create_rounded_button(
            assign_canvas,
            "Assign",
            lambda s=strain: assign_strain_to_group(window, s),
            0, 0,
            width=60,
            height=25,
            cornerradius=6,
            fill=LIGHT,
            accent=DARK,
            font_size=8,
            bold=False
        )
        
        # Create the rounded "X" delete button
        create_rounded_button(
            delete_canvas,
            "×",
            lambda s=strain, f=strain_frame: delete_strain(window, s, f),
            0, 0,
            width=25,
            height=25,
            cornerradius=6,
            fill=LIGHT,  # Red color for delete button
            accent=DARK,
            font_size=12,
            bold=True
        )
        
        window.strain_buttons.append((strain_label, assign_canvas, delete_canvas))
        update_plate_display(window)

def create_plate_info(window, plate, rows, cols, unordered_quantifications,
                      strains, column_indexes):
    # Create preview image
    preview_image = create_plate_preview_image(window, plate)
    image_bytes = base64.b64decode(preview_image)
    image = Image.open(io.BytesIO(image_bytes))

    # Show the image in the default viewer
    image.show()
    return {
        'mode': window.current_mode,
        'filename': plate['name'],
        'additive': plate.get('additive', None),
        'dilutions': [],
        'unorderedquantifications': unordered_quantifications,
        'IMGcontours': None,
        'IMGbinary': None,
        'IMGbinaryAutomatic':None,
        'IMGToolUsage': None,
        'IMGgrid': None,
        'threshold': 0,
        'smallArea': 0,
        'blocksize': 0,
        'strains': strains,
        'column_indexes': [list(indexes) for indexes in column_indexes],
        'normalisation_values': [],
        'strain_positions': window.plate_layout['strain_positions'],
        'split_quantifications':[],
        'ordered_quantifications':[],
        'layout': {
            'num_strains' : window.layout_data['strains'],
            'rows': rows,
            'columns': cols,
            'x_dilution': window.layout_data['x_dilution'],
            'y_dilution': window.layout_data['y_dilution'],
            'gap_between_strains': window.layout_data['gap_between_strains'],
            'square_grid':window.layout_data['square_grid'],
            'IMGPreview': preview_image  # Store the base64 encoded image
        }
    }
    
def assign_strain_to_group(window, strain):
    if window.current_mode =='A':
        if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
            messagebox.showwarning("Warning", "Please create a plate first")
            return
        if not window.plate_visible:
            return    
        window.column_assignments = window.plates[CURRENTPLATEINDEX]['column_assignments']
        # Create menu of available positions
        available_positions = []
        for strain_idx, (start_col, end_col) in window.plate_layout['strain_positions'].items():
            position_key = f"{start_col}-{end_col}"
            available_positions.append((strain_idx, start_col, end_col))

        if available_positions:
            strain_location_menu = tk.Menu(window, tearoff=0)
            for strain_idx, start_col, end_col in available_positions:
                label = f"Position {window.position_labels[strain_idx]}"
                strain_location_menu.add_command(
                    label=label,
                    command=lambda s=start_col, e=end_col, idx=strain_idx: 
                        assign_strain_to_columns(window, strain, s, e, idx)
                )

            try:
                strain_location_menu.tk_popup(window.winfo_pointerx(), window.winfo_pointery())
            finally:
                strain_location_menu.grab_release()

def assign_strain_to_columns(window, strain, start_col, end_col, position_idx):
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        return
        
    plate = window.plates[CURRENTPLATEINDEX]
    position_key = f"{start_col}-{end_col}"
    
    # Check if columns are already assigned
    # for existing_key in list(window.column_assignments.keys()):
    #     existing_start, existing_end = map(int, existing_key.split('-'))
    #     if (start_col <= existing_end and end_col >= existing_start):
    #         return
            
    window.column_assignments[position_key] = {
        'strain': strain,
        'position': window.position_labels[position_idx],
        'position_idx': position_idx
    }
    
    # Assign spots to strain
    for row in range(window.layout_data['rows']):
        for col in range(start_col, end_col + 1):
            pos_key = f"{row}-{col}"
            plate['assignments'][pos_key] = strain
                
    update_plate_display(window)

def delete_strain(window, strain, strain_frame):
        
    # Remove strain from window.strains
    if strain in window.strains:
        strain_index = window.strains.index(strain)
        window.strains.remove(strain)
        
        # Remove strain assignments from all plates
        for plate in window.plates:
            # Remove from assignments
            assignments_to_remove = []
            for pos_key, assigned_strain in plate.get('assignments', {}).items():
                if assigned_strain == strain:
                    assignments_to_remove.append(pos_key)
            
            for pos_key in assignments_to_remove:
                del plate['assignments'][pos_key]
            
            # Remove from column_assignments
            column_assignments_to_remove = []
            for pos_key, assignment in plate.get('column_assignments', {}).items():
                if assignment.get('strain') == strain:
                    column_assignments_to_remove.append(pos_key)
                    
            for pos_key in column_assignments_to_remove:
                del plate['column_assignments'][pos_key]
    
    # Destroy the strain frame
    strain_frame.destroy()
    
    # Recreate strain list to ensure correct numbering
    rebuild_strain_list(window)
    
    # Update the plate display
    update_plate_display(window)

def rebuild_strain_list(window):
    # Clear existing strain list frame
    for widget in window.strain_list_frame.winfo_children():
        widget.destroy()
    
    # Clear strain buttons list
    window.strain_buttons = []
    
    # Rebuild the strain list with correct numbering
    for i, strain in enumerate(window.strains, 1):
        # Create strain frame
        strain_frame = tk.Frame(window.strain_list_frame, bg=DARK)
        strain_frame.pack(fill=tk.X, pady=2)
        
        # Create circular color indicator
        color_indicator = tk.Label(
            strain_frame,
            bg=window.strain_colors[i - 1],
            width=2,
            height=1,
            relief="solid",
            borderwidth=1
        )
        color_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        # Truncate strain name if necessary
        truncated_strain = strain if len(strain) <= 19 else strain[:17] + "..."
        
        # Strain label with updated number
        strain_label = tk.Label(
            strain_frame,
            text=f"{i}. {truncated_strain}",
            font=(FONT, 8),
            fg=LIGHT,
            bg=DARK
        )
        strain_label.pack(side=tk.LEFT, expand=True, anchor='w')
        
              # Create a frame for buttons
        button_frame = tk.Frame(strain_frame, bg=DARK)
        button_frame.pack(side=tk.RIGHT, anchor='e')  # Ensure buttons are tight

             # Create a Canvas for the "X" delete button
        delete_canvas = tk.Canvas(button_frame, bg=DARK, highlightthickness=0, width=30, height=30)
        delete_canvas.pack(side=tk.RIGHT)  

        # Create a Canvas for the "Assign" button
        assign_canvas = tk.Canvas(button_frame, bg=DARK, highlightthickness=0, width=70, height=30)  # Slightly smaller width
        assign_canvas.pack(side=tk.RIGHT , padx=2)  # Use RIGHT for tight placement

   
        
        # Create the rounded "Assign" button
        create_rounded_button(
            assign_canvas,
            "Assign",
            lambda s=strain: assign_strain_to_group(window, s),
            0, 0,
            width=60,
            height=25,
            cornerradius=6,
            fill=LIGHT,
            accent=DARK,
            font_size=8,
            bold=False
        )
        
        # Create the rounded "X" delete button
        create_rounded_button(
            delete_canvas,
            "×",
            lambda s=strain, f=strain_frame: delete_strain(window, s, f),
            0, 0,
            width=25,
            height=25,
            cornerradius=6,
            fill=LIGHT,  # Red color for delete button
            accent=DARK,
            font_size=12,
            bold=True
        )
        
        window.strain_buttons.append((strain_label, assign_canvas, delete_canvas))
        

def hide_current_plate(window):
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        return
        
    # Mark plate as hidden
    window.plate_visible = False
    
    # Clear the current view
    window.plate_canvas.delete('all')
    
    # Show message
    window.plate_canvas.create_text(
        window.plate_canvas.winfo_width() // 2,
        window.plate_canvas.winfo_height() // 2,
        text="Layout Complete\nCreate a new plate or navigate to view other plates",
        font=(FONT, 16, 'bold'),
        fill=LIGHT,
        justify='center'
    )


# d8888b. db       .d8b.  d888888b d88888b     d8b   db  .d8b.  db    db d888888b  d888b   .d8b.  d888888b d888888b  .d88b.  d8b   db 
# 88  `8D 88      d8' `8b `~~88~~' 88'         888o  88 d8' `8b 88    88   `88'   88' Y8b d8' `8b `~~88~~'   `88'   .8P  Y8. 888o  88 
# 88oodD' 88      88ooo88    88    88ooooo     88V8o 88 88ooo88 Y8    8P    88    88      88ooo88    88       88    88    88 88V8o 88 
# 88~~~   88      88~~~88    88    88~~~~~     88 V8o88 88~~~88 `8b  d8'    88    88  ooo 88~~~88    88       88    88    88 88 V8o88 
# 88      88booo. 88   88    88    88.         88  V888 88   88  `8bd8'    .88.   88. ~8~ 88   88    88      .88.   `8b  d8' 88  V888 
# 88      Y88888P YP   YP    YP    Y88888P     VP   V8P YP   YP    YP    Y888888P  Y888P  YP   YP    YP    Y888888P  `Y88P'  VP   V8P 
                                                                                                                                  
                                                                                                                                  


def add_plate(window):
    print(window.plates)
    global CURRENTPLATEINDEX
    window.plate_visible = True 
    name = window.plate_entry.get().strip()
    if name:
        additive_name = window.additive_entry.get().strip() if window.additive_var.get() else None
        new_plate = {
            'name': name,
            'additive': additive_name,
            'assignments': {},
            'column_assignments': {}
        }
        window.plates.append(new_plate)
        window.plate_entry.delete(0, tk.END)
        window.current_plate = len(window.plates) - 1
        window.column_assignments = window.plates[CURRENTPLATEINDEX]['column_assignments']
        CURRENTPLATEINDEX = (len(window.plates) - 1)
        update_plate_display(window)
        print(f"Plate added. Total plates: {len(window.plates)}")

def delete_current_plate(window):
    global CURRENTPLATEINDEX
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        messagebox.showwarning("Warning", "No plate to delete")
        return
        
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the current plate?"):
        # Remove the current plate
        window.plates.pop(CURRENTPLATEINDEX)
        
        # Adjust current plate index if necessary
        if CURRENTPLATEINDEX >= len(window.plates):
            CURRENTPLATEINDEX = max(len(window.plates) - 1, 0)
            
        # Reset column assignments
        window.column_assignments = {}
        
        # Update display
        # Update display
        if len(window.plates) == 0:
            window.plate_canvas.delete('all')
        else:    
            update_plate_display(window)

def clear_current_plate(window):
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        messagebox.showwarning("Warning", "No plate to clear")
        return
        
    if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all assignments from the current plate?"):
        # Clear all assignments from current plate
        window.plates[CURRENTPLATEINDEX]['assignments'] = {}
        window.column_assignments = {}
        
        # Update display
        update_plate_display(window)

def rename_current_plate(window):
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        messagebox.showwarning("Warning", "No plate to rename")
        return
        
    current_name = window.plates[CURRENTPLATEINDEX]['name']
    
    # Create rename dialog
    rename_dialog = tk.Toplevel(window)
    rename_dialog.title("Rename Plate")
    rename_dialog.geometry("300x180")  # Increased height to accommodate rounded components
    rename_dialog.configure(bg=DARK)
    rename_dialog.iconbitmap("Icons/ICON.ico")
    
    # Make dialog modal
    rename_dialog.transient(window)
    rename_dialog.grab_set()
    
    # Create main canvas for custom drawing
    main_canvas = tk.Canvas(
        rename_dialog,
        width=300,
        height=180,
        bg=DARK,
        highlightthickness=0
    )
    main_canvas.pack(fill=tk.BOTH, expand=True)
    
    # Add label
    main_canvas.create_text(
        150, 30,
        text="Enter new plate name:",
        font=(FONT, 12),
        fill=LIGHT
    )
    
    # Create rounded entry
    name_entry = RoundedEntry(
        rename_dialog,
        width=260,
        height=35,
        corner_radius=10
    )
    name_entry.insert(0, current_name)
    # Position the entry widget on the canvas
    main_canvas.create_window(150, 80, window=name_entry)
    
    def do_rename():
        new_name = name_entry.get().strip()
        if new_name:
            window.plates[CURRENTPLATEINDEX]['name'] = new_name
            update_plate_display(window)
            rename_dialog.destroy()
    
    # Create rounded buttons using the existing create_rounded_button function
    create_rounded_button(
        main_canvas,
        "Cancel",
        rename_dialog.destroy,
        20,  # x position
        120,  # y position
        width=120,
        height=40,
        cornerradius=10,
        font_size=10,
        fill=LIGHT,
        accent=DARK,
        bold = False
    )
    
    create_rounded_button(
        main_canvas,
        "Rename",
        do_rename,
        160,  # x position
        120,  # y position
        width=120,
        height=40,
        cornerradius=10,
        font_size=10,
        fill=LIGHT,
        accent=DARK,
        bold = False
    )
    
    # Center the dialog on the window
    rename_dialog.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    dialog_width = rename_dialog.winfo_width()
    dialog_height = rename_dialog.winfo_height()
    x = window.winfo_x() + (window_width - dialog_width) // 2
    y = window.winfo_y() + (window_height - dialog_height) // 2
    rename_dialog.geometry(f"+{x}+{y}")
def prev_plate(window):
    global CURRENTPLATEINDEX
    if not window.plate_visible:
        window.plate_visible = True
        update_plate_display(window)
     
    if window.plates and window.current_plate > 0:
        # Clear current display
        window.plate_canvas.delete('all')
        CURRENTPLATEINDEX = CURRENTPLATEINDEX -1
        # Update current plate index
        window.current_plate -= 1

        new_plate = window.plates[window.current_plate]
        window.column_assignments = window.plates[CURRENTPLATEINDEX]['column_assignments']
        # Update entry fields
        window.plate_entry.delete(0, tk.END)
        window.plate_entry.insert(0, new_plate['name'])
        window.atc_var.set(new_plate.get('atc', ''))
        
        # Update display with new plate index
        update_plate_display(window)
        window.plate_canvas.focus_set()
    else:
        print("Cannot go to previous plate")

def next_plate(window):
    global CURRENTPLATEINDEX

    window.plate_visible = True
    if window.plates and window.current_plate < len(window.plates) - 1:
        # Clear current display
        CURRENTPLATEINDEX = CURRENTPLATEINDEX +1
        window.plate_canvas.delete('all')
        
        # Update current plate index
        window.current_plate += 1
        new_plate = window.plates[window.current_plate]
        
        # Update entry fields
        window.plate_entry.delete(0, tk.END)
        window.plate_entry.insert(0, new_plate['name'])
        window.atc_var.set(new_plate.get('atc', ''))
        


        window.column_assignments = window.plates[CURRENTPLATEINDEX]['column_assignments']
        # Update display with new plate index
        update_plate_display(window)
        window.plate_canvas.focus_set()
    else:
        print("Cannot go to next plate")

def create_plate_controls(window):
    # Main controls container at the top
    controls_container = tk.Frame(window.control_frame, bg=DARK)
    controls_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    
    # "Add a plate" header
    plate_header = tk.Label(
        controls_container, 
        text="Add a Plate", 
        font=(FONT, 14, 'bold'), 
        fg=LIGHT, 
        bg=DARK
    )
    plate_header.pack(pady=(0, 10))


       # Additive controls
    window.additive_var = tk.BooleanVar(value=False)
    additive_frame = tk.Frame(controls_container, bg=DARK)
    additive_frame.pack(fill=tk.X, pady=(0, 5))
    
    additive_check = RoundedCheckbox(
        additive_frame,
        text="Additive",
        variable=window.additive_var,
        command=lambda: toggle_additive_entry(window)
    )
    additive_check.pack(side=tk.LEFT)
    additive_check.label.pack(side=tk.LEFT, padx=(5, 0))
    
    window.additive_entry = RoundedEntry(
        additive_frame,
        width=150,
        height=35,
        state=tk.DISABLED
    )
    window.additive_entry.pack(side=tk.RIGHT)

    # Plate name entry frame
    name_frame = tk.Frame(controls_container, bg=DARK)
    name_frame.pack(fill=tk.X, pady=(0, 5))
    
    window.plate_entry = RoundedEntry(
        name_frame,
        width=200,
        height=35
    )
    window.plate_entry.pack(side=tk.LEFT, expand=True, padx=(0, 5))
    
 

    # Create a canvas for the add plate button on the name frame
    add_plate_canvas = tk.Canvas(name_frame, bg=DARK, highlightthickness=0, width=35, height=45)  # Increased height for the button
    add_plate_canvas.pack(side=tk.RIGHT, padx=(5, 0))  # Adding some padding to the right

    create_rounded_button(
        add_plate_canvas, 
        "+", 
        lambda: add_plate(window), 
        0, 5, 
        width=35, 
        height=35, 
        cornerradius=6,
        fill = LIGHT, accent = DARK
    )


    # Plate management buttons
    management_button_canvas = tk.Canvas(window.canvas, bg=DARK, width=300, height=40, highlightthickness=0)
    management_button_canvas .place(x=37, y=178-y_offset_edit)
    
    # Delete button
    create_rounded_button(
        management_button_canvas, 
        "Delete", 
        lambda: delete_current_plate(window), 
        0, 0, 
        width=80, 
        height=35, 
        cornerradius=6, 
        font_size=8,
        fill = LIGHT, accent = DARK,
        bold=False  # Unbolded text
    )

    # Rename button
    create_rounded_button(
            management_button_canvas, 
            "Rename", 
            lambda: rename_current_plate(window), 
            90, 0, 
            width=80, 
            height=35, 
            cornerradius=6,
            font_size=8,
            fill = LIGHT, accent = DARK,
            bold=False  # Unbolded text
        )
    
    # Clear button


    if window.current_mode == 'A':
        create_rounded_button(
        management_button_canvas, 
        "Clear", 
        lambda: clear_current_plate(window), 
        180, 0, 
        width=80, 
        height=35, 
        cornerradius=6,
        font_size=8,
        fill = LIGHT, accent = DARK,
        bold=False  # Unbolded text
        )


        
        



        management_button_canvas2 = tk.Canvas(window.canvas, bg=DARK, width=230, height=40, highlightthickness=0)
        management_button_canvas2.place(x=1100-257, y=178-y_offset_edit)


        create_rounded_button(
            management_button_canvas2,
            "Copy Previous",
            lambda: copy_from_previous_plate(window),
            0,
            0,
            width=110,
            height=35,
            cornerradius=6,
            fill=LIGHT,
            font_size=8,
            accent=DARK,
            bold=False
        )
        create_rounded_button(
        canvas=management_button_canvas2,
        text="Save Layout",
        command=lambda: hide_current_plate(window),
        x=120,  # Position next to other controls
        y=0,  # Position above "Apply Previous Layout"
        width=110,
        height=35,
        cornerradius=6,
        fill=LIGHT,
        font_size=8,
        accent=DARK,
        bold=False
    )




def toggle_additive_entry(window):
    if window.additive_var.get():
        window.additive_entry.entry.config(state=tk.NORMAL)
    else:
        window.additive_entry.entry.config(state=tk.DISABLED)
        window.additive_entry.entry.delete(0, tk.END)

def setup_frames(window):
    # Main frames
    window.plate_frame = tk.Frame(window.canvas, bg=DARK)
    window.plate_frame.place(x=27, y=178-y_offset_edit+20, width=1070, height=532)
    
    window.control_frame = tk.Frame(window.canvas, bg=DARK)
    window.control_frame.place(x=1130, y=178-y_offset_edit, width=282, height=532)
    
    # Create three subframes within the control frame
    window.plate_controls_frame = tk.Frame(window.control_frame, bg=DARK)
    window.plate_controls_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    
    
    # Populate the frames
    create_plate_controls(window)
    create_strain_controls(window) 
    # create_navigation_controls(window)
        # Add copy button directly in the control fram
    

    



    ####Create plate canvas:
    window.plate_canvas = tk.Canvas(
        window.plate_frame,
        bg=DARK,
        highlightthickness=0
    )
    window.plate_canvas.pack(expand=True, fill='both')
    
    # Force initial update with current plate index
    window.plate_canvas.after(100, lambda: update_plate_display(window))

def copy_from_previous_plate(window):
    global CURRENTPLATEINDEX
    
    # Check if there is a previous plate to copy from
    if CURRENTPLATEINDEX <= 0 or len(window.plates) < 2:
        messagebox.showwarning("Warning", "No previous plate to copy from")
        return
        

    # Get previous plate's assignments
    prev_plate = window.plates[CURRENTPLATEINDEX - 1]
    current_plate = window.plates[CURRENTPLATEINDEX]
    
    # Copy assignments and column assignments
    current_plate['assignments'] = prev_plate['assignments'].copy()
    current_plate['column_assignments'] = prev_plate['column_assignments'].copy()
    
    # Update the window's column assignments reference
    window.column_assignments = current_plate['column_assignments']
    
    # Update display
    update_plate_display(window)
    print("Copied positions from previous plate")

# Add this to the create_strain_controls function
def add_copy_button_to_controls(window):
    # Create a frame for the copy button
    copy_button_frame = tk.Frame(window.control_frame, bg=DARK)
    copy_button_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
    
    # Create canvas for the copy button
    copy_button_canvas = tk.Canvas(copy_button_frame, bg=DARK, highlightthickness=0, width=260, height=40)
    copy_button_canvas.pack(fill=tk.X)
    
    # Create the copy button
    create_rounded_button(
        copy_button_canvas,
        "Copy From Previous Plate",
        lambda: copy_from_previous_plate(window),
        0, 0,
        width=260,
        height=35,
        cornerradius=6,
        fill=LIGHT,
        accent=DARK,
        bold=False
    )


# d8888b. d8888b. d88888b db    db d888888b d88888b db   d8b   db 
# 88  `8D 88  `8D 88'     88    88   `88'   88'     88   I8I   88 
# 88oodD' 88oobY' 88ooooo Y8    8P    88    88ooooo 88   I8I   88 
# 88~~~   88`8b   88~~~~~ `8b  d8'    88    88~~~~~ Y8   I8I   88 
# 88      88 `88. 88.      `8bd8'    .88.   88.     `8b d8'8b d8' 
# 88      88   YD Y88888P    YP    Y888888P Y88888P  `8b8' `8d8'  



def draw_unified_plate_preview(window, surface, plate, is_image=False, image_size=(1600, 1200)):
    """
    Unified function for drawing plate previews on both GUI canvas and PIL Image
    with consistent styling and truncated labels
    """
    # Calculate dimensions based on surface type
    if is_image:
        canvas_width, canvas_height = image_size
        # Reserve space for header and additive text
        content_margin_top = 120  # Space for header and additive text
    else:
        canvas_width = surface.winfo_reqwidth()
        canvas_height = surface.winfo_reqheight()
        content_margin_top = 0  # Header is handled separately for canvas
    
    margin = 20
    grid_width = canvas_width - 2 * margin
    grid_height = canvas_height - 2 * margin - content_margin_top
    
    # Calculate dimensions considering gaps
    cols_per_strain = window.layout_data['columns'] // window.layout_data['strains']
    total_gaps = window.layout_data['strains'] - 1 if window.layout_data['gap_between_strains'] else 0
    total_width = window.layout_data['columns'] + total_gaps
    cell_width = grid_width / total_width
    cell_height = grid_height / window.layout_data['rows']
    
    def calculate_max_width(width):
        return max(int(width / 8) - 4, 5)
    
    def truncate_strain(strain, max_chars):
        if len(strain) > max_chars:
            return strain[:max_chars-3] + "..."
        return strain
    
    def draw_spot(x, y, color):
        # Increased spot size for both canvas and image
        spot_size = 20 if is_image else 8
        if is_image:
            surface.ellipse(
                [int(x-spot_size), int(y-spot_size), 
                 int(x+spot_size), int(y+spot_size)],
                fill=color,
                outline=color
            )
        else:
            surface.create_oval(
                x-spot_size, y-spot_size, 
                x+spot_size, y+spot_size,
                fill=color,
                outline=color
            )
    
    def draw_text(x, y, text, font_size=25, anchor='s'):
        if is_image:
            font = ImageFont.truetype("arial.ttf", font_size+10)
            # Center text horizontally
            text_width = surface.textlength(text, font=font)
            surface.text(
                (int(x - text_width/2), int(y)),
                text,
                font=font,
                fill=DARK
            )
        else:
            surface.create_text(
                x, y,
                text=text,
                font=(FONT, 10, 'bold'),
                fill=DARK,
                anchor=anchor
            )
    
    # Draw header and additive text for image
    if is_image:
        # Draw plate name
        draw_text(
            canvas_width // 2,
            margin,
            f"{plate.get('name', 'Unnamed')}",
            font_size=40,
            anchor='n'
        )
        # Draw additive information
        additive_text = f"Additive: {plate.get('additive', 'Control')}"
        draw_text(
            canvas_width // 2,
            margin + 60,
            additive_text,
            font_size=18,
            anchor='n'
        )
    
    # Draw strain sections and labels
    current_x = margin
    content_y_start = margin + (content_margin_top if is_image else 0)
    
    for position_idx in range(window.layout_data['strains']):
        start_col, end_col = window.plate_layout['strain_positions'][position_idx]
        position_width = (end_col - start_col + 1) * cell_width
        
        # Find strain assignment for this section
        assigned_strain = None
        for pos_key, assignment in plate.get('assignments', {}).items():
            row, col = map(int, pos_key.split('-'))
            if start_col <= col <= end_col:
                assigned_strain = assignment
                break
        
        if window.current_mode == 'A':
            # Calculate available width and create label
            max_chars = calculate_max_width(position_width)
            if assigned_strain and assigned_strain != "unassigned":
                strain_number = window.strains.index(assigned_strain) + 1

                truncated_strain = truncate_strain(assigned_strain, max_chars)
                label_text = f"{strain_number}. {truncated_strain}"
            else:
                if (max_chars >10):
                    label_text = f"Position: {window.position_labels[position_idx]}"
                elif (max_chars >5):
                    label_text = f"Pos: {window.position_labels[position_idx]}"  
                else:
                    label_text = f"{window.position_labels[position_idx]}"    
            
            draw_text(
                current_x + position_width/2,
                content_y_start,
                label_text
            )
        
        # Draw spots
        for col_offset in range(end_col - start_col + 1):
            col = start_col + col_offset
            x_pos = current_x + col_offset * cell_width + cell_width/2
            
            for row in range(window.layout_data['rows']):
                pos_key = f"{row}-{col}"

                y_pos = content_y_start + row * cell_height + cell_height/2
                
                # Determine spot color
                if window.current_mode == 'A':
                    spot_color = GRAY1
                else:
                    spot_color = "#073b3a"
                if pos_key in plate['assignments']:
                    strain = plate['assignments'][pos_key]
                    if strain != "unassigned":
                        strain_index = window.strains.index(strain)
                        spot_color = window.strain_colors[strain_index]
                
                draw_spot(x_pos, y_pos, spot_color)
        
        current_x += position_width
        
        if window.layout_data['gap_between_strains'] and position_idx < window.layout_data['strains'] - 1:
            current_x += cell_width

def create_plate_preview_image(window, plate, width=1600, height=1200):
    # Add extra height for header and additive text
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    draw_unified_plate_preview(window, draw, plate, is_image=True, 
                             image_size=(width, height))
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    
    return base64.b64encode(buffer.getvalue()).decode()

def draw_plate_preview(window, canvas, plate):
    draw_unified_plate_preview(window, canvas, plate, is_image=False)

def preview_all_plates(window):
    if not window.plates:
        messagebox.showinfo("Info", "No plates to preview")
        return
    
    preview_window = tk.Toplevel(window)
    preview_window.title("SpotPlotter: All Plates Preview")
    preview_window.geometry("1200x800")
    preview_window.iconbitmap("Icons/ICON.ico")
    

    main_frame = tk.Frame(preview_window, bg=LIGHT)
    main_frame.pack(fill='both', expand=True)
    canvas = tk.Canvas(main_frame, bg=DARK, highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=DARK)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    plates_per_row = 2
    plate_width = 500
    plate_height = 400
    margin = 50

    for i, plate in enumerate(window.plates):
        row = i // plates_per_row
        col = i % plates_per_row
        plate_frame = tk.Frame(scrollable_frame, bg=LIGHT, bd=2, relief='raised')
        plate_frame.grid(row=row, column=col, padx=margin, pady=margin)
        
        # Create header with plate name
        header = tk.Label(
            plate_frame,
            text=f"{plate.get('name', 'Unnamed')}",
            font=(FONT, 12, 'bold'),
            bg=LIGHT
        )
        header.pack(pady=(5, 0))
        
        # Add additive information or "Control"
        additive_text = plate.get('additive', 'Control')
        additive_label = tk.Label(
            plate_frame,
            text=f"Additive: {additive_text}",
            font=(FONT, 10, 'italic'),
            bg=LIGHT,
            fg='#666666'
        )
        additive_label.pack(pady=(0, 5))

        plate_canvas = tk.Canvas(
            plate_frame,
            width=plate_width - 40,
            height=plate_height - 60,
            bg=LIGHT,
            highlightthickness=1
        )
        plate_canvas.pack(padx=10, pady=5)
        draw_plate_preview(window, plate_canvas, plate)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)







# d88888b db    db d8888b.  .d88b.  d8888b. d888888b   .88b  d88. d88888b d888888b  .d8b.  d8888b.  .d8b.  d888888b  .d8b.  
# 88'     `8b  d8' 88  `8D .8P  Y8. 88  `8D `~~88~~'   88'YbdP`88 88'     `~~88~~' d8' `8b 88  `8D d8' `8b `~~88~~' d8' `8b 
# 88ooooo  `8bd8'  88oodD' 88    88 88oobY'    88      88  88  88 88ooooo    88    88ooo88 88   88 88ooo88    88    88ooo88 
# 88~~~~~  .dPYb.  88~~~   88    88 88`8b      88      88  88  88 88~~~~~    88    88~~~88 88   88 88~~~88    88    88~~~88 
# 88.     .8P  Y8. 88      `8b  d8' 88 `88.    88      88  88  88 88.        88    88   88 88  .8D 88   88    88    88   88 
# Y88888P YP    YP 88       `Y88P'  88   YD    YP      YP  YP  YP Y88888P    YP    YP   YP Y8888D' YP   YP    YP    YP   YP 
                                                                                                                          
                                                                                                                          




def export_data(window):
    """
    Export plate data and allow the user to choose the file location and name.
    Returns: List of plate info and saves to a user-specified JSON file.
    """
    all_plate_info = []
   
    for plate in window.plates:
        rows = window.layout_data['rows']
        cols = window.layout_data['columns']
        unordered_quantifications = [[0 for _ in range(cols)] for _ in range(rows)]
       
        ordered_assignments = []
        plate_assignments = plate.get('assignments', {})
       
        # Process assignments in order of positions
        for pos_idx in range(window.layout_data['strains']):
            start_col, end_col = window.plate_layout['strain_positions'][pos_idx]
           
            # Check if any column in this position is assigned
            strain = None
            for col in range(start_col, end_col + 1):
                test_key = f"0-{col}"
                if test_key in plate_assignments:
                    strain = plate_assignments[test_key]
                    break
           
            # If no strain is assigned, use "unassigned"
            if not strain:
                strain = "unassigned"
                # Add "unassigned" assignments to the plate
                for row in range(rows):
                    for col in range(start_col, end_col + 1):
                        pos_key = f"{row}-{col}"
                        plate_assignments[pos_key] = strain
           
            ordered_assignments.append({
                'strain': strain,
                'columns': list(range(start_col, end_col + 1))
            })
       
        strains = [assignment['strain'] for assignment in ordered_assignments]
        column_indexes = [assignment['columns'] for assignment in ordered_assignments]
       
        plate_info = create_plate_info(window, plate, rows, cols, unordered_quantifications,
                                     strains, column_indexes)
        all_plate_info.append(plate_info)
   
    # Ask the user for the file name and location
    filename = filedialog.asksaveasfilename(
        title="Save Plate Data",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
   
    # Check if the user canceled the file dialog
    if not filename:
        print("Export canceled by the user.")
        return None
       
    save_to_file(all_plate_info, filename)
    print(f"Data exported successfully to {filename}")
   
    window.all_plate_info = all_plate_info
    create_titleFrame(window)
    return all_plate_info

def save_to_file(data, filename):
    """
    Save plate data to a JSON file.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        raise

def upload_metadata_handler(window):
    """
    Handler for the Upload MetaData button.
    Opens file dialog, loads data, and displays it.
    """
    try:
        # Open file dialog for selecting the JSON file
        filename = filedialog.askopenfilename(
            title="Select Metadata File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:  # User cancelled
            return
            
        # Load the data
        with open(filename, 'r') as file:
            loaded_data = json.load(file)
            
        # Update the global data structure
        window.all_plate_info = loaded_data
        
        # Print the loaded data in a formatted way
        print("\nUploaded Metadata Contents:")
        print("-" * 50)
        
        for idx, plate in enumerate(loaded_data, 1):
            print(f"\nPlate {idx}:")
            print("  Strains:", ", ".join(plate.get('strains', [])))
            print("  Columns:", plate.get('column_indexes', []))
            # print("  Dimensions:", f"{plate.get('rows', 0)} rows x {plate.get('cols', 0)} columns")
            print("  Quantifications Available:", bool(plate.get('quantifications', [])))
            
        print("-" * 50)
        print(f"Successfully loaded data from: {filename}")

        return loaded_data
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON file format")
        return None
    except Exception as e:
        print(f"Error loading metadata: {str(e)}")
        return None





# d888888b d888888b d888888b db      d88888b 
# `~~88~~'   `88'   `~~88~~' 88      88'     
#    88       88       88    88      88ooooo 
#    88       88       88    88      88~~~~~ 
#    88      .88.      88    88booo. 88.     
#    YP    Y888888P    YP    Y88888P Y88888P 

def create_titleFrame(window):
    for widget in window.winfo_children():
        widget.destroy()
    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both")
    canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.pack(expand=True) 
   
    ###LOGO IMAGE

    image_path_10 = ("Icons/image_10.png")
    img_logobig = Image.open(image_path_10)
    img_logobig_resized = img_logobig.resize((img_logobig.width // 2, img_logobig.height //2), Image.LANCZOS) #this resizing method maintains the quality

    #has to be a photoimage for Tkinkter, 
    image_image_10 = ImageTk.PhotoImage(img_logobig_resized)
    canvas.image_image_10 = image_image_10
    canvas.create_image(720.0, 350.0, image=image_image_10)


    create_rounded_button(
        canvas=canvas,
        text="Upload Assays",
        command=lambda: upload_images(window),
        x=855.0,
        y=600.0, )


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
    x=385.0,
    y=600.0)    

    create_rounded_button(
    canvas=canvas,
    text="Upload MetaData",
    command=lambda: upload_metadata_handler(window),
    x=620.0,
    y=600.0)

    if hasattr(window, 'window.plates'):
        print("works")

    return canvas


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
        
        create_cropFrame(window)
    else:
        messagebox.showwarning("Warning", "Please upload both text file and images that match metadata entries.")


def process_image(window):
    for widget in window.winfo_children():
        widget.destroy()
    stretched, blurred, gray_image, idealContrast = stretch_and_gray(window.current_image, False)
    window.contrast_value = idealContrast
    window.contrast_value = 20
    #FLAG
    print("__________________________________________")
    print(idealContrast)
    print("__________________________________________")
    width = window.current_image.shape[1]

    colomns = window.all_plate_info[window.current_image_index]['layout']['columns']
    print (width)
    print(colomns)
    blocksize = width/colomns/2#blocksize is a half of he spot size
    print (blocksize)
    window.block_size = int(blocksize)
    window.block_size = 61
    if window.block_size %2 ==0:
        window.block_size =  window.block_size +1
    window.gray_image = gray_image
    binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.current_image, excludeSmallDots=window.excludeSmallDots, contrast=window.contrast_value, block_size = window.block_size)

    window.contour_img = contour_img
    window.binarized_image = final_binary
    window.debug_image = np.stack((final_binary,) * 3, axis=-1)
    
    # only initialize history if it's empty, othewise its adding doubles

    #create_editFrame(window)
    create_slidersFrame(window)


def upload_images(window):
    """
    Allow the user to upload image files in the order they appear in the metadata.
    Warn the user if there are filenames in the metadata that were not uploaded.
    """
    import os
    from tkinter import filedialog, messagebox
    
    # Allow user to select image files
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tif")])
    
    # Ensure file_paths are selected and window.all_plate_info is initialized
    if file_paths and hasattr(window, 'all_plate_info'):
        window.image_paths = []
        unmatched_filenames = []  # Collect filenames that don't match the metadata
        uploaded_filenames = {os.path.basename(path).lower(): path for path in file_paths}
       
        # Get the list of expected filenames from metadata in their original order
        expected_filenames = [info['filename'].lower() for info in window.all_plate_info]
        
        # Collect matched paths in the order of metadata
        for filename in expected_filenames:
            if filename in uploaded_filenames:
                window.image_paths.append(uploaded_filenames[filename])
            else:
                unmatched_filenames.append(filename)
        
        # Warn about missing files
        if unmatched_filenames:
            messagebox.showwarning(
                "Missing Files",
                f"The following expected files were not uploaded:\n"
                f"{', '.join(unmatched_filenames)}"
            )
        
        # Load the first matching image if there are matches
        if window.image_paths:
            window.current_image_index = 0
            load_current_image(window)  # Load the first matching image
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
    window.history = []
    if window.current_image_index < len(window.image_paths) - 1:
        window.current_image_index += 1
        load_current_image(window)
        create_cropFrame(window)
        # update_progress_bar(window)

    else:
        save_window_state(window, 'PhiaUVData4.pkl')

        display_results(window)
        


#  .o88b. d8888b.  .d88b.  d8888b. 
# d8P  Y8 88  `8D .8P  Y8. 88  `8D 
# 8P      88oobY' 88    88 88oodD' 
# 8b      88`8b   88    88 88~~~   
# Y8b  d8 88 `88. `8b  d8' 88      
#  `Y88P' 88   YD  `Y88P'  88      
                                 
#makes sure that the crop takes into account the scale of the image, since its downsized
def resize_for_display_crop(image, max_width=1000, max_height=600):  # Reduced from 650 to 600
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
            outline=DARK,
            width=5,
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
        canvas_height = 974  # From your create_cropFrame function
        
        # Calculate offset, accounting for the 25-pixel upward shift
        offset_x = (canvas_width - window.display_width) // 2 
        offset_y = ((canvas_height - window.display_height) // 2) 
        
        # Adjust crop coordinates relative to the original image
        x_start = int((min(window.x_start, window.x_end) - offset_x) * scale_x)
        y_start = int((min(window.y_start, window.y_end) - (offset_y)) * scale_y)  # Remove the 25-pixel shift here
        x_end = int((max(window.x_start, window.x_end) - offset_x) * scale_x)
        y_end = int((max(window.y_start, window.y_end) - (offset_y)) * scale_y)  # Remove the 25-pixel shift here
        
        # Ensure coordinates are within image bounds
        x_start = max(0, x_start)
        y_start = max(0, y_start)
        x_end = min(x_end, original_width)
        y_end = min(y_end, original_height)
        
        # Perform the crop
        window.current_image = window.original_image[y_start:y_end, x_start:x_end]
        
        # Update debug_image and process
        if window.current_image.size > 0:
            window.debug_image = window.current_image.copy()
            process_image(window)
        else:
            messagebox.showwarning("Warning", "Invalid crop area. Please try again.")
    else:
        messagebox.showwarning("Warning", "Please select an area to crop.")

        
def create_cropFrame(window):
    # Destroy existing widgets
    for widget in window.winfo_children():
        widget.destroy()

    # Create frame and canvas
    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both")
    canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.pack(expand=True)
    window.edit_images = []

    # Initialize missing attributes
    window.excludeSmallDots = getattr(window, 'excludeSmallDots', 15)
    window.contrast_value = getattr(window, 'contrast_value', 1.0)
    window.block_size = getattr(window, 'block_size', 11)
    window.gray_image = getattr(window, 'gray_image', None)
    window.current_image = getattr(window, 'current_image', None)

    # Load and place the image at the top
    image_image_1 = PhotoImage(file="Icons/image_1.png")
    window.edit_images.append(image_image_1)
    canvas.create_image(719.0, 57.0, image=image_image_1)

    # Add instructional text
    canvas.create_text(
        720,
        TITLEHEIGHT,
        text="Please crop image. Line up vertical sides with outer edges of the plate. Click ? for more information.",
        fill=DARK,
        font=(FONT, 12, "bold")
    )

    # Add help button
    create_rounded_button(
        canvas=canvas,
        text="?",
        command=lambda: open_help_manual(window, 3),
        x=20,
        y=20,
        width=50,
        height=50,
        font_size=15
    )

    # Resize image
    display_image, scale_factor = resize_for_display_crop(window.original_image)
    window.scale_factor = scale_factor

    # Convert OpenCV image to PhotoImage
    image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    photo = ImageTk.PhotoImage(image=image)

    # Place image on canvas
    canvas.create_image(720, 487, image=photo, anchor="center")
    canvas.image = photo

    # Store dimensions
    window.display_width = photo.width()
    window.display_height = photo.height()

    # Add crop button
    create_rounded_button(
        canvas=canvas,
        text="Crop",
        command=lambda: apply_crop(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag="cropNext"
    )

    # Default cropping variables
    window.cropping = False
    window.x_start, window.y_start, window.x_end, window.y_end = 0, 0, 0, 0

    # Bind mouse events
    canvas.bind("<ButtonPress-1>", lambda event: start_crop(event, window))
    canvas.bind("<B1-Motion>", lambda event: crop(event, window, canvas))
    canvas.bind("<ButtonRelease-1>", lambda event: end_crop(event, window, canvas))

    # Progress bar setup
    #progress bar was created with help from Chat GBT
    # window.progress_frame = Frame(canvas, bg=LIGHT)
    # window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)
    # window.progress_bar = ttk.Progressbar(window.progress_frame, style="styled.Horizontal.TProgressbar", orient="horizontal",
    #                                     length=150, mode="determinate", maximum=100, value=0)
    # window.progress_bar.pack(side="left", padx=(0, 10))
    # window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    # window.progress_label.pack(side="left")

    # update_progress_bar(window)









# .d8888. db      d888888b d8888b. d88888b d8888b. .d8888. 
# 88'  YP 88        `88'   88  `8D 88'     88  `8D 88'  YP 
# `8bo.   88         88    88   88 88ooooo 88oobY' `8bo.   
#   `Y8b. 88         88    88   88 88~~~~~ 88`8b     `Y8b. 
# db   8D 88booo.   .88.   88  .8D 88.     88 `88. db   8D 
# `8888Y' Y88888P Y888888P Y8888D' Y88888P 88   YD `8888Y' 

#progress bar update - help from chatGBT
def update_progress_bar(window):
    if hasattr(window, 'progress_bar') and window.progress_bar:
        progress = (window.current_image_index + 1) / len(window.image_paths) * 100
        window.progress_bar['value'] = progress
        window.progress_label.config(text=f"{window.current_image_index + 1}/{len(window.image_paths)}")
        
def create_slidersFrame(window):
    for widget in window.winfo_children():
        widget.destroy()
    x_offset  =max((window.winfo_width()-1440)/2,0)
    calculate_drawing_thickness(window)
    # Create main canvas
    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both") 
    canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.pack(expand=True)
    image_image_1 = PhotoImage(
        file=("Icons/image_1.png"))
    window.edit_images.append(image_image_1)
    image_1 = canvas.create_image(
        719.0,
        57.0,
        image=image_image_1
    )

    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: go_to_edit_frame(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag = "slidersNext",
        fill = LIGHT,
        accent = DARK  )
    
    create_rounded_button(
        canvas=canvas,
        text="Back",
        command=lambda: create_cropFrame(window),
        x=buttonPosXleft,
        y=buttonPosY
    ) 
    create_rounded_button(
        canvas=canvas,
        text="?",
        command=lambda: open_help_manual(window, 4),
        x=20,
        y=20,
        width=50,
        height=50,
        font_size=15

    )


    # Main dark rectangle for image area
    
    round_rectangle(canvas,
        17.0,
        168.0-y_offset_edit,
        1100.0,
        730.0,
        fill=DARK,
        outline="")

    # Control panel rectangle
    round_rectangle(canvas,
        1120.0,
        168.0-y_offset_edit,
        1422.0,
        730.0,
        fill=DARK,
        outline="")

    # Create frame for image canvas
    main_frame = Frame(canvas, bg=DARK)
    main_frame.place(x=27, y=178-y_offset_edit, width=1063, height=562)
  
    # Create single canvas for image display
    window.image_canvas = Canvas(
        canvas,
        width=1050,
        height=552,
        bg=DARK,
        highlightthickness=0
    )
    window.image_canvas.place(x=17, y=178-y_offset_edit)

    # Control panel
    control_frame = Frame(canvas, bg=DARK)
    control_frame.place(x=1130, y=178-y_offset_edit, width=282, height=542)

    # Sliders setup
    y_offset = 20
    spacing = 150



    # Threshold Slider
    threshold_label = Label(control_frame, text="Threshold", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    threshold_label.place(x=16 , y=y_offset)
    create_circular_slider(
        control_frame, 
        min_val=0, 
        max_val=60,
        position=(16 , y_offset + 30),
        command=lambda v: on_contrast_change(window, v, False),
        initial_value=window.contrast_value
    )

    # Size Slider
    size_label = Label(control_frame, text="Size", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    size_label.place(x=16, y=y_offset + spacing)
    create_circular_slider(
        control_frame, 
        min_val=1, 
        max_val=100,
        position=(16, y_offset + spacing + 30),
        command=lambda v: on_excludeSmallDots(window, v, False),
        initial_value=window.excludeSmallDots

    )

    # Block Size Slider
    block_label = Label(control_frame, text="Block Size", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    block_label.place(x=16, y=y_offset + spacing * 2)
    create_circular_slider(
        control_frame, 
        min_val=3, 
        max_val=601,
        position=(16, y_offset + spacing * 2 + 30),
        command=lambda v: on_block_size_change(window, v, False),
        initial_value=window.block_size if hasattr(window, 'block_size') else 301
    )
    # Position inside the control_frame
        # Add navigation buttons
    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: go_to_edit_frame_from_sliders(window),
        x=buttonPosX,
        y=buttonPosY
    )
    create_rounded_button(
        canvas=canvas,
        text="Back",
        command=lambda: create_cropFrame(window),
        x=buttonPosXleft,
        y=buttonPosY
    ) 


    # # Progress bar
    # window.progress_frame = Frame(canvas, bg=LIGHT)
    # window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)
    # window.progress_bar = ttk.Progressbar(
    #     window.progress_frame, 
    #     style="styled.Horizontal.TProgressbar", 
    #     orient="horizontal",
    #     length=150, 
    #     mode="determinate", 
    #     maximum=100, 
    #     value=0
    # )
    # window.progress_bar.pack(side="left", padx=(0, 10))
    # window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    # window.progress_label.pack(side="left")
    # update_progress_bar(window)

    display_image(window)
    return canvas


def on_contrast_change(window, value, backToEdit = False):
    global backToEdit2
    if (backToEdit2 == False):
        window.contrast_value = float(value)
        binary_image, contour_img, final_binary, block_size = binarize(window.gray_image, window.original_image, contrast=window.contrast_value, excludeSmallDots=window.excludeSmallDots, block_size = window.block_size)
        # cv2.imshow("grey", resize_for_display(window.gray_image))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        #save new iamges
        window.binarized_image = final_binary
        window.contour_img = contour_img
        window.debug_image = np.stack((final_binary,) * 3, axis=-1)
        # window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] = final_binary
        # print("SAVED")
        #cannot use undo redo buttons to undo this
        display_image(window)
        # print(f"contrast={window.contrast_value}, excludeSmallDots={window.excludeSmallDots}, block_size = {window.block_size}")
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
        # print(f"contrast={window.contrast_value}, excludeSmallDots={window.excludeSmallDots}, block_size = {window.block_size}")
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
        # print(f"contrast={window.contrast_value}, excludeSmallDots={window.excludeSmallDots}, block_size = {window.block_size}")
        # cv2.imshow()
    else:
        backToEdit2 = False


def display_image(window):
    try:
        # Get original image dimensions
        original_width = window.debug_image.shape[1]
        original_height = window.debug_image.shape[0]
        
        # Calculate available space
        canvas_width = 1050  # Fixed canvas width
        canvas_height = 552  # Fixed canvas height
        
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
        cv2.drawContours(contour_img, contours, -1, (0, 0, 255), window.contour_thickness)
        
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



# d88888b d8888b. d888888b d888888b 
# 88'     88  `8D   `88'   `~~88~~' 
# 88ooooo 88   88    88       88    
# 88~~~~~ 88   88    88       88    
# 88.     88  .8D   .88.      88    
# Y88888P Y8888D' Y888888P    YP    





def create_editFrame(window, backToEdit = False):
    
    for widget in window.winfo_children():
        widget.destroy()
    font_size = 12
    resize = 14
    button_offset = 30
    base_y = 240.0
    global backToEdit2 #have to put this here if i want to edit it within this function
    if backToEdit == False:
        # Only set if not already set, or force overwrite is needed
        if window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] is None:
            window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] = window.binarized_image.copy()
            print("IMGbinaryAutomatic updated")

    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both")
    canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.pack(expand=True)

    image_image_1 = PhotoImage(
        file=("Icons/image_1.png"))
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
    

    create_rounded_button(
        canvas=canvas,
        text="Back",
        command=lambda: create_slidersFrame(window),
        x=buttonPosXleft,
        y=buttonPosY
    )   
    create_rounded_button(
        canvas=canvas,
        text="?",
        command=lambda: open_help_manual(window,5),
        x=20,
        y=20,
        width=50,
        height=50,
        font_size=15

    )

    round_rectangle(canvas,
       1362.0,
        168.0 -y_offset_edit ,
        1422.0,
        730,
        fill=DARK,
        outline="")

    round_rectangle(canvas,
        17.0,
        168.0 -y_offset_edit,
        1350.0,
        730,
        fill=DARK,
        outline="")


    # Toggle section
    canvas.create_text(
        1391.0,
        base_y - 15-y_offset_edit,
        text="Toggle",
        fill=LIGHT,
        font=(FONT, font_size * -1, 'bold')
    )
    toggle = ("Icons/toggle.png")
    img_toggle = Image.open(toggle)
    img_toggle_resized = img_toggle.resize((img_toggle.width // resize, img_toggle.height // resize), Image.LANCZOS)
    image_toggle = ImageTk.PhotoImage(img_toggle_resized)
    window.edit_images.append(image_toggle)
    toggle_button = Button(
        canvas,
        image=image_toggle,
        borderwidth=0,
        highlightthickness=0,
        highlightbackground=DARK,
        activebackground=DARK,
        command=lambda: toggle_image(window),
        relief="flat",
        bg=DARK
    )
    toggle_button.place(x=1376.0 , y=base_y-y_offset_edit)

    # Zoom section
    canvas.create_text(
        1391.0,
        base_y + (button_offset) +heading_y-y_offset_edit,
        text="Zoom",
        fill=LIGHT,
        font=(FONT, font_size * -1, 'bold')
    )

    # Zoom in button
    zoomin = ("Icons/zoomin.png")
    img_zoomin = Image.open(zoomin)
    img_zoomin_resized = img_zoomin.resize((img_zoomin.width // resize, img_zoomin.height // resize), Image.LANCZOS)
    image_zoomin_2 = ImageTk.PhotoImage(img_zoomin_resized)
    window.edit_images.append(image_zoomin_2)
    button_zoomin = Button(
        canvas,
        image=image_zoomin_2,
        highlightthickness=0,
        borderwidth=0,
        highlightcolor=DARK,  # Match the background color
        highlightbackground=DARK,
        activebackground=DARK,
        command=lambda: adjust_zoom(window, 1.2),
        bg=DARK
    )
    button_zoomin.place(x=1376.0 , y=base_y + (2*button_offset) -y_offset_edit)

    # Zoom out button
    zoomout = ("Icons/zoomout.png")
    img_zoomout = Image.open(zoomout)
    img_zoomout_resized = img_zoomout.resize((img_zoomout.width // resize, img_zoomout.height // resize), Image.LANCZOS)
    image_zoomout_2 = ImageTk.PhotoImage(img_zoomout_resized)
    window.edit_images.append(image_zoomout_2)
    button_zoomout = Button(
        canvas,
        image=image_zoomout_2,
        borderwidth=0,
        relief="flat",
        highlightthickness=-1,
        activebackground=DARK,
        command=lambda: adjust_zoom(window, 0.8),
        bg=DARK
    )
    button_zoomout.place(x=1376.0 , y=base_y + (3*button_offset)-y_offset_edit)

    # History section (Undo and Redo)
    canvas.create_text(
        1391.0,
        base_y + (4*button_offset)+heading_y-y_offset_edit,
        text="History",
        fill=LIGHT,
        font=(FONT, font_size * -1, 'bold')
    )

    # Undo button (image_8)
    image_path_8 = ("Icons/image_8.png")
    img_undo = Image.open(image_path_8) 
    img_undo_resized = img_undo.resize((img_undo.width // resize, img_undo.height // resize), Image.LANCZOS)
    image_image_8 = ImageTk.PhotoImage(img_undo_resized)
    window.edit_images.append(image_image_8)
    undo_button = Button(
        canvas,
        image=image_image_8,
        borderwidth=0,
        highlightthickness=0,
        activebackground=DARK,
        command=lambda: undo(window),
        relief="flat",
        bg=DARK
    )
    undo_button.place(x=1376.0, y=base_y + (5*button_offset) -y_offset_edit)

    # Redo button (image_7)
    image_path_7 = ("Icons/image_7.png")
    img_redo = Image.open(image_path_7)
    img_redo_resized = img_redo.resize((img_redo.width // resize, img_redo.height // resize), Image.LANCZOS)
    image_image_7 = ImageTk.PhotoImage(img_redo_resized)
    window.edit_images.append(image_image_7)
    redo_button = Button(
        canvas,
        image=image_image_7,
        borderwidth=0,
        highlightthickness=0,
        activebackground=DARK,
        command=lambda: redo(window),
        relief="flat",
        bg=DARK
    )
    redo_button.place(x=1376.0, y=base_y + (6*button_offset)-y_offset_edit)

    # "Add" text 
    canvas.create_text(
        1391.0,
        base_y + (7*button_offset)+ heading_y-y_offset_edit,
        text="Add",
        fill=LIGHT,
        font=(FONT, font_size * -1, 'bold')
    )

    # Thin pen (image_2)
    image_path_2 = ("Icons/image_2.png")
    img_thinPen = Image.open(image_path_2) 
    img_thinPen_resized = img_thinPen.resize((img_thinPen.width // resize, img_thinPen.height // resize), Image.LANCZOS)
    image_image_2 = ImageTk.PhotoImage(img_thinPen_resized)
    window.edit_images.append(image_image_2)
    button_thin_pen = Button(
        canvas,
        image=image_image_2,
        borderwidth=0,
        highlightthickness=0,
        activebackground=DARK,
        command=lambda: set_mode(window, "thin_brush"),
        bg=DARK
    )
    button_thin_pen.place(x=1376.0, y=base_y + (8*button_offset)-y_offset_edit)

    # Big pen (image_5)
    image_path_5 = ("Icons/image_5.png")
    img_thickPen = Image.open(image_path_5) 
    img_thickPen_resized = img_thickPen.resize((img_thickPen.width // resize, img_thickPen.height // resize), Image.LANCZOS)
    image_image_5 = ImageTk.PhotoImage(img_thickPen_resized)
    window.edit_images.append(image_image_5)
    big_pen_button = Button(
        canvas,
        image=image_image_5,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: set_mode(window, "large_brush"),
        relief="flat",
        bg=DARK
    )
    big_pen_button.place(x=1376.0, y=base_y + (9*button_offset)-y_offset_edit)

    # "Delete" text
    canvas.create_text(
        1391.0,
        base_y + (10*button_offset) + heading_y -y_offset_edit,
        text="Delete",
        fill=LIGHT,
        font=(FONT, font_size * -1, 'bold')
    )

    # Flood eraser (image_6)
    image_path_6 = ("Icons/image_6.png")
    img_flood = Image.open(image_path_6) 
    img_flood_resized = img_flood.resize((img_flood.width // resize, img_flood.height // resize), Image.LANCZOS)
    image_image_6 = ImageTk.PhotoImage(img_flood_resized)
    window.edit_images.append(image_image_6)
    flood_eraser_button = Button(
        canvas,
        image=image_image_6,
        borderwidth=0,
        highlightthickness=0,
        activebackground=DARK,
        command=lambda: set_mode(window, "flood"),
        relief="flat",
        bg=DARK
    )
    flood_eraser_button.place(x=1376.0, y=base_y + (11*button_offset)-y_offset_edit)

    # Thin eraser (image_9)
    image_path_9 =("Icons/image_9.png")
    img_thinEraser = Image.open(image_path_9)
    img_thinEraser_resized = img_thinEraser.resize((img_thinEraser.width // resize, img_thinEraser.height // resize), Image.LANCZOS)
    image_image_9 = ImageTk.PhotoImage(img_thinEraser_resized)
    window.edit_images.append(image_image_9)
    thin_eraser_button = Button(
        canvas,
        image=image_image_9,
        borderwidth=0,
        highlightthickness=0,
        activebackground=DARK,
        command=lambda: set_mode(window, "small_brush"),
        relief="flat",
        bg=DARK
    )
    thin_eraser_button.place(x=1376.0, y=base_y + (12*button_offset)-y_offset_edit)



    #big eraser
    image_image_4 = Image.open("Icons/image_4.png")
    image_image_4_Resized = image_image_4.resize((image_image_4.width // resize, image_image_4.height // resize), Image.LANCZOS)
    image_image_4 = ImageTk.PhotoImage(image_image_4_Resized)
    window.edit_images.append(image_image_4)
    big_eraser_button = Button(
        canvas,
        image=image_image_4,
        borderwidth=0,
        highlightthickness=0,
        activebackground=DARK,
        command=lambda: set_mode(window, "large_brush"),
        relief="flat",
        bg = DARK
    )
    big_eraser_button.place(x=1375.0, y=base_y + (13*button_offset)-y_offset_edit)




    window.undo_button = undo_button
    window.redo_button = redo_button

    total_width = 1295 - 34
    total_height = 783 - 203 -100
    img_width = total_width // 2
    img_height = total_height
    toggle_button.place(x=1376.0 , y=base_y-y_offset_edit)
    # Create frames to hold canvas and scrollbars
    left_frame = Frame(canvas, bg=DARK)
    right_frame = Frame(canvas, bg=DARK)
    left_frame.pack(expand=True, fill="both")
    right_frame.pack(expand=True, fill="both")
    # Create canvases with scrollbars
    window.left_canvas = Canvas(
        left_frame,
        width=img_width,
        height=img_height,
        bg=DARK,
        highlightthickness=0
    )
    window.left_canvas.pack(expand=True) 
    left_scroll_y = Scrollbar(left_frame, orient="vertical", command=window.left_canvas.yview)
    left_scroll_x = Scrollbar(left_frame, orient="horizontal", command=window.left_canvas.xview)


    window.right_canvas = Canvas(
        right_frame,
        width=img_width,
        height=img_height,
        bg=DARK,
        highlightthickness=0
    )

    
    window.right_canvas.pack(expand=True) 
    right_scroll_y = Scrollbar(right_frame, orient="vertical", command=window.right_canvas.yview)
    right_scroll_x = Scrollbar(right_frame, orient="horizontal", command=window.right_canvas.xview)

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

    yposFrames= 207-y_offset_edit
    # Position the frames
    left_frame.place(x=30  , y=yposFrames, width=img_width + 20, height=img_height + 20)
    right_frame.place(x=690  , y=yposFrames, width=img_width + 20, height=img_height + 20)

    # Initialize zoom level
    window.zoom_level = 1.0
    
    # Set up zoom controls and bindings
    setup_zoom_controls(window)

    # window.progress_frame = Frame(canvas, bg=LIGHT)
    # window.progress_frame.place(x=PROGRESSX, y=PROGRESSY, width=200, height=50)
    # window.progress_bar = ttk.Progressbar(window.progress_frame, style="styled.Horizontal.TProgressbar", orient="horizontal",
    #                                     length=150, mode="determinate", maximum=100, value=0)
    # window.progress_bar.pack(side="left", padx=(0, 10))
    # window.progress_label = Label(window.progress_frame, text="", bg=LIGHT, font=(FONT, 12, 'bold'))
    # window.progress_label.pack(side="left")
    
    # update_progress_bar(window)
    # Display images
    display_images(window)
    


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



    return canvas

def calculate_drawing_thickness(window):
    original_width = window.debug_image.shape[1]
    print("ORIGIONAL WIDTH")
    print(original_width)
    contour_thickness = original_width *0.0022
    window.contour_thickness = math.floor(contour_thickness)
    print(window.contour_thickness)

def display_images(window):
    """Display images while maintaining original aspect ratio with zoom support"""
    try:
        # Get original image dimensions
        original_width = window.debug_image.shape[1]
        original_height = window.debug_image.shape[0]
        
        # Calculate available space
        max_width = int((1440//2 - 60) * window.zoom_level)
        max_height = int((900 - 200) * window.zoom_level)
        

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
            # img_np = window.debug_image
            # # img_editing_resized = cv2.resize(np.array(img_editing), (img_np.shape[1], img_np.shape[0]))
            # img_gray = cv2.cvtColor(img_editing_resized, cv2.COLOR_RGB2GRAY)
            # contours, _ = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # contour_img = img_np.copy()
            # for cntr in contours:
            #     cv2.drawContours(contour_img, [cntr], 0, (0, 0, 255), 3)
            img_np = window.debug_image
            img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            contours, _ = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            contour_img = window.current_image.copy()
            cv2.drawContours(contour_img, contours, -1, (0, 0, 255), window.contour_thickness)

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





# d888888b  .d88b.   .d88b.  db      .d8888. 
# `~~88~~' .8P  Y8. .8P  Y8. 88      88'  YP 
#    88    88    88 88    88 88      `8bo.   
#    88    88    88 88    88 88        `Y8b. 
#    88    `8b  d8' `8b  d8' 88booo. db   8D 
#    YP     `Y88P'   `Y88P'  Y88888P `8888Y' 



def set_mode(window, mode):
    window.mode = mode
    if mode == "small_brush" or mode == "small_eraser":
        window.brush_size = 5
    elif mode == "large_brush" or mode == "large_eraser":
        window.brush_size = 30

def toggle_image(window):
    window.show_original = not window.show_original
    display_images(window)

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
    # cv2.line(window.debug_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

def brush_erase(window, x1, y1, x2, y2):
    cv2.line(window.binarized_image, (x1, y1), (x2, y2), 0, window.brush_size * 2)
    window.debug_image = np.stack((window.binarized_image,) * 3, axis=-1)
    # cv2.line(window.debug_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
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
        window.binarized_image = window.history[-2].copy()  # Go to the second-to-last state
        window.history.pop()  # Remove the last state
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



# d88888D  .d88b.   .d88b.  .88b  d88. 
# YP  d8' .8P  Y8. .8P  Y8. 88'YbdP`88 
#    d8'  88    88 88    88 88  88  88 
#   d8'   88    88 88    88 88  88  88 
#  d8' db `8b  d8' `8b  d8' 88  88  88 
# d88888P  `Y88P'   `Y88P'  YP  YP  YP 
                                         

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

def setup_zoom_controls(window):
    """Set up zoom controls and initialize zoom-related variables"""
    window.zoom_level = 1.0
    window.zoom_min = 0.5
    window.zoom_max = 4.0
    
    

def adjust_zoom(window, factor):
    

    new_zoom = window.zoom_level * factor
    if window.zoom_min <= new_zoom <= window.zoom_max:
        window.zoom_level = new_zoom
        display_images(window)


#  d888b  d8888b. d888888b d8888b.   d8888b. d88888b .d8888. db    db db      d888888b 
# 88' Y8b 88  `8D   `88'   88  `8D   88  `8D 88'     88'  YP 88    88 88      `~~88~~' 
# 88      88oobY'    88    88   88   88oobY' 88ooooo `8bo.   88    88 88         88    
# 88  ooo 88`8b      88    88   88   88`8b   88~~~~~   `Y8b. 88    88 88         88    
# 88. ~8~ 88 `88.   .88.   88  .8D   88 `88. 88.     db   8D 88b  d88 88booo.    88    
#  Y888P  88   YD Y888888P Y8888D'   88   YD Y88888P `8888Y' ~Y8888P' Y88888P    YP    



def display_results(window):
    for widget in window.winfo_children():
        widget.destroy()
    x_offset  =max((window.winfo_width()-1440)/2,0)
  
    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both") 
    canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.pack(expand=True)
    #logo

    image_path_10 = "Icons/image_10.png"
    img_logobig = Image.open(image_path_10)
    img_logobig_resized = img_logobig.resize((img_logobig.width // 2, img_logobig.height //2), Image.LANCZOS)

    image_image_10 = ImageTk.PhotoImage(img_logobig_resized)
    canvas.image_image_10 = image_image_10 
    canvas.create_image(720.0, 420.0, image=image_image_10)


    canvas.create_text(
        720,  
        buttonPosY,
        text="Results downloading......",
        fill=DARK,
        font=(FONT, 12, "bold"),
        anchor="center" 
    )

    #this makes sure that the screen doesnt freeze on the previous screen. It loads up will here, generates the results and then displays the finish button
    window.update()

    #generates the PDF, the excel and the images 
    process_results(window)
    #this will only display once the results are generated
    create_rounded_button(
        canvas=canvas,
        text="Finish",
        command=lambda: window.quit(),#will exit the program
        x=720 - (200 // 2),  
        y=buttonPosY-50,
        button_tag="Finish"
    )

def display_final_image(window, override =False):
    x_offset  =max((window.winfo_width()-1440)/2,0)
    add_to_history(window) #incase the user goes back
    for widget in window.winfo_children():
        widget.destroy()

    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both")
    canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.pack(expand=True)

    image_image_1 = PhotoImage(
    file=("Icons/image_1.png"))
    window.edit_images.append(image_image_1)
    image_1 = canvas.create_image(
        719.0,
        57.0,
        image=image_image_1
    )

    round_rectangle(canvas,
        17.0,
        168.0 -y_offset_edit,
        1422.0,
        730,
        fill=DARK,
        outline="")



    create_rounded_button(
        canvas=canvas,
        text="Back",
        command=lambda: create_editFrame(window),
        x=buttonPosXleft,
        y=buttonPosY,
        button_tag = "back_button_edit" )


    create_rounded_button(
        canvas=canvas,
        text="Override Grid",
        command=lambda: open_grid_override(window),
        x=1440/2-100,
        y=buttonPosY,
        button_tag = "override_button" )

    create_rounded_button(
        canvas=canvas,
        text="Next",
        command=lambda: next_image(window),
        x=buttonPosX,
        y=buttonPosY,
        button_tag = "DisplayNext" )

    create_rounded_button(
        canvas=canvas,
        text="?",
        command=lambda: open_help_manual(window, 6),
        x=20,
        y=20,
        width=50,
        height=50,
        font_size=15

    )
    canvas.create_text(
        720,  
        450.0,
        text="Loading image please wait",
        fill=LIGHT,
        font=(FONT, 12, "bold"),
        anchor="center" 
    )

    window.update()
    #frame where result will be displayed
    frame = Frame(window, bg=LIGHT)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    if (override):#ie if the user has over ridden the grid
        marked_image = window.marked_image
        result_grid = window.result_grid
        window.all_plate_info[window.current_image_index]['unorderedquantifications'] = result_grid

    else:   
        gray_image = window.gray_image  
        columns = window.all_plate_info[window.current_image_index]['layout']['columns']
        if window.all_plate_info[window.current_image_index]['layout']['gap_between_strains']:
            columns = columns + int(window.all_plate_info[window.current_image_index]['layout']['num_strains']) - 1

        #FLAG
        rows = window.all_plate_info[window.current_image_index]['layout']['rows']
        square_grid =  window.all_plate_info[window.current_image_index]['layout']['square_grid']
        result_grid, marked_image = detect_and_draw_circles(window.binarized_image, gray_image, False,columns = columns, rows = rows , square_grid=square_grid)
        if result_grid is None:
            messagebox.showwarning("Could not detect a grid", "Please override grid and add center points to where expected spots would be.")
            marked_image = window.binarized_image
        else:    
            window.all_plate_info[window.current_image_index]['unorderedquantifications'] = result_grid

    #make sure its the correct type
    if isinstance(marked_image, Image.Image):
        marked_image = np.array(marked_image)
        # print("yes is instance")

    #this is also taking into account that the one uses RGB and the other uses BGR    
    marked_image = cv2.cvtColor(marked_image, cv2.COLOR_RGB2BGR)   


    #resizing the image to fit
    max_width, max_height = 1000, 550
    h, w = marked_image.shape[:2]
    scale = min(max_width / w, max_height / h)
    new_size = (int(w * scale), int(h * scale))


    #saving what values and images to be used in the PDF reort
    window.all_plate_info [window.current_image_index]["threshold"] = window.contrast_value
    window.all_plate_info [window.current_image_index]["smallArea"] = window.excludeSmallDots
    window.all_plate_info [window.current_image_index]["blocksize"] = window.block_size
    window.all_plate_info [window.current_image_index]["IMGgrid"] = marked_image
    window.all_plate_info [window.current_image_index]["IMGbinary"] = window.binarized_image

    
    #Has to be PIL image for tkinkter, resizing and displaying
    resized_image = cv2.resize(marked_image, new_size, interpolation=cv2.INTER_AREA)
    img = Image.fromarray(resized_image)
    photo = ImageTk.PhotoImage(img)
    x_position = (1440 - new_size[0]) // 2
    y_position = (730 + 168.0 -y_offset_edit - new_size[1]) // 2
    canvas.create_image(x_position, y_position, anchor="nw", image=photo)
    canvas.image = photo

 
def go_to_edit_frame_from_sliders(window):
    window.history = [window.binarized_image.copy()]
    window.all_plate_info[window.current_image_index]['IMGbinaryAutomatic'] = window.binarized_image.copy()
    print("Automatic Updated")
    window.redo_stack = []    

    update_undo_redo_buttons(window)
    create_editFrame(window)
  

def go_to_edit_frame(window):
    # if not window.history:
    #     window.history = [window.binarized_image.copy()]
    #     window.redo_stack = []

    window.history = [window.binarized_image.copy()]
    window.redo_stack = []    
    
    update_undo_redo_buttons(window)
    create_editFrame(window)

def open_grid_override(window):
    for widget in window.winfo_children():
        widget.destroy()

    frame = Frame(window, bg=LIGHT)
    frame.pack(expand=True, fill="both")

    canvas = Canvas(
        frame,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.pack(expand=True)

    image_image_1 = PhotoImage(
    file=("Icons/image_1.png"))
    window.edit_images.append(image_image_1)
    image_1 = canvas.create_image(
        719.0,
        57.0,
        image=image_image_1
    )

    round_rectangle(canvas,
    17.0,
    168.0 -y_offset_edit,
    1422.0,
    730,
    fill=DARK,
    outline="")




    

    binary_image = window.binarized_image.copy()
    window.binary_image = binary_image

    rgb_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2RGB)
   
    #resizing as the dataset images are HUGE
    max_width, max_height = 1000, 550
    h, w = rgb_image.shape[:2]
    scale = min(max_width / w, max_height / h)
    new_size = (int(w * scale), int(h * scale))
    resized_image = cv2.resize(rgb_image, new_size, interpolation=cv2.INTER_AREA)
   
    img = Image.fromarray(resized_image)
    photo = ImageTk.PhotoImage(img)
    x_position = (1440 - new_size[0]) // 2
    y_position = (730 + 168.0 -y_offset_edit - new_size[1]) // 2
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

    window.clicked_points = []

    cross_thickness = max(1,window.contour_thickness-2 )
    #allows the user to add points
    def draw_points():
        canvas.delete("point")
        for x, y in window.blob_points:
            scaled_x = x * scale + x_position
            scaled_y = y * scale + y_position
            canvas.create_line(scaled_x-5, scaled_y-5, scaled_x+5, scaled_y+5, fill=ACCENT, tags="point", width=cross_thickness)
            canvas.create_line(scaled_x-5, scaled_y+5, scaled_x+5, scaled_y-5, fill=ACCENT, tags="point", width=cross_thickness)
        for x, y in window.clicked_points:
            scaled_x = x * scale + x_position
            scaled_y = y * scale + y_position
            canvas.create_line(scaled_x-5, scaled_y-5, scaled_x+5, scaled_y+5, fill=ACCENT, tags="point", width=cross_thickness)
            canvas.create_line(scaled_x-5, scaled_y+5, scaled_x+5, scaled_y-5, fill=ACCENT, tags="point", width=cross_thickness)
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

    create_rounded_button(
        canvas=canvas,
        text="?",
        command=lambda: open_help_manual(window, 6),
        x=20,
        y=20,
        width=50,
        height=50,
        font_size=15

    )

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
    print("WINDOW>GEY SHAPE" + str(window.gray_image.shape))
    height, width = window.gray_image.shape
    square_grid =  window.all_plate_info[window.current_image_index]['layout']['square_grid']
    print("square_grid")
    print(square_grid)
    #new grid using user clicked AND previously detected
    columns = window.all_plate_info[window.current_image_index]['layout']['columns']
    rows = window.all_plate_info[window.current_image_index]['layout']['rows']
    grid_start_x, grid_start_y, cell_width, cell_height = calculate_grid(window.clicked_pointsx,window.clicked_pointsy, width, height, window.binary_image, window.gray_image, columns, rows, square_grid=square_grid)
    print(cell_width, cell_height)
    counts, marked_image= quantify_grid(window.binary_image, window.binary_image, grid_start_x, grid_start_y, cell_width, cell_height,columns, rows)

    window.all_plate_info[window.current_image_index]['unorderedquantifications'] = counts

    #update so the new override one is used
    window.result_grid= counts
    window.marked_image = marked_image
    display_final_image(window, True)



# d88888b d888888b d8b   db d888888b .d8888. db   db d888888b d8b   db  d888b  
# 88'       `88'   888o  88   `88'   88'  YP 88   88   `88'   888o  88 88' Y8b 
# 88ooo      88    88V8o 88    88    `8bo.   88ooo88    88    88V8o 88 88      
# 88~~~      88    88 V8o88    88      `Y8b. 88~~~88    88    88 V8o88 88  ooo 
# 88        .88.   88  V888   .88.   db   8D 88   88   .88.   88  V888 88. ~8~ 
# YP      Y888888P VP   V8P Y888888P `8888Y' YP   YP Y888888P VP   V8P  Y888P  

def process_tool_usage(window):
    """
    Process binary images to create a color-coded visualization of tool usage.
    
    Args:
        window: Window object containing all_plate_info with binary images
    """
    # print(window.all_plate_info)
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
        # Save the result back to the plate info
        plate_info['IMGToolUsage'] = tool_usage


def get_save_folder():
    """
    Opens a Save As dialog to allow the user to select a location and enter a folder name.
    Includes a default name with the current date, time, and version.
    Returns the path to the folder to be created.
    """
    # Generate a default folder name with the current date, time, and version
    current_date = datetime.now().strftime("%Y.%m.%d")
    current_time = datetime.now().strftime("%H.%M.")
    default_name = f"{current_date}_ExperimentName_V{VERSION}_{current_time}"

    # Open Save As dialog to select location and name
    file_path = filedialog.asksaveasfilename(
        title="Save Project As",
        initialfile=default_name,
        filetypes=[("All Files", "*.*")],  # No file extension required
    )
   
    if not file_path:
        # If the user cancels, return None
        print("Save canceled by the user.")
        return None

    # Return the full path with any extensions intact
    print(f"Folder path to save: {file_path}")
    return file_path


def process_results(window):
    # Get the save folder path
    # Get the save folder path
    save_folder = get_save_folder()
    file_name = os.path.basename(save_folder)
    print(save_folder)
    if not save_folder:
        return  # Exit if no path is selected
   
    # Create the folder (if it doesn't exist)
    os.makedirs(save_folder, exist_ok=True)
    # Define paths for the files inside the folder
    pdf_log_path = os.path.join(save_folder, f"{file_name}_log.pdf")
    pdf_report_path = os.path.join(save_folder, f"{file_name}_report.pdf")
    excel_path = os.path.join(save_folder, f"{file_name}_data.xlsx")
    
    # Process and export files
    process_tool_usage(window)
    print(window.all_plate_info[0]["mode"])
    
    if window.all_plate_info[0]["mode"] == 'A':
        process_split_order_quantifications(window)
        strain_data, dilution_series = generate_data_series(window)
        sorted_positions = get_sorted_positions(dilution_series)
        dilution_series = extract_values_at_positions(dilution_series, sorted_positions)
        
        # Export Excel with project name
        exported_df = export_strain_data_to_excel(strain_data, dilution_series, excel_path)
        
        all_strain_data = []
        for strain, series in strain_data.items():
            figures_and_stats = plot_multiadditive_graphs(series, dilution_series, strain)
            all_strain_data.append((strain, figures_and_stats))
        
        # Generate PDF with project name
        generate_pdf_report_MODEA(window.all_plate_info, all_strain_data, pdf_report_path, file_name)
        generate_pdf_log(window.all_plate_info, pdf_log_path, file_name)
        # Clean up matplotlib figures
        for _, figures_and_stats in all_strain_data:
            for fig, _, _ in figures_and_stats:
                plt.close(fig)
    else:
        df, mean_fig, knockdown_fig, individual_fig = analyze_plate_data(window.all_plate_info)
        
        # Generate PDF and Excel with project name
        generate_pdf_report_MODEB(
            window.all_plate_info,
            pdf_path,
            mean_fig,
            knockdown_fig,
            individual_fig,
            file_name
        )
        df = export_plate_data_to_excel(window.all_plate_info, excel_path)
    
    print(f"Files saved in: {save_folder}")


# .d8888. d888888b  .d8b.  d888888b d88888b 
# 88'  YP `~~88~~' d8' `8b `~~88~~' 88'     
# `8bo.      88    88ooo88    88    88ooooo 
#   `Y8b.    88    88~~~88    88    88~~~~~ 
# db   8D    88    88   88    88    88.     
# `8888Y'    YP    YP   YP    YP    Y88888P 

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
    window.excludeSmallDots = 100
    #FLAG
    window.contrast_value = 20
    window.block_size = 301
    window.image_paths = []
    window.current_image_index = 0
    window.next_button = None
    window.progress_bar = None
    window.progress_label = None
    window.current_image = None 


    #need to change this so that it updates 



# #creating the frame with title and icon
window = Tk()
window.geometry("1440x900")
window.configure(bg=LIGHT)
window.title("SpotPlotter")


window.iconbitmap("Icons/ICON.ico")
initialize_window_attributes(window)
content_frame = Frame(window, bg=LIGHT)
content_frame.pack(expand=True, fill="both")

title_frame_widgets = create_titleFrame(content_frame)
title_frame_widgets = create_titleFrame(window)

window.resizable(True, True)
window.mainloop()





# restore_window_state(window, 'PhiaUVData3.pkl')
# process_results(window)


# FORREPORTMODEARrepeats2 - ONLY 1 ADDITIVE














