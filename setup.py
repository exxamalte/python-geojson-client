from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

NAME = "geojson_client"
AUTHOR = "Malte Franken"
AUTHOR_EMAIL = "coding@subspace.de"
DESCRIPTION = "A GeoJSON client library."
URL = "https://github.com/exxamalte/python-geojson-client"

REQUIRES = [
    "geojson>=2.4.0",
    "haversine>=1.0.1",
    "pytz>=2018.04",
    "requests>=2.20.0",
]

setup(
    name=NAME,
    version="0.6",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(exclude=("tests*",)),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIRES,
)
