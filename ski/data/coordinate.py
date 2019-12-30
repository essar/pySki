"""
  Module providing functions and classes for manipulating and translating
  between different geometric coordinate conversions.
"""

from math import cos, degrees, pi, pow, radians, sin, sqrt, tan

################################
# COORDINATE CONSTANTS
########
SM_A = 6378137.0
SM_B = 6356752.314
UTM_SCALE_FACTOR = 0.9996
WGS_COORD_MODE_DEG = 0x01
WGS_COORD_MODE_RAD = 0x02


################################
# COORDINATE UTILITY FUNCTIONS
########

def add_seconds(degs, decimal_mins):
    mins = int(decimal_mins)
    secs = (decimal_mins % max(1, mins)) * 60.0
    return degs, mins, secs


def arc_length_of_meridian(phi):
    """
      Compute the ellipsoidal distance from the equator to a point at a given latitude.
      
      Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
      GPS: Theory and Practice, 3rd ed. New York: Springer-Verlag Wien, 1994.
      
      Globals:
        sm_a - Ellipsoid model major axis.
        sm_b - Ellipsoid model minor axis.
      
      Params:
        phi: Latitude of the point, in radians.
      
      Returns the ellipsoidal distance of the point from the equator, in metres.
    """
    # Calculate n
    n = (SM_A - SM_B) / (SM_A + SM_B)

    # Calculate alpha
    alpha = ((SM_A + SM_B) / 2.0) * (1.0 + (pow(n, 2) / 4.0) + (pow(n, 4) / 64.0))
    # Calculate beta
    beta = (-3.0 * n / 2.0) + (9.0 * pow(n, 3) / 16.0) + (-3.0 * pow(n, 5) / 32.0)
    # Calculate gamma
    gamma = (15.0 * pow(n, 2) / 16.0) + (-15.0 * pow(n, 4) / 32.0)
    # Calculate delta
    delta = (-35.0 * pow(n, 3) / 48.0) + (105.0 * pow(n, 5) / 256.0)
    # Calculate epsilon
    epsilon = 315.0 * pow(n, 4) / 512.0
    
    # Now calculate the sum of the series and return
    result = (alpha * (phi + (beta * sin(2.0 * phi))
              + (gamma * sin(4.0 * phi))
              + (delta * sin(6.0 * phi))
              + (epsilon * sin(8.0 * phi))
              ))

    return result


def calc_central_meridian(zone):
    """
      Determine the central meridian for the given UTM zone.
      @param zone: An integer value designating the UTM zone, range [1,60].
      @return The central meridian for the given UTM zone, in radians, or zero if
      the UTM zone parameter is outside the range [1,60].
      Range of the central meridian is the radian equivalent of [-177,+177].
    """
    if zone < 1 or zone > 60:
        return 0.0
    return radians(-183 + (zone * 6))


def footprint_latitude(y):
    """
      Compute the footpoint latitude for use in converting transverse
      Mercator coordinates to ellipsoidal coordinates.
    
      Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
      GPS: Theory and Practice, 3rd ed. New York: Springer-Verlag Wien, 1994.
     
      Params:
        y: The UTM northing coordinate, in meters.
      
      Returns the footpoint latitude, in radians.
    """
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
    """Represents an element within a DMS coordinate (degrees, minutes and seconds)."""
    def __init__(self, degs, minutes, seconds, hemisphere):
        self.degrees = degs
        self.minutes = minutes
        self.seconds = seconds
        self.hemisphere = hemisphere
        
    def __str__(self):
        return '({0:d} {1:02d}\'{2:.2f}"{3:1s})'.format(self.degrees, self.minutes, self.seconds, self.hemisphere)


class DMSCoordinate:
    """Represents a coordinate specified in DMS format (degrees, minutes and seconds)."""
    def __init__(self, lat_d, lat_m, lat_s, lon_d, lon_m, lon_s):
        #
        # LATITUDE
        #
        
        # Calculate hemisphere indicator
        lat_x = 'S' if lat_d < 0 else 'N'
        lat_d = abs(lat_d)
        
        # Adjust out-of-range minutes and seconds
        if lat_s >= 60:
            lat_m += lat_s / 60
            lat_s = lat_s % 60
        if lat_m >= 60:
            lat_d += lat_m / 60
            lat_m = lat_m % 60

        # Check coordinate in legal range
        if lat_d < -90 or lat_d > 90:
            raise CoordinateError('DMS latitude out of range: {:d}', lat_d)

        # Set latitude element
        self.latitude = DMSElement(lat_d, lat_m, lat_s, lat_x)

        #
        # LONGITUDE
        #
        
        # Calculate hemisphere indicator
        lon_x = 'W' if lon_d < 0 else 'E'
        lon_d = abs(lon_d)
        
        # Adjust out-of-range minutes and seconds
        if lon_s >= 60:
            lon_m += lon_s / 60
            lon_s = lon_s % 60
        if lon_m >= 60:
            lon_d += lon_m / 60
            lon_m = lon_m % 60

        # Check coordinate in legal range
        if lon_d < -180 or lon_d > 180:
            raise CoordinateError('DMS longitude out of range: {:d}', lon_d)

        # Set longitude element
        self.longitude = DMSElement(lon_d, lon_m, lon_s, lon_x)

    def __str__(self):
        return 'lat:{0}, lon:{1}'.format(str(self.latitude), str(self.longitude))


class UTMCoordinate:
    """Represents a coordinate specified in UTM format (cartesian X & Y)."""
    def __init__(self, x, y, zone, band):
        # Check easing in legal range
        if x < 0:
            raise CoordinateError('UTM easing coordinate out of range: {:d}', x)
        self.x = int(x)
        self.x_over = x % 1
        
        # Check northing in legal range
        if y < 0:
            raise CoordinateError('UTM northing coordinate out of range: {:d}', y)
        self.y = int(y)
        self.y_over = y % 1
        
        # Check zone in legal range
        if zone < 1 or zone > 60:
            raise CoordinateError('UTM zone input out of range: {:s}', zone)
        self.zone = zone
        
        # Check band is N or S
        if band != 'N' and band != 'S':
            raise CoordinateError('UTM band input out of range {:s)', band)
        self.band = band

    def __str__(self):
        return '{:d}{:s} {:d} {:d}'.format(self.zone, self.band, self.x, self.y)

    def get_central_meridian(self):
        return calc_central_meridian(self.zone)
    

class WGSCoordinate:
    """Represents a coordinate specified in WGS84 format (latitude & longitude)."""
    def __init__(self, latitude, longitude, coord_mode=WGS_COORD_MODE_DEG):
        if coord_mode == WGS_COORD_MODE_DEG:
            # Check latitude in legal range
            if latitude < -90.0 or latitude > 90.0:
                raise CoordinateError('Latitude degree input out of range: {:f}', latitude)
            self.latitude = radians(latitude)

            # Check longitude in legal range
            if longitude < -180.0 or longitude > 180.0:
                raise CoordinateError('Longitude degree input out of range: {:f}', longitude)
            self.longitude = radians(longitude)

        if coord_mode == WGS_COORD_MODE_RAD:
            # Check latitude in legal range
            if latitude < (-pi / 2.0) or latitude > (pi / 2.0):
                raise CoordinateError('Latitude radian input out of range: {:f}', latitude)
            self.latitude = latitude

            # Check longitude in legal range
            if longitude < -pi or longitude > pi:
                raise CoordinateError('Longitude radian input out of range {:f}', longitude)
            self.longitude = longitude

    def __str__(self):
        return '{:3.6f}, {:3.6f}'.format(self.get_latitude_degrees(), self.get_longitude_degrees())

    def get_latitude_degrees(self):
        return float(degrees(self.latitude))

    def get_longitude_degrees(self):
        return float(degrees(self.longitude))
    
    
################################
# COORDINATE CONVERSION FUNCTIONS
########
    
def dms_to_wgs(dms):
    """
      Convert from DMS to WGS format.

      Params:
        dms: the input coordinate in DMS format.
      
      Returns the same coordinate in WGS84 format.
    """
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

    return WGSCoordinate(float(lat), float(lon), WGS_COORD_MODE_DEG)


def wgs_to_dms(wgs):
    """
      Convert from WGS to DMS format.

      Params:
        wgs: the input coordinate in WGS84 format.
      
      Returns the same coordinate in DMS format.
    """
    # Break down latitude degrees into D M S components
    lat_deg = int(wgs.get_latitude_degrees())
    lat_ms = (wgs.get_latitude_degrees() - lat_deg) * 60.0 * 60.0
    lat_m = int(lat_ms / 60.0)
    lat_s = lat_ms % 60.0

    # Break down longitude degrees into D M S components
    lon_deg = int(wgs.get_longitude_degrees())
    lon_ms = (wgs.get_longitude_degrees() - lon_deg) * 60.0 * 60.0
    lon_m = int(lon_ms / 60)
    lon_s = lon_ms % 60

    # Build coordinate object
    return DMSCoordinate(lat_deg, lat_m, lat_s, lon_deg, lon_m, lon_s)


def utm_to_wgs(utm):
    """
      Converts x and y coordinates in the Transverse Mercator projection to
      a latitude/longitude pair. Note that Transverse Mercator is not
      the same as UTM; a scale factor is required to convert between them.
     
      Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
      GPS: Theory and Practice, 3rd ed. New York: Springer-Verlag Wien, 1994.
     
      Params:
        utm: the input coordinate in UTM format.
      
      Returns the same coordinate in WGS84 format.
    """
    
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
    lambda0 = utm.get_central_meridian()
    # Get the value of phif, the footpoint latitude.
    phif = footprint_latitude(y)
    # Calculate ep2
    ep2 = (pow(SM_A, 2) - pow(SM_B, 2)) / pow(SM_B, 2)
    # Calculate cos(phif)
    cf = cos(phif)
    # Calculate nuf2
    nuf2 = ep2 * pow(cf, 2)

    # Calculate nf and initialize nfpow
    nf = pow(SM_A, 2) / (SM_B * sqrt(1.0 + nuf2))
    nf_pow = nf
        
    # Calculate tf
    tf = tan(phif)
    tf2 = tf * tf
    tf4 = tf2 * tf2
        
    # Calculate fractional coefficients for x**n in the equations
    # below to simplify the expressions for latitude and longitude.
    x1frac = 1.0 / (nf_pow * cf)
        
    nf_pow *= nf     # now equals Nf^2
    x2frac = tf / (2.0 * nf_pow)
        
    nf_pow *= nf     # now equals Nf^3
    x3frac = 1.0 / (6.0 * nf_pow * cf)
        
    nf_pow *= nf     # now equals Nf^4
    x4frac = tf / (24.0 * nf_pow)
        
    nf_pow *= nf     # now equals Nf^5
    x5frac = 1.0 / (120.0 * nf_pow * cf)
        
    nf_pow *= nf     # now equals Nf^6
    x6frac = tf / (720.0 * nf_pow)
        
    nf_pow *= nf     # now equals Nf^7
    x7frac = 1.0 / (5040.0 * nf_pow * cf)
        
    nf_pow *= nf     # now equals Nf^8
    x8frac = tf / (40320.0 * nf_pow)
        
    # Calculate polynomial coefficients for x^n.
    #   -- x^1 does not have a polynomial coefficient.
    x2poly = -1.0 - nuf2
    x3poly = -1.0 - 2 * tf2 - nuf2
    x4poly = 5.0 + 3.0 * tf2 + 6.0 * nuf2 - 6.0 * tf2 * nuf2 - 3.0 * (nuf2 * nuf2) - 9.0 * tf2 * (nuf2 * nuf2)
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
           + x3frac * x3poly * pow(x, 3.0)
           + x5frac * x5poly * pow(x, 5.0)
           + x7frac * x7poly * pow(x, 7.0)
           )
        
    # Build coordinate
    return WGSCoordinate(float(lat), float(lon), WGS_COORD_MODE_RAD)


def wgs_to_utm(wgs):
    """
      Converts a latitude/longitude pair to x and y coordinates in the
      Transverse Mercator projection. Note that Transverse Mercator is not
      the same as UTM; a scale factor is required to convert between them.
     
      Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
      GPS: Theory and Practice, 3rd ed. New York: Springer-Verlag Wien, 1994.
     
      Params:
        wgs: the input coordinate, in WGS84 format.
      
      Returns the same coordinate in UTM format.
    """
    phi = wgs.latitude
    lda = wgs.longitude
    
    # Calculate UTM zone
    zone = int((wgs.get_longitude_degrees() + 180.0) / 6.0) + 1
        
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
    lda0 = calc_central_meridian(zone)
    lx = lda - lda0
    
    # Calculate coefficients for l^n in the equations below so a normal human being
    # can read the expressions for easting and northing
    
    # l^1 and l^2 have coefficients of 1.0 */
    
    l3 = 1.0 - t2 + nu2
    l4 = 5.0 - t2 + 9.0 * nu2 + 4.0 * (nu2 * nu2)
    l5 = 5.0 - 18.0 * t2 + (t2 * t2) + 14.0 * nu2 - 58.0 * t2 * nu2
    l6 = 61.0 - 58.0 * t2 + (t2 * t2) + 270.0 * nu2 - 330.0 * t2 * nu2
    l7 = 61.0 - 479.0 * t2 + 179.0 * (t2 * t2) - (t2 * t2 * t2)
    l8 = 1385.0 - 3111.0 * t2 + 543.0 * (t2 * t2) - (t2 * t2 * t2)
    
    # Calculate easing (x)
    x = (n * cos(phi) * lx
         + (n / 6.0 * pow(cos(phi), 3) * l3 * pow(lx, 3))
         + (n / 120.0 * pow(cos(phi), 5) * l5 * pow(lx, 5))
         + (n / 5040.0 * pow(cos(phi), 7) * l7 * pow(lx, 7))
         )
    
    # Calculate northing (y)
    y = (arc_length_of_meridian(phi)
         + (t / 2.0 * n * pow(cos(phi), 2) * pow(lx, 2))
         + (t / 24.0 * n * pow(cos(phi), 4) * l4 * pow(lx, 4))
         + (t / 720.0 * n * pow(cos(phi), 6) * l6 * pow(lx, 6))
         + (t / 40320.0 * n * pow(cos(phi), 8) * l8 * pow(lx, 8))
         )
    
    # Adjust easing and northing for UTM system.
    x0 = int(round(x * UTM_SCALE_FACTOR + 500000.0))
    y0 = int(round(y * UTM_SCALE_FACTOR))
    y0 += 10000000 if y0 < 0 else 0
    
    # Create coordinate
    return UTMCoordinate(x0, y0, zone, ('S' if lda < 0 else 'N'))


def tester():
    print('Testing DMS<->WGS...')
    print('----------------------------------------')
    dms = DMSCoordinate(50, 50, 50.555555555, 120, 40, 22.222222222)
    dms2 = wgs_to_dms(dms_to_wgs(dms))
    lat_drift = (((dms2.latitude.degrees - dms.latitude.degrees) * 3600.0)
                 + ((dms2.latitude.minutes - dms.latitude.minutes) * 60.0)
                 + (dms2.latitude.seconds - dms.latitude.seconds)
                 )
    lon_drift = (((dms2.longitude.degrees - dms.longitude.degrees) * 3600.0)
                 + ((dms2.longitude.minutes - dms.longitude.minutes) * 60.0)
                 + (dms2.longitude.seconds - dms.longitude.seconds)
                 )
    print('DMS in:  {:s}'.format(dms))
    print('DMS out: {:s}'.format(dms2))
    print('Latitude drift:  {:.16f}'.format(lat_drift))
    print('Longitude drift: {:.16f}'.format(lon_drift))
    print('----------------------------------------')
    
    print('Testing UTM<->WGS...')
    print('----------------------------------------')
    utm = UTMCoordinate(292303, 5013403, 33, 'N')
    utm2 = wgs_to_utm(utm_to_wgs(utm))
    
    x_drift = utm.x - utm2.x
    y_drift = utm.y - utm2.y
    
    print('UTM in:  {:s}'.format(utm))
    print('UTM out: {:s}'.format(utm2))
    print('X drift: {:.16f}'.format(x_drift))
    print('Y drift: {:.16f}'.format(y_drift))
    print('----------------------------------------')
    
    print('Testing WGS<->DMS...')
    print('----------------------------------------')
    wgs = WGSCoordinate(45.12345678, 12.3456789)
    wgs2 = dms_to_wgs(wgs_to_dms(wgs))
    lat_drift = wgs.get_latitude_degrees() - wgs2.get_latitude_degrees()
    lon_drift = wgs.get_longitude_degrees() - wgs2.get_longitude_degrees()
    print('WGS in:  {:s}'.format(wgs))
    print('WGS out: {:s}'.format(wgs2))
    print('Latitude drift:  {:.16f}'.format(lat_drift))
    print('Longitude drift: {:.16f}'.format(lon_drift))
    print('----------------------------------------')
    
    print('Testing WGS<->UTM...')
    print('----------------------------------------')
    wgs = WGSCoordinate(45.12345678, 12.3456789)
    wgs2 = utm_to_wgs(wgs_to_utm(wgs))
    lat_drift = wgs.get_latitude_degrees() - wgs2.get_latitude_degrees()
    lon_drift = wgs.get_longitude_degrees() - wgs2.get_longitude_degrees()
    print('WGS in:  {:s}'.format(wgs))
    print('WGS out: {:s}'.format(wgs2))
    print('Latitude drift:  {:.16f}'.format(lat_drift))
    print('Longitude drift: {:.16f}'.format(lon_drift))
    print('----------------------------------------')
