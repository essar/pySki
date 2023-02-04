import logging
import serial
import sys
from .dg100 import stream_records as stream_records_from_device
from .dg100 import serial_log
from .gsd import stream_records as stream_records_from_file
from .processor import build_point_from_gsd, enrich_point, linear_interpolate, map_all
from .stream import Stream
from .utils import MovingWindow


def cmdline(cmd_args:list):
    #logging.basicConfig(level=logging.INFO)
    """Process the command line"""
    while True:
        command = cmd_args.pop(0)

        if command == '-d':
            # Load from serial device
            device_path = cmd_args.pop(0)
            load_from_device(device_path)
            break

        if command == '-f':
            # Load from a file
            file_name = cmd_args.pop(0)
            load_from_gsd_file(file_name)
            break

        if command == '-v':
            # Enable debug logging
            logging.basicConfig(level=logging.DEBUG)
            continue

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

            window = MovingWindow(2)
            handle_f = load_stream
            build_f = build_point_from_gsd
            enrich_f = lambda p: enrich_point(window, p)
            result = map_all(stream_records_from_device(ser), handle_f, build_f, enrich_f)

            count = len(list(result))
            print(f'\rLoaded {count} point(s)')
            

    except serial.SerialException as err:
        print(err)


def load_from_gsd_file(filename):

    try:
        with open(filename, 'r') as f:
            loader_f = load_stream
            build_f = build_point_from_gsd

            interpolate_f = linear_interpolate

            enrich_window = MovingWindow(2)
            enrich_f = lambda p: enrich_point(enrich_window, p)
            
            records = stream_records_from_file(f)

            result = Stream.create(records).map(loader_f).map(build_f).pipe(interpolate_f).map(enrich_f)
            
            #result = map_all(records, handle_f, build_f, interp_f, enrich_f)
            count = len(list(result))
            print(f'\n{count} point(s) loaded and processed')

    except IOError as err:
        print(err)
        

if __name__ == '__main__':
    cmdline(sys.argv[1:])

