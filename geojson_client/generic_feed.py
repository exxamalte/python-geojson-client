"""
Generic GeoJSON feed.

Support for generic GeoJSON feeds from various sources.
"""
from geojson_client import GeoJsonFeed, FeedEntry
from geojson_client.consts import ATTR_GUID, ATTR_ID, ATTR_TITLE
from geojson_client.feed_manager import FeedManagerBase


class GenericFeedManager(FeedManagerBase):
    """Feed Manager for GeoJSON feeds."""

    def __init__(self, generate_callback, update_callback, remove_callback,
                 coordinates, url, filter_radius=None):
        """Initialize the Generic Feed Manager."""
        feed = GenericFeed(coordinates, url, filter_radius=filter_radius)
        super().__init__(feed, generate_callback, update_callback,
                         remove_callback)


class GenericFeed(GeoJsonFeed):
    """Generic GeoJSON feed."""

    def __init__(self, home_coordinates, url, filter_radius=None):
        """Initialise this service."""
        super().__init__(home_coordinates, url, filter_radius=filter_radius)

    def _new_entry(self, home_coordinates, feature, global_data):
        """Generate a new entry."""
        return GenericFeedEntry(home_coordinates, feature)


class GenericFeedEntry(FeedEntry):
    """Generic feed entry."""

    def __init__(self, home_coordinates, feature):
        """Initialise this service."""
        super().__init__(home_coordinates, feature)

    @property
    def title(self) -> str:
        """Return the title of this entry."""
        return self._search_in_properties(ATTR_TITLE)

    @property
    def external_id(self) -> str:
        """Return the external id of this entry."""
        """Find a suitable ID for the provided entry."""
        external_id = self._search_in_feature(ATTR_ID)
        if not external_id:
            external_id = self._search_in_properties(ATTR_ID)
        if not external_id:
            external_id = self._search_in_properties(ATTR_GUID)
        if not external_id:
            external_id = self.title
        if not external_id:
            # Use geometry as ID as a fallback.
            external_id = hash(self.coordinates)
        return external_id
