'''
Created on 1 Dec 2012

@author: sroberts
'''
import unittest
from Coordinate import DMSCoordinate, DMStoWGS, UTMCoordinate, WGSCoordinate, WGStoDMS, WGStoUTM, UTMtoWGS

accuracy = 8
dms = DMSCoordinate(50, 50, 50.555555555, 120, 40, 22.222222222)
utm = UTMCoordinate(292303, 5013403, 33, 'N')
wgs = WGSCoordinate(45.12345678, 12.3456789)

class Test(unittest.TestCase):
    
    def testDMStoWGS(self):
        dms2 = WGStoDMS(DMStoWGS(dms))
        latDrift = (((dms2.latitude.degrees - dms.latitude.degrees) * 3600.0)
                    + ((dms2.latitude.minutes - dms.latitude.minutes) * 60.0)
                    + (dms2.latitude.seconds - dms.latitude.seconds)
        )
        lonDrift = (((dms2.longitude.degrees - dms.longitude.degrees) * 3600.0)
                    + ((dms2.longitude.minutes - dms.longitude.minutes) * 60.0)
                    + (dms2.longitude.seconds - dms.longitude.seconds)
        )
        self.assertAlmostEqual(latDrift, 0.0, accuracy, 'DMS to WGS latitude drift:{:.16f}'.format(latDrift))
        self.assertAlmostEqual(lonDrift, 0.0, accuracy, 'DMS to WGS longitude drift:{:.16f}'.format(lonDrift))

    def testUTMtoWGS(self):
        utm2 = WGStoUTM(UTMtoWGS(utm))
        xDrift = utm.x - utm2.x
        yDrift = utm.y - utm2.y
        self.assertAlmostEqual(xDrift, 0.0, accuracy, 'UTM to WGS X drift:{:.16f}'.format(xDrift))
        self.assertAlmostEqual(yDrift, 0.0, accuracy, 'UTM to WGS Y drift:{:.16f}'.format(yDrift))

    def testWGStoDMS(self):
        wgs2 = DMStoWGS(WGStoDMS(wgs))
        latDrift = wgs.getLatitudeDegrees() - wgs2.getLatitudeDegrees()
        lonDrift = wgs.getLongitudeDegrees() - wgs2.getLongitudeDegrees()
        self.assertAlmostEqual(latDrift, 0.0, accuracy, 'WGS to DMS longitude drift:{:.16f}'.format(latDrift))
        self.assertAlmostEqual(lonDrift, 0.0, accuracy, 'WGS to DMS longitude drift:{:.16f}'.format(lonDrift))
        
    def testWGStoUTM(self):
        wgs2 = UTMtoWGS(WGStoUTM(wgs))
        latDrift = wgs.getLatitudeDegrees() - wgs2.getLatitudeDegrees()
        lonDrift = wgs.getLongitudeDegrees() - wgs2.getLongitudeDegrees()
        self.assertAlmostEqual(latDrift, 0.0, accuracy, 'WGS to UTM longitude drift:{:.16f}'.format(latDrift))
        self.assertAlmostEqual(lonDrift, 0.0, accuracy, 'WGS to UTM longitude drift:{:.16f}'.format(lonDrift))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDMStoWGS']
    unittest.main()