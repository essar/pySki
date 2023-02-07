# SkiData Dashboard

This is an application that displays skiier's GPS data on a set of dashboards for analysis.

## Capabilities

- Import data from a selection of sources
  - GSD format files
  - GPX format files
  - Direct from a Globalsat DG100/DG200 datalogger via USB/serial

- Store data in AWS DynamoDB for large scale processing.

- Interactive, dynamic HTML/JS charts using (Plotly)[https://plotly.com/python/].


## History

SkiData has undergone a number of iterations and evolutions. Various forms of the project have previously existed, written in Java (for Android), Python and JavaScript. These are stored in archive branches in the repository for prosterity, but are deprecated and unsupported.


## Dependencies & Libraries

- Pandas
- (Plotly)[https://plotly.com/python/]
- (pySerial)[https://pythonhosted.org/pyserial/index.html]
- (SciPi)[https://scipy.org/]
- (TimezoneFinder)[https://timezonefinder.readthedocs.io/en/latest/index.html]
