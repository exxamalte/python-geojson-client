# python-geojson-client

This library provides convenient access to [GeoJSON](https://tools.ietf.org/html/rfc7946) Feeds.


## Installation
`pip install geojson-client`

## Usage
See below for examples of how this library can be used for particular GeoJSON feeds. After instantiating a particular class and supply the required parameters, you can call `update` to retrieve the feed data. The return value will be a tuple of a status code and the actual data in the form of a list of feed entries specific to the selected feed.

Status Codes
* _UPDATE_OK_: Update went fine and data was retrieved. The library may still return empty data, for example because no entries fulfilled the filter criteria.
* _UPDATE_OK_NO_DATA_: Update went fine but no data was retrieved, for example because the server indicated that there was not update since the last request.
* _UPDATE_ERROR_: Something went wrong during the update

## Supported GeoJSON Feeds

### Generic Feed

Supported Filters: Distance

**Example**
```python
from geojson_client.generic_feed import GenericFeed
# Home Coordinates: Latitude: -33.0, Longitude: 150.0
# Filter radius: 5000 km
feed = GenericFeed((-33.0, 150.0), filter_radius=5000, url="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson")
status, entries = feed.update()
```

### [NSW Rural Fire Service](https://www.rfs.nsw.gov.au/fire-information/fires-near-me)

Supported Filters: Distance, Category

**Example**
```python
from geojson_client.nsw_rural_fire_service_feed import NswRuralFireServiceFeed
# Home Coordinates: Latitude: -33.0, Longitude: 150.0
# Filter radius: 50 km
# Filter categories: 'Advice'
feed = NswRuralFireServiceFeed((-33.0, 150.0), filter_radius=50, filter_categories=['Advice'])
status, entries = feed.update()
```
