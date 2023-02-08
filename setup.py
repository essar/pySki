import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "essar_pySki",
    version = "1.0.0",
    author = "Steve Roberts",
    author_email = "steve.roberts@essarsoftware.co.uk",
    description = ("Python implementation of GPS ski data analysis tool."),
    license = "MIT",
    keywords = "python gps ski gsd track",
    url = "https://github.com/essar/pySki",
    packages=['ski', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: Dash"
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)