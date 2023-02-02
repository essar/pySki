import logging
import serial
import sys
from .dg100 import stream_records as stream_records_from_device
from .dg100 import serial_log
from .gsd import stream_records as stream_records_from_file
from .processor import build_point_from_gsd, enrich_point, map_all
from .utils import MovingWindow


def cmdline(cmd_args:list):
    """Process the command line"""
    while True:
        command = cmd_args.pop(0)

        if command == '-d':
            device_path = cmd_args.pop(0)
            load_from_device(device_path)
            break

        if command == '-f':
            file_name = cmd_args.pop(0)
            load_from_gsd_file(file_name)
            break

        if command == '-v':
            logging.basicConfig(level=logging.DEBUG)
            continue

        print(f'Unknkown command: {command}')

        

def load_from_device(device_path):

    speed = 115200
    try:
        with serial.Serial(device_path, speed, timeout=1) as ser:
            serial_log.info(ser)

            window = MovingWindow(2)
            build_f = build_point_from_gsd
            enrich_f = lambda p: enrich_point(window, p)
            result = map_all(stream_records_from_device(ser), build_f, enrich_f)

            count = len(list(result))
            print(f'Total of {count} point(s)')
            

    except serial.SerialException as err:
        print(err)


def load_from_gsd_file(filename):

    try:
        with open(filename, 'r') as f:
            window = MovingWindow(2)
            build_f = build_point_from_gsd
            enrich_f = lambda p: enrich_point(window, p)
            result = map_all(stream_records_from_file(f), build_f, enrich_f)
            
            count = len(list(result))
            print(f'Total of {count} point(s)')

    except IOError as err:
        print(err)
        

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    print(sys.argv[1:])
    cmdline(sys.argv[1:])

