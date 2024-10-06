from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from  reportlab.platypus import Image as ImageReport
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO
import matplotlib.pyplot as plt

def generate_pdf_report(window, figA, statsA, figB, statsB, figC, statsC, output_filename):
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    story = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=18, alignment=1)
    heading_style = ParagraphStyle(name='Heading', parent=styles['Heading2'], fontSize=14)
    body_style = ParagraphStyle(name='Body', parent=styles['BodyText'], fontSize=10)

    # Logo
    logo_path = relative_to_assets("image_1.png")
    logo = ImageReport(logo_path, width=100, height=50)  # Adjust size as needed

    # Function to add a plot and its statistics to the story
    def add_plot_and_stats(fig, stats, strain):
        # Add logo
        story.append(logo)
        story.append(Spacer(1, 12))

        # Add title
        story.append(Paragraph(f"Growth Curve for {strain}", title_style))
        story.append(Spacer(1, 12))

        # Save plot to a BytesIO object
        img_data = BytesIO()
        fig.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
        img_data.seek(0)
        
        # Add plot
        story.append(ImageReport(img_data, width=450, height=300))
        story.append(Spacer(1, 12))

        # Add statistics
        story.append(Paragraph("Statistics:", heading_style))
        for stat in stats:
            data = [
                ["Label", stat['label']],
                ["Slope", f"{stat['slope']:.2f}"],
                ["Intercept", f"{stat['intercept']:.2f}"],
                ["R-squared", f"{stat['r_squared']:.3f}"],
                ["Formula", stat['formula']],
                ["Y-cut", f"{stat['y_cut']:.2f}"],
                ["X-cut", f"{stat['x_cut']:.2f}"],
                ["X at Y=50", f"{stat['x_at_y50']:.2f}"]
            ]
            t = Table(data, colWidths=[100, 300])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(t)
            story.append(Spacer(1, 12))

        story.append(Spacer(1, 24))

    # Add plots and statistics for each strain
    add_plot_and_stats(figA, statsA, window.image_info[0]['strainA'])
    story.append(Spacer(1, 24))  # Add a page break
    add_plot_and_stats(figB, statsB, window.image_info[0]['strainB'])
    story.append(Spacer(1, 24))  # Add a page break
    add_plot_and_stats(figC, statsC, window.image_info[0]['strainC'])

    # Build the PDF
    doc.build(story)

# Usage
