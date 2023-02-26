import json
import logging
import serial
import sys
from .dash import run_dashboard
from .dg100 import stream_records as stream_records_from_device
from .dg100 import serial_log
from .gsd import stream_records as stream_records_from_file, write_gsd
from .processor import add_timezone, build_point_from_gsd, enrich_point, linear_interpolate, summary
from .stream import Stream
from .utils import DateAwareJSONEncoder, MovingWindow


def cmdline(cmd_args:list):
    #logging.basicConfig(level=logging.INFO)
    """Process the command line"""
    while len(cmd_args) > 0:
        command = cmd_args.pop(0)

        if command == '-cp' or command == '--copy':
            # Load from serial device and write to a file
            device_path = cmd_args.pop(0)
            file_name = cmd_args.pop(0)
            load_from_device_to_file(device_path, file_name)
            break

        if command == '-d' or command == '--device':
            # Load from serial device
            device_path = cmd_args.pop(0)
            load_from_device(device_path)
            break

        if command == '-f' or command == '--file':
            # Load from a file
            file_name = cmd_args.pop(0)
            load_from_gsd_file(file_name)
            break

        if command == '-v':
            # Enable debug logging
            logging.basicConfig(level=logging.DEBUG)
            continue

        if command == '-D' or command == '--dash':
            # Start the dashboard display
            file_name = cmd_args.pop(0)
            run_dashboard(load_from_gsd_file, filename=file_name)

        print(f'Unknkown command: {command}')

        
def load_stream(data:dict) -> list:

    point_count = data['point_count']
    sections_complete = (data['section_count'] / data['total_sections']) * 100.0

    print(f'\rLoading GPS data... {sections_complete:.02f}%', end='')

    return data['point']


def load_from_device(device_path):

    speed = 115200
    try:
        with serial.Serial(device_path, speed, timeout=1) as ser:
            serial_log.info(ser)

            loader_f = load_stream
            build_f = build_point_from_gsd
            interpolate_f = linear_interpolate

            enrich_window = MovingWindow(2)
            enrich_f = lambda p: enrich_point(enrich_window, p)

            summary_obj = {}
            summary_f = lambda p: summary(summary_obj, p)

            records = stream_records_from_device(ser)

            result = Stream.create(records).map(loader_f).map(build_f).pipe(interpolate_f).map(enrich_f).map(summary_f)
            
            count = len(list(result))
            print(f'\n{count} point(s) loaded and processed')
            print(summary_obj)

    except serial.SerialException as err:
        print(err)


def load_from_device_to_file(device_path, filename):

    speed = 115200
    try:
        with serial.Serial(device_path, speed, timeout=1) as ser:
            serial_log.info(ser)
            
            with open(filename, mode='w') as f:

                write_f = lambda ps: write_gsd(f, ps)

                records = stream_records_from_device(ser)

                Stream.create(records).map(lambda x: x['point']).pipe(write_f)
            
            

    except serial.SerialException as err:
        print(err)


def load_from_gsd_file(filename):

    try:
        with open(filename, 'r') as f:
            loader_f = load_stream
            build_f = build_point_from_gsd

            interpolate_f = linear_interpolate

            tz_cache = {}
            add_timezone_f = lambda p: add_timezone(p, tz_cache)

            enrich_window = MovingWindow(2)
            enrich_f = lambda p: enrich_point(enrich_window, p)
            
            summary_obj = {}
            summary_f = lambda p: summary(summary_obj, p)

            records = stream_records_from_file(f)

            result = Stream.create(records).map(loader_f).map(build_f).pipe(interpolate_f).map(add_timezone_f).map(enrich_f).map(summary_f)
            
            points = list(result)
            count = len(points)
            print(f'\n{count} point(s) loaded and processed')
            print(summary_obj)

            #for p in points[1000:1010]:
            #    print(json.dumps(p, indent=2, cls=DateAwareJSONEncoder))

            return points
            

    except IOError as err:
        print(err)


if __name__ == '__main__':
    cmdline(sys.argv[1:])

