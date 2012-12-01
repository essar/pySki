'''
Created on 16 Nov 2012

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import csv
import datetime
import time

def unpack(row):
    '''
      Unpacks a list of strings into a GPS tuple
      @return: a GPS tuple (ts, ((lat, lon), (x, y), alt, spd)).
    '''
    ts = to_datetime(row[1].strip(), row[2].strip())
    lat = float(row[6].strip())
    lon = float(row[7].strip())
    x = int(row[10].strip())
    y = int(row[11].strip())
    a = int(row[8].strip())
    s = int(row[9].strip())
    return (ts, ((lat, lon), (x, y), a, s))


def to_datetime(datestr, timestr):
    '''
      Returns a date as the number of whole seconds since the epoch (1st January 1970)
      @param datestr: a string containing the date component to be parsed
      @param timestr: a string containing the date component to be parsed
      @return: an integer
    '''
    dt = datetime.datetime.strptime(datestr + timestr, '%d-%m-%Y%H:%M:%S')
    return int(time.mktime(dt.timetuple()))


def loadCSV(CSVData):
    '''
      Processes a set of CSV formatted data and returns a list of GPS tuples.
      @param CSVData: a sequence of rows of CSV data for parsing.
      @return: an array of GPS tuples (ts, ((lat, lon), (x, y), alt, spd)).
    '''
    data = []
    csvreader = csv.reader(CSVData, delimiter=',')
    for line in csvreader:
        if len(line) == 12 and line[0].isdigit():
            data.append(unpack(line))
    return data    


def loadCSVFile(fileName):
    '''
      Loads CSV data from a file and returns a list of GPS tuples.
      @param fileName: a string containing the path and name of the file to read.
      @return: an array of GPS tuples (ts, ((lat, lon), (x, y), alt, spd)).
    '''
    with open(fileName, 'rb') as csvfile:
        data = loadCSV(csvfile)
    
    print 'Loaded {0} data points from file'.format(len(data))
    
    return data