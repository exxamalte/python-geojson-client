"""Tests for base classes."""
import unittest
from geojson import Point, Polygon, GeometryCollection
from unittest.mock import MagicMock

from geojson_client import GeoJsonDistanceHelper


class TestGeoJsonDistanceHelper(unittest.TestCase):
    """Tests for the GeoJSON distance helper."""

    def test_extract_coordinates_from_point(self):
        """Test extracting coordinates from point."""
        mock_point = MagicMock(spec=Point)
        mock_point.coordinates = [151.0, -30.0]
        latitude, longitude = GeoJsonDistanceHelper.\
            extract_coordinates(mock_point)
        assert latitude == -30.0
        assert longitude == 151.0

    def test_extract_coordinates_from_geometry_collection(self):
        """Test extracting coordinates from geometry collection."""
        mock_point = MagicMock(spec=Point)
        mock_point.coordinates = [151.0, -30.0]
        mock_geometry_collection = MagicMock(spec=GeometryCollection)
        mock_geometry_collection.geometries = [mock_point]
        latitude, longitude = GeoJsonDistanceHelper.\
            extract_coordinates(mock_geometry_collection)
        assert latitude == -30.0
        assert longitude == 151.0

    def test_extract_coordinates_from_polygon(self):
        """Test extracting coordinates from polygon."""
        mock_polygon = MagicMock(spec=Polygon)
        mock_polygon.coordinates = [[
            [151.0, -30.0], [151.5, -30.0], [151.5, -30.5], [151.0, -30.5],
            [151.0, -30.0]
        ]]
        latitude, longitude = GeoJsonDistanceHelper.\
            extract_coordinates(mock_polygon)
        self.assertAlmostEqual(latitude, -30.2, 1)
        self.assertAlmostEqual(longitude, 151.2, 1)

    def test_extract_coordinates_from_unsupported_geometry(self):
        """Test extracting coordinates from unsupported geometry."""
        mock_unsupported_geometry = MagicMock()
        latitude, longitude = GeoJsonDistanceHelper.\
            extract_coordinates(mock_unsupported_geometry)
        self.assertIsNone(latitude)
        self.assertIsNone(longitude)

    def test_distance_to_point(self):
        """Test calculating distance to point."""
        home_coordinates = [-31.0, 150.0]
        mock_point = MagicMock(spec=Point)
        mock_point.coordinates = [151.0, -30.0]
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, mock_point)
        self.assertAlmostEqual(distance, 146.8, 1)

    def test_distance_to_geometry_collection(self):
        """Test calculating distance to geometry collection."""
        home_coordinates = [-31.0, 150.0]
        mock_point = MagicMock(spec=Point)
        mock_point.coordinates = [151.0, -30.0]
        mock_geometry_collection = MagicMock(spec=GeometryCollection)
        mock_geometry_collection.geometries = [mock_point]
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, mock_geometry_collection)
        self.assertAlmostEqual(distance, 146.8, 1)

    def test_distance_to_polygon(self):
        """Test calculating distance to point."""
        home_coordinates = [-31.0, 150.0]
        mock_polygon = MagicMock(spec=Polygon)
        mock_polygon.coordinates = [[
            [151.0, -30.0], [151.5, -30.0], [151.5, -30.5], [151.0, -30.5],
            [151.0, -30.0]
        ]]
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, mock_polygon)
        self.assertAlmostEqual(distance, 110.6, 1)

    def test_distance_to_unsupported_geometry(self):
        """Test calculating distance to unsupported geometry."""
        home_coordinates = [-31.0, 150.0]
        mock_unsupported_geometry = MagicMock()
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, mock_unsupported_geometry)
        assert distance == float("inf")
