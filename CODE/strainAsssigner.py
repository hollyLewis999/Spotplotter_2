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
    image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
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

    create_plate_controls(window)
    create_strain_controls(window)
    create_navigation_controls(window)
    create_plate_canvas(window)

    create_rounded_button(
        canvas=window.canvas,
        text="Next",
        command=lambda: print("processMetadata"),
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
    print("======== UPDATING PLATE DISPLAY ========")
    print(f"Total plates: {len(window.plates)}")
    
    if not window.plates:
        print("ERROR: No plates exist")
        return

    # Validate plate index
    if CURRENTPLATEINDEX < 0 or CURRENTPLATEINDEX >= len(window.plates):
        print(f"ERROR: Invalid plate index {CURRENTPLATEINDEX}")
        return

    current_plate = window.plates[CURRENTPLATEINDEX]
    print(f"Current Plate Index: {CURRENTPLATEINDEX}")
    print(f"Current Plate Name: {current_plate.get('name', 'NO NAME')}")
    print(f"Plate Assignments: {current_plate.get('assignments', 'NO ASSIGNMENTS')}")

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

def create_plate_controls(window):
    # "Add a plate" header
    plate_header = tk.Label(window.control_frame, text="Add a Plate", font=(FONT, 14, 'bold'), fg=LIGHT, bg=DARK)
    plate_header.pack(pady=(10, 5))
    

    # Additive controls
    window.additive_var = tk.BooleanVar(value=False)
    additive_frame = tk.Frame(window.control_frame, bg=DARK)
    additive_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
    
    additive_check = tk.Checkbutton(
        additive_frame,
        text="Additive",
        variable=window.additive_var,
        bg=DARK,
        fg=LIGHT,
        selectcolor=DARK,
        font=(FONT, 10)
    )
    additive_check.pack(side=tk.LEFT)
    
    window.additive_entry = ttk.Entry(additive_frame, width=25, state=tk.DISABLED)
    window.additive_entry.pack(side=tk.LEFT, padx=(10, 0))
    
    def toggle_additive_entry():
        if window.additive_var.get():
            window.additive_entry.config(state=tk.NORMAL)
        else:
            window.additive_entry.config(state=tk.DISABLED)
            window.additive_entry.delete(0, tk.END)
    
    window.additive_var.trace_add("write", lambda *args: toggle_additive_entry())


    # Plate name frame
    plate_frame = tk.Frame(window.control_frame, bg=DARK)
    plate_frame.pack(fill=tk.X, padx=10)
    



    
    # Initialize plates attribute if not exists
    if not hasattr(window, 'plates'):
        window.plates = []
    
    # Plate name entry
    window.plate_entry = ttk.Entry(plate_frame, width=25)
    window.plate_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
    
    # Add plate button (now a + button)
    add_plate_btn = tk.Button(
        plate_frame,
        text="+",
        command=lambda: add_plate(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK,
        width=3
    )
    add_plate_btn.pack(side=tk.RIGHT)
    
    # Rest of the code remains the same as in previous version...

def create_navigation_controls(window):
    # Clear current plate button
    clear_btn = tk.Button(
        window.bottom_frame,
        text="Clear Current Plate",
        command=lambda: clear_current_plate(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    clear_btn.pack(pady=(20, 5))  # Increased vertical padding
    
    # Rest of the code remains the same as in the previous artifact
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
    prev_plate_btn.pack(side=tk.LEFT, padx=5, expand=True)
    
    next_plate_btn = tk.Button(
        nav_frame,
        text="Next Plate",
        command=lambda: next_plate(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    next_plate_btn.pack(side=tk.LEFT, padx=5, expand=True)
    
    action_frame = tk.Frame(window.bottom_frame, bg=DARK)
    action_frame.pack(fill=tk.X, pady=5)
    
    preview_btn = tk.Button(
        action_frame,
        text="Preview All Plates",
        command=lambda: preview_all_plates(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    preview_btn.pack(side=tk.LEFT, padx=5, expand=True)
    
    export_btn = tk.Button(
        action_frame,
        text="Export All",
        command=lambda: export_data(window),
        font=(FONT, 10),
        bg=LIGHT,
        fg=DARK
    )
    export_btn.pack(side=tk.LEFT, padx=5, expand=True)

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
    atc = window.atc_var.get().strip()  # Get ATC value
    if name:
        additive_name = window.additive_entry.get().strip() if window.additive_var.get() else None
        new_plate = {
            'name': name,
            'atc': atc,  # Add ATC to plate metadata
            'additive': additive_name,
            'assignments': {},
            'column_assignments': {}
        }
        window.plates.append(new_plate)
        window.plate_entry.delete(0, tk.END)
        window.atc_var.set("")  # Clear ATC entry
        window.additive_var.set(False)
        window.additive_entry.delete(0, tk.END)
        window.current_plate = len(window.plates) - 1
        window.column_assignments = {}
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
    print("____________________________________________________DRAW PLATE GRID")
    print(CURRENTPLATEINDEX)
    print(plate)
    num_strains = window.layout_data['strains']

    # Draw plate header
    additive_display = f"  (Additive: {plate['additive_name']})" if plate.get('has_additive') and plate.get('additive_name') else ''
    
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


def prev_plate(window):
    global CURRENTPLATEINDEX
    if window.plates and window.current_plate > 0:
        # Clear current display
        window.plate_canvas.delete('all')
        CURRENTPLATEINDEX = CURRENTPLATEINDEX -1
        # Update current plate index
        window.current_plate -= 1
        new_plate = window.plates[window.current_plate]
        
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
        
        # Update display with new plate index
        update_plate_display(window)
        window.plate_canvas.focus_set()
    else:
        print("Cannot go to next plate")


