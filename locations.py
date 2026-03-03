import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from pathlib import Path
import os

# Pfad zur CSV-Datei
DATA_PATH = Path.cwd()
CSV_FILE = DATA_PATH / 'csv' / 'sentiments_locations.csv'

# 1. Daten laden und bereinigen
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath, delimiter=',')
    # Entferne NaN-Werte und ungültige Koordinaten
    df = df.dropna(subset=['latitude', 'longitude', 'count'])
    df = df[(df['latitude'].between(-90, 90)) & (df['longitude'].between(-180, 180))]
    df = df[df['count'] > 0]  # Nur Einträge mit Häufigkeit > 0
    return df

locationsDF = load_and_clean_data(CSV_FILE)

# 2. Karteneinstellungen
def setup_map():
    # Hintergrundkarte (OpenStreetMap oder Natural Earth)
    osm_img = cimgt.OSM()  # Alternativ: cimgt.GoogleTiles(style='satellite')

    # Projektion und Figur
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Kartenausschnitt (global)
    ax.set_global()
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax.add_feature(cfeature.LAKES, facecolor='lightblue', alpha=0.5)
    ax.add_feature(cfeature.RIVERS, edgecolor='blue', alpha=0.5)

    # Gitternetzlinien
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 10}

    return fig, ax, osm_img

# 3. Kreise basierend auf Häufigkeit erstellen
def create_circles(df, min_radius=2, max_radius=50):
    patches = []
    counts = df['count'].values
    norm = Normalize(vmin=counts.min(), vmax=counts.max())

    for _, row in df.iterrows():
        radius = min_radius + (max_radius - min_radius) * (row['count'] / counts.max())
        circle = Circle((row['longitude'], row['latitude']), radius,
                        transform=ccrs.PlateCarree(), zorder=10)
        patches.append(circle)

    return patches, norm

# 4. Karte plotten
def plot_map(df):
    fig, ax, osm_img = setup_map()

    # Kreise erstellen
    patches, norm = create_circles(df)

    # Farbskala (z. B. 'viridis', 'plasma', 'YlOrRd')
    cmap = cm.get_cmap('YlOrRd')
    p = PatchCollection(patches, cmap=cmap, alpha=0.7, edgecolor='black', linewidth=0.3)
    p.set_array(df['count'])
    p.set_clim([df['count'].min(), df['count'].max()])
    ax.add_collection(p)

    # Farblegende
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical', fraction=0.02, pad=0.1)
    cbar.set_label('Anzahl der Erdrutsche (count)', fontsize=12)

    # Titel
    plt.title('Globale Verteilung gravitativer Massenbewegungen (Erdrutsche)',
              fontsize=16, pad=20)

    # Speichern
    output_dir = DATA_PATH / 'img'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plt.savefig(output_dir / 'global_landslides_map.png', dpi=300, bbox_inches='tight')
    plt.show()

# 5. Ausführung
if not locationsDF.empty:
    plot_map(locationsDF)
else:
    print("Keine gültigen Daten zum Plotten gefunden.")





