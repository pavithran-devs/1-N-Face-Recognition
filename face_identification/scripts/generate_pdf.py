import os
import csv
import numpy as np
from fpdf import FPDF

# Path to testing directory
testing_dir = "/home/pavithranraj/Desktop/1:N Face recognition/face_identification/testing"

# Lists to collect data
folder_stats = []        # list of dicts
folder_max_records = []  # list of tuples: (max_score, img_name, matched_name, folder)
folder_min_records = []  # list of tuples: (min_score, img_name, matched_name, folder)

for i in range(1, 21):
    folder_name = f"Test{i}"
    csv_path = os.path.join(testing_dir, folder_name, "results.csv")
    if not os.path.exists(csv_path):
        continue
    
    success_scores = []
    success_records = []
    candidate_name = "N/A"
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status') == 'Success':
                try:
                    score = float(row['similarity_score'])
                    img_name = row['image_name']
                    name = row['matched_name']
                    success_scores.append(score)
                    success_records.append((score, img_name, name, folder_name))
                    if name != 'N/A' and name:
                        candidate_name = name
                except ValueError:
                    pass
    
    if success_records:
        avg_score = np.mean(success_scores)
        max_rec = max(success_records, key=lambda x: x[0])
        folder_max_records.append(max_rec)
        min_rec = min(success_records, key=lambda x: x[0])
        folder_min_records.append(min_rec)
        
        folder_stats.append({
            'folder': folder_name,
            'candidate': candidate_name,
            'avg_score': avg_score,
            'success_count': len(success_scores),
            'max_score': max_rec[0],
            'min_score': min_rec[0]
        })

# Calculations
averages = [f['avg_score'] for f in folder_stats]
average_of_averages = np.mean(averages) if averages else 0.0

folder_max_scores = [rec[0] for rec in folder_max_records]
average_of_highest = np.mean(folder_max_scores) if folder_max_scores else 0.0

folder_min_scores = [rec[0] for rec in folder_min_records]
average_of_lowest = np.mean(folder_min_scores) if folder_min_scores else 0.0

top_10_folder_averages = sorted(folder_stats, key=lambda x: x['avg_score'], reverse=True)[:10]
top_10_highest = sorted(folder_max_records, key=lambda x: x[0], reverse=True)[:10]
top_10_lowest = sorted(folder_min_records, key=lambda x: x[0])[:10]


# PDF Class Definition
class FaceRecognitionReportPDF(FPDF):
    def header(self):
        # Header banner
        self.set_fill_color(30, 41, 59) # Slate 800
        self.rect(0, 0, 210, 32, 'F')
        
        # White text inside banner
        self.set_text_color(255, 255, 255)
        self.set_y(6)
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'Face Recognition System Evaluation Report', ln=True, align='C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, 'Consolidated Statistics Across Test1 - Test20 Folders', ln=True, align='C')
        
        # Reset positioning for page content (below banner)
        self.set_y(38)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 116, 139) # Slate 500
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')


# Create PDF instance
pdf = FaceRecognitionReportPDF(orientation='P', unit='mm', format='A4')
pdf.set_margins(15, 38, 15)
pdf.alias_nb_pages()
pdf.add_page()

# Title Section
pdf.set_text_color(15, 23, 42) # Slate 900
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '1. Overview Statistics', ln=True)
pdf.set_draw_color(226, 232, 240) # Slate 200
pdf.line(15, pdf.get_y(), 195, pdf.get_y())
pdf.ln(4)

# Overview stats block in a clean box
pdf.set_fill_color(248, 250, 252) # Slate 50
pdf.set_text_color(51, 65, 85) # Slate 700
pdf.set_font('Helvetica', '', 10)

pdf.rect(15, pdf.get_y(), 180, 32, 'F')
y_start = pdf.get_y() + 4

pdf.set_y(y_start)
pdf.set_x(20)
pdf.cell(60, 8, 'Average of Folder Averages:')
pdf.set_font('Helvetica', 'B', 10)
pdf.cell(0, 8, f'{average_of_averages:.6f}', ln=True)

pdf.set_x(20)
pdf.set_font('Helvetica', '', 10)
pdf.cell(60, 8, 'Average of Folder Highest Scores:')
pdf.set_font('Helvetica', 'B', 10)
pdf.cell(0, 8, f'{average_of_highest:.6f}', ln=True)

pdf.set_x(20)
pdf.set_font('Helvetica', '', 10)
pdf.cell(60, 8, 'Average of Folder Lowest Scores:')
pdf.set_font('Helvetica', 'B', 10)
pdf.cell(0, 8, f'{average_of_lowest:.6f}', ln=True)

pdf.ln(8)

# Section 2: Folder-by-Folder Statistics
pdf.set_text_color(15, 23, 42) # Slate 900
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '2. Folder-by-Folder Statistics', ln=True)
pdf.line(15, pdf.get_y(), 195, pdf.get_y())
pdf.ln(4)

# Table Header
pdf.set_fill_color(241, 245, 249) # Slate 100
pdf.set_text_color(71, 85, 105) # Slate 600
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(20, 8, 'Folder', border=1, fill=True, align='C')
pdf.cell(45, 8, 'Candidate Name', border=1, fill=True, align='C')
pdf.cell(30, 8, 'Success Matches', border=1, fill=True, align='C')
pdf.cell(30, 8, 'Avg Similarity', border=1, fill=True, align='C')
pdf.cell(28, 8, 'Highest Score', border=1, fill=True, align='C')
pdf.cell(27, 8, 'Lowest Score', border=1, fill=True, align='C', ln=True)

# Table Content
pdf.set_text_color(51, 65, 85) # Slate 700
pdf.set_font('Helvetica', '', 9)

for idx, f in enumerate(folder_stats):
    # Alternating row colors
    fill_row = (idx % 2 == 1)
    if fill_row:
        pdf.set_fill_color(248, 250, 252) # Slate 50
    else:
        pdf.set_fill_color(255, 255, 255)
        
    pdf.cell(20, 7.5, f['folder'], border=1, fill=True, align='C')
    pdf.cell(45, 7.5, f['candidate'], border=1, fill=True, align='L')
    pdf.cell(30, 7.5, str(f['success_count']), border=1, fill=True, align='C')
    pdf.cell(30, 7.5, f"{f['avg_score']:.6f}", border=1, fill=True, align='C')
    pdf.cell(28, 7.5, f"{f['max_score']:.6f}", border=1, fill=True, align='C')
    pdf.cell(27, 7.5, f"{f['min_score']:.6f}", border=1, fill=True, align='C', ln=True)

# Add page break for Section 3 & 4
pdf.add_page()

# Section 3: Top 10 Folder Averages
pdf.set_text_color(15, 23, 42) # Slate 900
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '3. Top 10 Folder Averages', ln=True)
pdf.line(15, pdf.get_y(), 195, pdf.get_y())
pdf.ln(4)

# Table Header
pdf.set_fill_color(241, 245, 249)
pdf.set_text_color(71, 85, 105)
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(15, 8, 'Rank', border=1, fill=True, align='C')
pdf.cell(30, 8, 'Folder', border=1, fill=True, align='C')
pdf.cell(60, 8, 'Matched Candidate', border=1, fill=True, align='C')
pdf.cell(45, 8, 'Avg Similarity Score', border=1, fill=True, align='C')
pdf.cell(30, 8, 'Success Matches', border=1, fill=True, align='C', ln=True)

# Table Content
pdf.set_text_color(51, 65, 85)
pdf.set_font('Helvetica', '', 9)
for idx, f in enumerate(top_10_folder_averages, 1):
    fill_row = (idx % 2 == 1)
    if fill_row:
        pdf.set_fill_color(248, 250, 252)
    else:
        pdf.set_fill_color(255, 255, 255)
        
    pdf.cell(15, 7.5, str(idx), border=1, fill=True, align='C')
    pdf.cell(30, 7.5, f['folder'], border=1, fill=True, align='C')
    pdf.cell(60, 7.5, f" {f['candidate']}", border=1, fill=True, align='L')
    pdf.cell(45, 7.5, f"{f['avg_score']:.6f}", border=1, fill=True, align='C')
    pdf.cell(30, 7.5, str(f['success_count']), border=1, fill=True, align='C', ln=True)

pdf.ln(10)

# Section 4: Top 10 Highest scores
pdf.set_text_color(15, 23, 42) # Slate 900
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '4. Top 10 Highest Individual Similarity Scores (Folder Maxima)', ln=True)
pdf.line(15, pdf.get_y(), 195, pdf.get_y())
pdf.ln(4)

# Table Header
pdf.set_fill_color(241, 245, 249)
pdf.set_text_color(71, 85, 105)
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(15, 8, 'Rank', border=1, fill=True, align='C')
pdf.cell(25, 8, 'Score', border=1, fill=True, align='C')
pdf.cell(70, 8, 'Image Name', border=1, fill=True, align='C')
pdf.cell(25, 8, 'Folder', border=1, fill=True, align='C')
pdf.cell(45, 8, 'Candidate Name', border=1, fill=True, align='C', ln=True)

# Table Content
pdf.set_text_color(51, 65, 85)
pdf.set_font('Helvetica', '', 9)
for idx, item in enumerate(top_10_highest, 1):
    fill_row = (idx % 2 == 1)
    if fill_row:
        pdf.set_fill_color(248, 250, 252)
    else:
        pdf.set_fill_color(255, 255, 255)
        
    pdf.cell(15, 7.5, str(idx), border=1, fill=True, align='C')
    pdf.cell(25, 7.5, f"{item[0]:.6f}", border=1, fill=True, align='C')
    pdf.cell(70, 7.5, f" {item[1]}", border=1, fill=True, align='L')
    pdf.cell(25, 7.5, item[3], border=1, fill=True, align='C')
    pdf.cell(45, 7.5, f" {item[2]}", border=1, fill=True, align='L', ln=True)

# Add page break before Section 5
pdf.add_page()

# Section 5: Top 10 Lowest scores
pdf.set_text_color(15, 23, 42)
pdf.set_font('Helvetica', 'B', 12)
pdf.cell(0, 8, '5. Top 10 Lowest Individual Similarity Scores (Folder Minima)', ln=True)
pdf.line(15, pdf.get_y(), 195, pdf.get_y())
pdf.ln(4)

# Table Header
pdf.set_fill_color(241, 245, 249)
pdf.set_text_color(71, 85, 105)
pdf.set_font('Helvetica', 'B', 9)
pdf.cell(15, 8, 'Rank', border=1, fill=True, align='C')
pdf.cell(25, 8, 'Score', border=1, fill=True, align='C')
pdf.cell(70, 8, 'Image Name', border=1, fill=True, align='C')
pdf.cell(25, 8, 'Folder', border=1, fill=True, align='C')
pdf.cell(45, 8, 'Candidate Name', border=1, fill=True, align='C', ln=True)

# Table Content
pdf.set_text_color(51, 65, 85)
pdf.set_font('Helvetica', '', 9)
for idx, item in enumerate(top_10_lowest, 1):
    fill_row = (idx % 2 == 1)
    if fill_row:
        pdf.set_fill_color(248, 250, 252)
    else:
        pdf.set_fill_color(255, 255, 255)
        
    pdf.cell(15, 7.5, str(idx), border=1, fill=True, align='C')
    pdf.cell(25, 7.5, f"{item[0]:.6f}", border=1, fill=True, align='C')
    pdf.cell(70, 7.5, f" {item[1]}", border=1, fill=True, align='L')
    pdf.cell(25, 7.5, item[3], border=1, fill=True, align='C')
    pdf.cell(45, 7.5, f" {item[2]}", border=1, fill=True, align='L', ln=True)

# Output PDF to file
output_pdf_path = os.path.join(testing_dir, "consolidated_evaluation_report.pdf")
pdf.output(output_pdf_path)
print(f"PDF generated successfully at: {output_pdf_path}")
