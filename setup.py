from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIRES = [
    'geojson==2.4.0',
    'haversine==0.4.5',
    'pytz>=2018.04',
    'requests==2.19.1',
]

setup(
    name="geojson_client",
    version="0.2",
    author="Malte Franken",
    author_email="coding@subspace.de",
    description="A GeoJSON client library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/exxamalte/python-geojson-client",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIRES
)
