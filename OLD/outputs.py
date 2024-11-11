import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from pathlib import Path
import seaborn as sns
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as ImageR
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from io import BytesIO
import cv2
import sys
#from PIL import Image 
from datetime import datetime
from tkinter import filedialog, simpledialog
import os
import sys
import openpyxl




FONT = "Microsoft New Tai Lue"
plt.rcParams['font.family'] = FONT
sns.set_style("whitegrid")

sys.path.append(r'C:\Users\ThinkPad\AppData\Roaming\Python\Python312\site-packages')
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\ThinkPad\Documents\AA ACADEMIC 2024\Thesis\GUI\assets\frame0")


def write_image_info_to_file(window, figA, statsA, figB, statsB, figC, statsC, pdf_filename):
    #get save location and file name
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save Data and Create Folder"
    )
    if not file_path:
        return
    
    #the first part is the save location and the second part will be the file name
    save_location, filename = os.path.split(file_path)
    folder_name = os.path.splitext(filename)[0]  # Remove extension
    
    #making noew folder with specified name
    new_folder_path = os.path.join(save_location, folder_name)
    os.makedirs(new_folder_path, exist_ok=True)
    
    #filepath must now be insdie new solder
    file_path = os.path.join(new_folder_path, f"{folder_name}_rawdata.xlsx")
    
    #make excel file
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Image Data"
    

    #in future this should be variable to account for different experiment values
    dilutionSeries = [0, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
    
    headers = ["filename", "type", "detergent", "treatment", "repeat", "strain", "quantification", "fold_dilution", "normalization_value", "normalized_value"]
    ws.append(headers)
    #normalisation values is the average of the non ATP quantifications
    norm_value_A = (window.image_info[0]['QuantificationA'][0] + window.image_info[1]['QuantificationA'][0])/2
    norm_value_B = (window.image_info[0]['QuantificationB'][0] + window.image_info[1]['QuantificationB'][0])/2
    norm_value_C = (window.image_info[0]['QuantificationC'][0] + window.image_info[1]['QuantificationC'][0])/2


    #chatGBT helped with tidy data format
    for info in window.image_info:
        current_filename = info.get('filename', 'Unknown')  # Use a default if filename is not available
        base_row = [current_filename, info['type'], info['detergent'], info['treatment'], info['repeat']]
        

        def add_strain_rows(strain, quant_list, norm_value):
            for quant, dilution in zip(quant_list, dilutionSeries[:len(quant_list)]):
                normalized_value = 100 * quant / norm_value if norm_value else None
                row = base_row + [strain, quant, dilution, norm_value, normalized_value]
                ws.append(row)
        

        if info['QuantificationA']:
            add_strain_rows(info['strainA'], info['QuantificationA'], norm_value_A)
        if info['QuantificationB']:
            add_strain_rows(info['strainB'], info['QuantificationB'], norm_value_B)
        if info['QuantificationC']:
            add_strain_rows(info['strainC'], info['QuantificationC'], norm_value_C)
    
    #excel
    wb.save(file_path)
    
    #pdf
    pdf_filename = os.path.join(new_folder_path, f"{folder_name}_report.pdf")
    generate_pdf_report(window, figA, statsA, figB, statsB, figC, statsC, pdf_filename)
    
    #images
    save_graph_image(figA, os.path.join(new_folder_path, f"{folder_name}_{window.image_info[0]['strainA']}.png"))
    save_graph_image(figB, os.path.join(new_folder_path, f"{folder_name}_{window.image_info[0]['strainB']}.png"))
    save_graph_image(figC, os.path.join(new_folder_path, f"{folder_name}_{window.image_info[0]['strainC']}.png"))
    
    print(f"Files saved successfully in folder: {new_folder_path}")

#higher quality than in the report
def save_graph_image(fig, filename):
    fig.savefig(filename, format='png', dpi=300, bbox_inches='tight')




#  d888b  d8888b.  .d8b.  d8888b. db   db .d8888. 
# 88' Y8b 88  `8D d8' `8b 88  `8D 88   88 88'  YP 
# 88      88oobY' 88ooo88 88oodD' 88ooo88 `8bo.   
# 88  ooo 88`8b   88~~~88 88~~~   88~~~88   `Y8b. 
# 88. ~8~ 88 `88. 88   88 88      88   88 db   8D 
#  Y888P  88   YD YP   YP 88      YP   YP `8888Y' 



#normalise each quantification so that they are all a percentage
def normalize_array(arr, nom_value):
    normalized = []
    for val in arr:
        normalized.append(100 * val / nom_value)
    return normalized


def calculate_statistics(x, y, color, label):
    valid_x = []
    valid_y = []
    #only using ones that are above 10% becuse at that point there are a lot of very light ones that arent quantified and otherwise there are a lot of zeros
    for xi, yi in zip(x, y):
        if xi > 0 and yi > 10:
            #convert it to log 10 becuse of the dilution sequence
            valid_x.append(np.log10(xi))
            valid_y.append(yi)
    

    if len(valid_x) > 1:
        #getting all the statistics
        slope, intercept, r_value, p_value, std_err = stats.linregress(valid_x, valid_y)
        r_squared = r_value ** 2
        m, b = np.polyfit(valid_x, valid_y, 1)
        y_cut = b
        x_cut = 10 ** (-b / m)
        x_at_y50 = 10 ** ((50 - b) / m)
        formula = f"y = {m:.2f} * log10(x) + {b:.2f}"
        

        #retrun as a dictionart since it very nice to call values from
        return {
            'slope': m,
            'intercept': b,
            'r_squared': r_squared,
            'formula': formula,
            'y_cut': y_cut,
            'x_cut': x_cut,
            'x_at_y50': x_at_y50,
            'label': label
        }
    
    return None
def plot_logarithmic_graph(y1, y2, y3, y4, title, key1, key2, key3, key4):
    dilutionSeries = [1, 2, 4, 8, 10, 16, 20, 32, 40, 64, 80, 100, 128, 160, 200, 320, 400, 640, 800, 1000, 1280, 1600, 2000, 3200, 4000, 6400, 8000, 12800, 16000, 32000, 64000, 128000]
    
    #normalisation value is the average of the first spot of the 2 non ATP
    normValue = (y1[0] + y2[0]) / 2

    for y in [y1, y2, y3, y4]:
        norm_y = normalize_array(y, normValue)  # Normalize the array
        y_data.append(norm_y)

    #so that it can be looped through
    colors = ['#073B3A', '#0F8660', '#D3784A', '#D24C4A']
    markers = ['o', 's', '^', 'D']
    labels = [key1, key2, key3, key4]
    ATcs = ["-ATc", "-ATc", "+ATc", "+ATc"] #this asumes that the first two are ATC- but this should be changed at a later point
    statistics = []


    plt.figure(figsize=(12, 8))
    sns.set_context("notebook", font_scale=1.2)
    plt.xscale('log')
    ax = plt.gca()
    ax.set_facecolor('#F5F5F5') #very light grey

    


    for y, color, marker, label, ATc in zip(y_data, colors, markers, labels, ATcs):
        stats = calculate_statistics(dilutionSeries, y, color, label)
        if stats is not None:

            statistics.append(stats)
            label = ATc + " (" + label + " )"  #atc label and then the plate name in brackets
            sns.scatterplot(x=dilutionSeries, y=y, color=color, marker=marker, label=label, s=80)
            x_fit = np.logspace(np.log10(min(dilutionSeries)), np.log10(max(dilutionSeries)), num=100)
            y_fit = stats['slope'] * np.log10(x_fit) + stats['intercept']
            plt.plot(x_fit, y_fit, color=color, linestyle='--', label=("R² =" + str(round(stats['r_squared'], 3)) + "\n" + stats['formula'] + "\n")) #this is  a seperate plot plotting the line
    
    plt.title(f"Growth Curve for {title}", fontsize=20, fontweight='bold', pad=20)
    plt.ylim(0, 120)
    plt.xlabel('Dilution Series', fontsize=16, fontweight='bold')
    plt.ylabel('Relative Growth (%)', fontsize=16, fontweight='bold')
    plt.legend(fontsize=14, loc='upper right', bbox_to_anchor=(0.98, 0.98),
               ncol=1, frameon=True, facecolor='white', edgecolor='none', framealpha=0.7)
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.tight_layout()


    return plt.gcf(), statistics







# d8888b. d8888b. d88888b 
# 88  `8D 88  `8D 88'     
# 88oodD' 88   88 88ooo   
# 88~~~   88   88 88~~~   
# 88      88  .8D 88      
# 88      Y8888D' YP      

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def cv2_to_pil(cv2_img, convertColour = True):
    if cv2_img is None:
        return None
    if len(cv2_img.shape) == 2: #2 channels = greyscale
        return Image.fromarray(cv2_img)
    elif len(cv2_img.shape) == 3 and convertColour:  #3 channels = color
        return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))
    else:
        return Image.fromarray(cv2_img) 

#determining which proportion the image is contrained by and using that ration to keep everything the same proportion
def get_image_size(img, max_width, max_height):
    img_width, img_height = img.size
    aspect_ratio = img_width / img_height
    if img_width > max_width:
        img_width = max_width
        img_height = img_width / aspect_ratio
    if img_height > max_height:
        img_height = max_height
        img_width = img_height * aspect_ratio
    return img_width, img_height


def generate_pdf_report(window, figA, statsA, figB, statsB, figC, statsC, output_filename):

    doc = SimpleDocTemplate(output_filename, pagesize=letter, topMargin=0*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=16, alignment=1)
    heading_style = ParagraphStyle(name='Heading', parent=styles['Heading2'], fontSize=12)
    body_style = ParagraphStyle(name='Body', parent=styles['BodyText'], fontSize=8)


    logo_path = relative_to_assets("LogoHorizontalDark.png")
    logo = ImageR(logo_path, width=1170/4, height=407/4)

    #same color_scheme as before - should make it a global variable
    color_scheme = ['#073B3A', '#0F8660', '#D3784A', '#D24C4A']

    def add_plot_and_stats(fig, stats, strain):
        story.append(logo)
        story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

        #saving it in lower quality
        img_data = BytesIO()
        fig.savefig(img_data, format='png', dpi=150, bbox_inches='tight')
        img_data.seek(0)

        
        story.append(ImageR(img_data, width=6*inch, height=4*inch))
        story.append(Spacer(1, 80))


        #Used Chagbt to help generate this table
        table_data = [[''] + [stat['label'] for stat in stats]]
        for row_label in ['Formula', 'Slope', 'Intercept', 'R-squared', 'Y-cut', 'X-cut', 'X at Y=50']:
            row = [row_label]
            for stat in stats:
                if row_label == 'Formula':
                    value = stat['formula']
                elif row_label == 'R-squared':
                    value = f"{stat['r_squared']:.3f}"
                elif row_label == 'X at Y=50':
                    value = f"{stat['x_at_y50']:.2f}"
                else:
                    key = row_label.lower().replace('-', '_')
                    value = f"{stat[key]:.2f}"
                row.append(value)
            table_data.append(row)

        table = Table(table_data)
        table_style = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]

        for i in range(1, len(table_data[0])):
            table_style.append(('BACKGROUND', (i, 0), (i, 0), colors.HexColor(color_scheme[(i-1) % len(color_scheme)])))

        table.setStyle(TableStyle(table_style))
        story.append(table)
        story.append(PageBreak())

    def add_info_page(info):
        story.append(logo)
        story.append(Spacer(1, 1))
        
        #header to show connected info with titiles bolded
        header_text = f"""<br/><br/><br/><br/>
        <b>Filename:</b> &nbsp; {info['filename']}<br/>
        <b>Type:</b> &nbsp; {info['type']}<br/>
        <b>Detergent:</b> &nbsp; {info['detergent']}<br/>
        <b>Treatment:</b> &nbsp; {info['treatment']}<br/>
        <b>Repeat:</b> &nbsp; {info['repeat']}<br/>
        <b>Strain A:</b> &nbsp; {info['strainA']}<br/>
        <b>Strain B:</b> &nbsp; {info['strainB']}<br/>
        <b>Strain C:</b> &nbsp; {info['strainC']}<br/>
        <b>Parameters Used:</b> &nbsp;<br/>
        <b>Threshold:</b> &nbsp {info['threshold']}<br/>
        <b>Minimum Area:</b> &nbsp {info['smallArea']}<br/>
        """
        
        max_width = 230
        max_height = 200
        
        def create_image_with_caption(img_key, caption, max_width=max_width, max_height=max_height):
            if info[img_key] is not None:
                if img_key == "IMGgrid": #this is to deal with the RGB and BGR conversion, the otherone is an okay colour
                    pil_img = cv2_to_pil(info[img_key], False)
                else:
                    pil_img = cv2_to_pil(info[img_key])
                if pil_img:
                    img_width, img_height = get_image_size(pil_img, max_width, max_height)
                    img_data = BytesIO()
                    #saving to 40% quality
                    pil_img.save(img_data, format='JPEG', quality=40) 
                    img_data.seek(0)
                    img = ImageR(img_data, width=img_width, height=img_height)
                    return [img, Paragraph(caption, body_style)]
            return [Paragraph("Image not available", body_style), Paragraph(caption, body_style)]
        
        # Create top row table - ChatGBT
        top_row_data = [
            [Paragraph(header_text, body_style), create_image_with_caption('IMGcontours', "Contours Image", max_width = 350, max_height =300 )]
        ]
        top_row_table = Table(top_row_data, colWidths=[150, 350])
        top_row_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        # Create bottom row table - ChatGBT
        bottom_row_data = [
            [create_image_with_caption('IMGbinary', "Binary Image"), create_image_with_caption('IMGgrid', "Grid Image")]
        ]
        bottom_row_table = Table(bottom_row_data, colWidths=[250, 250])
        bottom_row_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        #adding the tables
        story.append(top_row_table)
        story.append(bottom_row_table)
        story.append(PageBreak())

    def add_final_info_page():
        story.append(logo)
        story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

        current_date = datetime.now().strftime("%Y-%m-%d")
        
        
        info_text = f"""
        This report was generated by <b>Spotplotter</b> version <b>1.0</b> on <b>{current_date}</b>

        Spotplotter was created by <b>Holly Lewis</b> with supervision from <b>R Verrinder</b> and <b>Dr. M Mason</b> as BSc (Eng) final year project submitted in partial fulfilment of the requirements for the degree of Bachelor of Science in Electrical and Computer Engineering in the Department of Electrical Engineering at the University of Cape Town.

        To read the full report please see: <i>GITHUB LINK</i>


        <b>Formula:</b> The formula represents the linear regression equation that models determined using the by linregress function from scipy.stats which determines the relationship between the logarithm of the dilution series and relative growth. It follows the form:
        y = m ⋅ log10(x) + b

        <b>Normalization:</b> The relative growth values were normalized to a baseline to make the results comparable across different conditions. The quantified values of each spot were divided by the average value of the first spot in the -ATP for each strain.

        <b>The slope (m):</b> indicates the rate of change in relative growth as the dilution series increases (on a logarithmic scale). A steep slope indicated that the growth has a faster knockdown as the dilution changes. A shallow slope indicates that the growth is more stable across dilutions.

        <b>The intercept (b)</b> and y-cut is the relative growth when the solution is not diluted.

        <b>The R-squared value</b> measures how well the linear regression line fits the data, where 1 represents a perfect fit and 0 represents no relationship. Higher R² values indicates that the growth follows a linear relationship.

        <b>The X-cut</b> refers to the point where the regression line crosses the x-axis, indicating the dilution value at which the relative growth would theoretically be zero (no growth).

        <b>X at Y = 50:</b> This value represents the dilution series value when the relative growth is 50% i.e., the knockdown is 50% in comparison to the -ATP series.
        """

        for paragraph in info_text.split('\n\n'):
            story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 6))

    #create plots of each one
    add_plot_and_stats(figA, statsA, window.image_info[0]['strainA'])
    add_plot_and_stats(figB, statsB, window.image_info[0]['strainB'])
    add_plot_and_stats(figC, statsC, window.image_info[0]['strainC'])

    #this should ways be 4
    for info in window.image_info:
        add_info_page(info)

    add_final_info_page()
    doc.build(story)





def generate_all_outputs(window):

    #plots and statistics from image info
    figA, statsA = plot_logarithmic_graph(window.image_info[0]['QuantificationA'], window.image_info[1]['QuantificationA'], window.image_info[2]['QuantificationA'], window.image_info[3]['QuantificationA'], window.image_info[0]['strainA'],window.image_info[0]['filename'].split('.')[0], window.image_info[1]['filename'].split('.')[0], window.image_info[2]['filename'].split('.')[0],  window.image_info[3]['filename'].split('.')[0])
    figB, statsB = plot_logarithmic_graph(window.image_info[0]['QuantificationB'], window.image_info[1]['QuantificationB'], window.image_info[2]['QuantificationB'], window.image_info[3]['QuantificationB'], window.image_info[0]['strainB'], window.image_info[0]['filename'].split('.')[0], window.image_info[1]['filename'].split('.')[0], window.image_info[2]['filename'].split('.')[0],  window.image_info[3]['filename'].split('.')[0])
    figC, statsC = plot_logarithmic_graph(window.image_info[0]['QuantificationC'], window.image_info[1]['QuantificationC'], window.image_info[2]['QuantificationC'], window.image_info[3]['QuantificationC'], window.image_info[0]['strainC'], window.image_info[0]['filename'].split('.')[0], window.image_info[1]['filename'].split('.')[0], window.image_info[2]['filename'].split('.')[0],  window.image_info[3]['filename'].split('.')[0])

    #report
    output_filename = "growth_curves_report.pdf"
    write_image_info_to_file(window, figA, statsA, figB, statsB, figC, statsC, output_filename)
    plt.close('all')





#ONLY FOR TESTING: HARD CODED VALUES ARE ALL FAKE AND GENERATED BY CHATGBT
# class MockWindow:
#     def __init__(self):
#         self.image_info = [
#             {
#                 'filename': 'test_image.jpg',
#                 'type': 'Growth Curve',
#                 'detergent': 'SDS',
#                 'treatment': 'Heat Shock',
#                 'repeat': '1',
#                 'strainA': 'E. coli K-12',
#                 'strainB': 'E. coli BL21',
#                 'strainC': 'E. coli DH5α',
#                 'IMGcontours': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'IMGbinary': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'IMGgrid': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'threshold': 128,
#                 'smallArea': 50,
#                 'QuantificationB': [300, 11485, 11504, 11271, 12283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0],
#                 'QuantificationC': [200, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0],
#                 'QuantificationA' :[100, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
           
           
#             },
#             {
#                 'filename': 'experiment2_image.jpg',
#                 'type': 'Protein Expression',
#                 'detergent': 'Triton X-100',
#                 'treatment': 'Cold Shock',
#                 'repeat': '2',
#                 'strainA': 'E. coli K-12',
#                 'strainB': 'E. coli BL21',
#                 'strainC': 'Pseudomonas aeruginosa',
#                 'IMGcontours': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'IMGbinary': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'IMGgrid': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'threshold': 140,
#                 'smallArea': 60,
#                 'QuantificationC': [400, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0],
#                 'QuantificationB': [600, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0],
#                 'QuantificationA' :[200, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
           
#             },
#             {
#                 'filename': 'experiment3_image.jpg',
#                 'type': 'Biofilm Formation',
#                 'detergent': 'Tween 20',
#                 'treatment': 'UV Exposure',
#                 'repeat': '1',
#                 'strainA': 'Bacillus subtilis',
#                 'strainB': 'E. coli K-12',
#                 'strainC': 'Staphylococcus aureus',
#                 'IMGcontours': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'IMGbinary': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'IMGgrid': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'threshold': 150,
#                 'smallArea': 40,
#                 'QuantificationA': [32104, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0],
#                 'QuantificationB': [35381, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0],
#                 'QuantificationC' :[20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
#             },
#             {
#                 'filename': 'experiment4_image.jpg',
#                 'type': 'Antibiotic Resistance',
#                 'detergent': 'SDS',
#                 'treatment': 'Heat Shock',
#                 'repeat': '3',
#                 'strainA': 'E. coli K-12',
#                 'strainB': 'Salmonella enterica',
#                 'strainC': 'Pseudomonas aeruginosa',
#                 'IMGcontours': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'IMGbinary': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'IMGgrid': np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8),
#                 'threshold': 135,
#                 'smallArea': 55,
#                 'QuantificationB': [32104, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0],
#                 'QuantificationA': [35381, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0],
#                 'QuantificationC' :[2644, 1099, 1724, 1425, 1952, 1382, 1310, 1245, 600, 1173, 223, 45, 277, 38, 0, 0, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
            
#             }

#         ]



# # Mock data
# y1 = [32104, 21485, 19504, 18271, 17283, 10029, 20164, 9907, 10611, 12160, 9120, 8598, 2442, 4719, 8308, 4957, 7553, 1160, 2043, 695, 0, 3840, 2944, 2703, 939, 0, 533, 0, 731, 0, 0, 0]
# y2 = [35381, 27773, 29721, 26322, 20777, 27826, 22096, 25658, 15214, 18442, 16458, 11103, 11263, 11343, 11245, 4970, 9886, 3830, 5635, 3304, 4045, 3195, 2033, 3204, 1140, 2708, 224, 134, 0, 0, 0, 0]
# y3 = [18909, 16152, 13604, 12738, 12577, 8611, 14617, 6462, 3661, 1967, 3733, 990, 1650, 590, 662, 0, 203, 0, 161, 0, 0, 0, 0, 0, 0, 165, 0, 0, 0, 0, 0, 0]
# y4 = [20644, 17099, 17124, 14325, 11952, 13282, 13110, 12045, 6060, 10173, 2723, 405, 2177, 368, 0, 0, 580, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 229, 0, 0, 0, 0]
# root = tk.Tk()
# root.withdraw() 

# window = MockWindow()