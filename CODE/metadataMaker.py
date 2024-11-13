import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Canvas, Frame, Label, Checkbutton
import json
from datetime import datetime
import random
# Constants
DARK = "#2B2B2B"
LIGHT = "#FFFFFF"
GRAY1 = "#F0F0F0"
GRAY2 = "#E0E0E0"
FONT = "Helvetica"

COLORS = ["#3B82F6", "#10B981", "#F97316", "#EF4444", "#8B5CF6", "#D53F8C", "#6B7280", "#4B5563"]

class PlateAssignmentScreen:
    def __init__(self, root, layout_data):
            self.root = root
            self.layout_data = layout_data
            self.plates = []
            self.strains = []
            self.strain_colors = ["#3B82F6", "#10B981", "#F97316", "#EF4444", "#8B5CF6", "#D53F8C", "#6B7280", "#4B5563"]
            self.current_color_index = 0
            self.current_plate = 0
            self.strain_buttons = []
            
            # Add these attributes from layout_data
            self.rows = layout_data['rows']
            self.columns = layout_data['columns']
            self.num_strains = layout_data['strains']
            self.gap_between_strains = layout_data['gap_between_strains']
            self.strain_positions = layout_data['strain_positions']
            self.removed_positions = set(layout_data['removed_positions'])
            self.column_assignments = {}  # Track which positions are assigned to which strains
            
            # Convert numerical positions to letters
            self.position_labels = {i: chr(65 + i) for i in range(self.num_strains)}
            
            self.setup_gui()

    def setup_gui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main canvas
        self.canvas = tk.Canvas(
            self.root,
            bg=LIGHT,
            height=1024,
            width=1440,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Main dark rectangles
        self.round_rectangle(17.0, 168.0, 1100.0, 826.0, fill=DARK, outline="")
        self.round_rectangle(1120.0, 168.0, 1422.0, 826.0, fill=DARK, outline="")

        # Create frames
        self.plate_frame = tk.Frame(self.root, bg=DARK)
        self.plate_frame.place(x=27, y=178, width=1070, height=638)

        self.control_frame = tk.Frame(self.root, bg=DARK)
        self.control_frame.place(x=1130, y=178, width=282, height=638)

        # Create a separate frame for strains list
        self.strains_frame = tk.Frame(self.control_frame, bg=DARK)
        self.strains_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a frame for bottom buttons
        self.bottom_frame = tk.Frame(self.control_frame, bg=DARK)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Plate management (at the top)
        plate_label = tk.Label(self.control_frame, text="Plate Name", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
        plate_label.pack(pady=(0, 5))

        plate_entry_frame = tk.Frame(self.control_frame, bg=DARK)
        plate_entry_frame.pack(fill=tk.X, padx=10)

        self.plate_entry = ttk.Entry(plate_entry_frame, width=20)
        self.plate_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.atc_var = tk.BooleanVar()
        atc_check = tk.Checkbutton(
            plate_entry_frame,
            text="ATC",
            variable=self.atc_var,
            bg=DARK,
            fg=LIGHT,
            selectcolor=DARK,
            font=(FONT, 10)
        )
        atc_check.pack(side=tk.LEFT)

        add_plate_btn = tk.Button(
            self.control_frame,
            text="Add Plate",
            command=self.add_plate,
            font=(FONT, 10),
            bg=LIGHT,
            fg=DARK
        )
        add_plate_btn.pack(pady=(5, 10))

        # Strain entry
        strain_frame = tk.Frame(self.control_frame, bg=DARK)
        strain_frame.pack(fill=tk.X, padx=10)

        self.strain_entry = ttk.Entry(strain_frame, width=20)
        self.strain_entry.pack(side=tk.LEFT, padx=(0, 5))

        add_strain_btn = tk.Button(
            strain_frame,
            text="Add Strain",
            command=self.add_strain,
            font=(FONT, 10),
            bg=LIGHT,
            fg=DARK
        )
        add_strain_btn.pack(side=tk.LEFT)

        # Bottom buttons
        nav_frame = tk.Frame(self.bottom_frame, bg=DARK)
        nav_frame.pack(fill=tk.X, pady=5)

        prev_plate_btn = tk.Button(
            nav_frame,
            text="Previous Plate",
            command=self.prev_plate,
            font=(FONT, 10),
            bg=LIGHT,
            fg=DARK
        )
        prev_plate_btn.pack(side=tk.LEFT, padx=5)

        next_plate_btn = tk.Button(
            nav_frame,
            text="Next Plate",
            command=self.next_plate,
            font=(FONT, 10),
            bg=LIGHT,
            fg=DARK
        )
        next_plate_btn.pack(side=tk.LEFT, padx=5)

        action_frame = tk.Frame(self.bottom_frame, bg=DARK)
        action_frame.pack(fill=tk.X, pady=5)

        export_btn = tk.Button(
            action_frame,
            text="Export All",
            command=self.export_data,
            font=(FONT, 10),
            bg=LIGHT,
            fg=DARK
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        preview_all_btn = tk.Button(
            action_frame,
            text="Preview All Plates",
            command=self.preview_all_plates,
            font=(FONT, 10),
            bg=LIGHT,
            fg=DARK
        )
        preview_all_btn.pack(side=tk.LEFT, padx=5)

        clear_plate_btn = tk.Button(
            action_frame,
            text="Clear Plate",
            command=self.clear_current_plate,
            font=(FONT, 10),
            bg=LIGHT,
            fg=DARK
        )
        clear_plate_btn.pack(side=tk.LEFT, padx=5)

        # Initialize plate display
        self.plate_canvas = tk.Canvas(
            self.plate_frame,
            bg=DARK,
            highlightthickness=0
        )
        self.plate_canvas.pack(expand=True, fill='both')
        self.plate_canvas.bind("<Button-3>", self.unselect_position)

    def add_strain(self):
        strain = self.strain_entry.get().strip()
        if strain and strain not in self.strains:
            if len(self.strains) >= len(self.strain_colors):
                messagebox.showwarning("Warning", "Maximum number of strains reached")
                return
                
            self.strains.append(strain)
            self.strain_entry.delete(0, tk.END)

            # Create strain label and assign button
            strain_frame = tk.Frame(self.strains_frame, bg=DARK)
            strain_frame.pack(fill=tk.X, pady=2)

            color_indicator = tk.Label(
                strain_frame,
                bg=self.strain_colors[len(self.strains)-1],
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
                command=lambda s=strain: self.assign_strain_to_group(s),
                font=(FONT, 8),
                bg=LIGHT,
                fg=DARK
            )
            assign_btn.pack(side=tk.RIGHT)

            self.strain_buttons.append((strain_label, assign_btn))
            self.update_plate_display()

    
    def add_plate(self):
        name = self.plate_entry.get().strip()
        if name:
            # Create a new plate with empty assignments
            new_plate = {
                'name': name,
                'atc': self.atc_var.get(),
                'assignments': {},
                'column_assignments': {}  # Add column assignments specific to this plate
            }
            self.plates.append(new_plate)
            self.plate_entry.delete(0, tk.END)
            self.atc_var.set(False)
            self.current_plate = len(self.plates) - 1
            
            # Reset column assignments for the new plate
            self.column_assignments = {}
            
            self.update_plate_display()
           
    def unselect_position(self, event):
        if not self.plates:
            return
            
        # Get the clicked position
        clicked_items = self.plate_canvas.find_closest(event.x, event.y)
        if not clicked_items:
            return
            
        clicked_item = clicked_items[0]
        tags = self.plate_canvas.gettags(clicked_item)
        
        # Check if we clicked on a spot
        if "spot" in tags:
            pos_key = tags[0]  # The position key is the first tag
            
            # Get the column from the position key
            row, col = map(int, pos_key.split('-'))
            
            # Find and remove the column assignment
            for position_key, strain in list(self.column_assignments.items()):
                start, end = map(int, position_key.split('-'))
                if start <= col <= end:
                    del self.column_assignments[position_key]
                    
            # Remove assignments for all spots in the same column group
            plate = self.plates[self.current_plate]
            for row_idx in range(self.rows):
                key = f"{row_idx}-{col}"
                if key in plate['assignments']:
                    del plate['assignments'][key]
            
            # Update the display
            self.update_plate_display()
    def update_strain_menu(self):
        # Remove existing menu if it exists
        for widget in self.control_frame.winfo_children():
            if isinstance(widget, tk.OptionMenu):
                widget.destroy()

        if self.strains:
            self.selected_strain = tk.StringVar(value=self.strains[0])
            menu = tk.OptionMenu(
                self.control_frame,
                self.selected_strain,
                *self.strains
            )
            menu.configure(font=(FONT, 10), bg=LIGHT, fg=DARK)
            menu.grid(row=3, column=2, padx=20, pady=10)

    def assign_strain_to_group(self, strain):
        if not self.plates:
            messagebox.showwarning("Warning", "Please create a plate first")
            return

        plate = self.plates[self.current_plate]
        
        # Create menu of available positions
        available_positions = []
        for strain_idx, (start_col, end_col) in self.strain_positions.items():
            position_key = f"{start_col}-{end_col}"
            if position_key not in self.column_assignments:
                available_positions.append((strain_idx, start_col, end_col))

        if available_positions:
            strain_location_menu = tk.Menu(self.root, tearoff=0)
            for strain_idx, start_col, end_col in available_positions:
                label = f"Position {self.position_labels[strain_idx]}"
                strain_location_menu.add_command(
                    label=label,
                    command=lambda s=start_col, e=end_col, idx=strain_idx: 
                        self.assign_strain_to_columns(strain, s, e, idx)
                )

            try:
                strain_location_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
            finally:
                strain_location_menu.grab_release()
        else:
            messagebox.showwarning("Warning", "All positions are already assigned.")

    def assign_strain_to_columns(self, strain, start_col, end_col, position_idx):
        if not self.plates:
            return
            
        plate = self.plates[self.current_plate]
        position_key = f"{start_col}-{end_col}"
        
        # Check if these columns are already assigned
        for existing_key in list(self.column_assignments.keys()):
            existing_start, existing_end = map(int, existing_key.split('-'))
            if (start_col <= existing_end and end_col >= existing_start):
                return  # Position already assigned
                
        self.column_assignments[position_key] = {
            'strain': strain,
            'position': self.position_labels[position_idx],
            'position_idx': position_idx
        }
        
        # Assign all valid spots in these columns to the strain
        for row in range(self.rows):
            for col in range(start_col, end_col + 1):
                pos_key = f"{row}-{col}"
                if pos_key not in self.removed_positions:
                    plate['assignments'][pos_key] = strain
                    
        self.update_plate_display()    
    def update_plate_display(self):
        self.plate_canvas.delete('all')

        width = self.plate_canvas.winfo_width()
        height = self.plate_canvas.winfo_height()
        if width <= 1 or height <= 1:
            self.plate_canvas.after(100, self.update_plate_display)
            return
            
        # Calculate margins and grid dimensions
        margin_left = 30
        margin_right = 30
        margin_top = 70   # Increased to accommodate position labels
        margin_bottom = 30
        
        grid_width = width - margin_left - margin_right
        grid_height = height - margin_top - margin_bottom
        
        # Calculate cell dimensions
        cols_per_strain = self.columns // self.num_strains
        total_gaps = self.num_strains - 1 if self.gap_between_strains else 0
        total_width = self.columns + total_gaps
        cell_width = grid_width / total_width
        cell_height = grid_height / self.rows
        
        if self.plates:
            plate = self.plates[self.current_plate]
            self.plate_canvas.create_text(
                width // 2,  # Center horizontally
                20,         # Position from top
                text=f"Current Plate: {plate['name']}{'  (ATC)' if plate['atc'] else ''}",
                fill=LIGHT,
                font=(FONT, 16, 'bold')
             )
            # Draw position labels and spots
            current_x = margin_left
            for position_idx in range(self.num_strains):
                start_col, end_col = self.strain_positions[position_idx]
                position_width = (end_col - start_col + 1) * cell_width
                
                # Find if this position is assigned to a strain
                assigned_strain = None
                for pos_key, assignment in self.column_assignments.items():
                    pos_start, pos_end = map(int, pos_key.split('-'))
                    if pos_start == start_col and pos_end == end_col:
                        assigned_strain = assignment['strain']
                        break
                
                # Draw position label
                label_text = assigned_strain if assigned_strain else f"Position {self.position_labels[position_idx]}"
                self.plate_canvas.create_text(
                    current_x + position_width/2,
                    margin_top - 35,
                    text=label_text,
                    fill=LIGHT,
                    font=(FONT, 14, 'bold')
                )
                
                # Draw spots for this position
                for col_offset in range(end_col - start_col + 1):
                    col = start_col + col_offset
                    x_pos = current_x + col_offset * cell_width + cell_width/2
                    
                    for row in range(self.rows):
                        pos_key = f"{row}-{col}"
                        if pos_key not in self.removed_positions:
                            y_pos = margin_top + row * cell_height + cell_height/2
                            
                            # Determine spot color
                            spot_color = "#E5E7EB"
                            if assigned_strain:
                                strain_index = self.strains.index(assigned_strain)
                                spot_color = self.strain_colors[strain_index]
                            
                            # Draw spot
                            self.plate_canvas.create_oval(
                                x_pos-10, y_pos-10, x_pos+10, y_pos+10,
                                fill=spot_color,
                                outline=spot_color,
                                tags=(pos_key, "spot")
                            )
                            
                            # Add strain label if assigned
                            if assigned_strain:
                                self.plate_canvas.create_text(
                                    x_pos, y_pos - 15,
                                    text=assigned_strain,
                                    font=(FONT, 8),
                                    fill=LIGHT
                                )
                
                # Update x position for next group
                current_x += position_width
                
                # Add gap after each position except the last one
                if self.gap_between_strains and position_idx < self.num_strains - 1:
                    current_x += cell_width
    def assign_strain_to_location(self, pos_key, strain):
        plate = self.plates[self.current_plate]
        plate['assignments'][pos_key] = strain
        self.plate_canvas.itemconfig(
            self.plate_canvas.find_withtag(pos_key)[0],
            fill=self.strain_colors[strain],
            outline=self.strain_colors[strain]
        )
        self.plate_canvas.create_text(
            self.plate_canvas.coords(self.plate_canvas.find_withtag(pos_key)[0])[0],
            self.plate_canvas.coords(self.plate_canvas.find_withtag(pos_key)[0])[1] - 15,
            text=strain,
            font=(FONT, 8),
            fill=LIGHT
        )
        self.update_plate_display()

    def clear_current_plate(self):
        if not self.plates:
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all assignments from this plate?"):
            plate = self.plates[self.current_plate]
            plate['assignments'] = {}
            self.column_assignments = {}
            self.update_plate_display()

    def preview_all_plates(self):
        if not self.plates:
            messagebox.showinfo("Info", "No plates to preview")
            return

        preview_window = tk.Toplevel(self.root)
        preview_window.title("All Plates Preview")
        preview_window.geometry("1200x800")

        # Create a frame with scrollbar
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

        # Calculate dimensions
        plates_per_row = 2
        plate_width = 400
        plate_height = 300
        margin = 20

        for i, plate in enumerate(self.plates):
            row = i // plates_per_row
            col = i % plates_per_row

            # Create frame for each plate
            plate_frame = tk.Frame(scrollable_frame, bg=LIGHT, bd=2, relief='raised')
            plate_frame.grid(row=row, column=col, padx=margin, pady=margin)

            # Plate header
            header = tk.Label(
                plate_frame,
                text=f"{plate['name']} ({'ATC' if plate['atc'] else 'No ATC'})",
                font=(FONT, 12, 'bold'),
                bg=LIGHT
            )
            header.pack(pady=5)

            # Create canvas for plate visualization
            plate_canvas = tk.Canvas(
                plate_frame,
                width=plate_width - 40,
                height=plate_height - 60,
                bg=LIGHT,
                highlightthickness=1
            )
            plate_canvas.pack(padx=10, pady=5)

            # Draw spots
            self.draw_plate_preview(plate_canvas, plate)

        # Configure scrollbar
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)


    def draw_plate_preview(self, canvas, plate):
        # Calculate cell dimensions
        canvas_width = canvas.winfo_reqwidth()
        canvas_height = canvas.winfo_reqheight()
        
        margin = 20
        grid_width = canvas_width - 2 * margin
        grid_height = canvas_height - 2 * margin
        
        # Calculate dimensions considering gaps
        cols_per_strain = self.columns // self.num_strains
        total_gaps = self.num_strains - 1 if self.gap_between_strains else 0
        total_width = self.columns + total_gaps
        cell_width = grid_width / total_width
        cell_height = grid_height / self.rows

        # Draw position labels and spots
        current_x = margin
        for position_idx in range(self.num_strains):
            start_col, end_col = self.strain_positions[position_idx]
            position_width = (end_col - start_col + 1) * cell_width
            
            # Find if this position is assigned to a strain
            assigned_strain = None
            for pos_key, assignment in plate.get('assignments', {}).items():
                row, col = map(int, pos_key.split('-'))
                if start_col <= col <= end_col:
                    assigned_strain = assignment
                    break
            
            # Draw position label
            label_text = assigned_strain if assigned_strain else f"Position {self.position_labels[position_idx]}"
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
                
                for row in range(self.rows):
                    pos_key = f"{row}-{col}"
                    if pos_key not in self.removed_positions:
                        y_pos = margin + row * cell_height + cell_height/2
                        
                        # Determine spot color
                        spot_color = GRAY1
                        if pos_key in plate['assignments']:
                            strain = plate['assignments'][pos_key]
                            strain_index = self.strains.index(strain)
                            spot_color = self.strain_colors[strain_index]
                        
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
            if self.gap_between_strains and position_idx < self.num_strains - 1:
                current_x += cell_width

    def prev_plate(self):
        if self.current_plate > 0:
            self.current_plate -= 1
            self.update_plate_display()

    def next_plate(self):
        if self.current_plate < len(self.plates) - 1:
            self.current_plate += 1
            self.update_plate_display()

    def export_data(self):
        export_data = {
            'layout': self.layout_data,
            'plates': self.plates,
            'strains': self.strains,
            'strain_colors': self.strain_colors,
            'timestamp': datetime.now().isoformat()
        }

        with open("plate_assignment_data.json", "w") as f:
            json.dump(export_data, f, indent=2)

        messagebox.showinfo("Success", "Data exported successfully!")
        
    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
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
                 x1, y1]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)


class PlateLayoutDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("Plate Layout Designer")
        self.root.geometry("1440x1024")
        self.root.configure(bg=LIGHT)
        
        # Initialize variables
        self.rows = tk.IntVar(value=8)
        self.columns = tk.IntVar(value=12)
        self.strains = tk.IntVar(value=2)
        self.x_dilution = tk.IntVar(value=2)
        self.y_dilution = tk.IntVar(value=2)
        self.gap_between_strains = tk.BooleanVar(value=False)
        self.removed_positions = set()
        
        self.create_main_frame()
        


    def create_main_frame(self):
        # Create main canvas
        self.canvas = Canvas(
            self.root,
            bg=LIGHT,
            height=1024,
            width=1440,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        # Main dark rectangles
        self.round_rectangle(17.0, 168.0, 1100.0, 826.0, fill=DARK, outline="")
        self.round_rectangle(1120.0, 168.0, 1422.0, 826.0, fill=DARK, outline="")
        
        # Create frames
        self.plate_frame = Frame(self.root, bg=DARK)
        self.plate_frame.place(x=27, y=178, width=1070, height=638)
        
        self.control_frame = Frame(self.root, bg=DARK)
        self.control_frame.place(x=1130, y=178, width=282, height=638)
        
        self.create_controls()
        self.create_plate_display()


    def create_controls(self):
        y_offset = 20
        spacing = 80
        
        # Row input
        row_label = Label(self.control_frame, text="Rows", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
        row_label.place(x=20, y=y_offset)
        row_entry = ttk.Entry(self.control_frame, textvariable=self.rows, width=10)
        row_entry.place(x=20, y=y_offset + 30)
        
        # Column input
        col_label = Label(self.control_frame, text="Columns", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
        col_label.place(x=20, y=y_offset + spacing)
        col_entry = ttk.Entry(self.control_frame, textvariable=self.columns, width=10)
        col_entry.place(x=20, y=y_offset + spacing + 30)
        
        # Strains input
        strain_label = Label(self.control_frame, text="Strains", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
        strain_label.place(x=20, y=y_offset + spacing * 2)
        strain_entry = ttk.Entry(self.control_frame, textvariable=self.strains, width=10)
        strain_entry.place(x=20, y=y_offset + spacing * 2 + 30)
        
        # X Dilution input
        x_dil_label = Label(self.control_frame, text="X-Dilution", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
        x_dil_label.place(x=20, y=y_offset + spacing * 3)
        x_dil_entry = ttk.Entry(self.control_frame, textvariable=self.x_dilution, width=10)
        x_dil_entry.place(x=20, y=y_offset + spacing * 3 + 30)
        
        # Y Dilution input
        y_dil_label = Label(self.control_frame, text="Y-Dilution", font=(FONT, 12, 'bold'), fg=LIGHT, bg=DARK)
        y_dil_label.place(x=20, y=y_offset + spacing * 4)
        y_dil_entry = ttk.Entry(self.control_frame, textvariable=self.y_dilution, width=10)
        y_dil_entry.place(x=20, y=y_offset + spacing * 4 + 30)
        
        # Gap checkbox
        gap_check = Checkbutton(
            self.control_frame,
            text="Gap Between Strains",
            variable=self.gap_between_strains,
            bg=DARK,
            fg=LIGHT,
            selectcolor=DARK,
            font=(FONT, 12),
            command=self.update_plate_display
        )
        gap_check.place(x=20, y=y_offset + spacing * 5)
        
        # Next screen button
        next_button = tk.Button(
            self.control_frame,
            text="Next",
            command=self.go_to_assignment_screen,
            font=(FONT, 12),
            bg=LIGHT,
            fg=DARK
        )
        next_button.place(x=20, y=y_offset + spacing * 6)
        
        # Bind all variables to update function
        self.rows.trace_add("write", lambda *args: self.update_plate_display())
        self.columns.trace_add("write", lambda *args: self.update_plate_display())
        self.strains.trace_add("write", lambda *args: self.update_plate_display())
        self.x_dilution.trace_add("write", lambda *args: self.update_plate_display())
        self.y_dilution.trace_add("write", lambda *args: self.update_plate_display())
        
    def create_plate_display(self):
        self.plate_canvas = Canvas(
            self.plate_frame,
            bg=DARK,
            highlightthickness=0
        )
        self.plate_canvas.pack(expand=True, fill='both')
        self.plate_canvas.bind("<Button-1>", self.handle_click)
        self.update_plate_display()
    
    def update_plate_display(self, *args):
        self.plate_canvas.delete('all')
        
        # Get current values and validate
        try:
            rows = max(1, self.rows.get())
            cols = max(1, self.columns.get())
            strains = max(1, self.strains.get())
            x_dil = max(1, self.x_dilution.get())
            y_dil = max(1, self.y_dilution.get())
        except tk.TclError:
            return
            
        # Calculate dimensions
        width = self.plate_canvas.winfo_width()
        height = self.plate_canvas.winfo_height()
        if width <= 1 or height <= 1:  # Handle initial load
            self.plate_canvas.after(100, self.update_plate_display)
            return
            
        margin = 50
        grid_width = width - 2 * margin
        grid_height = height - 2 * margin
        
        # Calculate columns including gaps
        cols_per_strain = cols // strains
        total_cols = cols
        
        if self.gap_between_strains.get():
            total_gaps = strains - 1
            total_cols = cols + total_gaps

        cell_width = grid_width / total_cols
        cell_height = grid_height / rows
        
        # Update strain positions
        self.strain_positions = {}
        current_col = 0
        
        for strain in range(strains):
            start_col = current_col
            end_col = start_col + cols_per_strain - 1
            self.strain_positions[strain] = (start_col, end_col)
            current_col = end_col + 1
            if self.gap_between_strains.get() and strain < strains - 1:
                current_col += 1  # Skip a column for gap
        
        # Draw dilution labels
        for row in range(rows):
            y_value = y_dil ** row
            self.plate_canvas.create_text(
                margin - 20,
                margin + row * cell_height + cell_height/2,
                text=f"1/{y_value}",
                fill=LIGHT,
                font=(FONT, 8)
            )
        
        # Draw spots and x-dilution labels for each strain
        for strain in range(strains):
            start_col, end_col = self.strain_positions[strain]
            for col_offset in range(end_col - start_col + 1):
                actual_col = start_col + col_offset
                x_value = x_dil ** col_offset
                x_pos = margin + actual_col * cell_width + cell_width/2
                
                # Draw x-dilution label
                self.plate_canvas.create_text(
                    x_pos,
                    margin - 20,
                    text=f"1/{x_value}",
                    fill=LIGHT,
                    font=(FONT, 8)
                )
                
                # Draw spots
                for row in range(rows):
                    pos_key = f"{row}-{actual_col}"
                    if pos_key not in self.removed_positions:
                        x = margin + actual_col * cell_width + cell_width/2
                        y = margin + row * cell_height + cell_height/2
                        color = COLORS[strain % len(COLORS)]
                        
                        self.plate_canvas.create_oval(
                            x-10, y-10, x+10, y+10,
                            fill=color,
                            outline=color,
                            tags=(pos_key, "spot", f"strain_{strain}")
                        )
        
        # Print strain positions for debugging
        print("Strain Positions:")
        for strain, (start, end) in self.strain_positions.items():
            print(f"Strain {strain}: columns {start}-{end}")

    def handle_click(self, event):
        closest = self.plate_canvas.find_closest(event.x, event.y)
        tags = self.plate_canvas.gettags(closest)
        
        if tags and len(tags) > 1:
            pos_key = tags[0]
            if pos_key in self.removed_positions:
                self.removed_positions.remove(pos_key)
            else:
                self.removed_positions.add(pos_key)
            self.update_plate_display()
            
    def go_to_assignment_screen(self):
        # Get valid positions for each strain
        valid_positions = {}
        for strain, (start_col, end_col) in self.strain_positions.items():
            strain_positions = []
            for row in range(self.rows.get()):
                for col in range(start_col, end_col + 1):
                    pos_key = f"{row}-{col}"
                    if pos_key not in self.removed_positions:
                        strain_positions.append(pos_key)
            valid_positions[strain] = strain_positions

        # Prepare layout data
        layout_data = {
            'rows': self.rows.get(),
            'columns': self.columns.get(),
            'strains': self.strains.get(),
            'x_dilution': self.x_dilution.get(),
            'y_dilution': self.y_dilution.get(),
            'gap_between_strains': self.gap_between_strains.get(),
            'removed_positions': list(self.removed_positions),
            'strain_positions': self.strain_positions,
            'valid_positions': valid_positions
        }

        # Create new assignment screen
        PlateAssignmentScreen(self.root, layout_data)
        
    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
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
                 x1, y1]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

def main():
    root = tk.Tk()
    app = PlateLayoutDesigner(root)
    root.mainloop()

if __name__ == "__main__":
    main()