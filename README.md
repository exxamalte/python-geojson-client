# python-geojson-client

[![Build Status](https://github.com/exxamalte/python-geojson-client/workflows/CI/badge.svg?branch=master)](https://github.com/exxamalte/python-geojson-client/actions?workflow=CI)
[![codecov](https://codecov.io/gh/exxamalte/python-geojson-client/branch/master/graph/badge.svg?token=QBJ5QJIDEF)](https://codecov.io/gh/exxamalte/python-geojson-client)
[![PyPi](https://img.shields.io/pypi/v/geojson-client.svg)](https://pypi.python.org/pypi/geojson-client)
[![Version](https://img.shields.io/pypi/pyversions/geojson-client.svg)](https://pypi.python.org/pypi/geojson-client)
[![Maintainability](https://api.codeclimate.com/v1/badges/8c87f480c5043a8599df/maintainability)](https://codeclimate.com/github/exxamalte/python-geojson-client/maintainability)

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

**Supported Filters**

| Filter |                 | Description |
|--------|-----------------|-------------|
| Radius | `filter_radius` | Radius in kilometers around the home coordinates in which events from feed are included. |

**Example**
```python
from geojson_client.generic_feed import GenericFeed
# Home Coordinates: Latitude: -33.0, Longitude: 150.0
# Filter radius: 500 km
feed = GenericFeed((-33.0, 150.0), filter_radius=500, 
                   url="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson")
status, entries = feed.update()
```

### [NSW Rural Fire Service](https://www.rfs.nsw.gov.au/fire-information/fires-near-me)

Please migrate to the async library https://github.com/exxamalte/python-aio-geojson-nsw-rfs-incidents instead. 

### [U.S. Geological Survey Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)

**Supported Feeds**

| Category                               | Feed                                 |
|----------------------------------------|--------------------------------------|
| Past Hour - Significant Earthquakes    | `past_hour_significant_earthquakes`  |
| Past Hour - M4.5+ Earthquakes          | `past_hour_m45_earthquakes`          |
| Past Hour - M2.5+ Earthquakes          | `past_hour_m25_earthquakes`          |
| Past Hour - M1.0+ Earthquakes          | `past_hour_m10_earthquakes`          |
| Past Hour - All Earthquakes            | `past_hour_all_earthquakes`          |
| Past Day - Significant Earthquakes     | `past_day_significant_earthquakes`   |
| Past Day - M4.5+ Earthquakes           | `past_day_m45_earthquakes`           |
| Past Day - M2.5+ Earthquakes           | `past_day_m25_earthquakes`           |
| Past Day - M1.0+ Earthquakes           | `past_day_m10_earthquakes`           |
| Past Day - All Earthquakes             | `past_day_all_earthquakes`           |
| Past 7 Days - Significant Earthquakes  | `past_week_significant_earthquakes`  |
| Past 7 Days - M4.5+ Earthquakes        | `past_week_m45_earthquakes`          |
| Past 7 Days - M2.5+ Earthquakes        | `past_week_m25_earthquakes`          |
| Past 7 Days - M1.0+ Earthquakes        | `past_week_m10_earthquakes`          |
| Past 7 Days - All Earthquakes          | `past_week_all_earthquakes`          |
| Past 30 Days - Significant Earthquakes | `past_month_significant_earthquakes` |
| Past 30 Days - M4.5+ Earthquakes       | `past_month_m45_earthquakes`         |
| Past 30 Days - M2.5+ Earthquakes       | `past_month_m25_earthquakes`         |
| Past 30 Days - M1.0+ Earthquakes       | `past_month_m10_earthquakes`         |
| Past 30 Days - All Earthquakes         | `past_month_all_earthquakes`         |

**Supported Filters**

| Filter            |                            | Description |
|-------------------|----------------------------|-------------|
| Radius            | `filter_radius`            | Radius in kilometers around the home coordinates in which events from feed are included. |
| Minimum Magnitude | `filter_minimum_magnitude` | Minimum magnitude as float value. Only event with a magnitude equal or above this value are included. |

**Example**
```python
from geojson_client.usgs_earthquake_hazards_program_feed import UsgsEarthquakeHazardsProgramFeed
# Home Coordinates: Latitude: 21.3, Longitude: -157.8
# Feed: Past Day - All Earthquakes
# Filter radius: 500 km
# Filter minimum magnitude: 4.0
feed = UsgsEarthquakeHazardsProgramFeed((21.3, -157.8), 'past_day_all_earthquakes', 
                                        filter_radius=500, filter_minimum_magnitude=4.0)
status, entries = feed.update()
```

## Feed Managers

The Feed Managers help managing feed updates over time, by notifying the 
consumer of the feed about new feed entries, updates and removed entries 
compared to the last feed update.

* If the current feed update is the first one, then all feed entries will be 
  reported as new. The feed manager will keep track of all feed entries' 
  external IDs that it has successfully processed.
* If the current feed update is not the first one, then the feed manager will 
  produce three sets:
  * Feed entries that were not in the previous feed update but are in the 
    current feed update will be reported as new.
  * Feed entries that were in the previous feed update and are still in the 
    current feed update will be reported as to be updated.
  * Feed entries that were in the previous feed update but are not in the 
    current feed update will be reported to be removed.
* If the current update fails, then all feed entries processed in the previous
  feed update will be reported to be removed.

After a successful update from the feed, the feed manager will provide two
different dates:

* `last_update` will be the timestamp of the last successful update from the
  feed. This date may be useful if the consumer of this library wants to
  treat intermittent errors from feed updates differently.
* `last_timestamp` will be the latest timestamp extracted from the feed data. 
  This requires that the underlying feed data actually contains a suitable 
  date. This date may be useful if the consumer of this library wants to 
  process feed entries differently if they haven't actually been updated.
