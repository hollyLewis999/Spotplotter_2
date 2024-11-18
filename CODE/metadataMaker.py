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


from Processing import *
from outputs import *






# d8888b. db       .d8b.  d888888b d88888b .d8888. 
# 88  `8D 88      d8' `8b `~~88~~' 88'     88'  YP 
# 88oodD' 88      88ooo88    88    88ooooo `8bo.   
# 88~~~   88      88~~~88    88    88~~~~~   `Y8b. 
# 88      88booo. 88   88    88    88.     db   8D 
# 88      Y88888P YP   YP    YP    Y88888P `8888Y' 



def create_plate_designer(window):
    # Clear window
    for widget in window.winfo_children():
        widget.destroy()
        
    # Initialize window properties
    window.title("Plate Layout Designer")
    window.geometry("1440x1024")
    window.configure(bg=LIGHT)
    
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

    
    
    # Main dark rectangles
    round_rectangle(canvas, 17.0, 168.0, 1100.0, 826.0, fill=DARK, outline="")
    round_rectangle(canvas, 1120.0, 168.0, 1422.0, 826.0, fill=DARK, outline="")
    
    # Create frames
    plate_frame = Frame(window, bg=DARK)
    plate_frame.place(x=27, y=178, width=1070, height=638)
    
    control_frame = Frame(window, bg=DARK)
    control_frame.place(x=1130, y=178, width=282, height=638)
    image_path_10 = relative_to_assets("image_10.png")
    img_logobig = Image.open(image_path_10)
    img_logobig_resized = img_logobig.resize((img_logobig.width // 2, img_logobig.height //2), Image.LANCZOS)
    create_controls(control_frame, window)
    create_plate_display(plate_frame, window)

def create_controls(control_frame, window):
    y_offset = 20
    spacing = 80
    
    # Row input
    row_label = Label(control_frame, text="Rows", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    row_label.place(x=20, y=y_offset)
    row_entry = ttk.Entry(control_frame, textvariable=window.plate_layout['rows'], width=10)
    row_entry.place(x=20, y=y_offset + 30)
    
    # Column input
    col_label = Label(control_frame, text="Columns", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    col_label.place(x=20, y=y_offset + spacing)
    col_entry = ttk.Entry(control_frame, textvariable=window.plate_layout['columns'], width=10)
    col_entry.place(x=20, y=y_offset + spacing + 30)
    
    # Strains input
    strain_label = Label(control_frame, text="Strains", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    strain_label.place(x=20, y=y_offset + spacing * 2)
    strain_entry = ttk.Entry(control_frame, textvariable=window.plate_layout['strains'], width=10)
    strain_entry.place(x=20, y=y_offset + spacing * 2 + 30)
    
    # X Dilution input
    x_dil_label = Label(control_frame, text="X-Dilution", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    x_dil_label.place(x=20, y=y_offset + spacing * 3)
    x_dil_entry = ttk.Entry(control_frame, textvariable=window.plate_layout['x_dilution'], width=10)
    x_dil_entry.place(x=20, y=y_offset + spacing * 3 + 30)
    
    # Y Dilution input
    y_dil_label = Label(control_frame, text="Y-Dilution", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    y_dil_label.place(x=20, y=y_offset + spacing * 4)
    y_dil_entry = ttk.Entry(control_frame, textvariable=window.plate_layout['y_dilution'], width=10)
    y_dil_entry.place(x=20, y=y_offset + spacing * 4 + 30)
    
    # Gap checkbox
    gap_check = Checkbutton(
        control_frame,
        text="Gap Between Strains",
        variable=window.plate_layout['gap_between_strains'],
        bg=DARK,
        fg=LIGHT,
        selectcolor=DARK,
        font=(FONT, 12),
        command=lambda: update_plate_display(window)
    )
    gap_check.place(x=20, y=y_offset + spacing * 5)
    
    # Next screen button
    next_button = tk.Button(
        control_frame,
        text="Next",
        command=lambda: go_to_assignment_screen(window),
        font=(FONT, 12),
        bg=LIGHT,
        fg=DARK
    )
    next_button.place(x=20, y=y_offset + spacing * 6)
    
    # Bind all variables to update function
    for var_name in ['rows', 'columns', 'strains', 'x_dilution', 'y_dilution']:
        window.plate_layout[var_name].trace_add("write", lambda *args: update_plate_display_layout_designer(window))

def create_plate_display(plate_frame, window):
    window.plate_canvas = Canvas(
        plate_frame,
        bg=DARK,
        highlightthickness=0
    )
    window.plate_canvas.pack(expand=True, fill='both')
    window.plate_canvas.bind("<Button-1>", lambda event: handle_click(event, window))
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
    
    draw_dilution_labels(window, rows, y_dil, margin, cell_height)
    draw_spots(window, strains, margin, cell_width, cell_height, x_dil, rows)

def draw_dilution_labels(window, rows, y_dil, margin, cell_height):
    for row in range(rows):
        y_value = y_dil ** row
        window.plate_canvas.create_text(
            margin - 20,
            margin + row * cell_height + cell_height/2,
            text=y_value,
            fill=LIGHT,
            font=(FONT, 8)
        )

def draw_spots(window, strains, margin, cell_width, cell_height, x_dil, rows):
    for strain in range(strains):
        start_col, end_col = window.plate_layout['strain_positions'][strain]
        for col_offset in range(end_col - start_col + 1):
            actual_col = start_col + col_offset
            x_value = x_dil ** col_offset
            x_pos = margin + actual_col * cell_width + cell_width/2
            
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

def handle_click(event, window):
    closest = window.plate_canvas.find_closest(event.x, event.y)
    tags = window.plate_canvas.gettags(closest)
    
    if tags and len(tags) > 1:
        pos_key = tags[0]
        if pos_key in window.plate_layout['removed_positions']:
            window.plate_layout['removed_positions'].remove(pos_key)
        else:
            window.plate_layout['removed_positions'].add(pos_key)
        update_plate_display_layout_designer(window)

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

def draw_plate(window, canvas, plate, margin_left, margin_top, grid_width, grid_height):
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
            margin_top - 10,
            text=label_text,
            font=(FONT, 10, 'bold'),
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

                    # Add strain label if assigned
                    if pos_key in plate['assignments']:
                        canvas.create_text(
                            x_pos, y_pos-12,
                            text=plate['assignments'][pos_key],
                            font=(FONT, 6),
                            fill=DARK
                        )

        # Update x position for next group
        current_x += position_width

        # Add gap after each position except the last one
        if window.layout_data['gap_between_strains'] and position_idx < window.layout_data['strains'] - 1:
            current_x += cell_width

def update_plate_display(window):
    window.plate_canvas.delete('all')

    width = window.plate_canvas.winfo_width()
    height = window.plate_canvas.winfo_height()
    if width <= 1 or height <= 1:
        window.plate_canvas.after(100, lambda: update_plate_display(window))
        return

    # Calculate dimensions
    margin_left = 30
    margin_right = 30
    margin_top = 70
    margin_bottom = 30

    grid_width = width - margin_left - margin_right
    grid_height = height - margin_top - margin_bottom

    # Draw the actual plate, not just a preview
    draw_plate(window, window.plate_canvas, window.plates[window.current_plate], 
               margin_left, margin_top, grid_width, grid_height)

    # Update the plate display title
    draw_plate_grid(window, width, height, margin_left, margin_right, margin_top, 
                    margin_bottom, grid_width, grid_height)

def create_strain_designer(window):
    # Clear window
    for widget in window.winfo_children():
        widget.destroy()
        #logo

        
    # # Initialize window properties
    # window.title("Plate Layout Designer")
    # window.geometry("1440x1024")
    # window.configure(bg=LIGHT)
    
    # Store all state as window attributes
    window.plates = []
    window.strains = []
    window.strain_colors = COLORS
    window.current_color_index = 0
    window.current_plate = 0
    window.strain_buttons = []
    window.position_labels = {i: chr(65 + i) for i in range(window.layout_data['strains'])}
    window.column_assignments = {}
    
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

    create_plate_controls(window)
    create_strain_controls(window)
    create_navigation_controls(window)
    create_plate_canvas(window)

def create_plate_controls(window):
    # Plate name controls
    plate_label = tk.Label(window.control_frame, text="Plate Name", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
    plate_label.pack(pady=(0, 5))

    plate_entry_frame = tk.Frame(window.control_frame, bg=DARK)
    plate_entry_frame.pack(fill=tk.X, padx=10)

    # Plate name entry
    window.plate_entry = ttk.Entry(plate_entry_frame, width=20)
    window.plate_entry.pack(side=tk.LEFT, padx=(0, 5))

    # Additive controls
    window.additive_var = tk.BooleanVar()
    additive_check = tk.Checkbutton(
        plate_entry_frame,
        text="Additive",
        variable=window.additive_var,
        bg=DARK,
        fg=LIGHT,
        selectcolor=DARK,
        font=(FONT, 10)
    )
    additive_check.pack(side=tk.LEFT, padx=(5, 5))

    window.additive_entry = ttk.Entry(plate_entry_frame, width=15, state=tk.DISABLED)
    window.additive_entry.pack(side=tk.LEFT)

    # Enable/disable additive entry based on checkbox
    def toggle_additive_entry():
        if window.additive_var.get():
            window.additive_entry.config(state=tk.NORMAL)
        else:
            window.additive_entry.config(state=tk.DISABLED)

    window.additive_var.trace_add("write", lambda *args: toggle_additive_entry())

    # Add plate button
    add_plate_btn = tk.Button(
        window.control_frame,
        text="Add Plate",
        command=lambda: add_plate(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    add_plate_btn.pack(pady=(5, 10))

def create_strain_controls(window):
    strain_frame = tk.Frame(window.control_frame, bg=DARK)
    strain_frame.pack(fill=tk.X, padx=10)

    window.strain_entry = ttk.Entry(strain_frame, width=20)
    window.strain_entry.pack(side=tk.LEFT, padx=(0, 5))

    add_strain_btn = tk.Button(
        strain_frame,
        text="Add Strain",
        command=lambda: add_strain(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    add_strain_btn.pack(side=tk.LEFT)

def create_navigation_controls(window):
    nav_frame = tk.Frame(window.bottom_frame, bg=DARK)
    nav_frame.pack(fill=tk.X, pady=5)

    prev_plate_btn = tk.Button(
        nav_frame,
        text="Previous Plate",
        command=lambda: prev_plate(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    prev_plate_btn.pack(side=tk.LEFT, padx=5)

    next_plate_btn = tk.Button(
        nav_frame,
        text="Next Plate",
        command=lambda: next_plate(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    next_plate_btn.pack(side=tk.LEFT, padx=5)

    action_frame = tk.Frame(window.bottom_frame, bg=DARK)
    action_frame.pack(fill=tk.X, pady=5)

    export_btn = tk.Button(
        action_frame,
        text="Export All",
        command=lambda: export_data(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    export_btn.pack(side=tk.LEFT, padx=5)

    preview_btn = tk.Button(
        action_frame,
        text="Preview All Plates",
        command=lambda: preview_all_plates(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    preview_btn.pack(side=tk.LEFT, padx=5)

    clear_btn = tk.Button(
        action_frame,
        text="Clear Plate",
        command=lambda: clear_current_plate(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    clear_btn.pack(side=tk.LEFT, padx=5)

def create_plate_canvas(window):
    window.plate_canvas = tk.Canvas(
        window.plate_frame,
        bg=DARK,
        highlightthickness=0
    )
    window.plate_canvas.pack(expand=True, fill='both')
    window.plate_canvas.bind("<Button-3>", lambda e: unselect_position(window, e))

def add_strain(window):
    strain = window.strain_entry.get().strip()
    if strain and strain not in window.strains:
        if len(window.strains) >= len(window.strain_colors):
            messagebox.showwarning("Warning", "Maximum number of strains reached")
            return
            
        window.strains.append(strain)
        window.strain_entry.delete(0, tk.END)

        strain_frame = tk.Frame(window.strains_frame, bg=DARK)
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

def add_plate(window):
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
        window.additive_var.set(False)
        window.additive_entry.delete(0, tk.END)
        window.current_plate = len(window.plates) - 1
        window.column_assignments = {}
        update_plate_display(window)

def unselect_position(window, event):
    if not window.plates:
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
                
        plate = window.plates[window.current_plate]
        for row_idx in range(window.layout_data['rows']):
            key = f"{row_idx}-{col}"
            if key in plate['assignments']:
                del plate['assignments'][key]
        
        update_plate_display(window)

def setup_frames(window):
    window.plate_frame = tk.Frame(window, bg=DARK)
    window.plate_frame.place(x=27, y=178, width=1070, height=638)
    
    window.control_frame = tk.Frame(window, bg=DARK)
    window.control_frame.place(x=1130, y=178, width=282, height=638)
    
    window.strains_frame = tk.Frame(window.control_frame, bg=DARK)
    window.strains_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    window.bottom_frame = tk.Frame(window.control_frame, bg=DARK)
    window.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

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
    if not window.plates:
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
    if not window.plates:
        return
        
    plate = window.plates[window.current_plate]
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
    if not window.plates:
        return
        
    plate = window.plates[window.current_plate]
    num_strains = window.layout_data['strains']

    # Draw plate header
    additive_display = f"  (Additive: {plate['additive_name']})" if plate.get('has_additive') and plate.get('additive_name') else ''
    
    # Draw plate header with corrected syntax
    window.plate_canvas.create_text(
        width // 2,
        20,
        text=f"Current Plate: {window.current_plate + 1} - {plate['name']}{additive_display}",
        fill=LIGHT,
        font=(FONT, 16, 'bold')
    )
    
    # Calculate cell dimensions
    cols_per_strain = window.layout_data['columns'] // num_strains
    total_gaps = num_strains - 1 if window.layout_data['gap_between_strains'] else 0
    total_width = window.layout_data['columns'] + total_gaps
    cell_width = grid_width / total_width
    cell_height = grid_height / window.layout_data['rows']
    
    draw_positions_and_spots(window, plate, margin_left, margin_top, 
                           cell_width, cell_height, num_strains)

def draw_positions_and_spots(window, plate, margin_left, margin_top, 
                           cell_width, cell_height, num_strains):
    current_x = margin_left
    
    for position_idx in range(num_strains):
        start_col, end_col = window.plate_layout['strain_positions'][position_idx]
        position_width = (end_col - start_col + 1) * cell_width
        
        # Find assigned strain
        assigned_strain = None
        for pos_key, assignment in window.column_assignments.items():
            pos_start, pos_end = map(int, pos_key.split('-'))
            if pos_start == start_col and pos_end == end_col:
                assigned_strain = assignment['strain']
                break
        
        draw_position_group(window, plate, current_x, margin_top, position_width,
                          position_idx, start_col, end_col, cell_width, cell_height,
                          assigned_strain)
        
        current_x += position_width
        if window.layout_data['gap_between_strains'] and position_idx < num_strains - 1:
            current_x += cell_width

def draw_position_group(window, plate, x_pos, y_pos, position_width, position_idx, 
                       start_col, end_col, cell_width, cell_height, assigned_strain):
    # Draw position label
    label_text = assigned_strain if assigned_strain else f"Position {window.position_labels[position_idx]}"
    window.plate_canvas.create_text(
        x_pos + position_width/2,
        y_pos - 35,
        text=label_text,
        font=(FONT, 10, 'bold'),
        fill=LIGHT
    )
    
    # Draw spots for this position
    for col_offset in range(end_col - start_col + 1):
        col = start_col + col_offset
        x = x_pos + col_offset * cell_width + cell_width/2
        
        for row in range(window.layout_data['rows']):
            pos_key = f"{row}-{col}"
            if pos_key not in window.layout_data['removed_positions']:
                y = y_pos + row * cell_height + cell_height/2
                
                # Determine spot color
                spot_color = "#E5E7EB"
                if assigned_strain:
                    strain_index = window.strains.index(assigned_strain)
                    spot_color = window.strain_colors[strain_index]
                
                # Draw spot
                window.plate_canvas.create_oval(
                    x-10, y-10, x+10, y+10,
                    fill=spot_color,
                    outline=spot_color,
                    tags=(pos_key, "spot")
                )
                
                # Add strain label if assigned
                if assigned_strain:
                    window.plate_canvas.create_text(
                        x, y - 12,
                        text=assigned_strain,
                        font=(FONT, 6),
                        fill=LIGHT
                    )

def create_plate_info(window, plate, rows, cols, unordered_quantifications,
                      strains, column_indexes):
    return {
        'filename': plate['name'],
        'additive': plate.get('additive', None),
        'dilutions': [],
        'unorderedquantifications': unordered_quantifications,
        'IMGcontours': None,
        'IMGbinary': None,
        'IMGgrid': None,
        'threshold': 0,
        'smallArea': 0,
        'blocksize': 0,
        'strains': strains,
        'column_indexes': [list(indexes) for indexes in column_indexes],  # Ensure column indexes are lists
        'strain_positions': window.plate_layout['strain_positions'],  # Use as-is if integers or tuples
        'removed_positions': list(window.plate_layout['removed_positions']),  # Convert sets to lists
        'layout': {
            'rows': rows,
            'columns': cols,
            'x_dilution': window.layout_data['x_dilution'],
            'y_dilution': window.layout_data['y_dilution'],
            'gap_between_strains': window.layout_data['gap_between_strains']
        }
    }

def preview_all_plates(window):
    if not window.plates:
        messagebox.showinfo("Info", "No plates to preview")
        return
    
    preview_window = tk.Toplevel(window)
    preview_window.title("All Plates Preview")
    preview_window.geometry("1200x800")

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
        
        # Safely get additive information using .get() method with default values
        has_additive = plate.get('has_additive', False)
        additive_name = plate.get('additive_name', '')
        
        # Create additive text only if both conditions are met
        additive_text = f" with {additive_name}" if has_additive and additive_name else ""
        
        header = tk.Label(
            plate_frame,
            text=f"{plate.get('name', 'Unnamed')}{additive_text}",
            font=(FONT, 12, 'bold'),
            bg=LIGHT
        )
        header.pack(pady=5)

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

    # Draw position labels and spots
    current_x = margin
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
            margin - 10,
            text=label_text,
            font=(FONT, 10, 'bold'),
            fill=DARK
        )
        
        # Draw spots
        for col_offset in range(end_col - start_col + 1):
            col = start_col + col_offset
            x_pos = current_x + col_offset * cell_width + cell_width/2
            
            for row in range(window.layout_data['rows']):
                pos_key = f"{row}-{col}"
                if pos_key not in window.plate_layout['removed_positions']:
                    y_pos = margin + row * cell_height + cell_height/2
                    
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
                        outline=spot_color
                    )
                    
                    # Add strain label if assigned
                    if pos_key in plate['assignments']:
                        canvas.create_text(
                            x_pos, y_pos-12,
                            text=plate['assignments'][pos_key],
                            font=(FONT, 6),
                            fill=DARK
                        )
        
        # Update x position for next group
        current_x += position_width
        
        # Add gap after each position except the last one
        if window.layout_data['gap_between_strains'] and position_idx < window.layout_data['strains'] - 1:
            current_x += cell_width

def prev_plate(window):
    if window.plates and window.current_plate > 0:
        window.current_plate -= 1
        window.plate_entry.delete(0, tk.END)
        window.plate_entry.insert(0, window.plates[window.current_plate]['name'])
        window.atc_var.set(window.plates[window.current_plate]['atc'])
        update_plate_display(window)
        window.plate_canvas.focus_set()

def next_plate(window):
    if window.plates and window.current_plate < len(window.plates) - 1:
        window.current_plate += 1
        window.plate_entry.delete(0, tk.END)
        window.plate_entry.insert(0, window.plates[window.current_plate]['name'])
        window.atc_var.set(window.plates[window.current_plate]['atc'])
        update_plate_display(window)
        window.plate_canvas.focus_set()






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









