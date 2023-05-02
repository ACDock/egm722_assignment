# Import modules
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches

# Load data from files and
# reproject data files into same crs as NI outline
outline = gpd.read_file('data_files/NI_outline.shp')
print()  # Prints an empty line to separate the outputs and make them easier to read
print('The CRS of the NI Outline file is: {}'. format(outline.crs))
print()
lgd = gpd.read_file('data_files/LGD.shp').to_crs(epsg=32629)
crimes = gpd.read_file('data_files/NI_crimes.shp').to_crs(epsg=32629)
towns = gpd.read_file('data_files/Towns.shp').to_crs(epsg=32629)

# Check all data in gdf's are in same crs
# returns True or False to screen
print('The data are all in the same CRS:{}'.format(outline.crs == lgd.crs == crimes.crs == towns.crs))
print()

# Summarize all NI Crime data by crime type totals
# print to screen in descending order
print('Total number of incidents for each crime type:')
print(crimes.groupby(['Crime_type'])['Crime_type'].count().sort_values(ascending=False))
print()

# Create spatial join between lgd and crime gdf's
join = gpd.sjoin(lgd, crimes, how='inner', lsuffix='left', rsuffix='right')

# Summarize NI Crime data by totals and crime types in each lgd
# Set Pandas to show all lines of output and print to screen
pd.set_option('display.max_rows', None)
print('Total number of incidents in each LGD:')
print(join.groupby(['LGDNAME'])['Crime_type'].count().sort_values(ascending=False))
print()
print('Total number of incidents in each LGD by crime type')
print(join.groupby(['LGDNAME', 'Crime_type'])['Crime_type'].count())
print()

# Check the total number of crimes in both gdf's
crimes_total = crimes['Crime_type'].count()
join_total = join['Crime_type'].count()
print('Total number of crime incidents from original file: {}'.format(crimes_total))
print('Total number of crime incidents from spatial join: {}'.format(join_total))

# Create a bar graph of total crime incidents by crime type
graph = pd.DataFrame(join, columns=['Crime_type'])
C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14 = len(graph[graph['Crime_type'] == 'Other crime']), \
    len(graph[graph['Crime_type'] == 'Violent crime']), len(graph[graph['Crime_type'] == 'Anti-social behaviour']), \
    len(graph[graph['Crime_type'] == 'Bicycle theft']), len(graph[graph['Crime_type'] == 'Burglary']), \
    len(graph[graph['Crime_type'] == 'Criminal damage and arson']), len(graph[graph['Crime_type'] == 'Drugs']), \
    len(graph[graph['Crime_type'] == 'Other theft']), len(graph[graph['Crime_type'] == 'Possession of weapons']), \
    len(graph[graph['Crime_type'] == 'Public order']), len(graph[graph['Crime_type'] == 'Robbery']), \
    len(graph[graph['Crime_type'] == 'Shoplifting']), len(graph[graph['Crime_type'] == 'Theft from the person']), \
    len(graph[graph['Crime_type'] == 'Vehicle crime'])
width = 0.5
Colours = ['red', 'orange', 'yellow', 'green', 'blue', 'plum', 'gold', 'silver', 'aqua', 'brown', 'wheat', 'cyan',
           'maroon', 'springgreen']

plt.bar(['Other crime', 'Violent crime', 'Anti-social behaviour', 'Bicycle theft', 'Burglary',
         'Criminal damage and arson', 'Drugs', 'Other theft', 'Possession of weapons', 'Public order', 'Robbery',
         'Shoplifting', 'Theft from the person', 'Vehicle crime'], [C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12,
                                                                    C13, C14], width, color=Colours)
plt.title('Crime incidents in Northern Ireland (Dec 17 - Nov 18)', fontsize=10)
plt.xlabel('Crime Type', fontsize=8)
plt.ylabel('Number of Incidents', fontsize=8)
plt.tick_params(labelsize=2)
plt.grid(True)
plt.savefig('Bar Chart.png', bbox_inches='tight', dpi=300)

# Enable the matplotlib interactive mode
plt.ion()

# Generate matplotlib legend handles
def generate_handles(labels, colors, edge='k', alpha=1):
    """This function generates handles for the map legend using Matplotlib.

    It creates a legend of the features put into the map by getting the length of the color list and
    uses a for loop to iterate over the labels list and assigns a rectangular color patch to each.

    Parameters:
          labels - uses the LGD name labels for the legend
          colors - uses the selected colors for the legend patches
          edge - black outline for color patches
          alpha - transparency of color patches

    Returns:
        Map legend handles

    """
    lc = len(colors)
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

# Create a scale bar for map
# adapted from: https://stackoverflow.com/q/32333870
# answered by SO user Siyh: https://stackoverflow.com/a/35705477
def scale_bar(ax, location=(0.92, 0.95)):
    """This function generates a scale bar for the map using Cartopy.

    It creates a scale bar of length 20km in top right corner of map which is
    divided by 10km and 20km labels with alternating black and white format.

    Parameters:
        ax - the axes to draw the scalebar on
        location - uses axis coordinates (0.5 is the centre of the plot)

    Returns:
        Map scalebar

    """
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    ax.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=ax.projection)
    ax.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=ax.projection)
    ax.plot([sbx-10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=ax.projection)

    ax.text(sbx, sby-4500, '20 km', transform=ax.projection, fontsize=8)
    ax.text(sbx-12500, sby-4500, '10 km', transform=ax.projection, fontsize=8)
    ax.text(sbx-24500, sby-4500, '0 km', transform=ax.projection, fontsize=8)

# Create a figure of size 10x10 representing the page size in inches
myFig = plt.figure(figsize=(10, 10))

# Create a UTM reference system to transform the data
myCRS = ccrs.UTM(29)

# Create an axes object in the figure where the data will be plotted
# using the UTM projection
ax = plt.axes(projection=myCRS)

# Add title to the map
# The text inside the quotation marks can be changed if mapping individual crime type
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

# Add the LGD outlines to the map using cartopy's ShapelyFeature
# using the selected colors
for ii, name in enumerate(lgd_names):
    feat = ShapelyFeature(lgd.loc[lgd['LGDNAME'] == name, 'geometry'],
                          myCRS,
                          edgecolor='black',
                          facecolor=lgd_colors[ii],
                          linewidth=1,
                          alpha=0.25)
    ax.add_feature(feat)

# Add point data of NI crimes, towns, and cities to the map
crimes_handle = ax.plot(crimes.geometry.x, crimes.geometry.y, 'o', color='black', ms=3,
                        transform=myCRS)  # Comment out this line if plotting individual crime types
town_handle = ax.plot(towns.loc[towns['STATUS'] == 'Town'].geometry.x, towns.loc[towns['STATUS'] == 'Town'].geometry.y,
                      's', color='orange', ms=4, transform=myCRS)
city_handle = ax.plot(towns.loc[towns['STATUS'] == 'City'].geometry.x, towns.loc[towns['STATUS'] == 'City'].geometry.y,
                      'o', color='r', ms=6, transform=myCRS)
# crimetype_handle = ax.plot(crimes.loc[crimes['Crime_type'] == 'Anti-Social Behaviour'].geometry.x,
#                            crimes.loc[crimes['Crime_type'] == 'Anti-Social Behaviour'].geometry.y, 'o', color='k',
#                            ms=4, transform=myCRS)

# Generate a list of handles for the LGD dataset
lgd_handle = generate_handles(lgd.LGDNAME.unique(), lgd_colors, alpha=0.25)

# Make a list of handles and labels corresponding to the objects required in legend
handles = lgd_handle + crimes_handle + town_handle + \
          city_handle  # Comment out this line if plotting individual crime types
labels = lgd_names + ['Crimes', 'Towns', 'Cities']  # Comment out this line if plotting individual crime types
# handles = lgd_handle + crimetype_handle + town_handle + city_handle
# labels = lgd_names + ['Anti-Social Behaviour', 'Towns', 'Cities']

# Add legend to map in upper left corner
leg = ax.legend(handles, labels, title='Legend', title_fontsize=10,
                fontsize=6, loc='upper left', frameon=True, framealpha=1)

# Add gridlines to the map with longitude and latitude lines at 0.5 deg intervals
# and no labels on left or bottom of map
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.left_labels = False
gridlines.bottom_labels = False

# Add the text labels for the towns and cities
for ind, row in towns.iterrows():
    x, y = row.geometry.x, row.geometry.y
    ax.text(x, y, row['TOWN_NAME'].title(), color='magenta', fontsize=10, fontweight='bold', transform=myCRS)

# Add the scale bar to the map
scale_bar(ax)

# Save the map
myFig.savefig('Map.png', bbox_inches='tight', dpi=300)
