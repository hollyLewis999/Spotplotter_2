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
ASSETS_PATH = OUTPUT_PATH /  "Icons"
buttonPosX = 1200

backToEdit2 = False
PROGRESSX = 1180
PROGRESSY = 36

def create_rounded_button(canvas, text, command, x, y, width=200, height=70, cornerradius=12, padding=2, button_tag=None, fill=DARK, accent=LIGHT, font_size=12, bold=True):
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

    # Add text in the middle of the button and tag it, with customizable font size and bold
    font_style = "bold" if bold else "normal"
    canvas.create_text(x + width / 2, y + height / 2, text=text, fill=accent, font=(FONT, font_size, font_style), tags=button_tag)

    # Bind the click event to the entire button with the unique tag
    canvas.tag_bind(button_tag, "<Button-1>", lambda event: command())


def create_circular_slider(master, min_val, max_val, position, width=270, command=None, initial_value=None):
    """
    Create a circular slider with variable length
    
    Parameters:
    - master: parent widget
    - min_val: minimum value of slider
    - max_val: maximum value of slider
    - position: (x, y) position tuple
    - width: width of the slider (default 300)
    - command: callback function when value changes
    - initial_value: starting value of slider
    """
    # Calculate dimensions
    height = 70
    padding = 20  # Left and right padding
    slider_width = width - (padding * 2)  # Actual slider width minus padding
    
    frame = Frame(master, width=width, height=height, bg=DARK)
    frame.place(x=position[0], y=position[1])
    
    canvas = Canvas(frame, width=width, height=height, bg=DARK, highlightthickness=0)
    canvas.pack()
    
    current_value = DoubleVar(value=min_val if initial_value is None else initial_value)
    last_update_time = 0
    update_interval = 100  # Update interval in milliseconds
    
    def value_to_position(value):
        """Convert slider value to x-position"""
        return (value - min_val) / (max_val - min_val) * slider_width + padding
    
    def position_to_value(x):
        """Convert x-position to slider value"""
        return (x - padding) / slider_width * (max_val - min_val) + min_val
    
    def draw_slider(update_label=False):
        """Draw the slider components"""
        canvas.delete("all")
        
        # Draw background line
        canvas.create_line(
            padding, height/2 + 10,  # y position moved down by 10
            width - padding, height/2 + 10,
            fill=GRAY,
            width=10,
            capstyle=ROUND
        )
        
        # Draw filled line
        filled_x = value_to_position(current_value.get())
        canvas.create_line(
            padding, height/2 + 10,
            filled_x, height/2 + 10,
            fill=LIGHT,
            width=10,
            capstyle=ROUND
        )
        
        # Draw knob
        knob_x = value_to_position(current_value.get())
        canvas.create_oval(
            knob_x-10, height/2,
            knob_x+10, height/2 + 20,
            fill=LIGHT,
            outline=DARK,
            tags="knob"
        )
        
        # Update value label if needed
        if update_label:
            canvas.delete("value_text")
            label_x = max(padding, min(knob_x, width - padding))
            canvas.create_text(
                label_x, height/2 - 15,
                text=str(int(current_value.get())),
                font=(FONT, 10, "bold"),
                fill=LIGHT,
                tags="value_text"
            )
    
    def on_drag(event):
        nonlocal last_update_time
        current_time = event.time
        
        # Check if click is within the slider's vertical bounds
        if height/2 <= event.y <= height/2 + 20:
            # Constrain x position to slider bounds
            x = max(padding, min(event.x, width - padding))
            new_value = position_to_value(x)
            current_value.set(max(min_val, min(max_val, new_value)))
            
            # Update display based on interval
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
    
    def set_value(value):
        """Set slider value programmatically"""
        current_value.set(max(min_val, min(max_val, value)))
        draw_slider(update_label=True)
    
    # Bind events
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    
    # Add methods to frame
    frame.set = set_value
    frame.get = lambda: int(current_value.get())
    
    # Initial draw
    draw_slider(update_label=True)
    
    return frame
        

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
        # Initialize variable if none provided
        self.variable = variable if variable is not None else tk.BooleanVar()
        self.command = command
        
        # Create the rounded rectangle for the checkbox
        self.box = self.create_rounded_rectangle(
            2, 2, 22, 22,
            5,  # corner radius
            outline="#cccccc",
            fill="white",
            width=2
        )
        
        # Create the checkmark (state based on variable)
        self.checkmark = self.create_line(
            6, 12, 10, 16, 18, 8,
            fill=DARK,
            width=3,
            state="normal" if self.variable.get() else "hidden"
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
        
        # Store the trace callback name
        self.trace_id = self.variable.trace_add('write', self._on_var_change)
        
        # Initial state update
        self.update_state()
    
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
        current_value = self.variable.get()
        self.variable.set(not current_value)
        if self.command:
            self.command()
    
    def update_state(self):
        try:
            current_state = "normal" if self.variable.get() else "hidden"
            if self.winfo_exists():  # Check if widget still exists
                self.itemconfigure(self.checkmark, state=current_state)
        except tk.TclError:
            pass  # Widget is being destroyed, ignore the error
    
    def _on_var_change(self, *args):
        try:
            if self.winfo_exists():  # Check if widget still exists
                self.update_state()
        except tk.TclError:
            pass  # Widget is being destroyed, ignore the error
    
    def destroy(self):
        """Properly clean up the widget and its resources"""
        try:
            # Remove the variable trace
            if hasattr(self, 'trace_id'):
                self.variable.trace_remove('write', self.trace_id)
            
            # Destroy the label if it exists
            if hasattr(self, 'label') and self.label.winfo_exists():
                self.label.destroy()
            
            # Call the parent's destroy method
            super().destroy()
        except tk.TclError:
            pass  # Widget is already being destroyed, ignore the error