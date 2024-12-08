from tkinter import (
    Toplevel, 
    Canvas, 
    Scrollbar, 
    Frame, 
    Label, 
    Button
)
from tkinter import BOTTOM,BooleanVar,Button,Canvas,CENTER,Checkbutton,DoubleVar,Entry,Frame,HORIZONTAL,Label,LEFT,Message,PhotoImage,RIGHT,ROUND,Scale,Scrollbar,Text,Toplevel,Tk,Y,X,filedialog,font,messagebox

DARK = "#092934"
LIGHT = "#FFFFFF"
FONT = "Microsoft New Tai Lue"

def create_help_popup_sliders(window):
    """
    Create a responsive popup window with detailed help information about thresholding parameters
    """
    help_window = Toplevel(window)
    help_window.title("Parameter Refinement Help")
    help_window.geometry("600x700")
    help_window.configure(bg=LIGHT)

    # Make the help window resizable
    help_window.grid_rowconfigure(0, weight=1)
    help_window.grid_columnconfigure(0, weight=1)

    # Create a frame to hold everything
    main_frame = Frame(help_window, bg=LIGHT)
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Create a canvas with a scrollbar
    canvas = Canvas(main_frame, bg=LIGHT)
    scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg=LIGHT)

    # Configure the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    # Make the scrollbar and canvas responsive
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.grid(row=0, column=0, sticky="nsew")
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)

    # Create a window in the canvas
    canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Function to update scroll region and wrap text
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Adjust wraplength to current canvas width
        wrap_length = canvas.winfo_width() - 40  # Leave some padding
        for widget in scrollable_frame.winfo_children():
            if isinstance(widget, Label):
                widget.configure(wraplength=max(wrap_length, 300))

    # Bind the configure event
    scrollable_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_frame_configure)

    # Content creation (similar to previous implementation)
    def create_section_title(parent, text):
        title = Label(
            parent, 
            text=text, 
            font=(FONT, 16, 'bold'), 
            bg=LIGHT, 
            fg=DARK,
            anchor='w'
        )
        title.pack(fill='x', padx=25, pady=(10, 0))
        return title

    def create_section_description(parent, text, is_main=False):
        font_size = 14 if is_main else 12
        font_weight = 'bold' if is_main else 'normal'
        desc = Label(
            parent, 
            text=text, 
            font=(FONT, font_size, font_weight), 
            bg=LIGHT, 
            fg=DARK,
            justify=LEFT
        )
        desc.pack(fill='x', padx=25, pady=(0, 10))
        return desc

    def create_bullet_point(parent, text):
        bullet = Label(
            parent, 
            text=text, 
            font=(FONT, 12), 
            bg=LIGHT, 
            fg=DARK,
            justify=LEFT
        )
        bullet.pack(fill='x', padx=40)
        return bullet

    # Main Title
    create_section_title(scrollable_frame, "Parameter Refinement for Local Adaptive Mean Thresholding")

    # Main Description
    create_section_description(scrollable_frame, 
        "This page allows you to adjust the parameters for local adaptive mean thresholding to optimize image segmentation. While default values are provided, they may not suit every image. Modifying these parameters will dynamically update the contours and produce results that better reflect your specific image. Final parameter settings will be included in the PDF export for reference.",
        is_main=True
    )

    # Threshold Section
    create_section_title(scrollable_frame, "What is Threshold?")
    create_section_description(scrollable_frame, 
        "Thresholding determines whether a pixel is classified as part of the foreground (e.g., a spot to be quantified) or the background (areas of no interest). This is done by comparing the pixel's intensity to its surrounding area."
    )
    create_bullet_point(scrollable_frame, 
        "• Lower Threshold Values: Classify more pixels as foreground, potentially overestimating spot size or misclassifying noise/light artifacts as spots."
    )
    create_bullet_point(scrollable_frame, 
        "• Higher Threshold Values: Classify more pixels as background, reducing noise but risking the exclusion of lighter spots. Choose a value that balances noise reduction and accurate spot detection for your image."
    )

    # Block Size Section
    create_section_title(scrollable_frame, "What is Block Size?")
    create_section_description(scrollable_frame, 
        "Block size defines the neighborhood area used to analyze pixel intensity differences."
    )
    create_bullet_point(scrollable_frame, 
        "• Smaller Block Sizes: Capture finer details but may introduce noise and complexity."
    )
    create_bullet_point(scrollable_frame, 
        "• Larger Block Sizes: Smooth the image, reducing noise but potentially losing small details. Adjust this parameter to balance detail retention and noise reduction based on your image's characteristics."
    )

    # Size Section
    create_section_title(scrollable_frame, "What is Size?")
    create_section_description(scrollable_frame, 
        "This parameter represents the minimum area (as a proportion of the image width) that will be considered for spot detection. Areas smaller than this size will be ignored during segmentation."
    )

    # Closing Advice
    closing_advice = Label(
        scrollable_frame, 
        text="Feel free to test different settings to achieve the most accurate segmentation results for your images.",
        font=(FONT, 12, 'italic'), 
        bg=LIGHT, 
        fg=DARK,
        justify=CENTER
    )
    closing_advice.pack(pady=(20, 10))

    # Close Button
    close_button = Button(
        scrollable_frame, 
        text="Close", 
        command=help_window.destroy,
        font=(FONT, 12),
        bg=DARK,
        fg=LIGHT,
        padx=20,
        pady=10
    )
    close_button.pack(pady=(0, 20))

    return help_window
    """
    Create a popup window with detailed help information about thresholding parameters
    """
    help_window = Toplevel(window)
    help_window.title("Parameter Refinement Help")
    help_window.geometry("600x700")
    help_window.configure(bg=LIGHT)

    # Create a canvas to allow scrolling if needed
    canvas = Canvas(help_window, bg=LIGHT)
    scrollbar = Scrollbar(help_window, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg=LIGHT)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Title
    title_label = Label(
        scrollable_frame, 
        text="Parameter Refinement for Local Adaptive Mean Thresholding", 
        font=(FONT, 16, 'bold'), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=CENTER
    )
    title_label.pack(pady=(20, 10))

    # Explanation text
    explanation = Label(
        scrollable_frame, 
        text="This page allows you to adjust the parameters for local adaptive mean thresholding to optimize image segmentation. While default values are provided, they may not suit every image. Modifying these parameters will dynamically update the contours and produce results that better reflect your specific image. Final parameter settings will be included in the PDF export for reference.",
        font=(FONT, 12), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=LEFT
    )
    explanation.pack(pady=(0, 20))

    # Threshold Section
    threshold_title = Label(
        scrollable_frame, 
        text="What is Threshold?", 
        font=(FONT, 14, 'bold'), 
        bg=LIGHT, 
        fg=DARK
    )
    threshold_title.pack(anchor='w', padx=25)

    threshold_desc = Label(
        scrollable_frame, 
        text="Thresholding determines whether a pixel is classified as part of the foreground (e.g., a spot to be quantified) or the background (areas of no interest). This is done by comparing the pixel's intensity to its surrounding area.",
        font=(FONT, 12), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=LEFT
    )
    threshold_desc.pack(padx=25)

    # Threshold bullet points
    threshold_lower = Label(
        scrollable_frame, 
        text="• Lower Threshold Values: Classify more pixels as foreground, potentially overestimating spot size or misclassifying noise/light artifacts as spots.",
        font=(FONT, 12), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=LEFT
    )
    threshold_lower.pack(padx=40)

    threshold_higher = Label(
        scrollable_frame, 
        text="• Higher Threshold Values: Classify more pixels as background, reducing noise but risking the exclusion of lighter spots. Choose a value that balances noise reduction and accurate spot detection for your image.",
        font=(FONT, 12), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=LEFT
    )
    threshold_higher.pack(padx=40)

    # Block Size Section
    block_title = Label(
        scrollable_frame, 
        text="What is Block Size?", 
        font=(FONT, 14, 'bold'), 
        bg=LIGHT, 
        fg=DARK
    )
    block_title.pack(anchor='w', padx=25, pady=(10, 0))

    block_desc = Label(
        scrollable_frame, 
        text="Block size defines the neighborhood area used to analyze pixel intensity differences.",
        font=(FONT, 12), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=LEFT
    )
    block_desc.pack(padx=25)

    # Block size bullet points
    block_smaller = Label(
        scrollable_frame, 
        text="• Smaller Block Sizes: Capture finer details but may introduce noise and complexity.",
        font=(FONT, 12), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=LEFT
    )
    block_smaller.pack(padx=40)

    block_larger = Label(
        scrollable_frame, 
        text="• Larger Block Sizes: Smooth the image, reducing noise but potentially losing small details. Adjust this parameter to balance detail retention and noise reduction based on your image's characteristics.",
        font=(FONT, 12), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=LEFT
    )
    block_larger.pack(padx=40)

    # Size Section
    size_title = Label(
        scrollable_frame, 
        text="What is Size?", 
        font=(FONT, 14, 'bold'), 
        bg=LIGHT, 
        fg=DARK
    )
    size_title.pack(anchor='w', padx=25, pady=(10, 0))

    size_desc = Label(
        scrollable_frame, 
        text="This parameter represents the minimum area (as a proportion of the image width) that will be considered for spot detection. Areas smaller than this size will be ignored during segmentation.",
        font=(FONT, 12), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=LEFT
    )
    size_desc.pack(padx=25)

    # Closing advice
    closing_advice = Label(
        scrollable_frame, 
        text="Feel free to test different settings to achieve the most accurate segmentation results for your images.",
        font=(FONT, 12, 'italic'), 
        bg=LIGHT, 
        fg=DARK,
        wraplength=550,
        justify=CENTER
    )
    closing_advice.pack(pady=(20, 20))

    # Close button
    close_button = Button(
        scrollable_frame, 
        text="Close", 
        command=help_window.destroy,
        font=(FONT, 12),
        bg=DARK,
        fg=LIGHT,
        padx=20,
        pady=10
    )
    close_button.pack(pady=(0, 20))

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

import tkinter as tk
from tkinter import font as tkfont

def create_help_popup(parent):
    # Create popup window
    help_window = tk.Toplevel(parent)
    help_window.title("Strain Assigner: Step-by-Step Guide")
    help_window.geometry("600x700")
    help_window.resizable(False, False)

    # Configure colors
    bg_color = "#2C3E50"  # Dark blue-gray
    text_color = "#ECF0F1"  # Light gray
    header_color = "#3498DB"  # Bright blue

    # Main frame with scrollbar
    main_frame = tk.Frame(help_window, bg=bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Canvas and scrollbar
    canvas = tk.Canvas(main_frame, bg=bg_color)
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg_color)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Custom fonts
    title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
    header_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
    body_font = tkfont.Font(family="Helvetica", size=12)

    # Title
    title_label = tk.Label(
        scrollable_frame, 
        text="Strain Assigner: Step-by-Step Guide", 
        font=title_font, 
        bg=bg_color, 
        fg=text_color,
        pady=10
    )
    title_label.pack(fill=tk.X)

    # Intro text
    intro_label = tk.Label(
        scrollable_frame, 
        text="This screen helps you prepare your experimental plate metadata. Follow these steps carefully to set up your strain information and plate layout.",
        font=body_font, 
        bg=bg_color, 
        fg=text_color,
        wraplength=550,
        justify=tk.LEFT,
        pady=10
    )
    intro_label.pack(fill=tk.X, padx=20)

    # Helper function to create section
    def create_section(title, steps):
        # Section header
        header = tk.Label(
            scrollable_frame, 
            text=title, 
            font=header_font, 
            bg=bg_color, 
            fg=header_color,
            anchor='w',
            pady=10
        )
        header.pack(fill=tk.X, padx=20)

        # Steps
        for step in steps:
            step_label = tk.Label(
                scrollable_frame, 
                text=step, 
                font=body_font, 
                bg=bg_color, 
                fg=text_color,
                wraplength=550,
                justify=tk.LEFT,
                anchor='w'
            )
            step_label.pack(fill=tk.X, padx=40)

    # Step 1: Add Strains
    create_section("Step 1: Add Your Strains", [
        "1. Click in the text field under \"Add a Strain\"",
        "2. Type the name of each unique strain in your experiment",
        "3. Press the \"+\" button to add the strain",
        "4. Each strain will be assigned a unique color automatically"
    ])

    # Step 2: Add a Plate
    create_section("Step 2: Add a Plate", [
        "1. Enter the exact filename for each plate (including extension)",
        "   Example: \"Plate1_experiment.jpg\"",
        "2. Add an Additive (Optional)",
        "   - Check the additive box if your experiment includes additional compounds",
        "   - Enter the additive name if applicable"
    ])

    # Step 3: Assign Strains
    create_section("Step 3: Assign Strains to Positions", [
        "For each plate:",
        "1. Click \"Assign\" next to a strain name",
        "2. Select the correct position on the plate grid",
        "3. Repeat for all strains",
        "4. Verify assignments visually on the plate grid",
        "5. Use \"Next Plate\" and \"Previous Plate\" buttons to move between plates"
    ])

    # Step 4: Preview and Verify
    create_section("Step 4: Preview and Verify", [
        "1. Click \"Preview All Plates\"",
        "2. Review your metadata carefully",
        "3. If you spot an error, use navigation buttons to return to the specific plate and make corrections",
        "4. Once you are finished, click \"Next\" to save the metadata for future use"
    ])

    # Close button
    close_button = tk.Button(
        scrollable_frame, 
        text="Close", 
        command=help_window.destroy,
        font=body_font,
        bg=header_color,
        fg=text_color,
        relief=tk.FLAT
    )
    close_button.pack(pady=20)

    return help_window

# Example usage:
root = tk.Tk()
help_popup = create_help_popup(root)
root.mainloop()
