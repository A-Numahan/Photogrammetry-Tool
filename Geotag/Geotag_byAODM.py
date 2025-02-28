from PIL import Image
import piexif
import os
import pandas as pd

def geotag_images_from_csv(csv_file):
    # อ่าน CSV
    data = pd.read_csv(csv_file)

    for index, row in data.iterrows():
        image_path = row['image_path']
        latitude = row['latitude']
        longitude = row['longitude']
        altitude = row['altitude']  # อ่านค่าระดับ

        # เปิดภาพ
        image = Image.open(image_path)

        # สร้างข้อมูล EXIF สำหรับ GPS
        exif_dict = piexif.load(image.info.get("exif", b''))
        gps_ifd = {
            2: ((int(latitude), 1), (int((latitude % 1) * 60 * 10000), 10000), (int((latitude * 3600) % 60 * 10000), 10000)),  # GPSLatitude
            1: "N" if latitude >= 0 else "S",  # GPSLatitudeRef
            4: ((int(longitude), 1), (int((longitude % 1) * 60 * 10000), 10000), (int((longitude * 3600) % 60 * 10000), 10000)),  # GPSLongitude
            3: "E" if longitude >= 0 else "W",  # GPSLongitudeRef
            6: (int(altitude * 100), 100)  # GPSAltitude
        }
        exif_dict["GPS"] = gps_ifd

        # บันทึกภาพใหม่พร้อม EXIF ที่อัปเดต
        exif_bytes = piexif.dump(exif_dict)
        new_image_path = os.path.splitext(image_path)[0] + "_geotagged.jpg"
        image.save(new_image_path, "jpeg", exif=exif_bytes)
        print(f"Geotagged: {new_image_path}")

# ใช้งานฟังก์ชัน
geotag_images_from_csv("POS_Paksong.csv")  # แทนที่ด้วยชื่อไฟล์ CSV ของคุณ
# format 
# image_path,latitude,longitude,altitude
# /path/to/image1.jpg,13.7563,100.5018,50.0
# /path/to/image2.jpg,14.5995,120.9842,75.5
