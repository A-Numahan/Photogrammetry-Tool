
library(exifr)
library(sf)
library(dplyr)


get_gps_coordinates <- function(image_path) {
  exif_data <- tryCatch({
    exifr::read_exif(image_path)
  }, error = function(e) {
    return(NULL)
  })
  

  if ("GPSLatitude" %in% colnames(exif_data) && "GPSLongitude" %in% colnames(exif_data)) {
    gps_coordinates <- c(longitude = exif_data$GPSLongitude, latitude = exif_data$GPSLatitude)
    return(gps_coordinates)
  } else {
    return(NULL)
  }
}


image_directory <- "P1/" #โฟล์เดอร์ภาพที่ต้องการคัดลอก
image_files <- list.files(image_directory, pattern = "\\.JPG$|\\.png$", full.names = TRUE) 


coordinates_list <- sapply(image_files, function(x) {
  coords <- get_gps_coordinates(x) 
  if (is.null(coords)) {
    return(c(NA, NA)) 
  } else {
    return(coords)
  }
})

coordinates_df <- data.frame(
  image_path = image_files, 
  longitude = coordinates_list[1, ],  
  latitude = coordinates_list[2, ]   
)


coordinates_df <- coordinates_df[!is.na(coordinates_df$longitude) & !is.na(coordinates_df$latitude), ]


kml_file <- "blk.kml" #ไฟล์ KML 
kml_data <- st_read(kml_file)
kml_polygon <- st_geometry(kml_data)

destination_directory <- "02/"  #โฟล์เดอร์ปลายทาง

for (i in 1:nrow(coordinates_df)) {
  image_path <- coordinates_df$image_path[i] 
  coords <- c(coordinates_df$longitude[i], coordinates_df$latitude[i])
  
  image_point <- st_sfc(st_point(coords), crs = 4326)
  

  if (st_intersects(image_point, kml_polygon, sparse = FALSE)[1]) {

    file.copy(image_path, file.path(destination_directory, basename(image_path)))
  }
}


cat("คัดลอกไฟล์ที่ตรงกับขอบเขต KML เสร็จสิ้น\n")
