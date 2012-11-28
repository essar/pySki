'''
Created on 16 Nov 2012

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import csv

'''
  Unpacks a list of strings into a GPS tuple
'''
def unpack(row):
    lat = float(row[6].strip())
    lon = float(row[7].strip())
    x = int(row[10].strip())
    y = int(row[11].strip())
    a = int(row[8].strip())
    s = int(row[9].strip())
    return (0, ((lat, lon), (x, y), a, s))

'''
  Processes a set of CSV formatted data and returns a list of GPS tuples
'''
def loadCSV(CSVData):
    data = []
    csvreader = csv.reader(CSVData, delimiter=',')
    for line in csvreader:
        if len(line) == 12 and line[0].isdigit():
            data.append(unpack(line))
    return data    


def loadCSVFile(fileName):
    with open(fileName, 'rb') as csvfile:
        data = loadCSV(csvfile)
    
    print 'Loaded {0} data points'.format(len(data))
    
    return data