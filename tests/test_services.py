"""
Tests for services.
"""
import pytest
from app.utils.matching import calculate_similarity, duration_match


def test_calculate_similarity():
    """Test string similarity calculation."""
    assert calculate_similarity("hello", "hello") == 1.0
    assert calculate_similarity("hello", "world") < 0.5
    assert 0.5 < calculate_similarity("hello", "hallo") < 1.0


def test_duration_match():
    """Test duration matching."""
    assert duration_match(180000, 180, tolerance=0.1) is True
    assert duration_match(180000, 200, tolerance=0.1) is False
    assert duration_match(180000, 190, tolerance=0.1) is True


# Add more tests as needed
