'''
Created on 1 Dec 2012

@author: sroberts
'''

import logging as log

import ski.data.Coordinate as coord
import ski.io as io

convert_coords = True


def __next_section(f):
    for line in f:
        if line.startswith('['):
            return line
    return None


def __parse_section_name(name):
    # Strip header characters if present
    if name.startswith('['): name = name[1:-1]
    
    # Parse into tuple
    nParts = name.split(',')
    if len(nParts) < 2: return name
    return (int(nParts[0].strip()), nParts[1].strip())


def __split_line(line):
    # Look for allocation marker
    ix = line.index('=')
    if ix < 0:
        return (0, [])
    
    # Get line parts and strip whitespace
    lParts = map(lambda a: a.strip(), line[ix + 1:].split(','))
    
    return (ix, lParts)


def __skip_to_section(f, name=None, section_id=0):
    while True:
        s = __next_section(f)
        if s is None: break
        # Search by section name
        if name is not None and s.strip() == '[{0}]'.format(name): return
        # Search by section ID
        if section_id > 0 and __parse_section_name(s.strip())[0] == section_id: return
    
    raise EOFError('Could not find section {0}'.format(name))


def load_data(f, first_section_id=None, last_section_id=None):
    global all_data, section_data
    
    # Go to start of file
    f.seek(0)
    
    # Skip to specified section if required
    if first_section_id is not None:
        __skip_to_section(f, section_id=first_section_id)
    else:
        # Skip to TP section
        __skip_to_section(f, name='TP')
        # Look for next header
        current_section = __parse_section_name(__next_section(f))
        
    current_section_data = []
    
    all_data = []
    section_data = []
    for line in f:
        # Stop if we reach the end section
        if last_section_id is not None and last_section_id == current_section[0]:
            break
        
        # Skip blank lines
        if len(line.strip()) == 0:
            continue
        
        # Start of a new section
        if line.startswith('['):
            # Save current section data to section data
            section_data.append((current_section, current_section_data))
            
            # Reset section values
            current_section_data = []
            current_section = __parse_section_name(line.strip()[1:-1])
            continue
        
        d = parse_data_line(line)
        all_data.append(d)
        current_section_data.append(d)
    
    return all_data

def load_header(f):
    sections = []
    # Advance to TP section
    __skip_to_section(f, 'TP')
    for line in f:
        # Skip blank lines
        if len(line.strip()) == 0:
            continue

        # Stop once we reach the next header
        if line.startswith('['):
            break
        
        sections.append(parse_header_line(line))
    
    return sections

def load_gsd_file(fileName):
    with open(fileName, 'r') as f:
        data = load_data(f)
        
    return data

def parse_data_line(line):
    # Get line parts
    (pid, lParts) = __split_line(line)
    
    try:
        # Parse latitude
        latStr = '{:08d}'.format(int(lParts[0]))
        
        i = 2 if int(latStr) > 0 else 3
        latD = int(latStr[:i])
        latDM = float(latStr[i:]) / 10000.0
        
        latDMS = coord.addSeconds(latD, latDM)
        log.debug('[GSDLoader] Latitude: %s->%s->%s->%s', lParts[0], latStr, (latD, latDM), latDMS)
        
        (latD, latM, latS) = latDMS
        
        # Parse longitude
        lonStr = '{:08d}'.format(int(lParts[1]))
        
        i = 3 if int(lonStr) > 0 else 4
        lonD = int(lonStr[:i])
        lonDM = float(lonStr[i:]) / 10000.0
        
        lonDMS = coord.addSeconds(lonD, lonDM)
        log.debug('[GSDLoader] Longitude: %s->%s->%s->%s', lParts[1], lonStr, (lonD, lonDM), lonDMS)
        
        (lonD, lonM, lonS) = lonDMS
        # Calculate coordinates
        dms = coord.DMSCoordinate(latD, latM, latS, lonD, lonM, lonS)
        log.debug('[GSDLoader] DMS: %s', dms)
        wgs = coord.DMStoWGS(dms)
        log.debug('[GSDLoader] WGS: %s', wgs)
        
        # Latitude & Longitude
        lat = wgs.getLatitudeDegrees()
        lon = wgs.getLongitudeDegrees()
        
        # Cartesian X & Y
        if convert_coords:
            utm = coord.WGStoUTM(wgs)
            x = utm.x
            y = utm.y
        else:
            x = y = 0
        
        # Date & Time
        t = '{:6d}'.format(int(lParts[2]))
        d = '{:6d}'.format(int(lParts[3]))
        ts = int(io.as_seconds(d, t))
        
        # Speed & Altitude
        spd = int(lParts[4]) / 100.0
        alt = int(lParts[5]) / 10000
    
    except ValueError:
        log.error('Could not parse point {0}', pid)
        
    
    # Build up data item
    return (ts, (lat, lon), (x, y), alt, spd)

def parse_header_line(line):
    # Get line parts
    lParts = __split_line(line)[1]
    return ((int(lParts[0].strip()), lParts[1].strip()))
