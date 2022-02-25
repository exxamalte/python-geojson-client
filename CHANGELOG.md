# Changes

## 0.7 (25/02/2022)
* Removed integration with NSW Rural Fire Service, please use async library https://github.com/exxamalte/python-aio-geojson-nsw-rfs-incidents instead.
* Added Python 3.10 support.
* Removed Python 3.6 support.
* Bumped library versions: black, flake8, isort.
* General code improvements.
* Migrated to github actions.

## 0.6 (23/05/2021)
* Allow overriding filters on update (with backwards compatibility).
* Add default `Accept-Encoding: deflate, gzip` request header.
* Added Python 3.9 support.
* Code housekeeping (black formatting, isort, flake8).

## 0.5 (21/10/2020)
* Added Python 3.8 support.
* Drop Python 3.5 support.
* Excluded tests from package.

## 0.4 (05/07/2019)
* Fetch NSW Rural Fire Service feed securely via HTTPS (thanks @davidjb).
* Provide last timestamp from NSW Rural Fire Service feed entries.

## 0.3 (01/11/2018)
* Simple Feed Manager for all feeds added.
* Feed update extracts timestamp in preparation for more sophisticated feed management.
* Third-party library updates.

## 0.2 (15/10/2018)
* Support for U.S. Geological Survey Earthquake Hazards Program feed.
* Filter out entries without any geo location data.

## 0.1 (17/09/2018)
* Initial release with support for generic GeoJSON feeds.
* Support for NSW Rural Fire Service feed.
* Calculating distance to home coordinates.
* Support for filtering by distance for all feeds.
* NSW Rural Fire Service feed supports filtering by category.
