import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
import osmnx as ox

# Load CSV data
df = pd.read_csv("health_facilities.csv")

# Drop rows with missing coordinates
df = df.dropna(subset=["X_Coord", "Y_Coord"])

# Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(df["X_Coord"], df["Y_Coord"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Get Kakamega County boundary from OSM
kakamega_boundary = ox.geocode_to_gdf("Kakamega County, Kenya").to_crs("EPSG:4326")

# Center map around Kakamega County
m = folium.Map(location=[0.2827, 34.7519], zoom_start=10)

# Define icons for different facility types
icon_mapping = {
    "hospital": ("red", "plus"),
    "clinic": ("blue", "stethoscope"),
    "pharmacy": ("green", "medkit"),
    "dispensary": ("purple", "medkit"),
}

# Add health facility markers
for idx, row in gdf.iterrows():
    amenity = str(row.get("amenity", "")).lower()
    healthcare = str(row.get("healthcare", "")).lower()

    # Pick icon style based on amenity/healthcare type
    if amenity in icon_mapping:
        color, icon = icon_mapping[amenity]
    elif healthcare in icon_mapping:
        color, icon = icon_mapping[healthcare]
    else:
        color, icon = ("gray", "info-sign")  # fallback

    # Keep original facility names (no replacement with "Unknown Facility")
    name = row.get("name")

    folium.Marker(
        [row.geometry.y, row.geometry.x],
        popup=name,
        tooltip=name,  # show name on hover
        icon=folium.Icon(color=color, icon=icon, prefix="fa")
    ).add_to(m)

# Add Kakamega County boundary outline
folium.GeoJson(
    kakamega_boundary.geometry,
    name="Kakamega County Boundary",
    style_function=lambda x: {"fillColor": "none", "color": "black", "weight": 2}
).add_to(m)

# Add custom legend
legend_html = """
<div style="
    position: fixed; 
    bottom: 30px; left: 30px; width: 200px; height: 150px; 
    z-index:9999; font-size:14px;
    background-color: white; padding: 10px; border:2px solid grey; border-radius:8px;
    ">
    <b>Health Facilities Legend</b><br>
    <i class="fa fa-plus fa-2x" style="color:red"></i>&nbsp; Hospital<br>
    <i class="fa fa-stethoscope fa-2x" style="color:blue"></i>&nbsp; Clinic<br>
    <i class="fa fa-medkit fa-2x" style="color:green"></i>&nbsp; Pharmacy<br>
    <i class="fa fa-medkit fa-2x" style="color:purple"></i>&nbsp; Dispensary<br>
    <i class="fa fa-info-circle fa-2x" style="color:gray"></i>&nbsp; Other
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Save map
m.save("kakamega_health_facilities.html")
print("Interactive map saved as kakamega_health_facilities.html")
