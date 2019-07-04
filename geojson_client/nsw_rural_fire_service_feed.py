"""
NSW Rural Fire Service.

Fetches GeoJSON feed from NSW Rural Fire Service.
"""
import pytz
import calendar
from datetime import datetime
from time import strptime

import logging
import re
from typing import Optional

from geojson_client import GeoJsonFeed, FeedEntry
from geojson_client.consts import ATTR_GUID, ATTR_TITLE, ATTR_CATEGORY, \
    ATTR_DESCRIPTION, ATTR_PUB_DATE
from geojson_client.feed_manager import FeedManagerBase

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "State of New South Wales (NSW Rural Fire Service)"

CUSTOM_ATTRIBUTE = 'custom_attribute'

REGEXP_ATTR_COUNCIL_AREA = 'COUNCIL AREA: (?P<{}>[^<]+) <br'\
    .format(CUSTOM_ATTRIBUTE)
REGEXP_ATTR_FIRE = 'FIRE: (?P<{}>[^<]+) <br'.format(CUSTOM_ATTRIBUTE)
REGEXP_ATTR_LOCATION = 'LOCATION: (?P<{}>[^<]+) <br'.format(CUSTOM_ATTRIBUTE)
REGEXP_ATTR_RESPONSIBLE_AGENCY = 'RESPONSIBLE AGENCY: (?P<{}>[^<]+) <br'\
    .format(CUSTOM_ATTRIBUTE)
REGEXP_ATTR_SIZE = 'SIZE: (?P<{}>[^<]+) <br'.format(CUSTOM_ATTRIBUTE)
REGEXP_ATTR_STATUS = 'STATUS: (?P<{}>[^<]+) <br'.format(CUSTOM_ATTRIBUTE)
REGEXP_ATTR_TYPE = 'TYPE: (?P<{}>[^<]+) <br'.format(CUSTOM_ATTRIBUTE)

URL = "https://www.rfs.nsw.gov.au/feeds/majorIncidents.json"

VALID_CATEGORIES = ['Emergency Warning', 'Watch and Act', 'Advice',
                    'Not Applicable']


class NswRuralFireServiceFeedManager(FeedManagerBase):
    """Feed Manager for NSW Rural Fire Services feed."""

    def __init__(self, generate_callback, update_callback, remove_callback,
                 coordinates, filter_radius=None, filter_categories=None):
        """Initialize the NSW Rural Fire Services Feed Manager."""
        feed = NswRuralFireServiceFeed(coordinates,
                                       filter_radius=filter_radius,
                                       filter_categories=filter_categories)
        super().__init__(feed, generate_callback, update_callback,
                         remove_callback)


class NswRuralFireServiceFeed(GeoJsonFeed):
    """NSW Rural Fire Services feed."""

    def __init__(self, home_coordinates, filter_radius=None,
                 filter_categories=None):
        """Initialise this service."""
        super().__init__(home_coordinates, URL, filter_radius=filter_radius)
        self._filter_categories = filter_categories

    def __repr__(self):
        """Return string representation of this feed."""
        return '<{}(home={}, url={}, radius={}, categories={})>'.format(
            self.__class__.__name__, self._home_coordinates, self._url,
            self._filter_radius, self._filter_categories)

    def _new_entry(self, home_coordinates, feature, global_data):
        """Generate a new entry."""
        return NswRuralFireServiceFeedEntry(home_coordinates, feature)

    def _filter_entries(self, entries):
        """Filter the provided entries."""
        entries = super()._filter_entries(entries)
        if self._filter_categories:
            return list(filter(lambda entry:
                               entry.category in self._filter_categories,
                               entries))
        return entries

    def _extract_last_timestamp(self, feed_entries):
        """Determine latest (newest) entry from the filtered feed."""
        if feed_entries:
            dates = sorted(filter(
                None, [entry.publication_date for entry in feed_entries]),
                reverse=True)
            return dates[0]
        return None


class NswRuralFireServiceFeedEntry(FeedEntry):
    """NSW Rural Fire Service feed entry."""

    def __init__(self, home_coordinates, feature):
        """Initialise this service."""
        super().__init__(home_coordinates, feature)

    @property
    def attribution(self) -> Optional[str]:
        """Return the attribution of this entry."""
        return ATTRIBUTION

    @property
    def title(self) -> str:
        """Return the title of this entry."""
        return self._search_in_properties(ATTR_TITLE)

    @property
    def category(self) -> str:
        """Return the category of this entry."""
        return self._search_in_properties(ATTR_CATEGORY)

    @property
    def external_id(self) -> str:
        """Return the external id of this entry."""
        return self._search_in_properties(ATTR_GUID)

    @property
    def publication_date(self) -> datetime:
        """Return the publication date of this entry."""
        publication_date = self._search_in_properties(ATTR_PUB_DATE)
        if publication_date:
            # Parse the date. Example: 15/09/2018 9:31:00 AM
            date_struct = strptime(publication_date, "%d/%m/%Y %I:%M:%S %p")
            publication_date = datetime.fromtimestamp(calendar.timegm(
                date_struct), tz=pytz.utc)
        return publication_date

    @property
    def description(self) -> str:
        """Return the description of this entry."""
        return self._search_in_properties(ATTR_DESCRIPTION)

    def _search_in_description(self, regexp):
        """Find a sub-string in the entry's description."""
        if self.description:
            match = re.search(regexp, self.description)
            if match:
                return match.group(CUSTOM_ATTRIBUTE)
        return None

    @property
    def location(self) -> str:
        """Return the location of this entry."""
        return self._search_in_description(REGEXP_ATTR_LOCATION)

    @property
    def council_area(self) -> str:
        """Return the council area of this entry."""
        return self._search_in_description(REGEXP_ATTR_COUNCIL_AREA)

    @property
    def status(self) -> str:
        """Return the status of this entry."""
        return self._search_in_description(REGEXP_ATTR_STATUS)

    @property
    def type(self) -> str:
        """Return the type of this entry."""
        return self._search_in_description(REGEXP_ATTR_TYPE)

    @property
    def fire(self) -> bool:
        """Return if this entry represents a fire or not."""
        return self._search_in_description(REGEXP_ATTR_FIRE) == 'Yes'

    @property
    def size(self) -> str:
        """Return the size of this entry."""
        return self._search_in_description(REGEXP_ATTR_SIZE)

    @property
    def responsible_agency(self) -> str:
        """Return the responsible agency of this entry."""
        return self._search_in_description(REGEXP_ATTR_RESPONSIBLE_AGENCY)
