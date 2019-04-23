'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

from datetime import datetime

class Track:

	def __init__(self, track_id, group_id, track_zdt):
		self.track_id = track_id
		self.group_id = group_id
		self.track_zdt = track_zdt


	def __str__(self):
		return '[{:s}] group={:s} zdt={:s}'.format(self.track_id, self.group_id, self.track_zdt)


class BasicGPSPoint:

	def __init__(self, ts=0, lat=0.0, lon=0.0, alt=0, spd=0.0):
		self.ts = ts
		self.lat = lat
		self.lon = lon
		self.alt = alt
		self.spd = spd


	def vals(self):
		return { 'ts': self.ts, 'lat': self.lat, 'lon': self.lon, 'alt': self.alt, 'spd': self.spd }


	def __str__(self):
		return 'ts={:010d}, lat={:.4f}, lon={:.4f}, a={:04d}, s={:06.2f}'.format(self.ts, self.lat, self.lon, self.alt, self.spd)


class BasicTrackPoint(BasicGPSPoint):

	def __init__(self, track_id, ts=0, lat=0.0, lon=0.0, alt=0, spd=0.0, x=0, y=0, zdt=datetime.fromtimestamp(0)):
		super().__init__(ts, lat, lon, alt, spd)
		self.track_id = track_id
		self.x = x
		self.y = y
		self.zdt = zdt


	def __str__(self):
		return '{:s}/{:d}: lat={:.4f}, lon={:.4f}, a={:d}, s={:.2f}, xy=({:d},{:d}), zdt={:s}'.format(self.track_id, self.ts, self.lat, self.lon, self.alt, self.spd, self.x, self.y, self.zdt.isoformat())
