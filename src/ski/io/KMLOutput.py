'''
Created on 24 Feb 2013

@author: sroberts
'''

import xml.dom.minidom as xml


class KMLDocument(xml.Document):
    
    def __init__(self):
        super.__init__()
        

def create_placemark(docElem, lat, lon, name=None, description=None):
    pmNode = docElem.createElement('Placemark')
    if name is not None:
        e = docElem.createElement('Name')
        e.appendChild(docElem.createTextNode(name))
        pmNode.appendChild(e)
    if description is not None:
        e = docElem.createElement('Description')
        e.appendChild(docElem.createTextNode(description))
        pmNode.appendChild(e)
    
    pointNode = docElem.createElement('Point')
    
    coordNode = docElem.createElement('coordinates')
    coordNode.appendChild(docElem.createTextNode('{:f},{:f},{:f}'.format(lon, lat, 0.0)))
    
    pointNode.appendChild(coordNode)
    pmNode.appendChild(pointNode)

    docElem.appendChild(pmNode)
    
    
def run():
    doc = xml.Document()
    
    create_placemark(doc, 123.0, 456.0, 'Test')
    
    print doc.toprettyxml()
    
run()