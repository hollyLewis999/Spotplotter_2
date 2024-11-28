from PIL import ImageFont

# List of common fonts
common_fonts = [
    "Arial", "Calibri", "Comic Sans MS", "Courier New", "Georgia",
    "Times New Roman", "Verdana", "Tahoma", "Helvetica", "DejaVu Sans"
]

for font in common_fonts:
    try:
        # Try loading the font at a specific size (e.g., 32)
        label_font = ImageFont.truetype("helvetica.ttf", 32)
        print(f"Font '{font}' loaded successfully")
        break
    except IOError:
        print(f"Font '{font}' not found, trying next.")