#Acknolgements: 
#Tkinter Designer by Parth Jadhav
#https://github.com/ParthJadhav/Tkinter-Designer

import pandas as pd
import numpy as np
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
from datetime import datetime
from collections import defaultdict
import pickle
from Processing import *
from outputs import *
from Style import *
COLORS = ["#3B82F6", "#10B981", "#F97316", "#EF4444", "#8B5CF6", "#D53F8C", "#6B7280", "#4B5563"]
import openpyxl
from singleDilution import *

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
from tkinter import Toplevel, Label
from PIL import Image, ImageTk
from Style import *
from PIL import ImageFont
DARK = "#092934"
LIGHT = "#FFFFFF"
COLORS = ["#D24C4A", "#D3784A", "#DFA24F", "#7DB46F", "#0F8660", "#46A2A2", "#7CC7BC", "#A9599C"] #https://coolors.co/d24c4a-d3784a-dfa24f-7db46f-0f8660-46a2a2-7cc7bc-a9599c
COLORS = ["#D24C4A", "#DFA24F", "#7DB46F", "#7CC7BC", "#46A2A2", "#0F8660", "#A9599C", "#D3784A"] #https://coolors.co/d24c4a-d3784a-dfa24f-7db46f-0f8660-46a2a2-7cc7bc-a9599c
CURRENTPLATEINDEX =-1
GRAY1 = "#F0F0F0"
GRAY2 = "#E0E0E0"
GRAY = "#B0B0B0"
FONT = "Microsoft New Tai Lue"
DARK = "#092934"
LIGHT = "#FFFFFF"
# DARK = "#FFFFFF"
# LIGHT = "#092934"
GRAY = "#B0B0B0"
ACCENT = "#4169E1"
FONT = "Microsoft New Tai Lue"
TITLEHEIGHT = 130




buttonPosX = 1200
buttonPosY = 800
backToEdit2 = False
PROGRESSX = 1180
PROGRESSY = 36
base_y = 212.0
heading_y = 20


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
            print("  Dimensions:", f"{plate.get('rows', 0)} rows x {plate.get('cols', 0)} columns")
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


def create_mode_switcher(control_frame, window):
    def switch_mode(new_mode):
        create_plate_designer(window, mode=new_mode)
   #bookmark 
    # Label for mode selection
    mode_label = Label(
        control_frame,
        text="Select Mode:",
        font=(FONT, 12, "bold"),
        fg=LIGHT,
        bg=DARK
    )
    mode_label.place(x=10, y=10)
    
    # Dropdown menu for mode selection
    mode_var = tk.StringVar(value=window.current_mode)  # Keep track of the current mode
    mode_dropdown = ttk.Combobox(
        control_frame,
        textvariable=mode_var,
        values=["A", "B"],
        state="readonly",
        font=(FONT, 11)
    )
    mode_dropdown.place(x=110, y=10, width=100)
    
    # Bind selection change to switch_mode function
    mode_dropdown.bind("<<ComboboxSelected>>", lambda event: switch_mode(mode_var.get()))

def create_controls(control_frame, window, mode):
    y_offset = 60
    spacing = 80
    label_width = 100  # Width for right-aligned labels
    
    # Function to create styled input row
    def create_input_row(label_text, variable, y_pos):
        # Right-aligned label
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
        
        # Custom rounded entry box
        entry_frame = RoundedEntry(control_frame, width=100, height=35)
        entry_frame.place(x=140, y=y_pos - 5)
        entry_frame.entry.config(textvariable=variable, font=(FONT, 11))
        
        return entry_frame.entry
    
    # Create input rows based on the mode
    create_input_row("Rows:", window.plate_layout['rows'], y_offset)
    create_input_row("Columns:", window.plate_layout['columns'], y_offset + spacing)
    
    if mode == "A":  # Show additional options in Mode A
        create_input_row("Strains:", window.plate_layout['strains'], y_offset + spacing * 2)
        create_input_row("X-Dilution:", window.plate_layout['x_dilution'], y_offset + spacing * 3)
        create_input_row("Y-Dilution:", window.plate_layout['y_dilution'], y_offset + spacing * 4)
        
        # Create checkbox for gap between strains
        checkbox = RoundedCheckbox(
            control_frame,
            text="Gap Between Strains",
            variable=window.plate_layout['gap_between_strains'],
            command=lambda: update_plate_display_layout_designer(window)
        )
        checkbox.place(x=20, y=y_offset + spacing * 5)
        checkbox.label.place(x=50, y=y_offset + spacing * 5)
    
    # Bind all variables to update function
    for var_name in ['rows', 'columns', 'strains', 'x_dilution', 'y_dilution']:
        window.plate_layout[var_name].trace_add(
            "write",
            lambda *args: update_plate_display_layout_designer(window)
        )


def create_plate_display(plate_frame, window):
    window.plate_canvas = tk.Canvas(
        plate_frame,
        bg=DARK,
        highlightthickness=0
    )
    window.plate_canvas.pack(expand=True, fill='both')
    update_plate_display_layout_designer(window)

def update_plate_display_layout_designer(window):
    window.plate_canvas.delete('all')
    
    try:
        rows = max(1, window.plate_layout['rows'].get())
        cols = max(1, window.plate_layout['columns'].get())
        strains = max(1, window.plate_layout['strains'].get())
        x_dil = max(1, window.plate_layout['x_dilution'].get())
        y_dil = max(1, window.plate_layout['y_dilution'].get())
    except tk.TclError:
        return
        
    width = window.plate_canvas.winfo_width()
    height = window.plate_canvas.winfo_height()
    if width <= 1 or height <= 1:
        window.plate_canvas.after(100, lambda: update_plate_display_layout_designer(window))
        return
        
    margin = 50
    grid_width = width - 2 * margin
    grid_height = height - 2 * margin
    
    cols_per_strain = cols // strains
    total_cols = cols
    
    if window.plate_layout['gap_between_strains'].get():
        total_gaps = strains - 1
        total_cols = cols + total_gaps

    cell_width = grid_width / total_cols
    cell_height = grid_height / rows
    
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
    
    
    draw_spots(window, strains, margin, cell_width, cell_height, x_dil, rows)


def draw_spots(window, strains, margin, cell_width, cell_height, x_dil, rows):
    for strain in range(strains):
        start_col, end_col = window.plate_layout['strain_positions'][strain]
        for col_offset in range(end_col - start_col + 1):
            actual_col = start_col + col_offset
            x_value = x_dil ** col_offset
            x_pos = margin + actual_col * cell_width + cell_width/2
            
            if window.current_mode =='A':
                window.plate_canvas.create_text(
                    x_pos,
                    margin - 20,
                    text=x_value,
                    fill=LIGHT,
                    font=(FONT, 8)
                )
            
            for row in range(rows):
                pos_key = f"{row}-{actual_col}"
                if pos_key not in window.plate_layout['removed_positions']:
                    x = margin + actual_col * cell_width + cell_width/2
                    y = margin + row * cell_height + cell_height/2
                    color = COLORS[strain % len(COLORS)]
                    
                    window.plate_canvas.create_oval(
                        x-10, y-10, x+10, y+10,
                        fill=color,
                        outline=color,
                        tags=(pos_key, "spot", f"strain_{strain}")
                    )


def go_to_assignment_screen(window):
    valid_positions = {}
    for strain, (start_col, end_col) in window.plate_layout['strain_positions'].items():
        strain_positions = []
        for row in range(window.plate_layout['rows'].get()):
            for col in range(start_col, end_col + 1):
                pos_key = f"{row}-{col}"
                if pos_key not in window.plate_layout['removed_positions']:
                    strain_positions.append(pos_key)
        valid_positions[strain] = strain_positions

    layout_data = {
        'rows': window.plate_layout['rows'].get(),
        'columns': window.plate_layout['columns'].get(),
        'strains': window.plate_layout['strains'].get(),
        'x_dilution': window.plate_layout['x_dilution'].get(),
        'y_dilution': window.plate_layout['y_dilution'].get(),
        'gap_between_strains': window.plate_layout['gap_between_strains'].get(),
        'removed_positions': list(window.plate_layout['removed_positions']),
        'strain_positions': window.plate_layout['strain_positions'],
        'valid_positions': valid_positions
    }


    window.layout_data = layout_data
    create_strain_designer(window)



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
    # Create main canvas
    window.canvas = tk.Canvas(
        window,
        bg=LIGHT,
        height=1024,
        width=1440,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    window.canvas.place(x=0, y=0)

    # Load the image using PhotoImage (or Pillow for more formats)
    image_image_1 = PhotoImage(file="Icons/image_1.png")
    window.canvas.image_image_1 = image_image_1  # Keep a reference to prevent garbage collection

    # Place the image on the canvas
    image_1 = window.canvas.create_image(719.0, 57.0, image=image_image_1)

    # Main dark rectangles
    round_rectangle(window.canvas, 17.0, 168.0, 1100.0, 826.0, fill=DARK, outline="")
    round_rectangle(window.canvas, 1120.0, 168.0, 1422.0, 826.0, fill=DARK, outline="")

    # Create frames
    window.plate_frame = tk.Frame(window, bg=DARK)
    window.plate_frame.place(x=27, y=178, width=1070, height=638)

    window.control_frame = tk.Frame(window, bg=DARK)
    window.control_frame.place(x=1130, y=178, width=282, height=638)

    # Create subframes
    window.strains_frame = tk.Frame(window.control_frame, bg=DARK)
    window.strains_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    window.bottom_frame = tk.Frame(window.control_frame, bg=DARK)
    window.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    setup_frames(window)



    create_rounded_button(
        canvas=window.canvas,
        text="Next",
        command=lambda:export_data(window),
        x=buttonPosX,
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
        label_text = assigned_strain if assigned_strain else f"Position {window.position_labels[position_idx]}"
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
                if pos_key not in window.layout_data['removed_positions']:
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

    print("======== PLATE DISPLAY UPDATE COMPLETE ========")



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
    rename_dialog.geometry("300x120")
    rename_dialog.configure(bg=DARK)
    
    # Make dialog modal
    rename_dialog.transient(window)
    rename_dialog.grab_set()
    
    # Create and pack widgets
    tk.Label(
        rename_dialog,
        text="Enter new plate name:",
        font=(FONT, 12),
        bg=DARK,
        fg=LIGHT
    ).pack(pady=10)
    
    name_entry = ttk.Entry(rename_dialog, width=30)
    name_entry.insert(0, current_name)
    name_entry.pack(pady=5)
    
    def do_rename():
        new_name = name_entry.get().strip()
        if new_name:
            window.plates[CURRENTPLATEINDEX]['name'] = new_name
            update_plate_display(window)
            rename_dialog.destroy()
    
    button_frame = tk.Frame(rename_dialog, bg=DARK)
    button_frame.pack(pady=10)
    
    tk.Button(
        button_frame,
        text="Cancel",
        command=rename_dialog.destroy,
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        button_frame,
        text="Rename",
        command=do_rename,
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    ).pack(side=tk.LEFT, padx=5)
    
    # Center the dialog on the window
    rename_dialog.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    dialog_width = rename_dialog.winfo_width()
    dialog_height = rename_dialog.winfo_height()
    x = window.winfo_x() + (window_width - dialog_width) // 2
    y = window.winfo_y() + (window_height - dialog_height) // 2
    rename_dialog.geometry(f"+{x}+{y}")


def create_strain_controls(window):
    if window.current_mode =='A':
        # "Add a strain" header
        strain_header = tk.Label(window.control_frame, text="Add a Strain", font=(FONT, 14, 'bold'), fg=LIGHT, bg=DARK)
        strain_header.pack(pady=(10, 5))
        
        # Strain name frame
        strain_frame = tk.Frame(window.control_frame, bg=DARK)
        strain_frame.pack(fill=tk.X, padx=10)
        
        # Initialize strains attribute if not exists
        if not hasattr(window, 'strains'):
            window.strains = []
        
        # Strain entry
        window.strain_entry = ttk.Entry(strain_frame, width=25)
        window.strain_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        # Add strain button (now a + button)
        add_strain_btn = tk.Button(
            strain_frame,
            text="+",
            command=lambda: add_strain(window),
            font=(FONT, 10),
            bg=LIGHT,
            fg=DARK,
            width=3
        )
        add_strain_btn.pack(side=tk.RIGHT)
        
        # Blank space for added strains
        window.strain_list_frame = tk.Frame(window.control_frame, bg=DARK)
        window.strain_list_frame.pack(fill=tk.X, padx=10, pady=(5, 20))

def add_strain(window):
    strain = window.strain_entry.get().strip()
    if strain and strain not in window.strains:
        if len(window.strains) >= len(window.strain_colors):
            messagebox.showwarning("Warning", "Maximum number of strains reached")
            return
        
        window.strains.append(strain)
        window.strain_entry.delete(0, tk.END)
        
        # Create strain frame within strain_list_frame instead of strains_frame
        strain_frame = tk.Frame(window.strain_list_frame, bg=DARK)
        strain_frame.pack(fill=tk.X, pady=2)
        
        color_indicator = tk.Label(
            strain_frame,
            bg=window.strain_colors[len(window.strains)-1],
            width=2,
            height=1
        )
        color_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        strain_label = tk.Label(
            strain_frame,
            text=strain,
            font=(FONT, 10),
            fg=LIGHT,
            bg=DARK
        )
        strain_label.pack(side=tk.LEFT, expand=True, anchor='w')
        
        assign_btn = tk.Button(
            strain_frame,
            text="Assign",
            command=lambda s=strain: assign_strain_to_group(window, s),
            font=(FONT, 8),
            bg=LIGHT,
            fg=DARK
        )
        assign_btn.pack(side=tk.RIGHT)
        
        window.strain_buttons.append((strain_label, assign_btn))
        update_plate_display(window)

        
def create_plate_canvas(window):
    window.plate_canvas = tk.Canvas(
        window.plate_frame,
        bg=DARK,
        highlightthickness=0
    )
    window.plate_canvas.pack(expand=True, fill='both')
    window.plate_canvas.bind("<Button-3>", lambda e: unselect_position(window, window.current_plate, e))
    
    # Force initial update with current plate index
    window.plate_canvas.after(100, lambda: update_plate_display(window))


def add_plate(window):
    global CURRENTPLATEINDEX
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

def unselect_position(window, event):
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        return
        
    clicked_items = window.plate_canvas.find_closest(event.x, event.y)
    if not clicked_items:
        return
        
    clicked_item = clicked_items[0]
    tags = window.plate_canvas.gettags(clicked_item)
    
    if "spot" in tags:
        pos_key = tags[0]
        row, col = map(int, pos_key.split('-'))
        
        for position_key, strain in list(window.column_assignments.items()):
            start, end = map(int, position_key.split('-'))
            if start <= col <= end:
                del window.column_assignments[position_key]
                
        plate = window.plates[CURRENTPLATEINDEX]
        for row_idx in range(window.layout_data['rows']):
            key = f"{row_idx}-{col}"
            if key in plate['assignments']:
                del plate['assignments'][key]
        
        update_plate_display(window)



def update_strain_menu(window):
    # Remove existing menu if it exists
    for widget in window.control_frame.winfo_children():
        if isinstance(widget, tk.OptionMenu):
            widget.destroy()

    if window.strains:
        selected_strain = tk.StringVar(value=window.strains[0])
        menu = tk.OptionMenu(
            window.control_frame,
            selected_strain,
            *window.strains
        )
        menu.configure(font=(FONT, 10), bg=LIGHT, fg=DARK)
        menu.grid(row=3, column=2, padx=20, pady=10)


def assign_strain_to_group(window, strain):
    if window.current_mode =='A':
        if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
            messagebox.showwarning("Warning", "Please create a plate first")
            return

        # Create menu of available positions
        available_positions = []
        for strain_idx, (start_col, end_col) in window.plate_layout['strain_positions'].items():
            position_key = f"{start_col}-{end_col}"
            if position_key not in window.column_assignments:
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
        else:
            messagebox.showwarning("Warning", "All positions are already assigned.")


def assign_strain_to_columns(window, strain, start_col, end_col, position_idx):
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        return
        
    plate = window.plates[CURRENTPLATEINDEX]
    position_key = f"{start_col}-{end_col}"
    
    # Check if columns are already assigned
    for existing_key in list(window.column_assignments.keys()):
        existing_start, existing_end = map(int, existing_key.split('-'))
        if (start_col <= existing_end and end_col >= existing_start):
            return
            
    window.column_assignments[position_key] = {
        'strain': strain,
        'position': window.position_labels[position_idx],
        'position_idx': position_idx
    }
    
    # Assign spots to strain
    for row in range(window.layout_data['rows']):
        for col in range(start_col, end_col + 1):
            pos_key = f"{row}-{col}"
            if pos_key not in window.layout_data['removed_positions']:
                plate['assignments'][pos_key] = strain
                
    update_plate_display(window)


def draw_plate_grid(window, width, height, margin_left, margin_right, margin_top, 
                   margin_bottom, grid_width, grid_height):
    if not window.plates or CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        return
        
    plate = window.plates[CURRENTPLATEINDEX]
    num_strains = window.layout_data['strains']

    # Draw plate header
    additive_display = f"( Additive: {plate['additive']})" if plate.get('additive') is not None else ''
    
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


def draw_positions_and_spots(window, margin_left, margin_top, 
                           cell_width, cell_height, num_strains):
    plate = window.plates[CURRENTPLATEINDEX]                  
    current_x = margin_left
    for position_idx in range(num_strains):
        start_col, end_col = window.plate_layout['strain_positions'][position_idx]
        position_width = (end_col - start_col + 1) * cell_width
        
        # Find assigned strain from the current plate's assignments
        assigned_strain = None
        for pos_key in plate.get('assignments', {}):
            row, col = map(int, pos_key.split('-'))
            if start_col <= col <= end_col:
                assigned_strain = plate['assignments'][pos_key]
                break
        
        if window.current_mode =='A':
            # Draw position label
            label_text = assigned_strain if assigned_strain else f"Position {window.position_labels[position_idx]}"
            window.plate_canvas.create_text(
                current_x + position_width/2,
                margin_top,
                text=label_text,
                font=(FONT, 16, 'bold'),
                fill=LIGHT
            )

        
        current_x += position_width
        if window.layout_data['gap_between_strains'] and position_idx < num_strains - 1:
            current_x += cell_width


def create_plate_info(window, plate, rows, cols, unordered_quantifications,
                      strains, column_indexes):
    # Create preview image
    preview_image = create_plate_preview_image(window, plate)
    
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
        'removed_positions': list(window.plate_layout['removed_positions']),
        'layout': {
            'rows': rows,
            'columns': cols,
            'x_dilution': window.layout_data['x_dilution'],
            'y_dilution': window.layout_data['y_dilution'],
            'gap_between_strains': window.layout_data['gap_between_strains'],
            'IMGPreview': preview_image  # Store the base64 encoded image
        }
    }
    
def create_plate_preview_image(window, plate, width=1600, height=1200):
    """
    Creates a preview image for a single plate and returns it as a base64 string.
    Uses PIL for direct drawing instead of taking screenshots.
    """
    import io
    import base64
    from PIL import Image, ImageDraw, ImageFont
    
    # Create new image with white background
    margin = 20
    img_width = width - 40
    img_height = height - 60
    image = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Calculate dimensions
    grid_width = img_width - 2 * margin
    grid_height = img_height - 2 * margin
    
    cols_per_strain = window.layout_data['columns'] // window.layout_data['strains']
    total_gaps = window.layout_data['strains'] - 1 if window.layout_data['gap_between_strains'] else 0
    total_width = window.layout_data['columns'] + total_gaps
    cell_width = grid_width / total_width
    cell_height = grid_height / window.layout_data['rows']
    
    # Try to load fonts (fallback to default if not available)
    try:
        # Try to load Helvetica Bold
        label_font = ImageFont.truetype("arial.ttf", 45)
        strain_font = ImageFont.truetype("arial.ttf", 45)
    except IOError:
        try:
            # Fallback to default font if Helvetica-Bold is not found
            label_font = ImageFont.load_default()
            strain_font = ImageFont.load_default()
            print("Helvetica Bold not found, using default font")
        except:
            print("Failed to load default font")
    
    # Draw strain sections and labels
    current_x = margin
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
        
        # Draw strain label if assigned
        if assigned_strain:
            text_width = draw.textlength(assigned_strain, font=strain_font)
            draw.text(
                (current_x + position_width/2 - text_width/2, margin),
                assigned_strain,
                font=strain_font,
                fill='black'
            )
        
        # Draw spots
        for col_offset in range(end_col - start_col + 1):
            col = start_col + col_offset
            x_pos = int(current_x + col_offset * cell_width + cell_width/2)
            
            for row in range(window.layout_data['rows']):
                pos_key = f"{row}-{col}"
                if pos_key not in window.plate_layout['removed_positions']:
                    y_pos = int(margin + row * cell_height + cell_height/2)
                    
                    # Determine spot color
                    spot_color = GRAY1  # Your default gray color
                    if pos_key in plate['assignments']:
                        strain = plate['assignments'][pos_key]
                        strain_index = window.strains.index(strain)
                        spot_color = window.strain_colors[strain_index]
                    
                    # Draw spot (circle)
                    size = 16
                    draw.ellipse(
                        [x_pos-size, y_pos-size, x_pos+size, y_pos+size],
                        fill=spot_color,
                        outline=spot_color
                    )
        
        # Update x position for next group
        current_x += position_width
        
        # Add gap after each position except the last one
        if window.layout_data['gap_between_strains'] and position_idx < window.layout_data['strains'] - 1:
            current_x += cell_width
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

def preview_all_plates(window):
    if not window.plates:
        messagebox.showinfo("Info", "No plates to preview")
        return
    
    preview_window = tk.Toplevel(window)
    preview_window.title("SpotPlotter: All Plates Preview")
    preview_window.geometry("1200x800")
    
    BASE_PATH = Path(__file__).parent

    # Construct the path to the icon file
    icon_path = BASE_PATH / "Icons" / "ICON.ico"

    # Set the window icon
    preview_window.iconbitmap(icon_path)

    main_frame = tk.Frame(preview_window, bg=DARK)
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
    plate_width = 400
    plate_height = 300
    margin = 20

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

def draw_plate_preview(window, canvas, plate):
    # Calculate cell dimensions
    canvas_width = canvas.winfo_reqwidth()
    canvas_height = canvas.winfo_reqheight()
   
    margin = 20
    grid_width = canvas_width - 2 * margin
    grid_height = canvas_height - 2 * margin
   
    # Calculate dimensions considering gaps
    cols_per_strain = window.layout_data['columns'] // window.layout_data['strains']
    total_gaps = window.layout_data['strains'] - 1 if window.layout_data['gap_between_strains'] else 0
    total_width = window.layout_data['columns'] + total_gaps
    cell_width = grid_width / total_width
    cell_height = grid_height / window.layout_data['rows']
    # Draw strain sections and labels
    current_x = margin
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
       
        if window.current_mode =='A':
            # Draw position label
            position_label = f"Position {window.position_labels[position_idx]}"
            canvas.create_text(
                current_x + position_width/2,
                margin,
                text=position_label,
                font=(FONT, 12, 'bold'),
                fill=DARK,
                anchor='s',


            )
       
        # # Draw strain label if assigned - moved higher up
        # if assigned_strain:
        #     canvas.create_text(
        #         current_x + position_width/2,
        #         margin - 5,  # Moved higher, above the spot area
        #         text=assigned_strain,
        #         font=(FONT, 9),
        #         fill=DARK,
        #         anchor='s'  # Changed to 's' (south) to align bottom of text with this point
        #     )
       
        # Draw spots
        for col_offset in range(end_col - start_col + 1):
            col = start_col + col_offset
            x_pos = current_x + col_offset * cell_width + cell_width/2
           
            for row in range(window.layout_data['rows']):
                pos_key = f"{row}-{col}"
                if pos_key not in window.plate_layout['removed_positions']:
                    y_pos = margin + row * cell_height + cell_height/2
                   
                    # Determine spot color based on strain assignment
                    spot_color = GRAY1
                    if pos_key in plate['assignments']:
                        strain = plate['assignments'][pos_key]
                        strain_index = window.strains.index(strain)
                        spot_color = window.strain_colors[strain_index]
                   
                    # Draw spot
                    canvas.create_oval(
                        x_pos-8, y_pos-8, x_pos+8, y_pos+8,
                        fill=spot_color,
                        outline=spot_color
                    )
       
        # Update x position for next group
        current_x += position_width
       
        # Add gap after each position except the last one
        if window.layout_data['gap_between_strains'] and position_idx < window.layout_data['strains'] - 1:
            current_x += cell_width



def prev_plate(window):
    global CURRENTPLATEINDEX
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
           
            strain = None
            for col in range(start_col, end_col + 1):
                test_key = f"0-{col}"
                if test_key in plate_assignments:
                    strain = plate_assignments[test_key]
                    break
           
            if strain:
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

def load_from_file(filename):
    """
    Load plate data from a JSON file
    Returns: List of plate info loaded from file
    """
    try:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
            
        with open(filename, 'r') as f:
            data = json.load(f)
            print(f"Data loaded successfully from {filename}")
            return data
            
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        raise

def get_available_data_files():
    """
    Get list of available plate data files in current directory
    Returns: List of filenames matching the plate data pattern
    """
    files = [f for f in os.listdir('.') if f.startswith('plate_data_') and f.endswith('.json')]
    return sorted(files, reverse=True)


def create_plate_controls(window):
    # Main controls container at the top
    controls_container = tk.Frame(window.control_frame, bg=DARK)
    controls_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    
    # "Add a plate" header
    plate_header = tk.Label(
        controls_container, 
        text="Add a Plate", 
        font=(FONT, 14, 'bold'), 
        fg=LIGHT, 
        bg=DARK
    )
    plate_header.pack(pady=(0, 10))

    # Plate name entry frame

    # Additive controls
    window.additive_var = tk.BooleanVar(value=False)
    additive_frame = tk.Frame(controls_container, bg=DARK)
    additive_frame.pack(fill=tk.X, pady=(0, 10))
    
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

    name_frame = tk.Frame(controls_container, bg=DARK)
    name_frame.pack(fill=tk.X, pady=(0, 10))
    
    window.plate_entry = RoundedEntry(
        name_frame,
        width=200,
        height=35
    )
    window.plate_entry.pack(side=tk.LEFT, expand=True, padx=(0, 5))
    
    add_plate_btn = tk.Button(
        name_frame,
        text="+",
        command=lambda: add_plate(window),
        font=(FONT, 12, 'bold'),
        bg=LIGHT,
        fg=DARK,
        width=3,
        height=1,
        relief="flat",
        bd=0
    )
    add_plate_btn.pack(side=tk.RIGHT)

    

    # Plate management buttons
    buttons_frame = tk.Frame(controls_container, bg=DARK)
    buttons_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Create a consistent button style
    def create_control_button(parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT, 11),
            bg=LIGHT,
            fg=DARK,
            relief="flat",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
    
    delete_btn = create_control_button(
        buttons_frame,
        "Delete",
        lambda: delete_current_plate(window)
    )
    delete_btn.pack(side=tk.LEFT, expand=True, padx=2)
    
    clear_btn = create_control_button(
        buttons_frame,
        "Clear",
        lambda: clear_current_plate(window)
    )
    clear_btn.pack(side=tk.LEFT, expand=True, padx=2)
    
    rename_btn = create_control_button(
        buttons_frame,
        "Rename",
        lambda: rename_current_plate(window)
    )
    rename_btn.pack(side=tk.LEFT, expand=True, padx=2)

def toggle_additive_entry(window):
    if window.additive_var.get():
        window.additive_entry.entry.config(state=tk.NORMAL)
    else:
        window.additive_entry.entry.config(state=tk.DISABLED)
        window.additive_entry.entry.delete(0, tk.END)

def create_navigation_controls(window):
    # Navigation controls at the bottom
    nav_container = tk.Frame(window.control_frame, bg=DARK)
    nav_container.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    
    def create_nav_button(parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT, 11),
            bg=LIGHT,
            fg=DARK,
            relief="flat",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
    
    # Navigation buttons
    nav_frame = tk.Frame(nav_container, bg=DARK)
    nav_frame.pack(fill=tk.X, pady=(0, 10))
    
    prev_plate_btn = create_nav_button(
        nav_frame,
        "Previous Plate",
        lambda: prev_plate(window)
    )
    prev_plate_btn.pack(side=tk.LEFT, expand=True, padx=2)
    
    next_plate_btn = create_nav_button(
        nav_frame,
        "Next Plate",
        lambda: next_plate(window)
    )
    next_plate_btn.pack(side=tk.LEFT, expand=True, padx=2)
    
    # Action buttons
    action_frame = tk.Frame(nav_container, bg=DARK)
    action_frame.pack(fill=tk.X)
    
    preview_btn = create_nav_button(
        action_frame,
        "Preview All Plates",
        lambda: preview_all_plates(window)
    )
    preview_btn.pack(side=tk.LEFT, expand=True, padx=2)
    


def setup_frames(window):
    # Main frames
    window.plate_frame = tk.Frame(window, bg=DARK)
    window.plate_frame.place(x=27, y=178, width=1070, height=638)
    
    window.control_frame = tk.Frame(window, bg=DARK)
    window.control_frame.place(x=1130, y=178, width=282, height=638)
    
    # Create three subframes within the control frame
    window.plate_controls_frame = tk.Frame(window.control_frame, bg=DARK)
    window.plate_controls_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    
    # window.strains_frame = tk.Frame(window.control_frame, bg=DARK)
    # window.strains_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    
    # # Create a frame for strain input and list
    # window.strain_input_frame = tk.Frame(window.strains_frame, bg=DARK)
    # window.strain_input_frame.pack(fill=tk.X, pady=(0, 10))
    
    # # Strain input elements
    # strain_label = tk.Label(
    #     window.strain_input_frame, 
    #     text="Add Strain", 
    #     font=(FONT, 14, 'bold'), 
    #     fg=LIGHT, 
    #     bg=DARK
    # )
    # strain_label.pack(pady=(0, 10))
    
    # strain_entry_frame = tk.Frame(window.strain_input_frame, bg=DARK)
    # strain_entry_frame.pack(fill=tk.X)
    
    # window.strain_entry = RoundedEntry(
    #     strain_entry_frame,
    #     width=200,
    #     height=35
    # )
    # window.strain_entry.pack(side=tk.LEFT, expand=True, padx=(0, 5))
    
    # # add_strain_btn = tk.Button(
    # #     strain_entry_frame,
    # #     text="+",
    # #     command=lambda: add_strain(window),
    # #     font=(FONT, 12, 'bold'),
    # #     bg=LIGHT,
    # #     fg=DARK,
    # #     width=3,
    # #     height=1,
    # #     relief="flat",
    # #     bd=0
    # # )
    # # add_strain_btn.pack(side=tk.RIGHT)
    
    # # Frame for strain list (where strains will be added)
    # window.strain_list_frame = tk.Frame(window.strains_frame, bg=DARK)
    # window.strain_list_frame.pack(fill=tk.X, padx=10, pady=(5, 20))
    
    window.bottom_frame = tk.Frame(window.control_frame, bg=DARK)
    window.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    
    # Populate the frames
    create_plate_controls(window)
    create_strain_controls(window)  # You'll need to define this function
    create_navigation_controls(window)
    create_plate_canvas(window)

class RoundedEntry(tk.Frame):
    def __init__(self, parent, width=100, height=35, corner_radius=10, **kwargs):
        super().__init__(parent, bg=DARK)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create rounded canvas background
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=DARK,
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0)
        
        # Draw rounded rectangle
        self.canvas.create_rounded_rectangle = lambda x1, y1, x2, y2, r, **kwargs: self.canvas.create_polygon(
            x1+r, y1,
            x1+r, y1,
            x2-r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1,
            smooth=True,
            **kwargs
        )
        
        bg_box = self.canvas.create_rounded_rectangle(
            2, 2, width-2, height-2,
            corner_radius,
            fill="white",
            outline="#cccccc"
        )
        
        self.entry = tk.Entry(
            self,
            bg="white",
            fg=DARK,  # Ensure the text color is dark
            bd=0,
            highlightthickness=0,
            **kwargs
        )
        self.entry.place(
            x=10,
            y=height//2,
            width=width-20,
            anchor="w"
        )

    # Add these delegate methods
    def get(self):
        """Delegate get() to the internal entry widget"""
        return self.entry.get()
    
    def delete(self, first, last=None):
        """Delegate delete() to the internal entry widget"""
        return self.entry.delete(first, last)
    
    def insert(self, index, string):
        """Delegate insert() to the internal entry widget"""
        return self.entry.insert(index, string)


class RoundedCheckbox(tk.Canvas):
    def __init__(self, parent, text="", command=None, variable=None, **kwargs):
        super().__init__(
            parent,
            width=24,
            height=24,
            highlightthickness=0,
            bg=DARK,
            **kwargs
        )
        self.variable = variable
        self.command = command
        
        # Create the rounded rectangle for the checkbox
        self.box = self.create_rounded_rectangle(
            2, 2, 22, 22,
            5,  # corner radius
            outline="#cccccc",
            fill="white",
            width=2
        )
        
        # Create the checkmark (hidden initially)
        self.checkmark = self.create_line(
            6, 12, 10, 16, 18, 8,
            fill=DARK,
            width=3,
            state="hidden"
        )
        
        # Bind click event
        self.bind("<Button-1>", self.toggle)
        
        # Create label
        self.label = Label(
            parent,
            text=text,
            bg=DARK,
            fg=LIGHT,
            font=(FONT, 12)
        )
        
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def toggle(self, event=None):
        if self.variable:
            self.variable.set(not self.variable.get())
            self.update_state()
            if self.command:
                self.command()
    
    def update_state(self):
        if self.variable and self.variable.get():
            self.itemconfigure(self.checkmark, state="normal")
        else:
            self.itemconfigure(self.checkmark, state="hidden")

def create_plate_designer(window, mode="A"):
    # Clear window
    for widget in window.winfo_children():
        widget.destroy()
    
    # Initialize plate layout attributes with defaults
    window.plate_layout = {
        'rows': tk.IntVar(value=8),
        'columns': tk.IntVar(value=12),
        'strains': tk.IntVar(value=1 if mode == "B" else 3),
        'x_dilution': tk.IntVar(value=-1 if mode == "B" else 10),
        'y_dilution': tk.IntVar(value=-1 if mode == "B" else 2),
        'gap_between_strains': tk.BooleanVar(value=False),
        'removed_positions': set(),
        'strain_positions': {}
    }
    
    # Store the current mode
    window.current_mode = mode
    
    # Create canvas for layout
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
    
    # Add background images and frames

    image_image_1 = PhotoImage("Icons/image_1.png")
    canvas.image_image_1 = image_image_1  # Keeping a reference to prevent garbage collection
    image_1 = canvas.create_image(719.0, 57.0, image=image_image_1)
    round_rectangle(canvas, 17.0, 168.0, 1100.0, 826.0, fill=DARK, outline="")
    round_rectangle(canvas, 1120.0, 168.0, 1422.0, 826.0, fill=DARK, outline="")
    
    # Create frames for plate and controls
    plate_frame = Frame(window, bg=DARK)
    plate_frame.place(x=27, y=178, width=1070, height=638)
    
    control_frame = Frame(window, bg=DARK)
    control_frame.place(x=1130, y=178, width=282, height=638)
    
    # Create mode switcher and controls
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

    image_path_10 = ("Icons/image_10.png")
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
        x=855.0,
        y=670.0, )


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
    y=670.0)    

    create_rounded_button(
    canvas=canvas,
    text="Upload MetaData",
    command=lambda: upload_metadata_handler(window),
    x=620.0,
    y=670.0)

    if hasattr(window, 'window.plates'):
        print("works")

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

    image_path_10 = "Icons/image_10.png"
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
    processResults(window)
    #this will only display once the results are generated
    create_rounded_button(
        canvas=canvas,
        text="Finish",
        command=lambda: window.quit(),#will exit the program
        x=720 - (200 // 2),  
        y=buttonPosY-100,
        button_tag="Finish"
    )

def create_plate_designer(window, mode="A"):
    # Clear window
    for widget in window.winfo_children():
        widget.destroy()
    
    # Initialize plate layout attributes with defaults
    window.plate_layout = {
        'rows': tk.IntVar(value=8),
        'columns': tk.IntVar(value=12),
        'strains': tk.IntVar(value=1 if mode == "B" else 3),
        'x_dilution': tk.IntVar(value=-1 if mode == "B" else 10),
        'y_dilution': tk.IntVar(value=-1 if mode == "B" else 2),
        'gap_between_strains': tk.BooleanVar(value=False),
        'removed_positions': set(),
        'strain_positions': {}
    }
    
    # Store the current mode
    window.current_mode = mode
    
    # Create canvas for layout
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
    
    # Add background images and frames
    image_image_1 = PhotoImage(file=("Icons/image_1.png"))
    canvas.image_image_1 = image_image_1  # Keeping a reference to prevent garbage collection
    image_1 = canvas.create_image(719.0, 57.0, image=image_image_1)
    round_rectangle(canvas, 17.0, 168.0, 1100.0, 826.0, fill=DARK, outline="")
    round_rectangle(canvas, 1120.0, 168.0, 1422.0, 826.0, fill=DARK, outline="")
    
    # Create frames for plate and controls
    plate_frame = Frame(window, bg=DARK)
    plate_frame.place(x=27, y=178, width=1070, height=638)
    
    control_frame = Frame(window, bg=DARK)
    control_frame.place(x=1130, y=178, width=282, height=638)
    
    # Create mode switcher and controls
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
        text="Back",
        command=lambda: create_titleFrame(window),
        x=17.0,
        y=buttonPosY
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
    file=("Icons/image_1.png"))
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


    canvas.create_text(
        720,  
        750.0,
        text="Loading Image Please wait",
        fill=DARK,
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
        # print(f"Debug: CURRENT INDEX {window.current_image_index}")
        # print(f"Debug: Current image info: {window.current_info}")
        # print(f"Debug: 345434 ALL INFO : {window.image_info}" )
    else:   
        gray_image = window.gray_image  
        columns = window.all_plate_info[window.current_image_index]['layout']['columns']
        rows = window.all_plate_info[window.current_image_index]['layout']['rows']
        result_grid, marked_image = detect_and_draw_circles(window.binarized_image, gray_image, False,columns = columns, rows = rows )
        window.all_plate_info[window.current_image_index]['unorderedquantifications'] = result_grid

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
    spacing = 150

    # Threshold Slider
    threshold_label = Label(control_frame, text="Threshold", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    threshold_label.place(x=16, y=y_offset)
    create_circular_slider(
        control_frame, 
        min_val=0, 
        max_val=40,
        position=(16, y_offset + 30),
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
        min_val=51, 
        max_val=1001,
        position=(16, y_offset + spacing * 2 + 30),
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
           
            strain = None
            for col in range(start_col, end_col + 1):
                test_key = f"0-{col}"
                if test_key in plate_assignments:
                    strain = plate_assignments[test_key]
                    break
           
            if strain:
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








    # Vertical positioning base
    

    # Toggle section
    canvas.create_text(
        1391.0,
        base_y - 15,
        text="Toggle",
        fill=LIGHT,
        font=(FONT, 14 * -1, 'bold')
    )
    toggle = ("Icons/toggle.png")
    img_toggle = Image.open(toggle)
    img_toggle_resized = img_toggle.resize((img_toggle.width // 11, img_toggle.height // 11), Image.LANCZOS)
    image_toggle = ImageTk.PhotoImage(img_toggle_resized)
    window.edit_images.append(image_toggle)
    toggle_button = Button(
        window,
        image=image_toggle,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: toggle_image(window),
        relief="flat",
        bg=DARK
    )
    toggle_button.place(x=1376.0, y=base_y)

    # Zoom section
    canvas.create_text(
        1391.0,
        base_y + 39+heading_y,
        text="Zoom",
        fill=LIGHT,
        font=(FONT, 14 * -1, 'bold')
    )

    # Zoom in button
    zoomin = ("Icons/zoomin.png")
    img_zoomin = Image.open(zoomin)
    img_zoomin_resized = img_zoomin.resize((img_zoomin.width // 11, img_zoomin.height // 11), Image.LANCZOS)
    image_zoomin_2 = ImageTk.PhotoImage(img_zoomin_resized)
    window.edit_images.append(image_zoomin_2)
    button_zoomin = Button(
        window,
        image=image_zoomin_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: adjust_zoom(window, 1.2),
        bg=DARK
    )
    button_zoomin.place(x=1377.0, y=base_y + 78)

    # Zoom out button
    zoomout = ("Icons/zoomout.png")
    img_zoomout = Image.open(zoomout)
    img_zoomout_resized = img_zoomout.resize((img_zoomout.width // 11, img_zoomout.height // 11), Image.LANCZOS)
    image_zoomout_2 = ImageTk.PhotoImage(img_zoomout_resized)
    window.edit_images.append(image_zoomout_2)
    button_zoomout = Button(
        window,
        image=image_zoomout_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: adjust_zoom(window, 0.8),
        bg=DARK
    )
    button_zoomout.place(x=1377.0, y=base_y + 117)

    # History section (Undo and Redo)
    canvas.create_text(
        1391.0,
        base_y + 156+heading_y,
        text="History",
        fill=LIGHT,
        font=(FONT, 14 * -1, 'bold')
    )

    # Undo button (image_8)
    image_path_8 = ("Icons/image_8.png")
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
        bg=DARK
    )
    undo_button.place(x=1376.0, y=base_y + 195)

    # Redo button (image_7)
    image_path_7 = ("Icons/image_7.png")
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
        bg=DARK
    )
    redo_button.place(x=1376.0, y=base_y + 234)

    # "Add" text 
    canvas.create_text(
        1391.0,
        base_y + 273+ heading_y,
        text="Add",
        fill=LIGHT,
        font=(FONT, 14 * -1, 'bold')
    )

    # Thin pen (image_2)
    image_path_2 = ("Icons/image_2.png")
    img_thinPen = Image.open(image_path_2) 
    img_thinPen_resized = img_thinPen.resize((img_thinPen.width // 11, img_thinPen.height // 11), Image.LANCZOS)
    image_image_2 = ImageTk.PhotoImage(img_thinPen_resized)
    window.edit_images.append(image_image_2)
    button_thin_pen = Button(
        window,
        image=image_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: set_mode(window, "thin_brush"),
        bg=DARK
    )
    button_thin_pen.place(x=1377.0, y=base_y + 312)

    # Big pen (image_5)
    image_path_5 = ("Icons/image_5.png")
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
        bg=DARK
    )
    big_pen_button.place(x=1377.0, y=base_y + 351)

    # "Delete" text
    canvas.create_text(
        1391.0,
        base_y + 390 + heading_y ,
        text="Delete",
        fill=LIGHT,
        font=(FONT, 14 * -1, 'bold')
    )

    # Flood eraser (image_6)
    image_path_6 = ("Icons/image_6.png")
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
        bg=DARK
    )
    flood_eraser_button.place(x=1376.0, y=base_y + 429)

    # Thin eraser (image_9)
    image_path_9 =("Icons/image_9.png")
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
        bg=DARK
    )
    thin_eraser_button.place(x=1376.0, y=base_y + 468)



 #big eraser
    image_image_4 = PhotoImage(file=("Icons/image_4.png"))
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
    big_eraser_button.place(x=1377.0, y=base_y + 468+39)




    window.undo_button = undo_button
    window.redo_button = redo_button

    total_width = 1295 - 34
    total_height = 783 - 203
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

    yposFrames= 207
    # Position the frames
    left_frame.place(x=30, y=yposFrames, width=img_width + 20, height=img_height + 20)
    right_frame.place(x=690, y=yposFrames, width=img_width + 20, height=img_height + 20)

    # Initialize zoom level
    window.zoom_level = 1.0
    
    # Set up zoom controls and bindings
    setup_zoom_controls(window)


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
    file=("Icons/image_1.png"))
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
    file=("Icons/image_1.png"))
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

def upload_images(window):
    """
    Allow the user to upload image files, but only those that match filenames in window.all_plate_info.
    """
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
   
    # Ensure file_paths are selected and window.all_plate_info is initialized
    if file_paths and hasattr(window, 'all_plate_info'):
        window.image_paths = []
        unmatched_filenames = []  # Collect unmatched filenames
        print("Does have attribute")
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
        # save_window_state(window, 'window_state_singleDilutionRepeatsEcoliNotOverwrite.pkl')
        # print("saved")
        # # 
        display_results(window)
        


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

def processResults(window):
    # Open a directory selection dialog
    output_directory = filedialog.askdirectory(title="Choose Output Directory")
    
    if not output_directory:
        print("Export canceled by the user.")
        return
    
    # Ask user for project/folder name
    project_name = simpledialog.askstring("Project Name", "Enter a name for your project:")
    
    if not project_name:
        print("Project name is required.")
        return
    
    # Create project folder
    project_folder = os.path.join(output_directory, project_name)
    os.makedirs(project_folder, exist_ok=True)
    
    # Define full file paths
    pdf_path = os.path.join(project_folder, f"{project_name}_report.pdf")
    excel_path = os.path.join(project_folder, f"{project_name}_data.xlsx")
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
        generate_pdf_report_MODEA(window.all_plate_info, all_strain_data, pdf_path)
        
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
            version="1.0.0"
        )
        df = export_plate_data_to_excel(window.all_plate_info, excel_path)
    
    print(f"Files saved in: {project_folder}")

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








##     ##  #######  ########  ########  ######  
###   ### ##     ## ##     ## ##       ##    ## 
#### #### ##     ## ##     ## ##       ##       
## ### ## ##     ## ##     ## ######    ######  
##     ## ##     ## ##     ## ##             ## s
##     ## ##     ## ##     ## ##       ##    ## 
##     ##  #######  ########  ########  ###### 



def set_mode(window, mode):
    window.mode = mode
    if mode == "small_brush" or mode == "small_eraser":
        window.brush_size = 40
    elif mode == "large_brush" or mode == "large_eraser":
        window.brush_size = 120

def toggle_image(window):
    window.show_original = not window.show_original
    display_images(window)


def setup_zoom_controls(window):
    """Set up zoom controls and initialize zoom-related variables"""
    window.zoom_level = 1.0
    window.zoom_min = 0.5
    window.zoom_max = 5.0
    
    # Create zoom frame
    zoom_frame = Frame(window, bg=DARK)
    zoom_frame.place(x=1376, y=300)
    

    
 # Zoom in button
    zoomin = ("Icons/zoomin.png")
    img_zoomin = Image.open(zoomin)
    img_zoomin_resized = img_zoomin.resize((img_zoomin.width // 11, img_zoomin.height // 11), Image.LANCZOS)
    image_zoomin_2 = ImageTk.PhotoImage(img_zoomin_resized)
    window.edit_images.append(image_zoomin_2)
    button_zoomin = Button(
        window,
        image=image_zoomin_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: adjust_zoom(window, 1.2),
        bg=DARK
    )
    button_zoomin.place(x=1377.0, y=base_y + 78)

    # Zoom out button
    zoomout = ("Icons/zoomout.png")
    img_zoomout = Image.open(zoomout)
    img_zoomout_resized = img_zoomout.resize((img_zoomout.width // 11, img_zoomout.height // 11), Image.LANCZOS)
    image_zoomout_2 = ImageTk.PhotoImage(img_zoomout_resized)
    window.edit_images.append(image_zoomout_2)
    button_zoomout = Button(
        window,
        image=image_zoomout_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: adjust_zoom(window, 0.8),
        bg=DARK
    )
    button_zoomout.place(x=1377.0, y=base_y + 117)











    

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
            cv2.drawContours(contour_img, contours, -1, (0, 0, 255), 3)

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


# #creating the frame with title and icon
window = Tk()
window.geometry("1440x1000")
window.configure(bg=LIGHT)
window.title("SpotPlotter")
BASE_PATH = Path(__file__).parent

# Construct the path to the icon file
icon_path = BASE_PATH / "Icons" / "ICON.ico"

# Set the window icon
window.iconbitmap(icon_path)
initialize_window_attributes(window)
title_frame_widgets = create_titleFrame(window)

window.resizable(True, True)
window.mainloop()

# restore_window_state(window, 'window_state_singleDilutionRepeatsEcoli.pkl')


# process_split_order_quantifications(window)
# strain_data, dilution_series = generate_data_series(window)
# # df, fig = analyze_plate_data(strain_data)
# print(df)
# plt.show()
# processResults(window)







#Different saved states:

#window_state.pkl   - real test its testing these images where https://www.dropbox.com/scl/fo/55v2k6p7hfb4hws18diod/AK-1lWdCixipX0rCeqPYjYc?rlkey=4uou81nqbu13wig1f8vwbx4ie&e=1&st=4vqqji7x&dl=0 
#1 additive and 4 repeats for each

#'window_state_multipulAdditives.pkl   4 attitives with 2 repeats for each

#window_state_IntermediaryImages.pkl checking to see if the binary images and preview are saving correctyl
#window_state_Test_Positions.pkl testing the postitions are correct













