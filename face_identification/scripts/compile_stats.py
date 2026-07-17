import os
import csv
import numpy as np

# Path to testing directory
testing_dir = "/home/pavithranraj/Desktop/1:N Face recognition/face_identification/testing"

# Lists to collect data
folder_stats = []        # list of dicts: {folder, candidate, avg_score, success_count, max_score, min_score}
folder_max_records = []  # list of tuples: (max_score, img_name, matched_name, folder)
folder_min_records = []  # list of tuples: (min_score, img_name, matched_name, folder)

for i in range(1, 21):
    folder_name = f"Test{i}"
    csv_path = os.path.join(testing_dir, folder_name, "results.csv")
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found.")
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
        
        # Find maximum record in this folder
        max_rec = max(success_records, key=lambda x: x[0])
        folder_max_records.append(max_rec)
        
        # Find minimum record in this folder
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

# Calculate average of highest scores
folder_max_scores = [rec[0] for rec in folder_max_records]
average_of_highest = np.mean(folder_max_scores) if folder_max_scores else 0.0

# Calculate average of lowest scores
folder_min_scores = [rec[0] for rec in folder_min_records]
average_of_lowest = np.mean(folder_min_scores) if folder_min_scores else 0.0

# Top 10 folder averages
top_10_folder_averages = sorted(folder_stats, key=lambda x: x['avg_score'], reverse=True)[:10]

# Top 10 highest among the 20 folder-level max scores
top_10_highest = sorted(folder_max_records, key=lambda x: x[0], reverse=True)[:10]

# Top 10 lowest among the 20 folder-level min scores (sorted ascending)
top_10_lowest = sorted(folder_min_records, key=lambda x: x[0])[:10]

# Print report in markdown format
print("# Consolidated 1:N Face Recognition Evaluation Report (Test1 - Test20)")
print("\n## Overview Statistics")
print(f"- **Average of the Averages**: `{average_of_averages:.6f}`")
print(f"- **Average of the Highest Scores**: `{average_of_highest:.6f}`")
print(f"- **Average of the Lowest Scores**: `{average_of_lowest:.6f}`")

print("\n## Folder-by-Folder Statistics")
print("| Folder | Matched Candidate | Success Matches | Average Similarity | Highest Score | Lowest Score |")
print("| :--- | :--- | :---: | :---: | :---: | :---: |")
for f in folder_stats:
    print(f"| {f['folder']} | {f['candidate']} | {f['success_count']} | **{f['avg_score']:.6f}** | **{f['max_score']:.6f}** | **{f['min_score']:.6f}** |")

print("\n## Top 10 Folder Averages")
print("| Rank | Folder | Matched Candidate | Average Similarity Score | Success Matches |")
print("| :---: | :---: | :--- | :---: | :---: |")
for idx, f in enumerate(top_10_folder_averages, 1):
    print(f"| {idx} | **{f['folder']}** | {f['candidate']} | **{f['avg_score']:.6f}** | {f['success_count']} |")

print("\n## Top 10 Highest Individual Similarity Scores (Folder Maxima)")
print("| Rank | Score | Image Name | Folder | Matched Candidate |")
print("| :---: | :---: | :--- | :---: | :--- |")
for idx, item in enumerate(top_10_highest, 1):
    print(f"| {idx} | **{item[0]:.6f}** | {item[1]} | {item[3]} | {item[2]} |")

print("\n## Top 10 Lowest Individual Similarity Scores (Folder Minima)")
print("| Rank | Score | Image Name | Folder | Matched Candidate |")
print("| :---: | :---: | :--- | :---: | :--- |")
for idx, item in enumerate(top_10_lowest, 1):
    print(f"| {idx} | **{item[0]:.6f}** | {item[1]} | {item[3]} | {item[2]} |")
