"""Test for the NSW Rural Fire Service feed."""
import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock

from geojson_client import UPDATE_OK
from geojson_client.nsw_rural_fire_service_feed import \
    NswRuralFireServiceFeed, ATTRIBUTION, NswRuralFireServiceFeedManager, \
    NswRuralFireServiceFeedEntry
from tests.utils import load_fixture


class TestNswRuralFireServiceFeed(unittest.TestCase):
    """Test the NSW Rural Fire Service feed."""

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_ok(self, mock_session, mock_request):
        """Test updating feed is ok."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = \
            load_fixture('nsw_rural_fire_service_feed.json')

        feed = NswRuralFireServiceFeed(home_coordinates, None)
        assert repr(feed) == "<NswRuralFireServiceFeed(" \
                             "home=(-31.0, 151.0), " \
                             "url=https://www.rfs.nsw.gov.au/feeds/" \
                             "majorIncidents.json, radius=None, " \
                             "categories=None)>"
        status, entries = feed.update()
        assert status == UPDATE_OK
        self.assertIsNotNone(entries)
        assert len(entries) == 3
        assert feed.last_timestamp \
            == datetime.datetime(2018, 9, 21, 6, 40,
                                 tzinfo=datetime.timezone.utc)

        feed_entry = entries[0]
        assert feed_entry.title == "Title 1"
        assert feed_entry.category == "Category 1"
        assert feed_entry.external_id == "1234"
        assert feed_entry.coordinates == (-37.2345, 149.1234)
        self.assertAlmostEqual(feed_entry.distance_to_home, 714.4, 1)
        assert feed_entry.publication_date \
            == datetime.datetime(2018, 9, 21, 6, 30,
                                 tzinfo=datetime.timezone.utc)
        assert feed_entry.location == "Location 1"
        assert feed_entry.council_area == "Council 1"
        assert feed_entry.status == "Status 1"
        assert feed_entry.type == "Type 1"
        self.assertTrue(feed_entry.fire)
        assert feed_entry.size == "10 ha"
        assert feed_entry.responsible_agency == "Agency 1"
        assert feed_entry.attribution == ATTRIBUTION

        feed_entry = entries[1]
        assert feed_entry.title == "Title 2"
        assert feed_entry.category == "Category 2"
        self.assertFalse(feed_entry.fire)

        feed_entry = entries[2]
        assert feed_entry.title == "Title 3"
        self.assertIsNone(feed_entry.category)

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_ok_with_categories(self, mock_session, mock_request):
        """Test updating feed is ok, filtered by category."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = \
            load_fixture('nsw_rural_fire_service_feed.json')

        feed = NswRuralFireServiceFeed(home_coordinates,
                                       filter_categories=['Category 1'])
        status, entries = feed.update()
        assert status == UPDATE_OK
        self.assertIsNotNone(entries)
        assert len(entries) == 1

        feed_entry = entries[0]
        assert feed_entry.title == "Title 1"
        assert feed_entry.category == "Category 1"

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_feed_manager(self, mock_session, mock_request):
        """Test the feed manager."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = load_fixture(
                'nsw_rural_fire_service_feed.json')

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

        feed_manager = NswRuralFireServiceFeedManager(_generate_entity,
                                                      _update_entity,
                                                      _remove_entity,
                                                      home_coordinates,
                                                      None)
        assert repr(feed_manager) == "<NswRuralFireServiceFeedManager(" \
                                     "feed=<NswRuralFireServiceFeed(" \
                                     "home=(-31.0, 151.0), " \
                                     "url=https://www.rfs.nsw.gov.au/feeds/" \
                                     "majorIncidents.json, radius=None, " \
                                     "categories=None)>)>"
        feed_manager.update()
        entries = feed_manager.feed_entries
        self.assertIsNotNone(entries)
        assert len(entries) == 3
        assert feed_manager.last_timestamp \
            == datetime.datetime(2018, 9, 21, 6, 40,
                                 tzinfo=datetime.timezone.utc)
        assert len(generated_entity_external_ids) == 3
        assert len(updated_entity_external_ids) == 0
        assert len(removed_entity_external_ids) == 0

    def test_last_timestamp_empty(self):
        """Test last timestamp."""
        feed = NswRuralFireServiceFeed(None)

        # Entries are None.
        last_timestamp = feed._extract_last_timestamp(None)
        self.assertIsNone(last_timestamp)

        # Entries are empty.
        last_timestamp = feed._extract_last_timestamp([])
        self.assertIsNone(last_timestamp)

        # Entries contain one with None date.
        mock_entry_1 = MagicMock(spec=NswRuralFireServiceFeedEntry)
        mock_entry_1.publication_date = None
        datetime_1 = datetime.datetime(2019, 7, 4, 8, 0,
                                       tzinfo=datetime.timezone.utc)
        mock_entry_2 = MagicMock(spec=NswRuralFireServiceFeedEntry)
        mock_entry_2.publication_date = datetime_1

        last_timestamp = feed._extract_last_timestamp([mock_entry_1,
                                                       mock_entry_2])
        assert last_timestamp == datetime_1

        # Entries contain multiple dates.
        datetime_2 = datetime.datetime(2019, 7, 3, 8, 0,
                                       tzinfo=datetime.timezone.utc)
        mock_entry_3 = MagicMock(spec=NswRuralFireServiceFeedEntry)
        mock_entry_3.publication_date = datetime_2
        last_timestamp = feed._extract_last_timestamp([mock_entry_3,
                                                       mock_entry_1,
                                                       mock_entry_2])
        assert last_timestamp == datetime_1
