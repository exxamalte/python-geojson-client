"""Test for the USGS Earthquake Hazards Program feed."""
import datetime
import unittest
from unittest import mock

from geojson_client import UPDATE_OK
from geojson_client.exceptions import GeoJsonException
from geojson_client.usgs_earthquake_hazards_program_feed import \
    UsgsEarthquakeHazardsProgramFeed, UsgsEarthquakeHazardsProgramFeedManager
from tests.utils import load_fixture


class TestUsgsEarthquakeHazardsProgramFeed(unittest.TestCase):
    """Test the USGS Earthquake Hazards Program feed."""

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_ok(self, mock_session, mock_request):
        """Test updating feed is ok."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = \
            load_fixture('usgs_earthquake_hazards_program_feed.json')

        feed = UsgsEarthquakeHazardsProgramFeed(
            home_coordinates, 'past_hour_significant_earthquakes')
        assert repr(feed) == "<UsgsEarthquakeHazardsProgramFeed(" \
                             "home=(-31.0, 151.0), " \
                             "url=https://earthquake.usgs.gov/earthquakes/" \
                             "feed/v1.0/summary/significant_hour.geojson, " \
                             "radius=None, magnitude=None)>"
        status, entries = feed.update()
        assert status == UPDATE_OK
        self.assertIsNotNone(entries)
        assert len(entries) == 3

        feed_entry = entries[0]
        assert feed_entry.title == "Title 1"
        assert feed_entry.external_id == "1234"
        assert feed_entry.coordinates == (-32.2345, 149.1234)
        self.assertAlmostEqual(feed_entry.distance_to_home, 224.5, 1)
        assert feed_entry.place == "Place 1"
        assert feed_entry.magnitude == 3.0
        assert feed_entry.time \
            == datetime.datetime(2018, 9, 22, 8, 0,
                                 tzinfo=datetime.timezone.utc)
        assert feed_entry.updated \
            == datetime.datetime(2018, 9, 22, 8, 30,
                                 tzinfo=datetime.timezone.utc)
        assert feed_entry.alert == "Alert 1"
        assert feed_entry.type == "Type 1"
        assert feed_entry.status == "Status 1"
        assert feed_entry.attribution == "Feed Title"

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_update_ok_with_minimum_magnitude(self, mock_session,
                                              mock_request):
        """Test updating feed is ok."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = \
            load_fixture('usgs_earthquake_hazards_program_feed.json')

        feed = UsgsEarthquakeHazardsProgramFeed(
            home_coordinates, 'past_hour_significant_earthquakes',
            filter_minimum_magnitude=2.5)
        status, entries = feed.update()
        assert status == UPDATE_OK
        self.assertIsNotNone(entries)
        assert len(entries) == 1

        feed_entry = entries[0]
        assert feed_entry.title == "Title 1"
        assert feed_entry.external_id == "1234"

    def test_update_wrong_feed(self):
        """Test invalid feed name."""
        home_coordinates = (-31.0, 151.0)

        with self.assertRaises(GeoJsonException):
            UsgsEarthquakeHazardsProgramFeed(home_coordinates,
                                             'DOES NOT EXIST')

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_feed_manager(self, mock_session, mock_request):
        """Test the feed manager."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = True
        mock_session.return_value.__enter__.return_value.send\
            .return_value.text = load_fixture(
                'usgs_earthquake_hazards_program_feed.json')

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

        feed_manager = UsgsEarthquakeHazardsProgramFeedManager(
            _generate_entity, _update_entity, _remove_entity,
            home_coordinates, 'past_hour_significant_earthquakes')
        assert repr(feed_manager) == "<UsgsEarthquakeHazardsProgramFeed" \
                                     "Manager(feed=<UsgsEarthquakeHazards" \
                                     "ProgramFeed(home=(-31.0, 151.0), " \
                                     "url=https://earthquake.usgs.gov/" \
                                     "earthquakes/feed/v1.0/summary/" \
                                     "significant_hour.geojson, " \
                                     "radius=None, magnitude=None)>)>"
        feed_manager.update()
        entries = feed_manager.feed_entries
        self.assertIsNotNone(entries)
        assert len(entries) == 3
        assert len(generated_entity_external_ids) == 3
        assert len(updated_entity_external_ids) == 0
        assert len(removed_entity_external_ids) == 0
