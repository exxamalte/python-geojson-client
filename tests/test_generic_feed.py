"""Test for the generic geojson feed."""
import requests
import unittest
from json import JSONDecodeError
from unittest import mock

from geojson_client import UPDATE_ERROR, UPDATE_OK
from geojson_client.generic_feed import GenericFeed, GenericFeedManager
from tests.utils import load_fixture


class TestGenericFeed(unittest.TestCase):
    """Test the generic feed."""

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_ok(self, mock_session, mock_request):
        """Test updating feed is ok."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = load_fixture('generic_feed_1.json')

        feed = GenericFeed(home_coordinates, None)
        assert repr(feed) == "<GenericFeed(home=(-31.0, 151.0), url=None, " \
                             "radius=None)>"
        status, entries = feed.update()
        assert status == UPDATE_OK
        self.assertIsNotNone(entries)
        assert len(entries) == 5

        feed_entry = entries[0]
        assert feed_entry.title == "Title 1"
        assert feed_entry.external_id == "3456"
        assert feed_entry.coordinates == (-37.2345, 149.1234)
        self.assertAlmostEqual(feed_entry.distance_to_home, 714.4, 1)
        assert repr(feed_entry) == "<GenericFeedEntry(id=3456)>"

        feed_entry = entries[1]
        assert feed_entry.title == "Title 2"
        assert feed_entry.external_id == "4567"

        feed_entry = entries[2]
        assert feed_entry.title == "Title 3"
        assert feed_entry.external_id == "Title 3"

        feed_entry = entries[3]
        self.assertIsNone(feed_entry.title)
        assert feed_entry.external_id == -7266545992534134585

        feed_entry = entries[4]
        assert feed_entry.title == "Title 5"
        assert feed_entry.external_id == "7890"

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_ok_with_filtering(self, mock_session, mock_request):
        """Test updating feed is ok."""
        home_coordinates = (-37.0, 150.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = load_fixture('generic_feed_1.json')

        feed = GenericFeed(home_coordinates, None, filter_radius=90.0)
        status, entries = feed.update()
        assert status == UPDATE_OK
        self.assertIsNotNone(entries)
        assert len(entries) == 4
        self.assertAlmostEqual(entries[0].distance_to_home, 82.0, 1)
        self.assertAlmostEqual(entries[1].distance_to_home, 77.0, 1)
        self.assertAlmostEqual(entries[2].distance_to_home, 84.6, 1)

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_error(self, mock_session, mock_request):
        """Test updating feed results in error."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = False

        feed = GenericFeed(home_coordinates, None)
        status, entries = feed.update()
        assert status == UPDATE_ERROR
        self.assertIsNone(feed.last_timestamp)

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_with_request_exception(self, mock_session, mock_request):
        """Test updating feed raises exception."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .side_effect = requests.exceptions.RequestException

        feed = GenericFeed(home_coordinates, None)
        status, entries = feed.update()
        assert status == UPDATE_ERROR
        self.assertIsNone(entries)

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_with_json_decode_error(self, mock_session, mock_request):
        """Test updating feed raises exception."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .side_effect = JSONDecodeError("", "", 0)

        feed = GenericFeed(home_coordinates, None)
        status, entries = feed.update()
        assert status == UPDATE_ERROR
        self.assertIsNone(entries)

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_feed_manager(self, mock_session, mock_request):
        """Test the feed manager."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = load_fixture('generic_feed_1.json')

        # This will just record calls and keep track of external ids.
        generated_entity_external_ids = []
        updated_entity_external_ids = []
        removed_entity_external_ids = []

        def _generate_entity(external_id):
            """Generate new entity."""
            generated_entity_external_ids.append(external_id)

        def _update_entity(external_id):
            """Update entity."""
            updated_entity_external_ids.append(external_id)

        def _remove_entity(external_id):
            """Remove entity."""
            removed_entity_external_ids.append(external_id)

        feed_manager = GenericFeedManager(_generate_entity, _update_entity,
                                          _remove_entity, home_coordinates,
                                          None)
        assert repr(feed_manager) == "<GenericFeedManager(feed=<GenericFeed(" \
                                     "home=(-31.0, 151.0), url=None, " \
                                     "radius=None)>)>"
        feed_manager.update()
        entries = feed_manager.feed_entries
        self.assertIsNotNone(entries)
        assert len(entries) == 5
        self.assertIsNotNone(feed_manager.last_update)

        assert len(generated_entity_external_ids) == 5
        assert len(updated_entity_external_ids) == 0
        assert len(removed_entity_external_ids) == 0

        feed_entry = entries.get("3456")
        assert feed_entry.title == "Title 1"
        assert feed_entry.external_id == "3456"
        assert feed_entry.coordinates == (-37.2345, 149.1234)
        self.assertAlmostEqual(feed_entry.distance_to_home, 714.4, 1)
        assert repr(feed_entry) == "<GenericFeedEntry(id=3456)>"

        feed_entry = entries.get("4567")
        assert feed_entry.title == "Title 2"
        assert feed_entry.external_id == "4567"

        feed_entry = entries.get("Title 3")
        assert feed_entry.title == "Title 3"
        assert feed_entry.external_id == "Title 3"

        feed_entry = entries.get(-7266545992534134585)
        self.assertIsNone(feed_entry.title)
        assert feed_entry.external_id == -7266545992534134585

        feed_entry = entries.get("7890")
        assert feed_entry.title == "Title 5"
        assert feed_entry.external_id == "7890"

        # Simulate an update with several changes.
        generated_entity_external_ids.clear()
        updated_entity_external_ids.clear()
        removed_entity_external_ids.clear()

        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = load_fixture('generic_feed_2.json')

        feed_manager.update()
        entries = feed_manager.feed_entries
        self.assertIsNotNone(entries)
        assert len(entries) == 3
        assert len(generated_entity_external_ids) == 1
        assert len(updated_entity_external_ids) == 2
        assert len(removed_entity_external_ids) == 3

        feed_entry = entries.get("3456")
        assert feed_entry.title == "Title 1 UPDATED"

        feed_entry = entries.get("4567")
        assert feed_entry.title == "Title 2"

        feed_entry = entries.get("8901")
        assert feed_entry.title == "Title 6"

        # Simulate an update with no data.
        generated_entity_external_ids.clear()
        updated_entity_external_ids.clear()
        removed_entity_external_ids.clear()

        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = False

        feed_manager.update()
        entries = feed_manager.feed_entries

        assert len(entries) == 0
        assert len(generated_entity_external_ids) == 0
        assert len(updated_entity_external_ids) == 0
        assert len(removed_entity_external_ids) == 3
