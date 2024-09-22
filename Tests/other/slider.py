import tkinter as tk

DARK = "#092934"
LIGHT = "#FFFFFF"
GRAY = "#c9c9c9"
FONT = "Microsoft New Tai Lue"

class CircularSlider(tk.Canvas):
    def __init__(self, master=None, min_val=0, max_val=100, position=(0, 0), **kwargs):
        super().__init__(master, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.current_value = min_val
        
        # Increase canvas height to accommodate the label
        self.config(width=400, height=70, bg=DARK, highlightthickness=0)
        self.place(x=position[0], y=position[1])
        
        # Create a label to display the current value
        self.value_label = tk.Label(self, text=str(self.current_value), font=(FONT, 10, "bold"),
                                    bg=DARK, fg=LIGHT)
        
        # Draw initial slider
        self.draw_slider()
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)

    def draw_slider(self):
        self.delete("all")
        # Draw the track with left side gray and right side light
        filled_x = self.value_to_position(self.current_value)
        self.create_line(10, 45, 290, 45, fill=GRAY, width=10, capstyle=tk.ROUND)  # Gray background
        self.create_line(10, 45, filled_x, 45, fill=LIGHT, width=10, capstyle=tk.ROUND)  # Light filled part
        
        # Draw the knob
        self.knob_x = self.value_to_position(self.current_value)
        self.create_oval(self.knob_x-10, 35, self.knob_x+10, 55, fill=LIGHT, outline=DARK, tags="knob")
        
        # Update the value label
        self.value_label.config(text=str(self.current_value))
        
        # Calculate label position, ensuring it stays within the canvas
        label_x = max(0, min(self.knob_x - 20, 300))  # Keeps label within 0-260 x-range
        self.value_label.place(x=label_x, y=5)
        
        # Raise the label to be on top
        self.value_label.lift()

    def value_to_position(self, value):
        return (value - self.min_val) / (self.max_val - self.min_val) * 280 + 10

    def on_drag(self, event):
        if 35 <= event.y <= 55:  # Adjusted for new knob position
            new_value = int(self.position_to_value(event.x))
            self.current_value = max(self.min_val, min(self.max_val, new_value))
            self.draw_slider()
            self.event_generate("<<ValueChanged>>")

    def position_to_value(self, x):
        return (x - 10) / 280 * (self.max_val - self.min_val) + self.min_val

    def on_release(self, event):
        self.event_generate("<<ValueChanged>>")

# Example usage
def on_value_changed(event):
    print("New value:", slider.current_value)

window = tk.Tk()
slider = CircularSlider(window, min_val=0, max_val=10000, position=(50, 50))
slider.bind("<<ValueChanged>>", on_value_changed)
window.geometry("1440x1024")
window.configure(bg=DARK)  # Set background color for the window
window.mainloop()