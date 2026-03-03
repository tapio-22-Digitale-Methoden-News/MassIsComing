import pandas as pd
import numpy as np
import numbers
import math
import random

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import io
from urllib.request import urlopen, Request
from PIL import Image

import folium
import webbrowser
from folium.plugins import HeatMap

from pathlib import Path
import os.path

DATA_PATH = Path.cwd()



#adapt limits and zoom-level (scale) according to data
limits = {'latMin':-90.0, 'latMax':90.0, 'lonMin':-180.0, 'lonMax':180.0}
scale = 3

'''
labels = [{'lon':6.08342, 'lat':50.77664,  'name':"Aachen"},
          {'lon':6.95,'lat':50.93333,'name':"Cologne"},
          {'lon':7.09549,'lat':50.73438,'name':"Bonn"},
          {'lon':7.14816,'lat':51.25627,'name':"Wuppertal"},
          {'lon':7.466,'lat':51.51494,'name':"Dortmund"}, 
          {'lon':7.62571,'lat':51.96236,'name':"Münster"}, 
          {'lon':6.79387,'lat':50.81481,'name':"Erftstadt"}, 
          {'lon':6.95,'lat':50.33333,'name':"Nürburg"}, 
          {'lon':7.57883,'lat':50.35357,'name':"Koblenz"},
          {'lon':6.66667,'lat':50.25,'name':"Eifel"}, 
          {'lon':7.09549,'lat':50.54169,'name':"Ahrweiler"}
]
'''

#rivers_10m = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m')
#rivers_europe_10m = cfeature.NaturalEarthFeature('physical', 'rivers_europe', '10m')

locationsDF = pd.read_csv(DATA_PATH / 'csv' / 'sentiments_locations.csv', delimiter=',')
locationsDF = locationsDF.dropna()
if(not locationsDF.empty):
  locationsDF = locationsDF[(locationsDF['count'] > 1)]

print(locationsDF['latitude'].min())
print(locationsDF['latitude'].max())
print(locationsDF['longitude'].min())
print(locationsDF['longitude'].max())

def image_spoof(self, tile): 
    url = self._image_url(tile) 
    req = Request(url) 
    req.add_header('User-agent','Anaconda 3') 
    fh = urlopen(req) 
    im_data = io.BytesIO(fh.read()) 
    fh.close() 
    img = Image.open(im_data) 
    img = img.convert(self.desired_tile_form) 
    return img, self.tileextent(tile), 'lower' 


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
    #ax.add_feature(cfeature.LAKES, facecolor='lightblue', alpha=0.5)
    #ax.add_feature(cfeature.RIVERS, edgecolor='blue', alpha=0.5)

    # Gitternetzlinien
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 10}

    return fig, ax, osm_img

# alternative zu oben
"""
#cartopy OSM
cimgt.OSM.get_image = image_spoof 
osm_img = cimgt.OSM() 
fig = plt.figure(figsize=(15,10))
#ax = fig.add_subplot(1,1,1, projection = ccrs.PlateCarree())
# project using coordinate reference system (CRS) of street map 
ax1 = plt.axes(projection=osm_img.crs) 
ax1.set_title('Hazard Location Map',fontsize=18)
extent = [limits['lonMin'], limits['lonMax'], limits['latMin'], limits['latMax']] 
ax1.set_extent(extent)
ax1.set_xticks(np.linspace(limits['lonMin'],limits['lonMax'],9),crs=ccrs.PlateCarree()) 
ax1.set_yticks(np.linspace(limits['latMin'],limits['latMax'],7)[1:],crs=ccrs.PlateCarree()) 
lon_formatter = LongitudeFormatter(number_format='0.2f',degree_symbol='',dateline_direction_label=True)
lat_formatter = LatitudeFormatter(number_format='0.2f',degree_symbol='') 
ax1.xaxis.set_major_formatter(lon_formatter) 
ax1.yaxis.set_major_formatter(lat_formatter) 
ax1.xaxis.set_tick_params(labelsize=14)
ax1.yaxis.set_tick_params(labelsize=14)
# add OSM with zoom specification
ax1.add_image(osm_img, scale) 
"""



#ax1.coastlines(resolution='50m', color='black', linewidth=1)
"""
sumCounts = np.sum(locationsDF['count'])
maxCount = np.max(locationsDF['count'])
print(['sum',sumCounts,'max',maxCount])   #211,28
lat1,long1,size1 = [],[],[]
for index, column in locationsDF.iterrows():
  if(isinstance(column['longitude'], numbers.Number) and isinstance(column['latitude'], numbers.Number)):
    if((limits['latMin']<column['latitude']<limits['latMax']) and (limits['lonMin']<column['longitude']<limits['lonMax'])):
        delta = 1.0
        counter = int(column['count']/maxCount*250+column['count']/sumCounts*1800)
        if(column['geotype']=='L'):   #large
            #counter = 1
            delta = 30.0
        if(column['geotype']=='A'):   #country
            delta = 7.0
        if(column['geotype']=='P'):  #city  T
            delta = 2.0 

        for i in range(counter):
            x=random.gauss(column['longitude'],delta)
            y=random.gauss(column['latitude'],delta)
            lat1.append(x)
            long1.append(y)
            ax1.plot(x, y, 
                    markersize=35,marker='o',linestyle='', markeredgecolor=None,
                    color='#aa3322', alpha=0.003,transform=ccrs.PlateCarree())                     
            ax1.plot(x, y, 
                    markersize=15,marker='o',linestyle='', markeredgecolor=None,
                    color='#bb4422', alpha=0.005,transform=ccrs.PlateCarree())  
"""


# alternative zu oben
# 3. Kreise basierend auf Häufigkeit erstellen
def create_circles(df, min_radius=2, max_radius=50):
    patches = []
    counts = locationsDF['count'].values
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
    p.set_array(locatiosDF['count'])
    p.set_clim([locationsDF['count'].min(), locationsDF['count'].max()])
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


# alternative zu oben
"""
#contour-plot
sns.kdeplot(x=lat1, y=long1, fill=False,  levels=10, thresh=.0005, color='grey', transform=ccrs.PlateCarree()  )  
#ax1.add_feature(rivers_10m, facecolor='None', edgecolor='cyan', linewidth=1.5, zorder=2)
#ax1.add_feature(rivers_europe_10m, facecolor='None', edgecolor='red', linewidth=1.5, zorder=2)

#North-Arrow
#ax1.text(-75.0, 175.0,u'\u25B2 \nN ', ha='center', fontsize=30, family='Arial', rotation = 0)

#for label in labels:
#    ax1.text(label['lon'],label['lat'],label['name'], color='#200000', fontsize=14, ha='center', va='center',transform=ccrs.PlateCarree())
"""


"""
if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')
plt.savefig(DATA_PATH / 'img' / 'locations.png', dpi=300)


heatdata = []
for index, column in locationsDF.iterrows():
    if(isinstance(column['longitude'], numbers.Number) and isinstance(column['latitude'], numbers.Number)):
    #if((50<column['latitude']<52) and (6<column['longitude']<8) and not ('Nordrhein-Westfalen' == column['phrase'])):
        #print([column['phrase'],column['count']])
        print([column['latitude'],column['longitude']])
        heatdata.append([column['latitude'],column['longitude'],1])
"""


map_osm = folium.Map(location=[51,7],zoom_start=6,tiles='Stamen Terrain',attr = "My Data Attribution",control_scale=True)
HeatMap(heatdata).add_to(map_osm)
map_osm.save(str(DATA_PATH / "img" / "locations.html"))
