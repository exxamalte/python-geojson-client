"""
USGS Earthquake Hazards Program.

Fetches GeoJSON feed from U.S. Geological Survey Earthquake Hazards Program.
"""
import datetime
import logging

from geojson_client import GeoJsonFeed, FeedEntry
from geojson_client.consts import ATTR_TITLE, ATTR_PLACE, ATTR_ID, \
    ATTR_ATTRIBUTION, ATTR_MAG, ATTR_TIME, ATTR_UPDATED, ATTR_ALERT, \
    ATTR_TYPE, ATTR_STATUS
from geojson_client.exceptions import GeoJsonException
from geojson_client.feed_manager import FeedManagerBase

_LOGGER = logging.getLogger(__name__)

URL_PREFIX = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/'
URLS = {
    'past_hour_significant_earthquakes':
        URL_PREFIX + 'significant_hour.geojson',
    'past_hour_m45_earthquakes': URL_PREFIX + '4.5_hour.geojson',
    'past_hour_m25_earthquakes': URL_PREFIX + '2.5_hour.geojson',
    'past_hour_m10_earthquakes': URL_PREFIX + '1.0_hour.geojson',
    'past_hour_all_earthquakes': URL_PREFIX + 'all_hour.geojson',

    'past_day_significant_earthquakes':
        URL_PREFIX + 'significant_day.geojson',
    'past_day_m45_earthquakes': URL_PREFIX + '4.5_day.geojson',
    'past_day_m25_earthquakes': URL_PREFIX + '2.5_day.geojson',
    'past_day_m10_earthquakes': URL_PREFIX + '1.0_day.geojson',
    'past_day_all_earthquakes': URL_PREFIX + 'all_day.geojson',

    'past_week_significant_earthquakes':
        URL_PREFIX + 'significant_week.geojson',
    'past_week_m45_earthquakes': URL_PREFIX + '4.5_week.geojson',
    'past_week_m25_earthquakes': URL_PREFIX + '2.5_week.geojson',
    'past_week_m10_earthquakes': URL_PREFIX + '1.0_week.geojson',
    'past_week_all_earthquakes': URL_PREFIX + 'all_week.geojson',

    'past_month_significant_earthquakes':
        URL_PREFIX + 'significant_month.geojson',
    'past_month_m45_earthquakes': URL_PREFIX + '4.5_month.geojson',
    'past_month_m25_earthquakes': URL_PREFIX + '2.5_month.geojson',
    'past_month_m10_earthquakes': URL_PREFIX + '1.0_month.geojson',
    'past_month_all_earthquakes': URL_PREFIX + 'all_month.geojson',
}


class UsgsEarthquakeHazardsProgramFeedManager(FeedManagerBase):
    """Feed Manager for USGS Earthquake Hazards Program feed."""

    def __init__(self, generate_callback, update_callback, remove_callback,
                 coordinates, feed_type, filter_radius=None,
                 filter_minimum_magnitude=None):
        """Initialize the USGS Earthquake Hazards Program Feed Manager."""
        feed = UsgsEarthquakeHazardsProgramFeed(
            coordinates, feed_type, filter_radius=filter_radius,
            filter_minimum_magnitude=filter_minimum_magnitude)
        super().__init__(feed, generate_callback, update_callback,
                         remove_callback)


class UsgsEarthquakeHazardsProgramFeed(GeoJsonFeed):
    """USGS Earthquake Hazards Program feed."""

    def __init__(self, home_coordinates, feed_type, filter_radius=None,
                 filter_minimum_magnitude=None):
        """Initialise this service."""
        if feed_type in URLS:
            super().__init__(home_coordinates, URLS[feed_type],
                             filter_radius=filter_radius)
        else:
            _LOGGER.error("Unknown feed category %s", feed_type)
            raise GeoJsonException("Feed category must be one of %s" %
                                   URLS.keys())
        self._filter_minimum_magnitude = filter_minimum_magnitude

    def __repr__(self):
        """Return string representation of this feed."""
        return '<{}(home={}, url={}, radius={}, magnitude={})>'.format(
            self.__class__.__name__, self._home_coordinates, self._url,
            self._filter_radius, self._filter_minimum_magnitude)

    def _new_entry(self, home_coordinates, feature, global_data):
        """Generate a new entry."""
        attribution = None if not global_data and ATTR_ATTRIBUTION not in \
            global_data else global_data[ATTR_ATTRIBUTION]
        return UsgsEarthquakeHazardsProgramFeedEntry(home_coordinates,
                                                     feature, attribution)

    def _filter_entries(self, entries):
        """Filter the provided entries."""
        entries = super()._filter_entries(entries)
        if self._filter_minimum_magnitude:
            # Return only entries that have an actual magnitude value, and
            # the value is equal or above the defined threshold.
            return list(filter(lambda entry:
                               entry.magnitude and entry.magnitude >= self.
                               _filter_minimum_magnitude, entries))
        return entries

    def _extract_last_timestamp(self, feed_entries):
        """Determine latest (newest) entry from the filtered feed."""
        if feed_entries:
            dates = sorted([entry.updated for entry in feed_entries],
                           reverse=True)
            return dates[0]
        return None

    def _extract_from_feed(self, feed):
        """Extract global metadata from feed."""
        global_data = {}
        title = self._search_in_metadata(feed, ATTR_TITLE)
        if title:
            global_data[ATTR_ATTRIBUTION] = title
        return global_data

    @staticmethod
    def _search_in_metadata(feed, name):
        """Find an attribute in the metadata object."""
        if feed and 'metadata' in feed and name in feed.metadata:
            return feed.metadata[name]
        return None


class UsgsEarthquakeHazardsProgramFeedEntry(FeedEntry):
    """USGS Earthquake Hazards Program feed entry."""

    def __init__(self, home_coordinates, feature, attribution):
        """Initialise this service."""
        super().__init__(home_coordinates, feature)
        self._attribution = attribution

    @property
    def external_id(self) -> str:
        """Return the external id of this entry."""
        return self._search_in_feature(ATTR_ID)

    @property
    def attribution(self) -> str:
        """Return the attribution of this entry."""
        return self._attribution

    @property
    def title(self) -> str:
        """Return the title of this entry."""
        return self._search_in_properties(ATTR_TITLE)

    @property
    def place(self) -> str:
        """Return the place of this entry."""
        return self._search_in_properties(ATTR_PLACE)

    @property
    def magnitude(self) -> float:
        """Return the magnitude of this entry."""
        return self._search_in_properties(ATTR_MAG)

    @property
    def time(self) -> datetime:
        """Return the time when this event occurred of this entry."""
        publication_date = self._search_in_properties(ATTR_TIME)
        if publication_date:
            # Parse the date. Timestamp in microseconds from unix epoch.
            publication_date = datetime.datetime.fromtimestamp(
                publication_date / 1000, tz=datetime.timezone.utc)
        return publication_date

    @property
    def updated(self) -> datetime:
        """Return the updated date of this entry."""
        updated_date = self._search_in_properties(ATTR_UPDATED)
        if updated_date:
            # Parse the date. Timestamp in microseconds from unix epoch.
            updated_date = datetime.datetime.fromtimestamp(
                updated_date / 1000, tz=datetime.timezone.utc)
        return updated_date

    @property
    def alert(self) -> str:
        """Return the alert level of this entry."""
        return self._search_in_properties(ATTR_ALERT)

    @property
    def type(self) -> str:
        """Return the type of this entry."""
        return self._search_in_properties(ATTR_TYPE)

    @property
    def status(self) -> str:
        """Return the status of this entry."""
        return self._search_in_properties(ATTR_STATUS)
