'''
Created on 10 Feb 2013

@author: sroberts
'''

import logging as log

log.basicConfig(level=log.INFO)

import time
import xml.dom.minidom as xml

import ski.data.coordinate as coord

convert_coords = True

def __get_text(elem):
    rc = []
    for e in elem:
        if e.nodeType == e.TEXT_NODE:
            rc.append(e.data)
    return ''.join(rc)


def __process_trackpt_elem(elem):
    xml_lat = elem.getAttribute("lat")
    xml_lon = elem.getAttribute("lon")
    xml_ts = __get_text(elem.getElementsByTagName("time")[0].childNodes)
    xml_alt = __get_text(elem.getElementsByTagName("ele")[0].childNodes)
    xml_spd = __get_text(elem.getElementsByTagName("speed")[0].childNodes)
    log.debug('[GSDLoader] XML data: lat=%s; lon=%s; ts=%s; alt=%s; spd=%s', xml_lat, xml_lon, xml_ts, xml_alt, xml_spd)
    
    try:
        # Parse latitude
        lat = float(xml_lat)
            
        # Parse longitude
        lon = float(xml_lon)    
        
        # Cartesian X & Y
        if convert_coords:
            wgs = coord.WGSCoordinate(lat, lon)
            utm = coord.WGStoUTM(wgs)
            x = utm.x
            y = utm.y
        else:
            x = y = 0
        
        # Date & Time
        dt = time.strptime(xml_ts, '%Y-%m-%dT%H:%M:%SZ')
        ts = time.mktime(dt)
        
        # Speed & Altitude
        alt = int(float(xml_alt))
        spd = float(xml_spd)
            
    except ValueError:
        log.error('Could not parse point')
    
    # Build up data item
    return (ts, (lat, lon), (x, y), alt, spd)


def load_data(f):
    global all_data
    
    # Go to start of file
    f.seek(0)
    
    # Parse XML document
    doc = xml.parse(f)

    all_data = []
    elems = doc.getElementsByTagName("trkpt")
    log.debug('[GPXLoader] %d points found to load', len(elems))
    for e in elems:
        d = __process_trackpt_elem(e)
        all_data.append(d)
        
    return all_data
    
    
def load_gpx_file(fileName):
    with open(fileName, 'r') as f:
        data = load_data(f)
        
    return data

