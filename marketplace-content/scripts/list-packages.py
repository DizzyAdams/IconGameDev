# List .mcpack files and generate CSV summary
import os, csv
output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
mcpack_files = [f for f in os.listdir(output_dir) if f.endswith('.mcpack')]
csv_path = os.path.join(output_dir, 'mcpack_summary.csv')
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Filename', 'Size_bytes'])
    for f in sorted(mcpack_files):
        size = os.path.getsize(os.path.join(output_dir, f))
        writer.writerow([f, size])
print(f"CSV written to {csv_path}")
