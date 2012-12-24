'''
  Module providing functions and classes for manipulating and translating
  between different geometric coordinate conversions.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (30 Nov 2012)
'''

from math import cos, degrees, pi, pow, radians, sin, sqrt, tan

################################
# COORDINATE CONSTANTS
########
SM_A = 6378137.0;
SM_B = 6356752.314;
UTM_SCALE_FACTOR = 0.9996;
WGS_COORD_MODE_DEG = 0x01;
WGS_COORD_MODE_RAD = 0x02;


################################
# COORDINATE UTILITY FUNCTIONS
########

def addSeconds(degrees, decimalMins):
    mins = int(decimalMins)
    secs = (decimalMins % max(1, mins)) * 60.0
    return (degrees, mins, secs)


def arcLengthOfMeridian(phi):
    '''
      Computes the ellipsoidal distance from the equator to a point at a given latitude.
      
      Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
      GPS: Theory and Practice, 3rd ed. New York: Springer-Verlag Wien, 1994.
      
      Globals:
        sm_a - Ellipsoid model major axis.
        sm_b - Ellipsoid model minor axis.
      
      @param phi: Latitude of the point, in radians.
      @return: The ellipsoidal distance of the point from the equator, in metres.
    '''
    # Calculate n
    n = (SM_A - SM_B) / (SM_A + SM_B)

    # Calculate alpha
    alpha = ((SM_A + SM_B) / 2.0) * (1.0 + (pow(n, 2) / 4.0) + (pow(n, 4) / 64.0))
    # Calculate beta
    beta = (-3.0 * n / 2.0) + (9.0 * pow(n, 3) / 16.0) + (-3.0 * pow(n, 5) / 32.0)
    # Calculate gamma
    gamma = (15.0 * pow(n, 2) / 16.0) + (-15.0 * pow (n, 4) / 32.0)
    # Calculate delta
    delta = (-35.0 * pow(n, 3) / 48.0) + (105.0 * pow(n, 5) / 256.0)
    # Calculate epsilon
    epsilon = 315.0 * pow(n, 4) / 512.0
    
    # Now calculate the sum of the series and return
    result = (alpha * (phi + (beta * sin(2.0 * phi))
         + (gamma * sin(4.0 * phi))
         + (delta * sin(6.0 * phi))
         + (epsilon * sin(8.0 * phi)))
    )

    return result;

def calcCentralMeridian(zone):
    '''
      Determines the central meridian for the given UTM zone.
      @param zone: An integer value designating the UTM zone, range [1,60].
      @return The central meridian for the given UTM zone, in radians, or zero if
      the UTM zone parameter is outside the range [1,60].
      Range of the central meridian is the radian equivalent of [-177,+177].
    '''
    if zone < 1 or zone > 60:
        return 0.0
    return radians(-183 + (zone * 6))

def footpointLatitude(y):
    '''
      Computes the footpoint latitude for use in converting transverse
      Mercator coordinates to ellipsoidal coordinates.
    
      Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
      GPS: Theory and Practice, 3rd ed. New York: Springer-Verlag Wien, 1994.
     
      @param y: The UTM northing coordinate, in meters.
      @return: the footpoint latitude, in radians.
    '''
    # Calculate n (Eq. 10.18)
    n = (SM_A - SM_B) / (SM_A + SM_B)
        
    # Calculate alpha_ (Eq. 10.22)
    # (Same as alpha in Eq. 10.17)
    alpha_ = ((SM_A + SM_B) / 2.0) * (1 + (pow(n, 2) / 4) + (pow(n, 4) / 64))
    # Calculate y_ (Eq. 10.23)
    y_ = y / alpha_
    # Calculate beta_ (Eq. 10.22)
    beta_ = (3.0 * n / 2.0) + (-27.0 * pow(n, 3) / 32.0) + (269.0 * pow(n, 5) / 512.0)
    # Calculate gamma_ (Eq. 10.22)
    gamma_ = (21.0 * pow(n, 2) / 16.0) + (-55.0 * pow(n, 4) / 32.0)
    # Calculate delta_ (Eq. 10.22)
    delta_ = (151.0 * pow(n, 3) / 96.0) + (-417.0 * pow(n, 5) / 128.0)
    # Calculate epsilon_ (Eq. 10.22)
    epsilon_ = (1097.0 * pow(n, 4) / 512.0)
        
    # Now calculate the sum of the series (Eq. 10.21)
    result = (y_ + (beta_ * sin(2.0 * y_))
         + (gamma_ * sin(4.0 * y_))
         + (delta_ * sin(6.0 * y_))
         + (epsilon_ * sin(8.0 * y_))
    )
        
    return result


################################
# COORDINATE CLASSES
########

class CoordinateError(Exception):
    def __init__(self, msg, *args):
        self.msg = msg
        self.args = args
    
    def __str__(self):
        return self.msg.format(*self.args)


class DMSElement:
    def __init__(self, degrees, minutes, seconds, hemisphere):
        self.degrees = degrees
        self.minutes = minutes
        self.seconds = seconds
        self.hemisphere = hemisphere
        
    def __str__(self):
        return '({0:d} {1:02d}\'{2:.2f}"{3:1s})'.format(self.degrees, self.minutes, self.seconds, self.hemisphere)


class DMSCoordinate:
    def __init__(self, latD, latM, latS, lonD, lonM, lonS):
        #
        # LATITUDE
        #
        
        # Calculate hemisphere indicator
        latX = 'S' if latD < 0 else 'N'
        latD = abs(latD)
        
        # Adjust out-of-range minutes and seconds
        if latS >= 60:
            latM += latS / 60;
            latS = latS % 60;
        if latM >= 60:
            latD += latM / 60;
            latM = latM % 60;

        # Check coordinate in legal range
        if latD < -90 or latD > 90:
            raise CoordinateError('DMS latitude out of range: {:d}', latD);

        # Set latitude element
        self.latitude = DMSElement(latD, latM, latS, latX);

        #
        # LONGITUDE
        #
        
        # Calculate hemisphere indicator
        lonX = 'W' if lonD < 0 else 'E'
        lonD = abs(lonD);
        
        # Adjust out-of-range minutes and seconds
        if lonS >= 60:
            lonM += lonS / 60;
            lonS = lonS % 60;
        if lonM >= 60:
            lonD += lonM / 60;
            lonM = lonM % 60;

        # Check coordinate in legal range
        if lonD < -180 or lonD > 180:
            raise CoordinateError('DMS longitude out of range: {:d}', lonD);

        # Set longitude element
        self.longitude = DMSElement(lonD, lonM, lonS, lonX);

    def __str__(self):
        return 'lat: {0}, lon:{1}'.format(str(self.latitude), str(self.longitude))


class UTMCoordinate:
    def __init__(self, x, y, zone, band):
        # Check easing in legal range
        if x < 0:
            raise CoordinateError('UTM easing coordinate out of range: {:d}', x);
        self.x = int(x);
        self.x_over = x % 1
        
        # Check northing in legal range
        if y < 0:
            raise CoordinateError('UTM northing coordinate out of range: {:d}', y);
        self.y = int(y);
        self.y_over = y % 1
        
        # Check zone in legal range
        if zone < 1 or zone > 60:
            raise CoordinateError('UTM zone input out of range: {:s}', zone);
        self.zone = zone;
        
        # Check band is N or S
        if band != 'N' and band != 'S':
            raise CoordinateError('UTM band input out of range {:s)', band);
        self.band = band;

    def __str__(self):
        return '{:d}{:s} {:d} {:d}'.format(self.zone, self.band, self.x, self.y)

    def getCentralMeridian(self):
        return calcCentralMeridian(self.zone)
    

class WGSCoordinate:
    def __init__(self, latitude, longitude, coordMode=WGS_COORD_MODE_DEG):
        if coordMode == WGS_COORD_MODE_DEG:
            # Check latitude in legal range
            if latitude < -90.0 or latitude > 90.0:
                raise CoordinateError('Latitude degree input out of range: {:f}', latitude);
            self.latitude = radians(latitude);

            # Check longitude in legal range
            if longitude < -180.0 or longitude > 180.0:
                raise CoordinateError('Longitude degree input out of range: {:f}', longitude);
            self.longitude = radians(longitude);

        if coordMode == WGS_COORD_MODE_RAD:
            # Check latitude in legal range
            if latitude < (-pi / 2.0) or latitude > (pi / 2.0):
                raise CoordinateError('Latitude radian input out of range: {:f}', latitude);
            self.latitude = latitude;

            # Check longitude in legal range
            if longitude < -pi or longitude > pi:
                raise CoordinateError('Longitude radian input out of range {:f}', longitude);
            self.longitude = longitude;

    def __str__(self):
        return '{:3.6f}, {:3.6f}'.format(self.getLatitudeDegrees(), self.getLongitudeDegrees());
    
    def getLatitudeDegrees(self):
        return float(degrees(self.latitude))
    
    def getLongitudeDegrees(self):
        return float(degrees(self.longitude))
    
    
################################
# COORDINATE CONVERSION FUNCTIONS
########   
    
def DMStoWGS(dms):
    # Build latitude value
    lat = (dms.latitude.degrees
        + (dms.latitude.minutes / 60.0)
        + (dms.latitude.seconds / 3600.0)
    )
    # Check N/S - South is negative
    lat *= -1 if dms.latitude.hemisphere == 'S' else 1

    # Build longitude value
    lon = (dms.longitude.degrees
           + (dms.longitude.minutes / 60.0)
           + (dms.longitude.seconds / 3600.0)
    )
    # Check E/W - West is negative
    lon *= -1 if dms.longitude.hemisphere == 'W' else 1

    return WGSCoordinate(float(lat), float(lon), WGS_COORD_MODE_DEG);


def WGStoDMS(wgs):
    # Break down latitude degrees into D M S components
    latDeg = int(wgs.getLatitudeDegrees())
    latMS = (wgs.getLatitudeDegrees() - latDeg) * 60.0 * 60.0
    latM = int(latMS / 60.0)
    latS = latMS % 60.0

    # Break down longitude degrees into D M S components
    lonDeg = int(wgs.getLongitudeDegrees())
    longMS = (wgs.getLongitudeDegrees() - lonDeg) * 60.0 * 60.0
    longM = int(longMS / 60)
    longS = longMS % 60

    # Build coordinate object
    return DMSCoordinate(latDeg, latM, latS, lonDeg, longM, longS)


def UTMtoWGS(utm):
    '''
      Converts x and y coordinates in the Transverse Mercator projection to
      a latitude/longitude pair. Note that Transverse Mercator is not
      the same as UTM; a scale factor is required to convert between them.
     
      Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
      GPS: Theory and Practice, 3rd ed. New York: Springer-Verlag Wien, 1994.
     
      @param utm: the input coordinate in UTM format.
      @return: the same coordinate in WGS84 format.
    '''
    
    '''
    * Remarks:
    * The local variables Nf, nuf2, tf, and tf2 serve the same purpose as
    * N, nu2, t, and t2 in WGS2UTM, but they are computed with respect
    * to the footpoint latitude phif.
    *
    * x1frac, x2frac, x2poly, x3poly, etc. are to enhance readability and
    * to optimize computations.
    '''
    
    x = float(utm.x)
    y = float(utm.y)
    
    # Adjust easing and northing for UTM system.
    x -= 500000.0
    x /= UTM_SCALE_FACTOR
        
    # If in southern hemisphere, adjust y accordingly.
    y -= 10000000.0 if utm.band == 'S' else 0.0
    y /= UTM_SCALE_FACTOR
    
    # Calculate lambda0
    lambda0 = utm.getCentralMeridian()
    # Get the value of phif, the footpoint latitude.
    phif = footpointLatitude(y)
    # Calculate ep2
    ep2 = (pow(SM_A, 2) - pow(SM_B, 2)) / pow(SM_B, 2)
    # Calculate cos(phif)
    cf = cos(phif)
    # Calculate nuf2
    nuf2 = ep2 * pow(cf, 2)

    # Calculate nf and initialize nfpow
    nf = pow(SM_A, 2) / (SM_B * sqrt(1.0 + nuf2))
    nfpow = nf
        
    # Calculate tf
    tf = tan(phif)
    tf2 = tf * tf
    tf4 = tf2 * tf2
        
    # Calculate fractional coefficients for x**n in the equations
    # below to simplify the expressions for latitude and longitude.
    x1frac = 1.0 / (nfpow * cf)
        
    nfpow *= nf     # now equals Nf^2
    x2frac = tf / (2.0 * nfpow)
        
    nfpow *= nf     # now equals Nf^3
    x3frac = 1.0 / (6.0 * nfpow * cf)
        
    nfpow *= nf     # now equals Nf^4
    x4frac = tf / (24.0 * nfpow)
        
    nfpow *= nf     # now equals Nf^5
    x5frac = 1.0 / (120.0 * nfpow * cf)
        
    nfpow *= nf     # now equals Nf^6
    x6frac = tf / (720.0 * nfpow)
        
    nfpow *= nf     # now equals Nf^7
    x7frac = 1.0 / (5040.0 * nfpow * cf)
        
    nfpow *= nf     # now equals Nf^8
    x8frac = tf / (40320.0 * nfpow)
        
    # Calculate polynomial coefficients for x^n.
    #   -- x^1 does not have a polynomial coefficient.
    x2poly = -1.0 - nuf2
    x3poly = -1.0 - 2 * tf2 - nuf2
    x4poly = 5.0 + 3.0 * tf2 + 6.0 * nuf2 - 6.0 * tf2 * nuf2 - 3.0 * (nuf2 *nuf2) - 9.0 * tf2 * (nuf2 * nuf2)
    x5poly = 5.0 + 28.0 * tf2 + 24.0 * tf4 + 6.0 * nuf2 + 8.0 * tf2 * nuf2
    x6poly = -61.0 - 90.0 * tf2 - 45.0 * tf4 - 107.0 * nuf2 + 162.0 * tf2 * nuf2
    x7poly = -61.0 - 662.0 * tf2 - 1320.0 * tf4 - 720.0 * (tf4 * tf2)
    x8poly = 1385.0 + 3633.0 * tf2 + 4095.0 * tf4 + 1575 * (tf4 * tf2)
        
    # Calculate latitude
    lat = (phif + x2frac * x2poly * (x * x)
           + x4frac * x4poly * pow(x, 4.0)
           + x6frac * x6poly * pow(x, 6.0)
           + x8frac * x8poly * pow(x, 8.0)
    )
        
    # Calculate longitude
    lon = (lambda0 + x1frac * x
           + x3frac * x3poly * pow (x, 3.0)
           + x5frac * x5poly * pow (x, 5.0)
           + x7frac * x7poly * pow (x, 7.0)
    )
        
    # Build coordinate
    return WGSCoordinate(float(lat), float(lon), WGS_COORD_MODE_RAD);


def WGStoUTM(wgs):
    '''
      Converts a latitude/longitude pair to x and y coordinates in the
      Transverse Mercator projection. Note that Transverse Mercator is not
      the same as UTM; a scale factor is required to convert between them.
     
      Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
      GPS: Theory and Practice, 3rd ed. New York: Springer-Verlag Wien, 1994.
     
      @param wgs: the input coordinate, in WGS84 format.
      @return: the same coordinate in UTM format.
    '''
    phi = wgs.latitude
    lda = wgs.longitude
    
    # Calculate UTM zone
    zone = int((wgs.getLongitudeDegrees() + 180.0) / 6.0) + 1
        
    # Calculate ep2
    ep2 = (pow(SM_A, 2) - pow(SM_B, 2)) / pow(SM_B, 2)
    # Calculate nu2
    nu2 = ep2 * pow(cos(phi), 2)
    # Calculate n
    n = pow(SM_A, 2) / (SM_B * sqrt(1.0 + nu2))
    # Calculate t
    t = tan(phi)
    t2 = t * t
        
    # Calculate l
    lda0 = calcCentralMeridian(zone)
    l = lda - lda0;
    
    # Calculate coefficients for l^n in the equations below so a normal human being
    # can read the expressions for easting and northing
    
    # l^1 and l^2 have coefficients of 1.0 */
    
    l3coef = 1.0 - t2 + nu2
    l4coef = 5.0 - t2 + 9.0 * nu2 + 4.0 * (nu2 * nu2)
    l5coef = 5.0 - 18.0 * t2 + (t2 * t2) + 14.0 * nu2 - 58.0 * t2 * nu2
    l6coef = 61.0 - 58.0 * t2 + (t2 * t2) + 270.0 * nu2 - 330.0 * t2 * nu2
    l7coef = 61.0 - 479.0 * t2 + 179.0 * (t2 * t2) - (t2 * t2 * t2)
    l8coef = 1385.0 - 3111.0 * t2 + 543.0 * (t2 * t2) - (t2 * t2 * t2)
    
    # Calculate easing (x)
    x = (n * cos(phi) * l 
         + (n / 6.0 * pow(cos(phi), 3) * l3coef * pow(l, 3))
         + (n / 120.0 * pow(cos(phi), 5) * l5coef * pow(l, 5))
         + (n / 5040.0 * pow(cos(phi), 7) * l7coef * pow(l, 7))
    )
    
    # Calculate northing (y)
    y = (arcLengthOfMeridian(phi)
         + (t / 2.0 * n * pow(cos(phi), 2) * pow(l, 2))
         + (t / 24.0 * n * pow(cos(phi), 4) * l4coef * pow(l, 4))
         + (t / 720.0 * n * pow(cos(phi), 6) * l6coef * pow(l, 6))
         + (t / 40320.0 * n * pow(cos(phi), 8) * l8coef * pow(l, 8))
    )
    
    # Adjust easing and northing for UTM system.
    x0 = int(round(x * UTM_SCALE_FACTOR + 500000.0))
    y0 = int(round(y * UTM_SCALE_FACTOR))
    y0 += 10000000 if y0 < 0 else 0
    
    # Create coordinate
    return UTMCoordinate(x0, y0, zone, ('S' if lda < 0 else 'N'));



def tester():
    print 'Testing DMS<->WGS...'
    print '----------------------------------------'
    dms = DMSCoordinate(50, 50, 50.555555555, 120, 40, 22.222222222)
    dms2 = WGStoDMS(DMStoWGS(dms))
    latDrift = (((dms2.latitude.degrees - dms.latitude.degrees) * 3600.0)
                + ((dms2.latitude.minutes - dms.latitude.minutes) * 60.0)
                + (dms2.latitude.seconds - dms.latitude.seconds)
    )
    lonDrift = (((dms2.longitude.degrees - dms.longitude.degrees) * 3600.0)
                + ((dms2.longitude.minutes - dms.longitude.minutes) * 60.0)
                + (dms2.longitude.seconds - dms.longitude.seconds)
    )
    print 'DMS in:  {:s}'.format(dms)
    print 'DMS out: {:s}'.format(dms2)
    print 'Latitude drift:  {:.16f}'.format(latDrift)
    print 'Longitude drift: {:.16f}'.format(lonDrift)
    print '----------------------------------------'
    
    print 'Testing UTM<->WGS...'
    print '----------------------------------------'
    utm = UTMCoordinate(292303, 5013403, 33, 'N')
    utm2 = WGStoUTM(UTMtoWGS(utm))
    
    xDrift = utm.x - utm2.x
    yDrift = utm.y - utm2.y
    
    print 'UTM in:  {:s}'.format(utm)
    print 'UTM out: {:s}'.format(utm2)
    print 'X drift: {:.16f}'.format(xDrift)
    print 'Y drift: {:.16f}'.format(yDrift)
    print '----------------------------------------'
    
    print 'Testing WGS<->DMS...'
    print '----------------------------------------'
    wgs = WGSCoordinate(45.12345678, 12.3456789)
    wgs2 = DMStoWGS(WGStoDMS(wgs))
    latDrift = wgs.getLatitudeDegrees() - wgs2.getLatitudeDegrees()
    lonDrift = wgs.getLongitudeDegrees() - wgs2.getLongitudeDegrees()
    print 'WGS in:  {:s}'.format(wgs)
    print 'WGS out: {:s}'.format(wgs2)
    print 'Latitude drift:  {:.16f}'.format(latDrift)
    print 'Longitude drift: {:.16f}'.format(lonDrift)
    print '----------------------------------------'
    
    print 'Testing WGS<->UTM...'
    print '----------------------------------------'
    wgs = WGSCoordinate(45.12345678, 12.3456789)
    wgs2 = UTMtoWGS(WGStoUTM(wgs))
    latDrift = wgs.getLatitudeDegrees() - wgs2.getLatitudeDegrees()
    lonDrift = wgs.getLongitudeDegrees() - wgs2.getLongitudeDegrees()
    print 'WGS in:  {:s}'.format(wgs)
    print 'WGS out: {:s}'.format(wgs2)
    print 'Latitude drift:  {:.16f}'.format(latDrift)
    print 'Longitude drift: {:.16f}'.format(lonDrift)
    print '----------------------------------------'
