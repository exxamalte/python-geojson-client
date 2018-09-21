"""Test for the NSW Rural Fire Service feed."""
import datetime
import unittest
from unittest import mock

from geojson_client import UPDATE_OK
from geojson_client.nsw_rural_fire_service_feed import \
    NswRuralFireServiceFeed, ATTRIBUTION
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
        status, entries = feed.update()
        assert status == UPDATE_OK
        self.assertIsNotNone(entries)
        assert len(entries) == 3

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
