# Import the required modules
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
from shapely.geometry import Point, Polygon
import matplotlib.lines as mlines

# Load data from the files and reproject LGD, NI crimes, and Towns data
# into same coordinate system as NI outline
outline = gpd.read_file('data_files/NI_outline.shp')

lgd = gpd.read_file('data_files/LGD.shp').to_crs(epsg=32629)
crimes = gpd.read_file('data_files/NI_crimes.shp').to_crs(epsg=32629)
towns = gpd.read_file('data_files/Towns.shp').to_crs(epsg=32629)

# Check that all data in gdf's are in same crs and print result to screen
print(outline.crs)
print(outline.crs == lgd.crs)
print(outline.crs == crimes.crs)
print(outline.crs == towns.crs)

# Summarize NI Crime data by crime type using Geopandas and print output to screen
crimes_total = crimes['Crime_type'].count()
print(crimes.groupby(['Crime_type'])['Crime_type'].count())

# Create spatial join between lgd and crime gdf's to enable the data to be analysed spatially
join = gpd.sjoin(lgd, crimes, how='inner', lsuffix='left', rsuffix='right')

# Summarize NI Crime data totals by crime type in each LGD,
# Set Pandas to show all lines of output and print output to screen
join_summary = join['Crime_type'].count()
pd.set_option('display.max_rows', None)
print(join.groupby(['LGDNAME', 'Crime_type'])['Crime_type'].count())

# Check the total number of crimes in both gdf's and print output to screen
print('Total number of crimes from original file: {}'.format(crimes_total))
print('Total number of crimes from spatial join: {}'.format(join_summary))

# Enable the matplotlib interactive mode to update plots after every plotting command
plt.ion()

# Generate matplotlib handles to create a legend of the features put into the map
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

# Create a scale bar of length 20km in the upper right corner of the map
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

# Create a figure of size 10x10 inches representing the page size in inches
myFig = plt.figure(figsize=(10, 10))

# Create a UTM reference system to transform the data
myCRS = ccrs.UTM(29)

# Create an axes object in the figure, using the UTM projection where the data will be plotted
ax = plt.axes(projection=myCRS)

# Add title to the map
ax.set_title('Crime incidents in Northern Ireland (Dec 17 - Nov 18)', fontsize=14, fontweight='bold')

# Add the outline of Northern Ireland using cartopy's ShapelyFeature
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='black', facecolor='white')
xmin, ymin, xmax, ymax = outline.total_bounds
ax.add_feature(outline_feature)

# Zoom the map to the area of interest using the boundary of the shapefile features
# with a buffer of 5km around each edge
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=myCRS)

# Pick colors for the individual LDG boundary polygons
lgd_colors = ['palegreen', 'cyan', 'violet', 'pink', 'teal', 'yellow', 'red', 'orange', 'indigo', 'olive', 'aqua']

# Get a list of unique LGD boundary names and sort alphabetically
lgd_names = list(lgd.LGDNAME.unique())
lgd_names.sort()

# Add the LGD outlines to the map using cartopy's ShapelyFeature using the selected colors
for ii, name in enumerate(lgd_names):
    feat = ShapelyFeature(lgd.loc[lgd['LGDNAME'] == name, 'geometry'],
                          myCRS,
                          edgecolor='black',
                          facecolor=lgd_colors[ii],
                          linewidth=1,
                          alpha=0.25)
    ax.add_feature(feat)

# Add point data of NI crimes to the map
crimes_handle = ax.plot(crimes.geometry.x, crimes.geometry.y, 'o', color='black', ms=4, transform=myCRS)

# Generate a list of handles for the LGD dataset
lgd_handles = generate_handles(lgd.LGDNAME.unique(), lgd_colors, alpha=0.25)

# Make a list of handles and labels corresponding to the objects required in legend
handles = lgd_handles + crimes_handle
labels = lgd_names + ['Crimes']

# Add legend to map in upper left corner
leg = ax.legend(handles, labels, title='Legend', title_fontsize=10,
                 fontsize=6, loc='upper left', frameon=True, framealpha=1)

# Add gridlines to the map with longitude and latitude lines at 0.5 deg intervals
# and no labels on left or bottom of map
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.left_labels = False # turn off the left-side labels
gridlines.bottom_labels = False # turn off the bottom labels

# Add the scale bar to the map
scale_bar(ax)

# Save the map
myFig.savefig('map.png', bbox_inches='tight', dpi=300)