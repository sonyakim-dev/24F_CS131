# read shapefile
property_gdf = gpd.read_file('/content/drive/MyDrive/LA_City_Parcels.shp') # you need all the shapefiles(.shp, .shx, .crs, etc) in the same location
building_gdf = gpd.read_file('/content/drive/MyDrive/LA_City_Buildings.shp')
print(property_gdf.head())
print(property_gdf.crs, building_gdf.crs)

# convert epsg from 3857(web mapping) to 4326(latitude/longitude coordinate system)
if property_gdf.crs != 'EPSG:4326':
    try:
        print("⏳ Converting property to EPSG:4326..")
        property_gdf = property_gdf.to_crs(epsg=4326)
        print("✅ Conversion succeed: ", property_gdf.crs)
    except:
        print("❌ FAILED: Converting property to EPSG:4326")
        exit(1)
    
if building_gdf.crs != 'EPSG:4326':
  print("⏳ Converting buildings to EPSG:4326..")
  building_gdf = building_gdf.to_crs(epsg=4326)
  print("✅ Conversion succeed: ", building_gdf.crs)
