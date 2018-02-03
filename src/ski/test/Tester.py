from pytz import timezone
import ski.io.gpx as gpx
from ski.io.gpx import GPXFile
import ski.io.json as json
from ski.coordinate import WGSCoordinate, wgs_to_utm
from ski.gps import LinkedGPSPoint, interpolate_linked_point
from ski.tracks import *

__author__ = 'Steve Roberts'


def __gps_to_tp(gps_point, min_v, _min_t):

    (_min_x, _min_y) = min_v

    tp = TrackPoint()
    tp.lat = gps_point.lat
    tp.lon = gps_point.lon
    tp.x = (gps_point.x - _min_x) * 100000.0
    tp.y = (gps_point.y - _min_y) * 100000.0
    tp.a = gps_point.a
    tp.s = gps_point.s
    tp.ts = gps_point.ts
    tp.t = gps_point.ts.timestamp() - _min_t
    # tp.m = 1

    return tp


def __quick_to_gps(d):

    wgs = WGSCoordinate(d.lat, d.lon)
    utm = wgs_to_utm(wgs)

    d.x = utm.x
    d.y = utm.y

    return d


if __name__ == '__main__':

    gpx_file = GPXFile()
    gpx_file.tz = timezone("US/Mountain")
    # gpx_file.tz = timezone("US/Pacific")

    # gps_data = gpx.parse_gpx_file('../../../data/ski_20130214_sjr.gpx', gpx_file)
    # gps_data = gpx.parse_gpx_file('/home/sroberts/Documents/GPS/WP_2015/20150306_sjr.gpx', gpx_file)

    file_list = ['/home/sroberts/Documents/GPS/Banff_2017/20170316_sjr.gpx']

    # file_list = ['/home/sroberts/Documents/GPS/WP_2015/20150226_sjr.gpx',
    #             '/home/sroberts/Documents/GPS/WP_2015/20150227_sjr.gpx',
    #             '/home/sroberts/Documents/GPS/WP_2015/20150228_sjr.gpx',
    #             '/home/sroberts/Documents/GPS/WP_2015/20150301_sjr.gpx',
    #             '/home/sroberts/Documents/GPS/WP_2015/20150302_sjr.gpx',
    #             '/home/sroberts/Documents/GPS/WP_2015/20150303_car.gpx',
    #             '/home/sroberts/Documents/GPS/WP_2015/20150304_sjr.gpx',
    #             '/home/sroberts/Documents/GPS/WP_2015/20150305_sjr.gpx',
    #             '/home/sroberts/Documents/GPS/WP_2015/20150306_sjr.gpx',
    #            ]

    # file_list = []
    # for fi in range(11, 20):
    #     file_list.append('/home/sroberts/Documents/GPS/Whistler_2016/201602{}_sjr.gpx'.format(fi))

    all_gps_data = []

    for f in file_list:

        gps_data = gpx.parse_gpx_file(f, gpx_file)

        print("Parsed {} points".format(len(gps_data)))

        # Do some GPS shit

        gps_data = list(map(__quick_to_gps, gps_data))  # [3000:6000]
        print(gps_data[0])

        # Interpolation
        print("{} GPS points before interpolation".format(len(gps_data)))
        linked_gps = LinkedGPSPoint.from_list(gps_data)
        print(linked_gps, linked_gps.next_point)
        interpolate_linked_point(linked_gps)
        print("{} GPS points after interpolation".format(len(linked_gps.as_list())))
        gps_data = linked_gps.as_list()  # append here
        all_gps_data.extend(gps_data)

    # Get min X & Y
    gps_min_x = min(map(lambda x: x.x, all_gps_data))
    gps_min_y = min(map(lambda x: x.y, all_gps_data))

    min_t = min(map(lambda x: x.ts.timestamp(), all_gps_data))

    # Build a list of track points from the GPS data
    track_data = list(map(lambda x: __gps_to_tp(x, (gps_min_x, gps_min_y), min_t), all_gps_data))
    print(track_data[0])

    # Add control points
    calc_control_points(track_data)
    print(track_data[0])

    # New mode calcs
    new_all_tracks = build_tracks(track_data)
    print("all_tracks: ", len(new_all_tracks))

    track_groups = group_tracks(new_all_tracks)
    print("ski_tracks: ", len(track_groups[MODE_SKI]))
    print("lift_tracks: ", len(track_groups[MODE_LIFT]))

    # Figure modes
    all_tracks = calc_modes(track_data)
    stop_data = list(filter(lambda tp: tp.m == MODE_STOP, track_data))
    print("stop_data: {} points, {} instances".format(len(stop_data), len(all_tracks[MODE_STOP])))
    ski_data = list(filter(lambda tp: tp.m == MODE_SKI, track_data))
    print("ski_data:  {} points, {} runs".format(len(ski_data), len(all_tracks[MODE_SKI])))
    lift_data = list(filter(lambda tp: tp.m == MODE_LIFT, track_data))
    print("lift_data: {} points, {} lifts".format(len(lift_data), len(all_tracks[MODE_LIFT])))

    # Figure out min & max x & y
    min_x = min(map(lambda x: x.x, track_data))
    min_y = min(map(lambda x: x.y, track_data))
    max_x = max(map(lambda x: x.x, track_data))
    max_y = max(map(lambda x: x.y, track_data))
    width = max(map(lambda x: x.x, track_data)) - min_x
    height = max(map(lambda x: x.y, track_data)) - min_y

    # Generate track summary info
    track_info = TrackInfo()
    generate_track_info(track_info, track_data)
    generate_lift_info(track_info, lift_data, all_tracks[MODE_LIFT])
    generate_ski_info(track_info, ski_data, all_tracks[MODE_SKI])

    # Temporary data for testing
    track_info.stop_points = len(stop_data)
    track_info.ski_points = len(ski_data)
    track_info.lift_points = len(lift_data)

    json.write_track("20170316.json",
                     track_info,
                     {"minX": min_x, "minY": min_y,
                      "maxX": max_x, "maxY": max_y,
                      "startT": min_t,
                      "points": track_data}
                     )