"""
Base class for the feed manager.

This allows managing feeds and their entries throughout their life-cycle.
"""
from datetime import datetime
import logging
from typing import Optional

from geojson_client import UPDATE_OK, UPDATE_OK_NO_DATA

_LOGGER = logging.getLogger(__name__)


class FeedManagerBase:
    """Generic Feed manager."""

    def __init__(self, feed, generate_callback, update_callback,
                 remove_callback):
        """Initialise feed manager."""
        self._feed = feed
        self.feed_entries = {}
        self._managed_external_ids = set()
        self._last_update = None
        self._generate_callback = generate_callback
        self._update_callback = update_callback
        self._remove_callback = remove_callback

    def __repr__(self):
        """Return string representation of this feed."""
        return '<{}(feed={})>'.format(
            self.__class__.__name__, self._feed)

    def update(self):
        """Update the feed and then update connected entities."""
        status, feed_entries = self._feed.update()
        if status == UPDATE_OK:
            _LOGGER.debug("Data retrieved %s", feed_entries)
            # Keep a copy of all feed entries for future lookups by entities.
            self.feed_entries = {entry.external_id: entry
                                 for entry in feed_entries}
            # Record current time of update.
            self._last_update = datetime.now()
            # For entity management the external ids from the feed are used.
            feed_external_ids = set(self.feed_entries)
            remove_external_ids = self._managed_external_ids.difference(
                feed_external_ids)
            self._remove_entities(remove_external_ids)
            update_external_ids = self._managed_external_ids.intersection(
                feed_external_ids)
            self._update_entities(update_external_ids)
            create_external_ids = feed_external_ids.difference(
                self._managed_external_ids)
            self._generate_new_entities(create_external_ids)
        elif status == UPDATE_OK_NO_DATA:
            _LOGGER.debug(
                "Update successful, but no data received from %s", self._feed)
        else:
            _LOGGER.warning(
                "Update not successful, no data received from %s", self._feed)
            # Remove all entities.
            self._remove_entities(self._managed_external_ids.copy())
            # Remove all feed entries and managed external ids.
            self.feed_entries.clear()
            self._managed_external_ids.clear()

    def _generate_new_entities(self, external_ids):
        """Generate new entities for events."""
        for external_id in external_ids:
            self._generate_callback(external_id)
            _LOGGER.debug("New entity added %s", external_id)
            self._managed_external_ids.add(external_id)

    def _update_entities(self, external_ids):
        """Update entities."""
        for external_id in external_ids:
            _LOGGER.debug("Existing entity found %s", external_id)
            self._update_callback(external_id)

    def _remove_entities(self, external_ids):
        """Remove entities."""
        for external_id in external_ids:
            _LOGGER.debug("Entity not current anymore %s", external_id)
            self._managed_external_ids.remove(external_id)
            self._remove_callback(external_id)

    @property
    def last_timestamp(self) -> Optional[datetime]:
        """Return the last timestamp extracted from this feed."""
        return self._feed.last_timestamp

    @property
    def last_update(self) -> Optional[datetime]:
        """Return the last successful update of this feed."""
        return self._last_update
