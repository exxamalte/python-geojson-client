"""Test for the generic geojson feed."""
import unittest
from unittest import mock

from geojson_client import UPDATE_ERROR
from geojson_client.generic_feed import GenericFeed


class TestGenericFeed(unittest.TestCase):
    """Test the generic feed."""

    @mock.patch("requests.Request")
    @mock.patch("requests.Session")
    def test_response_not_ok(self, mock_session, mock_request):
        """Test general setup."""
        home_coordinates = (-31.0, 151.0)
        mock_session.return_value.__enter__.return_value.send\
            .return_value.ok = False

        feed = GenericFeed(home_coordinates, None)
        status, entries = feed.update()
        assert status == UPDATE_ERROR
