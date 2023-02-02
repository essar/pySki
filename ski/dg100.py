"""
  Module providing functions for reading GPS data from a Globalat DG-100 (or DG-200) data logger.
  Specification: (https://github.com/essar/pySki/wiki/Communication-Specification-for-GlobalSat-DG-100)
"""

import datetime
import logging
import serial

# Test serial parameters
device='/dev/cu.usbserial-310'
speed=115200


# Protocol constants
START_SEQ=b'\xA0\xA2'
END_SEQ=b'\xB0\xB3'

COMMAND_IDs={
    0xB5: 'TRACK_RECORDS',
    0xBB: 'TRACK_HEADER'
}
TRACK_HEADER_MSG=b'\xBB'
TRACK_RECORDS_MSG=b'\xB5'

# Define loggers
log = logging.getLogger(__name__)
parser_log = logging.getLogger(name='parser')
serial_log = logging.getLogger(name='serial')


class MessageBuilder:
    """
    Class containing methods for building messages to send to a DG100/DG200 data logger.
    """

    def request_track_file(self, track_index:int) -> bytearray:
        """Request track file for the specified index."""
        payload_bytes = bytearray(3)
        payload_bytes[0:1] = TRACK_RECORDS_MSG
        payload_bytes[1:3] = _to_bytes(track_index)

        return payload_bytes


    def request_track_headers(self, header_index:int) -> bytearray:
        """Request track headers starting at the specified index."""
        payload_bytes = bytearray(3)
        payload_bytes[0:1] = TRACK_HEADER_MSG
        payload_bytes[1:3] = _to_bytes(header_index)

        return payload_bytes


class MessageParser:
    """
    Class containing messages for parsing messages received from a DG100/DG200 data logger.
    """

    def _parse_track_record(self, record_bytes:bytes, format:int) -> dict:
        """Parse track file data into a dict."""
        log.debug(record_bytes.hex(' '))

        # Format A fields - position only (8 bytes)
        if format == 0:
            log.debug('Parsing track record as format A')

            if len(record_bytes) != 8:
                raise ValueError(f'Invalid data; expected 8 byte(s), received {len(record_bytes)} byte(s)')
            
            # Latitude is first 4 bytes;
            lat = _from_bytes(record_bytes[0:4])
            # Lonitude is next 4 bytes;
            lon = _from_bytes(record_bytes[4:8])

            parser_log.info('RECORD: %s => %d %d', record_bytes.hex(), lat, lon)

            return {
                'lat': lat,
                'lon': lon
            }

        # Format B fields - position, date/time and speed (20 bytes)
        if format == 1: 
            log.debug('Parsing track record as format B')

            if len(record_bytes) != 20:
                raise ValueError(f'Invalid data; expected 20 byte(s), received {len(record_bytes)} byte(s)')
            
            # Latitude is first 4 bytes;
            lat = _from_bytes(record_bytes[0:4])
            # Lonitude is next 4 bytes;
            lon = _from_bytes(record_bytes[4:8])
            # Time is in the next 4 bytes; pad to a 6 digit string
            timestr = str(_from_bytes(record_bytes[8:12])).zfill(6)
            # Date is in the next 4 bytes; pad to a 6 digit string
            datestr = str(_from_bytes(record_bytes[12:16])).zfill(6)
            # Speed is next 4 bytes;
            spd = _from_bytes(record_bytes[16:20])

            parser_log.info('RECORD: %s => %d %d %6s %6s %d', record_bytes.hex(), lat, lon, timestr, datestr, spd)

            # Format into datetime object
            datetime.datetime.strptime(f'{datestr} {timestr}', '%d%m%y %H%M%S')
            
            return {
                'lat': lat,
                'lon': lon,
                'tm': timestr,
                'dt': datestr,
                'spd': spd
            }

        # Format C fields - position, date/time, speed and altitude (32 bytes):
        if format == 2:
            log.debug('Parsing track record as format C')

            if len(record_bytes) != 32:
                raise ValueError(f'Invalid data; expected 32 byte(s), received {len(record_bytes)} byte(s)')
            
            # Latitude is first 4 bytes;
            lat = _from_bytes(record_bytes[0:4])
            # Lonitude is next 4 bytes;
            lon = _from_bytes(record_bytes[4:8])
            # Time is in the next 4 bytes; pad to a 6 digit string
            timestr = str(_from_bytes(record_bytes[8:12])).zfill(6)
            # Date is in the next 4 bytes; pad to a 6 digit string
            datestr = str(_from_bytes(record_bytes[12:16])).zfill(6)
            # Speed is next 4 bytes;
            spd = _from_bytes(record_bytes[16:20])
            # Altitude is next 4 bytes;
            alt = _from_bytes(record_bytes[20:24])
            # Record format is last 4 bytes
            record_format = _from_bytes(record_bytes[28:32])

            parser_log.info('RECORD: %s => %d %d %6s %6s %d %d %d', record_bytes.hex(), lat, lon, timestr, datestr, spd, alt, record_format)

            return {
                'lat': lat,
                'lon': lon,
                'tm': timestr,
                'dt': datestr,
                'spd': spd,
                'alt': alt,
                'format': record_format
            }

    def _parse_track_header(self, header_bytes:bytes) -> dict:
        """Parse track header data into a dict."""
        log.debug(header_bytes.hex(' '))

        if len(header_bytes) != 12:
            raise ValueError(f'Invalid data; expected 12 byte(s), received {len(header_bytes)} byte(s)')

        # Time is in the first 4 bytes; pad to a 6 digit string
        timestr = str(_from_bytes(header_bytes[0:4])).zfill(6)
        # Date is in the second 4 bytes; pad to a 6 digit string
        datestr = str(_from_bytes(header_bytes[4:8])).zfill(6)
        # Track index is in last 4 (or maybe 2?) bytes
        track_index = _from_bytes(header_bytes[8:12])

        parser_log.info('HEADER: %s => %6s %6s %d', header_bytes.hex(), timestr, datestr, track_index)
        
        # Format into datetime object
        track_date = datetime.datetime.strptime(f'{datestr} {timestr}', '%d%m%y %H%M%S')
        
        return {
            'index': track_index,
            'date': track_date
        }

    def track_file_response(self, payload_bytes:bytes) -> dict:
        """Parse track file response message."""
        log.info('Parse track file: %d byte(s)', len(payload_bytes))
        
        # First record is always 32 bytes
        track_records = [self._parse_track_record(payload_bytes[0:32], 2)]

         # Check format of remaining records
        record_format = track_records[0]['format']
        record_length = {0: 8, 1: 20, 2: 32}[record_format]

        # Parse remaining records based on record format and length from first record
        track_records.extend([self._parse_track_record(payload_bytes[x:(x + record_length)], record_format) for x in range(record_length, len(payload_bytes), record_length)])

        return {
            'records': track_records
        }

    def track_headers_response(self, payload_bytes:bytes) -> dict:
        """Parse track header response message."""
        log.info('Parse track headers: %d byte(s)', len(payload_bytes))

        headers_count = _from_bytes(payload_bytes[0:2])
        next_header_index = _from_bytes(payload_bytes[2:4])
        header_data = payload_bytes[4:-4]
        tail = payload_bytes[-4:]
        log.debug('%d %d [%d byte(s)] %s', headers_count, next_header_index, len(header_data), tail.hex())

        # Each header is 12-bytes
        track_headers = [self._parse_track_header(header_data[x:(x + 12)]) for x in range(0, len(header_data), 12)]

        if headers_count != len(track_headers):
            raise ValueError('Header count mismatch')

        return {
            'headers': track_headers,
            'headers_count': headers_count,
            'next_index': next_header_index
        }
        

def _from_bytes(bytes:bytes) -> int:
    """Convert bytes to an int."""
    return int.from_bytes(bytes, byteorder='big')


def _message_checksum(message_bytes:bytes) -> bytes:
    """Extract checksum field from message."""
    return message_bytes[-4:-2]


def _message_eb(message_bytes:bytes) -> bytes:
    """Extract end-byte from message."""
    return message_bytes[-2:]


def _message_len(message_bytes:bytes) -> bytes:
    """Extract payload length from message."""
    return message_bytes[2:4]


def _message_payload(message_bytes:bytes) -> bytes:
    """Extract payload from message."""
    return message_bytes[4:-4]


def _message_sb(message_bytes:bytes) -> bytes:
    """Extract start-byte from message"""
    return message_bytes[0:2]


def _to_bytes(value:int, length:int=2) -> bytes:
    """Convert an int to bytes."""
    return value.to_bytes(length, byteorder='big')


def calculate_checksum(payload_bytes:bytes) -> bytes:
    """Calculates the checksum of a message payload according to the specification."""
    payload_len = len(payload_bytes)
    checksum = payload_bytes[0];
    for i in range(1, payload_len):
        checksum = checksum + payload_bytes[i]
    # From spec doc: The last line of the checksum function masks bit 15 (i.e. the most significant bit in the checksum.) This means that the checksum will never be larger than 32767 (decimal.)
    checksum = checksum & 0x7FFF
    return _to_bytes(checksum)


def format_track_record_as_gsd(track_record:dict) -> list:
    return [
        str(track_record['lat']),
        str(track_record['lon']),
        str(track_record['tm']),
        str(track_record['dt']),
        str(track_record['spd']),
        str(track_record['alt'])
    ]


def get_track_records(ser:serial.Serial, track_index:int) -> list:
    """Gets a list of track records for a file index from a serial connection."""
    log.info('Requesting records for index %d', track_index)

    # Write a message
    request_message = prepare_message(MessageBuilder().request_track_file(track_index))
    serial_log.info('> Sending message: %d byte(s) %s', len(request_message), print_message(request_message))
    ser.write(request_message)

    merged_payload = bytearray()

    # Response will be sent over two messages
    for i in range(0, 1):
        # Read the response
        response_message = ser.read_until(END_SEQ)
        serial_log.info('< Received message: %d byte(s) %s', len(response_message), print_message(response_message))

        # Parse and validate the message
        message_type, payload_bytes = parse_message(response_message, ignore_length=True)
        
        # Check message is of expected type
        if message_type != TRACK_RECORDS_MSG:
            log.error('Received a message of type %X when expecting one of type %X', message_type, TRACK_RECORDS_MSG)
            raise ValueError(f'Unexpected message type ({message_type})')

        merged_payload += payload_bytes

    # Parse record data
    records = MessageParser().track_file_response(merged_payload)['records']

    log.info('Read %d track record(s)', len(records))
    return records


def get_track_headers(ser:serial.Serial) -> list:
    """Gets a list of all track headers from a serial connection."""
    # Start at zero
    track_index = 0
    output = []

    while True:
        log.info('Requesting headers starting at %d', track_index)

        # Write a message
        request_message = prepare_message(MessageBuilder().request_track_headers(track_index))
        serial_log.info('> Sending message: %s byte(s) %s', len(request_message), print_message(request_message))
        ser.write(request_message)

        # Read the response
        response_message = ser.read_until(END_SEQ)
        serial_log.info('< Received message: %d byte(s) %s', len(response_message), print_message(response_message))
        
        # Parse and validate the message
        message_type, payload_bytes = parse_message(response_message, ignore_length=True)
        
        # Check message is of expected type
        if message_type != TRACK_HEADER_MSG:
            log.error('Received a message of type %X when expecting one of type %X', message_type, TRACK_HEADER_MSG)
            raise ValueError(f'Unexpected message type ({message_type})')
        
        # Parse header data
        headers = MessageParser().track_headers_response(payload_bytes)
        log.debug('Read %d headers from message', len(headers))

        if headers['headers_count'] == 0:
            # No headers read, so leave now
            log.debug('No headers read, exiting loop')
            break

        # Add headers to our response
        output.extend(headers['headers'])
        log.debug('%d header(s) read so far', len(output))

        # Set next track index
        track_index = headers['next_index']

    log.info('Read %d track header(s)', len(output))
    return output


def parse_message(message_bytes:bytes, ignore_length:bool=False, ignore_checksum:bool=False) -> tuple:
    """Parses a message from raw bytes and returns the payload bytes."""
    payload_len = _from_bytes(_message_len(message_bytes))
    payload_bytes = _message_payload(message_bytes)
    checksum_in = _message_checksum(message_bytes)
    
    # Validate length
    if not ignore_length and len(payload_bytes) != payload_len:
        raise ValueError(f'Message length mismatch: read {len(payload_bytes)} byte(s); expected {payload_len} byte(s)')

    # Validate checksum
    checksum_calc = calculate_checksum(payload_bytes)
    if not ignore_checksum and checksum_calc != checksum_in:
        raise ValueError(f'Message checksum mismatch: calculated {checksum_calc}; received {checksum_in}')

    # Check the message type
    message_type = payload_bytes[0:1]

    return message_type, payload_bytes[1:payload_len]


def prepare_message(payload_bytes:bytes) -> bytearray:
    """Packages the supplied payload into a message with start/end markers, length and checksum."""
    payload_len = len(payload_bytes)
    checksum_bytes = calculate_checksum(payload_bytes)

    # Output message adds 8 bytes to payload size
    message = bytearray(payload_len + 8)

    # Assemble message
    message[0:2] = START_SEQ
    message[2:4] = _to_bytes(payload_len)
    message[4:-4] = payload_bytes
    message[-4:-2] = checksum_bytes
    message[-2:] = END_SEQ

    return message


def print_message(message_bytes:bytes) -> str:
    """Format message bytes for printing."""
    sb = _message_sb(message_bytes)
    l = _message_len(message_bytes)
    p = _message_payload(message_bytes)
    cs = _message_checksum(message_bytes)
    eb = _message_eb(message_bytes)

    payload_width = 64

    try:
        str = f'\n{"----------------------------------------------------------------------------------------------------------"}'
        str += f'\n{"FIELD":16} {"VALUE":16} {"LENGTH":7} {"BYTES"}'
        str += f'\n{"----------------"} {"----------------"} {"-------"} {"----------------------------------------------------------------"}'
        str += f'\n{"START_MARKER":16} {"":16} [{len(sb):05d}] {sb.hex()}'
        str += f'\n{"LENGTH":16} {_from_bytes(l):<16d} [{len(l):05d}] {l.hex()}'
        str += f'\n{"PAYLOAD":16} {COMMAND_IDs.get(p[0] if len(p) > 0 else None, "UNKNOWN"):16} [{len(p):05d}] {p.hex()[0:payload_width]}'
        for i in range(payload_width, len(p), payload_width):
            str += f'\n{"":16} {"":16} {"":7} {p.hex()[i:i + payload_width]}'
        str += f'\n{"CHECKSUM":16} {_from_bytes(cs):<16d} [{len(cs):05d}] {cs.hex()}'
        str += f'\n{"END_MARKER":16} {"":16} [{len(eb):05d}] {eb.hex()}'
        str += f'\n{"----------------------------------------------------------------------------------------------------------"}'

    except RuntimeError as e:
        log.warn('%s whilst formatting message: %s', type(e), e, exc_info=True)
        str = f'[[ Error formatting message: {e} ]]'

    
    return str


def print_track_header(header_data:dict) -> str:
    """Format a track header for printing."""
    return f'[{header_data["index"]:03d}] {header_data["date"].isoformat()}'


def print_track_record(record_data:dict) -> str:
    """Format a track record for printing."""
    return f'{record_data["date"].isoformat()} lat={record_data["lat"]}, lon={record_data["lon"]}, alt={record_data["alt"]}, spd={record_data["spd"]}'


def stream_records(ser: serial.Serial) -> dict:
    """Streams records from a serial connection."""
    # Get headers from the device
    headers = get_track_headers(ser)
    log.info('Loaded %d header(s) from DG100', len(headers))

    header_count = 0
    record_count = 0
    # Loop across all headers
    for h in headers:
        try:
            # For every header, get the records
            records = get_track_records(ser, track_index=h['index'])
            
            # Loop across all records
            for r in records:
                # Return point data to the caller
                yield {
                    'point': format_track_record_as_gsd(r),
                    'point_count': record_count,
                    'section_count': header_count,
                    'total_sections': len(headers)
                }
                # Increment counter
                record_count += 1

            header_count += 1

        except ValueError as e:
            log.warn('Unable to load records for file %d: %s, skipping', h['index'], e)

    log.info('Loaded %d record(s) from DG100', record_count)
    return {
        'point_count': record_count,
        'section_count': header_count,
        'total_sections': len(headers)
    }


def test_connect():

    # Create serial device
    try:
        with serial.Serial(device, speed, timeout=1) as ser:
            print(ser)

            # Write a message
            request_message = MessageBuilder().request_track_headers(0)
            ser.write(prepare_message(request_message))

            # Read the response
            response_message = ser.read_until(END_SEQ)
            print(response_message)

            payload = parse_message(response_message)
            print(payload.hex())
        
    except serial.SerialException as err:
        print(err)


def test_download():

    try:
        with serial.Serial(device, speed, timeout=1) as ser:
            serial_log.info(ser)

            headers = get_track_headers(ser)
            for h in headers:
                print(print_track_header(h))

            records = get_track_records(ser, 1)
            for r in records:
                print(print_track_record(r))

    except serial.SerialException as err:
        print(err)


def test_headers():
    message = b'\xa0\xa2\x07\x12\xbb\x00\x96\x00\x96\x00\x01N3\x00\x02\xbf\xfe\x00\x00\x00\x00\x00\x01N\xc5\x00\x02\xbf\xfe\x00\x00\x00\x01\x00\x01O-\x00\x02\xbf\xfe\x00\x00\x00\x02\x00\x01O\x95\x00\x02\xbf\xfe\x00\x00\x00\x03\x00\x01_\x9d\x00\x02\xbf\xfe\x00\x00\x00\x04\x00\x01`#\x00\x02\xbf\xfe\x00\x00\x00\x05\x00\x01aX\x00\x02\xbf\xfe\x00\x00\x00\x06\x00\x01bM\x00\x02\xbf\xfe\x00\x00\x00\x07\x00\x01c\x1d\x00\x02\xbf\xfe\x00\x00\x00\x08\x00\x01c\x87\x00\x02\xbf\xfe\x00\x00\x00\t\x00\x01d\n\x00\x02\xbf\xfe\x00\x00\x00\n\x00\x01e\x8d\x00\x02\xbf\xfe\x00\x00\x00\x0b\x00\x01e\xf5\x00\x02\xbf\xfe\x00\x00\x00\x0c\x00\x01f]\x00\x02\xbf\xfe\x00\x00\x00\r\x00\x01f\xc5\x00\x02\xbf\xfe\x00\x00\x00\x0e\x00\x01g.\x00\x02\xbf\xfe\x00\x00\x00\x0f\x00\x01g\x97\x00\x02\xbf\xfe\x00\x00\x00\x10\x00\x01i\x1d\x00\x02\xbf\xfe\x00\x00\x00\x11\x00\x01i\xbb\x00\x02\xbf\xfe\x00\x00\x00\x12\x00\x01jI\x00\x02\xbf\xfe\x00\x00\x00\x13\x00\x01kT\x00\x02\xbf\xfe\x00\x00\x00\x14\x00\x01l\xa2\x00\x02\xbf\xfe\x00\x00\x00\x15\x00\x01m\\\x00\x02\xbf\xfe\x00\x00\x00\x16\x00\x01n6\x00\x02\xbf\xfe\x00\x00\x00\x17\x00\x01o\x05\x00\x02\xbf\xfe\x00\x00\x00\x18\x00\x01o\xa7\x00\x02\xbf\xfe\x00\x00\x00\x19\x00\x01q7\x00\x02\xbf\xfe\x00\x00\x00\x1a\x00\x01q\x9f\x00\x02\xbf\xfe\x00\x00\x00\x1b\x00\x01r\x08\x00\x02\xbf\xfe\x00\x00\x00\x1c\x00\x01rp\x00\x02\xbf\xfe\x00\x00\x00\x1d\x00\x01r\xd8\x00\x02\xbf\xfe\x00\x00\x00\x1e\x00\x01sE\x00\x02\xbf\xfe\x00\x00\x00\x1f\x00\x01s\xb2\x00\x02\xbf\xfe\x00\x00\x00 \x00\x01tM\x00\x02\xbf\xfe\x00\x00\x00!\x00\x01t\xc3\x00\x02\xbf\xfe\x00\x00\x00"\x00\x01u8\x00\x02\xbf\xfe\x00\x00\x00#\x00\x01u\xa0\x00\x02\xbf\xfe\x00\x00\x00$\x00\x01vC\x00\x02\xbf\xfe\x00\x00\x00%\x00\x01v\xab\x00\x02\xbf\xfe\x00\x00\x00&\x00\x01\x87#\x00\x02\xbf\xfe\x00\x00\x00\'\x00\x01\x87\xea\x00\x02\xbf\xfe\x00\x00\x00(\x00\x01\x88k\x00\x02\xbf\xfe\x00\x00\x00)\x00\x01\x89+\x00\x02\xbf\xfe\x00\x00\x00*\x00\x01\x8aI\x00\x02\xbf\xfe\x00\x00\x00+\x00\x01\x8bS\x00\x02\xbf\xfe\x00\x00\x00,\x00\x01\x8b\xdb\x00\x02\xbf\xfe\x00\x00\x00-\x00\x01\x8c\x89\x00\x02\xbf\xfe\x00\x00\x00.\x00\x01\x8d\xbc\x00\x02\xbf\xfe\x00\x00\x00/\x00\x01\x8e1\x00\x02\xbf\xfe\x00\x00\x000\x00\x01\x8e\xa9\x00\x02\xbf\xfe\x00\x00\x001\x00\x01\x8fj\x00\x02\xbf\xfe\x00\x00\x002\x00\x01\x90s\x00\x02\xbf\xfe\x00\x00\x003\x00\x01\x915\x00\x02\xbf\xfe\x00\x00\x004\x00\x01\x91\xfb\x00\x02\xbf\xfe\x00\x00\x005\x00\x01\x92k\x00\x02\xbf\xfe\x00\x00\x006\x00\x01\x93D\x00\x02\xbf\xfe\x00\x00\x007\x00\x01\x93\xfd\x00\x02\xbf\xfe\x00\x00\x008\x00\x01\x94\x83\x00\x02\xbf\xfe\x00\x00\x009\x00\x01\x94\xeb\x00\x02\xbf\xfe\x00\x00\x00:\x00\x01\x96D\x00\x02\xbf\xfe\x00\x00\x00;\x00\x01\x973\x00\x02\xbf\xfe\x00\x00\x00<\x00\x01\x97\x9b\x00\x02\xbf\xfe\x00\x00\x00=\x00\x01\x98\x03\x00\x02\xbf\xfe\x00\x00\x00>\x00\x01\x98k\x00\x02\xbf\xfe\x00\x00\x00?\x00\x01\x98\xd3\x00\x02\xbf\xfe\x00\x00\x00@\x00\x01\x99d\x00\x02\xbf\xfe\x00\x00\x00A\x00\x01\x9aS\x00\x02\xbf\xfe\x00\x00\x00B\x00\x01\x9a\xf9\x00\x02\xbf\xfe\x00\x00\x00C\x00\x01\x9b\xc3\x00\x02\xbf\xfe\x00\x00\x00D\x00\x01\x9c>\x00\x02\xbf\xfe\x00\x00\x00E\x00\x01\x9c\xa6\x00\x02\xbf\xfe\x00\x00\x00F\x00\x01\x9d\xda\x00\x02\xbf\xfe\x00\x00\x00G\x00\x01\xae"\x00\x02\xbf\xfe\x00\x00\x00H\x00\x01\xae\x8d\x00\x02\xbf\xfe\x00\x00\x00I\x00\x01\xafm\x00\x02\xbf\xfe\x00\x00\x00J\x00\x01\xaf\xd5\x00\x02\xbf\xfe\x00\x00\x00K\x00\x01\xb0A\x00\x02\xbf\xfe\x00\x00\x00L\x00\x01\xb0\xe5\x00\x02\xbf\xfe\x00\x00\x00M\x00\x01\xb1\xae\x00\x02\xbf\xfe\x00\x00\x00N\x00\x01\xb2c\x00\x02\xbf\xfe\x00\x00\x00O\x00\x01\xb2\xe8\x00\x02\xbf\xfe\x00\x00\x00P\x00\x01\xb3c\x00\x02\xbf\xfe\x00\x00\x00Q\x00\x01\xb4\x1d\x00\x02\xbf\xfe\x00\x00\x00R\x00\x01\xb4\xde\x00\x02\xbf\xfe\x00\x00\x00S\x00\x01\xb5M\x00\x02\xbf\xfe\x00\x00\x00T\x00\x01\xb5\xb8\x00\x02\xbf\xfe\x00\x00\x00U\x00\x01\xb6V\x00\x02\xbf\xfe\x00\x00\x00V\x00\x01\xb77\x00\x02\xbf\xfe\x00\x00\x00W\x00\x01\xb7\xef\x00\x02\xbf\xfe\x00\x00\x00X\x00\x01\xb8\xcc\x00\x02\xbf\xfe\x00\x00\x00Y\x00\x01\xb9t\x00\x02\xbf\xfe\x00\x00\x00Z\x00\x01\xb9\xea\x00\x02\xbf\xfe\x00\x00\x00[\x00\x01\xbaa\x00\x02\xbf\xfe\x00\x00\x00\\\x00\x01\xbb\x07\x00\x02\xbf\xfe\x00\x00\x00]\x00\x01\xbb\x8e\x00\x02\xbf\xfe\x00\x00\x00^\x00\x01\xbcP\x00\x02\xbf\xfe\x00\x00\x00_\x00\x01\xbc\xb8\x00\x02\xbf\xfe\x00\x00\x00`\x00\x01\xbd]\x00\x02\xbf\xfe\x00\x00\x00a\x00\x01\xbd\xd8\x00\x02\xbf\xfe\x00\x00\x00b\x00\x01\xbe\xe6\x00\x02\xbf\xfe\x00\x00\x00c\x00\x01\xbf\xb9\x00\x02\xbf\xfe\x00\x00\x00d\x00\x01\xc0\xa9\x00\x02\xbf\xfe\x00\x00\x00e\x00\x01\xc2\x17\x00\x02\xbf\xfe\x00\x00\x00f\x00\x01\xc2\x93\x00\x02\xbf\xfe\x00\x00\x00g\x00\x01\xc3]\x00\x02\xbf\xfe\x00\x00\x00h\x00\x01\xc4]\x00\x02\xbf\xfe\x00\x00\x00i\x00\x01\xd4\xc1\x00\x02\xbf\xfe\x00\x00\x00j\x00\x01\xd5\xa4\x00\x02\xbf\xfe\x00\x00\x00k\x00\x01\xd6z\x00\x02\xbf\xfe\x00\x00\x00l\x00\x01\xd7~\x00\x02\xbf\xfe\x00\x00\x00m\x00\x01\xd8e\x00\x02\xbf\xfe\x00\x00\x00n\x00\x01\xd9!\x00\x02\xbf\xfe\x00\x00\x00o\x00\x01\xd9\xe6\x00\x02\xbf\xfe\x00\x00\x00p\x00\x01\xda\xa9\x00\x02\xbf\xfe\x00\x00\x00q\x00\x01\xdc\x01\x00\x02\xbf\xfe\x00\x00\x00r\x00\x01\xdc\x9e\x00\x02\xbf\xfe\x00\x00\x00s\x00\x01\xdd\x0b\x00\x02\xbf\xfe\x00\x00\x00t\x00\x01\xdd\xf4\x00\x02\xbf\xfe\x00\x00\x00u\x00\x01\xde\xb9\x00\x02\xbf\xfe\x00\x00\x00v\x00\x01\xdf\x84\x00\x02\xbf\xfe\x00\x00\x00w\x00\x01\xe0\x14\x00\x02\xbf\xfe\x00\x00\x00x\x00\x01\xe0|\x00\x02\xbf\xfe\x00\x00\x00y\x00\x01\xe0\xe4\x00\x02\xbf\xfe\x00\x00\x00z\x00\x01\xe1L\x00\x02\xbf\xfe\x00\x00\x00{\x00\x01\xe1\xb4\x00\x02\xbf\xfe\x00\x00\x00|\x00\x01\xe2\x8b\x00\x02\xbf\xfe\x00\x00\x00}\x00\x01\xe3P\x00\x02\xbf\xfe\x00\x00\x00~\x00\x01\xe4\x06\x00\x02\xbf\xfe\x00\x00\x00\x7f\x00\x01\xe4\x94\x00\x02\xbf\xfe\x00\x00\x00\x80\x00\x01\xe6i\x00\x02\xbf\xfe\x00\x00\x00\x81\x00\x01\xe6\xeb\x00\x02\xbf\xfe\x00\x00\x00\x82\x00\x01\xe7\x9e\x00\x02\xbf\xfe\x00\x00\x00\x83\x00\x01\xe8S\x00\x02\xbf\xfe\x00\x00\x00\x84\x00\x02\x0b\x7f\x00\x02\xbf\xfe\x00\x00\x00\x85\x00\x02\r\x02\x00\x02\xbf\xfe\x00\x00\x00\x86\x00\x02\r\x80\x00\x02\xbf\xfe\x00\x00\x00\x87\x00\x02\r\xe8\x00\x02\xbf\xfe\x00\x00\x00\x88\x00\x02\x0eP\x00\x02\xbf\xfe\x00\x00\x00\x89\x00\x02\x0e\xb8\x00\x02\xbf\xfe\x00\x00\x00\x8a\x00\x02\x0f \x00\x02\xbf\xfe\x00\x00\x00\x8b\x00\x02\x0f\x88\x00\x02\xbf\xfe\x00\x00\x00\x8c\x00\x02\x10=\x00\x02\xbf\xfe\x00\x00\x00\x8d\x00\x02\x11\x0c\x00\x02\xbf\xfe\x00\x00\x00\x8e\x00\x02\x11x\x00\x02\xbf\xfe\x00\x00\x00\x8f\x00\x02\x11\xe2\x00\x02\xbf\xfe\x00\x00\x00\x90\x00\x02\x12\xaa\x00\x02\xbf\xfe\x00\x00\x00\x91\x00\x02\x13\x14\x00\x02\xbf\xfe\x00\x00\x00\x92\x00\x02#y\x00\x02\xbf\xfe\x00\x00\x00\x93\x00\x02$(\x00\x02\xbf\xfe\x00\x00\x00\x94\x00\x02$\x9d\x00\x02\xbf\xfe\x00\x00\x00\x95\xe4B\r\x00QM\xb0\xb3'
    
    message_type, payload_bytes = parse_message(message, ignore_length=True)
    
    headers = MessageParser().track_headers_response(payload_bytes)
    for h in headers['headers']:
        print(print_track_header(h))


def test_records():
    message1 = b'\xa0\xa2\x04\x01\xb5\x02\xb7#?\x00cm\\\x00\x01N\xc5\x00\x02\xbf\xfe\x00\x00\x05\xdc\x00\xc0\xdf\x00\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7#Z\x00cmB\x00\x01N\xc6\x00\x02\xbf\xfe\x00\x00\x06\x86\x00\xc1T0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7#u\x00cm)\x00\x01N\xc7\x00\x02\xbf\xfe\x00\x00\x06r\x00\xc1\xa2P\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7#\x89\x00cm\x15\x00\x01N\xc8\x00\x02\xbf\xfe\x00\x00\x06,\x00\xc2\x17\x80\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7#\x9c\x00cm\x04\x00\x01N\xc9\x00\x02\xbf\xfe\x00\x00\x06g\x00\xc2\x8c\xb0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7#\xb6\x00cl\xf0\x00\x01N\xca\x00\x02\xbf\xfe\x00\x00\x07\x12\x00\xc3\x01\xe0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7#\xcf\x00cl\xe2\x00\x01N\xcb\x00\x02\xbf\xfe\x00\x00\x06\x99\x00\xc3\x9e \x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7#\xe4\x00cl\xd2\x00\x01N\xcc\x00\x02\xbf\xfe\x00\x00\x066\x00\xc4\x13P\x00\x00\x00\x00\x00\x00\x00\x02\x02\xb7#\xfb\x00cl\xc2\x00\x01N\xcd\x00\x02\xbf\xfe\x00\x00\x06"\x00\xc4\xaf\x90\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$\r\x00cl\xb3\x00\x01N\xce\x00\x02\xbf\xfe\x00\x00\x05\xfa\x00\xc5$\xc0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$ \x00cl\xa2\x00\x01N\xcf\x00\x02\xbf\xfe\x00\x00\x05\xe6\x00\xc5\x99\xf0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$=\x00cl\x88\x00\x01N\xd0\x00\x02\xbf\xfe\x00\x00\x06"\x00\xc6\x0f \x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$L\x00cl|\x00\x01N\xd1\x00\x02\xbf\xfe\x00\x00\x05\xe6\x00\xc6\xab`\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$_\x00cll\x00\x01N\xd2\x00\x02\xbf\xfe\x00\x00\x06\x0e\x00\xc7 \x90\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$p\x00cl`\x00\x01N\xd3\x00\x02\xbf\xfe\x00\x00\x05\x8c\x00\xc7\xbc\xd0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$\x7f\x00clP\x00\x01N\xd4\x00\x02\xbf\xfe\x00\x00\x05\xe6\x00\xc82\x00\x00\x00\x00\x00\x00\x00\x00\x02\x02\xb7$\x90\x00clA\x00\x01N\xd5\x00\x02\xbf\xfe\x00\x00\x05\x82\x00\xc8\xa70\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$\xa5\x00cl.\x00\x01N\xd6\x00\x02\xbf\xfe\x00\x00\x06,\x00\xc9Cp\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$\xb1\x00cl%\x00\x01N\xd7\x00\x02\xbf\xfe\x00\x00\x052\x00\xc9\xb8\xa0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$\xbe\x00cl\x1d\x00\x01N\xd8\x00\x02\xbf\xfe\x00\x00\x04j\x00\xcaT\xe0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$\xcf\x00cl\x10\x00\x01N\xd9\x00\x02\xbf\xfe\x00\x00\x04.\x00\xca\xf1 \x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$\xe5\x00ck\xfa\x00\x01N\xda\x00\x02\xbf\xfe\x00\x00\x05\x82\x00\xcb?@\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7$\xfd\x00ck\xe5\x00\x01N\xdb\x00\x02\xbf\xfe\x00\x00\x05\xfa\x00\xcb\xb4p\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%\x15\x00ck\xd3\x00\x01N\xdc\x00\x02\xbf\xfe\x00\x00\x05\xa0\x00\xcc)\xa0\x00\x00\x00\x00\x00\x00\x00\x02\x02\xb7%*\x00ck\xc2\x00\x01N\xdd\x00\x02\xbf\xfe\x00\x00\x06\x04\x00\xcc\x9e\xd0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%A\x00ck\xaf\x00\x01N\xde\x00\x02\xbf\xfe\x00\x00\x06r\x00\xcd\x14\x00\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%U\x00ck\x9c\x00\x01N\xdf\x00\x02\xbf\xfe\x00\x00\x066\x00\xcd\x890\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%i\x00ck\x8c\x00\x01N\xe0\x00\x02\xbf\xfe\x00\x00\x06,\x00\xcd\xfe`\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%\x7f\x00ck|\x00\x01N\xe1\x00\x02\xbf\xfe\x00\x00\x06@\x00\xces\x90\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%\x95\x00ckj\x00\x01N\xe2\x00\x02\xbf\xfe\x00\x00\x06\x86\x00\xce\xe8\xc0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%\xac\x00ckY\x00\x01N\xe3\x00\x02\xbf\xfe\x00\x00\x06^\x00\xcf]\xf0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%\xc0\x00ckH\x00\x01N\xe4\x00\x02\xbf\xfe\x00\x00\x06J\x00\xcf\xd3 \x00\x00\x00\x00\x00\x00\x00\x02e\x16\r\x00xO\xb0\xb3'
    message2 = b'\xa0\xa2\x04\x01\xb5\x02\xb7%\xd8\x00ck9\x00\x01N\xe5\x00\x02\xbf\xfe\x00\x00\x066\x00\xd0o`\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7%\xee\x00ck)\x00\x01N\xe6\x00\x02\xbf\xfe\x00\x00\x066\x00\xd0\xe4\x90\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&\x02\x00ck\x15\x00\x01N\xe7\x00\x02\xbf\xfe\x00\x00\x066\x00\xd12\xb0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&\x13\x00ck\x01\x00\x01N\xe8\x00\x02\xbf\xfe\x00\x00\x05\xf0\x00\xd1\xa7\xe0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&(\x00cj\xee\x00\x01N\xe9\x00\x02\xbf\xfe\x00\x00\x06\x18\x00\xd2\x1d\x10\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&>\x00cj\xdc\x00\x01N\xea\x00\x02\xbf\xfe\x00\x00\x06g\x00\xd2\x92@\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&T\x00cj\xca\x00\x01N\xeb\x00\x02\xbf\xfe\x00\x00\x06J\x00\xd3\x07p\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&i\x00cj\xb8\x00\x01N\xec\x00\x02\xbf\xfe\x00\x00\x066\x00\xd3|\xa0\x00\x00\x00\x00\x00\x00\x00\x02\x02\xb7&\x7f\x00cj\xa8\x00\x01N\xed\x00\x02\xbf\xfe\x00\x00\x06"\x00\xd3\xf1\xd0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&\x96\x00cj\x97\x00\x01N\xee\x00\x02\xbf\xfe\x00\x00\x06r\x00\xd4\x8e\x10\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&\xa7\x00cj\x7f\x00\x01N\xef\x00\x02\xbf\xfe\x00\x00\x06,\x00\xd4\xdc0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&\xb7\x00cjj\x00\x01N\xf0\x00\x02\xbf\xfe\x00\x00\x06\x18\x00\xd5*P\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&\xcb\x00cjX\x00\x01N\xf1\x00\x02\xbf\xfe\x00\x00\x06^\x00\xd5\x9f\x80\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&\xe2\x00cjH\x00\x01N\xf2\x00\x02\xbf\xfe\x00\x00\x06r\x00\xd6\x14\xb0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7&\xf8\x00cj6\x00\x01N\xf3\x00\x02\xbf\xfe\x00\x00\x06,\x00\xd6\xb0\xf0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'\r\x00cj&\x00\x01N\xf4\x00\x02\xbf\xfe\x00\x00\x06,\x00\xd7& \x00\x00\x00\x00\x00\x00\x00\x02\x02\xb7\'#\x00cj\x12\x00\x01N\xf5\x00\x02\xbf\xfe\x00\x00\x06@\x00\xd7\x9bP\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'5\x00cj\x07\x00\x01N\xf6\x00\x02\xbf\xfe\x00\x00\x05\xdc\x00\xd87\x90\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'J\x00ci\xf4\x00\x01N\xf7\x00\x02\xbf\xfe\x00\x00\x06"\x00\xd8\xac\xc0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'b\x00ci\xde\x00\x01N\xf8\x00\x02\xbf\xfe\x00\x00\x06J\x00\xd8\xfa\xe0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'s\x00ci\xcd\x00\x01N\xf9\x00\x02\xbf\xfe\x00\x00\x06\x0e\x00\xd9p\x10\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'\x82\x00ci\xb8\x00\x01N\xfa\x00\x02\xbf\xfe\x00\x00\x06\x0e\x00\xd9\xe5@\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'\x92\x00ci\xa0\x00\x01N\xfb\x00\x02\xbf\xfe\x00\x00\x06\x04\x00\xda3`\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'\xa4\x00ci\x86\x00\x01N\xfc\x00\x02\xbf\xfe\x00\x00\x06T\x00\xda\x81\x80\x00\x00\x00\x00\x00\x00\x00\x02\x02\xb7\'\xba\x00cig\x00\x01N\xfd\x00\x02\xbf\xfe\x00\x00\x06g\x00\xda\xcf\xa0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'\xd2\x00ciM\x00\x01N\xfe\x00\x02\xbf\xfe\x00\x00\x06\x86\x00\xdb\x1d\xc0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'\xe6\x00ci9\x00\x01N\xff\x00\x02\xbf\xfe\x00\x00\x06^\x00\xdb\x92\xf0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7\'\xfc\x00ci)\x00\x01O(\x00\x02\xbf\xfe\x00\x00\x066\x00\xdc/0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7(\r\x00ci\x15\x00\x01O)\x00\x02\xbf\xfe\x00\x00\x06\x18\x00\xdc\xa4`\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7(!\x00ch\xfe\x00\x01O*\x00\x02\xbf\xfe\x00\x00\x06\x0e\x00\xdd\x19\x90\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7(1\x00ch\xee\x00\x01O+\x00\x02\xbf\xfe\x00\x00\x06\x18\x00\xdd\x8e\xc0\x00\x00\x00\x01\x00\x00\x00\x02\x02\xb7(@\x00ch\xe3\x00\x01O,\x00\x02\xbf\xfe\x00\x00\x06"\x00\xde+\x00\x00\x00\x00\x00\x00\x00\x00\x02\xce]\r\x00u8\xb0\xb3'

    message_type1, payload_bytes1 = parse_message(message1, ignore_length=True)
    message_type2, payload_bytes2 = parse_message(message2, ignore_length=True)

    records = MessageParser().track_file_response(payload_bytes1 + payload_bytes2)
    for r in records['records']:
        print(print_track_record(r))


def test_stream():

    try:
        with serial.Serial(device, speed, timeout=1) as ser:
            serial_log.info(ser)
            
            records = stream_records(ser)
            for r in records:
                print(print_track_record(r))

    except serial.SerialException as err:
        print(err)


if __name__ == '__main__':
    logging.basicConfig()
    log.setLevel(logging.INFO)
    #serial_log.setLevel(logging.INFO)

    #test_connect()
    #test_headers()
    #test_records()
    test_stream()
