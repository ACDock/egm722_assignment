# import required modules
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# make the plotting interactive
plt.ion()

# generate matplotlib handles to create a legend of the features in the map
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

# create a scale bar of length 20km in the upper right corner of the map
def scale_bar(ax, location=(0.92, 0.95)):
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    ax.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=ax.projection)
    ax.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=ax.projection)
    ax.plot([sbx-10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=ax.projection)

    ax.text(sbx, sby-4500, '20 km', transform=ax.projection, fontsize=8)
    ax.text(sbx-12500, sby-4500, '10 km', transform=ax.projection, fontsize=8)
    ax.text(sbx-24500, sby-4500, '0 km', transform=ax.projection, fontsize=8)

# load data from file
outline = gpd.read_file('data_files/NI_outline.shp')
lgd = gpd.read_file('data_files/LGD.shp')
crime_data = gpd.read_file('data_files/NI_crimes.shp')

# create a figure of size 10x10
myFig = plt.figure(figsize=(10, 10))

# create a UTM reference system to transform the data
myCRS = ccrs.UTM(29)

# Create an axes object in the figure, using the UTM projection
ax = plt.axes(projection=myCRS)

# Add the outline of Northern Ireland using cartopy's ShapelyFeature
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='black', facecolor='white')
xmin, ymin, xmax, ymax = outline.total_bounds
ax.add_feature(outline_feature)

# Zoom the map to our area of interest using the boundary of the shapefile features
# with a buffer of 5km around each edge
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=myCRS)

# pick colors for the individual LDG boundaries
lgd_colors = ['palegreen', 'cyan', 'violet', 'pink', 'teal', 'yellow', 'red', 'orange', 'indigo', 'olive', 'aqua']

# get a list of unique LGD boundary names and sort alphabetically
lgd_names = list(lgd.LGDNAME.unique())
lgd_names.sort()

# Add the LGD outlines to the map using the selected colors
for ii, name in enumerate(lgd_names):
    feat = ShapelyFeature(lgd.loc[lgd['LGDNAME'] == name, 'geometry'],
                          myCRS,
                          edgecolor='black',
                          facecolor=lgd_colors[ii],
                          linewidth=1,
                          alpha=0.25)
    ax.add_feature(feat)


myFig.savefig('map.png', bbox_inches='tight', dpi=300)