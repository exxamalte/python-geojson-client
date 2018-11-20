"""
Base class for GeoJSON services.

Fetches GeoJSON feed from URL to be defined by sub-class.
"""
from datetime import datetime
import geojson
import logging

import requests
from geojson import Point, GeometryCollection, Polygon
from haversine import haversine
from json import JSONDecodeError
from typing import Optional

_LOGGER = logging.getLogger(__name__)

UPDATE_OK = 'OK'
UPDATE_OK_NO_DATA = 'OK_NO_DATA'
UPDATE_ERROR = 'ERROR'


class GeoJsonFeed:
    """Geo JSON feed base class."""

    def __init__(self, home_coordinates, url, filter_radius=None):
        """Initialise this service."""
        self._home_coordinates = home_coordinates
        self._filter_radius = filter_radius
        self._url = url
        self._request = requests.Request(method="GET", url=url).prepare()
        self._last_timestamp = None

    def __repr__(self):
        """Return string representation of this feed."""
        return '<{}(home={}, url={}, radius={})>'.format(
            self.__class__.__name__, self._home_coordinates, self._url,
            self._filter_radius)

    def _new_entry(self, home_coordinates, feature, global_data):
        """Generate a new entry."""
        pass

    def update(self):
        """Update from external source and return filtered entries."""
        status, data = self._fetch()
        if status == UPDATE_OK:
            if data:
                entries = []
                global_data = self._extract_from_feed(data)
                # Extract data from feed entries.
                for feature in data.features:
                    entries.append(self._new_entry(self._home_coordinates,
                                                   feature, global_data))
                filtered_entries = self._filter_entries(entries)
                self._last_timestamp = self._extract_last_timestamp(
                    filtered_entries)
                return UPDATE_OK, filtered_entries
            else:
                # Should not happen.
                return UPDATE_OK, None
        elif status == UPDATE_OK_NO_DATA:
            # Happens for example if the server returns 304
            return UPDATE_OK_NO_DATA, None
        else:
            # Error happened while fetching the feed.
            return UPDATE_ERROR, None

    def _fetch(self):
        """Fetch GeoJSON data from external source."""
        try:
            with requests.Session() as session:
                response = session.send(self._request, timeout=10)
            if response.ok:
                feature_collection = geojson.loads(response.text)
                return UPDATE_OK, feature_collection
            else:
                _LOGGER.warning(
                    "Fetching data from %s failed with status %s",
                    self._request.url, response.status_code)
                return UPDATE_ERROR, None
        except requests.exceptions.RequestException as request_ex:
            _LOGGER.warning("Fetching data from %s failed with %s",
                            self._request.url, request_ex)
            return UPDATE_ERROR, None
        except JSONDecodeError as decode_ex:
            _LOGGER.warning("Unable to parse JSON from %s: %s",
                            self._request.url, decode_ex)
            return UPDATE_ERROR, None

    def _filter_entries(self, entries):
        """Filter the provided entries."""
        filtered_entries = entries
        # Always remove entries without geometry
        filtered_entries = list(
            filter(lambda entry:
                   entry.geometry is not None,
                   filtered_entries))
        # Filter by distance.
        if self._filter_radius:
            filtered_entries = list(
                filter(lambda entry:
                       entry.distance_to_home <= self._filter_radius,
                       filtered_entries))
        return filtered_entries

    def _extract_from_feed(self, feed):
        """Extract global metadata from feed."""
        return None

    def _extract_last_timestamp(self, feed_entries):
        """Determine latest (newest) entry from the filtered feed."""
        return None

    @property
    def last_timestamp(self) -> Optional[datetime]:
        """Return the last timestamp extracted from this feed."""
        return self._last_timestamp


class FeedEntry:
    """Feed entry base class."""

    def __init__(self, home_coordinates, feature):
        """Initialise this feed entry."""
        self._home_coordinates = home_coordinates
        self._feature = feature

    def __repr__(self):
        """Return string representation of this entry."""
        return '<{}(id={})>'.format(self.__class__.__name__, self.external_id)

    @property
    def geometry(self):
        """Return all geometry details of this entry."""
        if self._feature:
            return self._feature.geometry
        return None

    @property
    def coordinates(self):
        """Return the best coordinates (latitude, longitude) of this entry."""
        if self.geometry:
            return GeoJsonDistanceHelper.extract_coordinates(self.geometry)
        return None

    @property
    def title(self) -> Optional[str]:
        """Return the title of this entry."""
        return None

    @property
    def external_id(self) -> Optional[str]:
        """Return the external id of this entry."""
        return None

    @property
    def attribution(self) -> Optional[str]:
        """Return the attribution of this entry."""
        return None

    @property
    def distance_to_home(self):
        """Return the distance in km of this entry to the home coordinates."""
        return GeoJsonDistanceHelper.distance_to_geometry(
            self._home_coordinates, self.geometry)

    def _search_in_feature(self, name):
        """Find an attribute in the feature object."""
        if self._feature and name in self._feature:
            return self._feature[name]
        return None

    def _search_in_properties(self, name):
        """Find an attribute in the feed entry's properties."""
        if self._feature and self._feature.properties \
                and name in self._feature.properties:
            return self._feature.properties[name]
        return None


class GeoJsonDistanceHelper:
    """Helper to calculate distances between GeoJSON geometries."""

    def __init__(self):
        """Initialize the geo distance helper."""
        pass

    @staticmethod
    def extract_coordinates(geometry):
        """Extract the best coordinates from the feature for display."""
        latitude = longitude = None
        if isinstance(geometry, Point):
            # Just extract latitude and longitude directly.
            latitude, longitude = geometry.coordinates[1], \
                                  geometry.coordinates[0]
        elif isinstance(geometry, GeometryCollection):
            # Go through the collection, and extract the first suitable
            # geometry.
            for entry in geometry.geometries:
                latitude, longitude = \
                    GeoJsonDistanceHelper.extract_coordinates(entry)
                if latitude is not None and longitude is not None:
                    break
        elif isinstance(geometry, Polygon):
            # Find the polygon's centroid as a best approximation for the map.
            longitudes_list = [point[0] for point in geometry.coordinates[0]]
            latitudes_list = [point[1] for point in geometry.coordinates[0]]
            number_of_points = len(geometry.coordinates[0])
            longitude = sum(longitudes_list) / number_of_points
            latitude = sum(latitudes_list) / number_of_points
            _LOGGER.debug("Centroid of %s is %s", geometry.coordinates[0],
                          (latitude, longitude))
        else:
            _LOGGER.debug("Not implemented: %s", type(geometry))
        return latitude, longitude

    @staticmethod
    def distance_to_geometry(home_coordinates, geometry):
        """Calculate the distance between home coordinates and geometry."""
        distance = float("inf")
        if isinstance(geometry, Point):
            distance = GeoJsonDistanceHelper._distance_to_point(
                home_coordinates, geometry)
        elif isinstance(geometry, GeometryCollection):
            distance = GeoJsonDistanceHelper._distance_to_geometry_collection(
                home_coordinates, geometry)
        elif isinstance(geometry, Polygon):
            distance = GeoJsonDistanceHelper._distance_to_polygon(
                home_coordinates, geometry.coordinates[0])
        else:
            _LOGGER.debug("Not implemented: %s", type(geometry))
        return distance

    @staticmethod
    def _distance_to_point(home_coordinates, point):
        """Calculate the distance between home coordinates and the point."""
        # Swap coordinates to match: (latitude, longitude).
        return GeoJsonDistanceHelper._distance_to_coordinates(
            home_coordinates, (point.coordinates[1], point.coordinates[0]))

    @staticmethod
    def _distance_to_geometry_collection(home_coordinates,
                                         geometry_collection):
        """Calculate the distance between home coordinates and the geometry
        collection."""
        distance = float("inf")
        for geometry in geometry_collection.geometries:
            distance = min(distance,
                           GeoJsonDistanceHelper.distance_to_geometry(
                               home_coordinates, geometry))
        return distance

    @staticmethod
    def _distance_to_polygon(home_coordinates, polygon):
        """Calculate the distance between home coordinates and the polygon."""
        distance = float("inf")
        # Calculate distance from polygon by calculating the distance
        # to each point of the polygon but not to each edge of the
        # polygon; should be good enough
        for polygon_point in polygon:
            distance = min(distance,
                           GeoJsonDistanceHelper._distance_to_coordinates(
                               home_coordinates,
                               (polygon_point[1], polygon_point[0])))
        return distance

    @staticmethod
    def _distance_to_coordinates(home_coordinates, coordinates):
        """Calculate the distance between home coordinates and the
        coordinates."""
        # Expecting coordinates in format: (latitude, longitude).
        return haversine(coordinates, home_coordinates)
