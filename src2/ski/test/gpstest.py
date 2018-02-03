__author__ = 'sroberts'

import src2.ski.gps as gps
import src2.ski.io.gpx as gpx


# Read file

gps_points = gpx.parse_gpx_file('/home/sroberts/Documents/GPS/WP_2015/20150304_sjr.gpx')
print("Loaded {} points from file".format(len(gps_points)))

