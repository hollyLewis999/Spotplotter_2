from tkinter import *
import tkinter as tk

root = Tk()
DARK = "#092934"
LIGHT = "#E4EDF5"

class RoundedButton(tk.Canvas):
    def __init__(self, parent,text, command, width =200, height=60, cornerradius=10, padding=2):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
            relief="flat", highlightthickness=0, bg=LIGHT)
        self.command = command
        self.text = text

        rad = 2 * cornerradius
        def shape():
            self.create_polygon(
                (padding, height - cornerradius - padding,
                 padding, cornerradius + padding,
                 padding + cornerradius, padding,
                 width - padding - cornerradius, padding,
                 width - padding, cornerradius + padding,
                 width - padding, height - cornerradius - padding,
                 width - padding - cornerradius, height - padding,
                 padding + cornerradius, height - padding),
                fill=DARK, outline=DARK
            )
            self.create_arc(
                (padding, padding + rad, padding + rad, padding),
                start=90, extent=90, fill=DARK, outline=DARK
            )
            self.create_arc(
                (width - padding - rad, padding, width - padding, padding + rad),
                start=0, extent=90, fill=DARK, outline=DARK
            )
            self.create_arc(
                (width - padding, height - rad - padding, width - padding - rad, height - padding),
                start=270, extent=90, fill=DARK, outline=DARK
            )
            self.create_arc(
                (padding, height - padding - rad, padding + rad, height - padding),
                start=180, extent=90, fill=DARK, outline=DARK
            )

        shape()
        (x0, y0, x1, y1) = self.bbox("all")
        width = x1 - x0
        height = y1 - y0
        self.configure(width=width, height=height)
        
        # Add text in the middle of the button
        self.create_text(width / 2, height / 2, text=self.text, fill=LIGHT, font=("Microsoft New Tai Lue", 12, "bold"))

        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_release(self, event):
        if self.command is not None:
            self.command()

def test():
    print("Hello")

canvas = Canvas(root, height=300, width=500)
canvas.pack()

button = RoundedButton(root, 'Click Me',test)
button.place(relx=.1, rely=.1)

root.mainloop()
