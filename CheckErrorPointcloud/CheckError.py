import laspy
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
import matplotlib.pyplot as plt

# กำหนดชื่อไฟล์
lidar_file = "Damblock_Ground.las"
topo_file = "Topo-mlm.csv"
output_file = "error_analysis.csv"
filtered_output_file_0_30 = "error_filtered_0_to_0.30.csv"

# โหลดไฟล์ LiDAR
las = laspy.read(lidar_file)
lidar_points = np.vstack((las.x, las.y, las.z)).T

# โหลดข้อมูล TOPO RTK
topo_data = pd.read_csv(topo_file)
topo_points = topo_data[['Easting', 'Northing', 'Elevation']].values

tree = KDTree(lidar_points[:, :2]) 
distances, indices = tree.query(topo_points[:, :2]) 

# กำหนด threshold
threshold = 1

# คำนวณค่าความคลาดเคลื่อนทางดิ่ง (ΔZ = Z_Topo - Z_LiDAR) โดยกำหนด NaN หากไม่ตรงเงื่อนไข
z_error = np.full(len(topo_points), np.nan)  # กำหนดค่าเริ่มต้นเป็น NaN
valid_mask = distances <= threshold  # ตรวจสอบว่าจุดที่ match กันอยู่ในระยะที่กำหนด
z_error[valid_mask] = topo_points[valid_mask, 2] - lidar_points[indices[valid_mask], 2]

topo_data["Z_error"] = z_error

# กำหนดช่วงค่าตามเกณฑ์
bins = [0, 0.05, 0.15, 0.30, 0.50, 1.00, 50.00]
bin_labels = ["0 to +/-0.05", "+/-0.05 to +/-0.15", "+/-0.15 to +/-0.30", "+/-0.30 to +/-0.50", "+/-0.50 to +/-1.00", "+/-1.00 to +/-50"]
topo_data["Z_error_category"] = pd.cut(abs(z_error), bins=bins, labels=bin_labels, include_lowest=True, ordered=True)

# คำนวณเปอร์เซ็นต์ของแต่ละช่วง และเรียงตามลำดับที่กำหนด
category_counts = topo_data["Z_error_category"].value_counts(normalize=True) * 100
category_counts = category_counts.reindex(bin_labels)  # จัดเรียงลำดับ

# บันทึกผลลัพธ์เป็น CSV
topo_data.to_csv(output_file, index=False, encoding='utf-8')

# กรองเฉพาะค่าความคลาดเคลื่อนในช่วง 0 ถึง +/-0.30
filtered_data_0_30 = topo_data[topo_data["Z_error_category"].isin(["0 to +/-0.05", "+/-0.05 to +/-0.15", "+/-0.15 to +/-0.30"])]
filtered_data_0_30.to_csv(filtered_output_file_0_30, index=False, encoding='utf-8')

# แสดงตารางเปอร์เซ็นต์
print("\nPercentage of Errors by Category:\n")
print(category_counts.to_frame("Percentage (%)").to_string(index=True))

# แสดง histogram ของค่าความคลาดเคลื่อน จำกัดที่ 1 เมตร
plt.figure(figsize=(8,5))
plt.hist(z_error[~np.isnan(z_error) & (abs(z_error) <= 1)], bins=np.linspace(0, 1, 50), edgecolor="black")
plt.xlabel("Vertical Error (ΔZ) [meters]")
plt.ylabel("Frequency")
plt.title("Distribution of Vertical Error (TOPO RTK vs LiDAR)")
plt.grid(True)
plt.xlim(0, 1)  # กำหนดค่าแกน X สูงสุดที่ 1 เมตร
plt.show()

print(f"ผลลัพธ์ถูกบันทึกในไฟล์: {output_file}")
print(f"ไฟล์ที่มีเฉพาะค่าความคลาดเคลื่อน 0 ถึง +/-0.30 ถูกบันทึกใน: {filtered_output_file_0_30}")