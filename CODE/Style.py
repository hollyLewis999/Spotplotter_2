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
from metadataMaker import *

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
