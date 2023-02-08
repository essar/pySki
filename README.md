# SkiData Dashboard

This is an application that displays skier's GPS data on a set of dashboards for analysis.

![Tests](https://github.com/essar/pySki/actions/workflows/tests.yml/badge.svg)  ![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/essar/208eb98099788c4db260c7791537bd85/raw/pySki_coverage_badge.json)

## Capabilities

- Import data from a selection of sources
  - GSD format files
  - GPX format files
  - Direct from a Globalsat DG100/DG200 datalogger via USB/serial
- Store data in AWS DynamoDB for large scale processing.
- Interactive, dynamic HTML/JS charts using [Dash](https://dash.plotly.com/).


## History

SkiData has undergone a number of iterations and evolutions. Various forms of the project have previously existed, written in Java (for Android), Python and JavaScript. These are stored in archive branches in the repository for prosterity, but are deprecated and unsupported.

## Dependencies & Libraries

- Pandas
- [Plotly](https://plotly.com/python/)
- [pySerial](https://pythonhosted.org/pyserial/index.html)
- [SciPi](https://scipy.org/)
- [TimezoneFinder](https://timezonefinder.readthedocs.io/en/latest/index.html)
