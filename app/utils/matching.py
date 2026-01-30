"""
Utility functions for matching and filtering YouTube results.
"""
from typing import List, Dict
from difflib import SequenceMatcher


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity between two strings.
    
    Args:
        str1: First string
        str2: Second string
    
    Returns:
        Similarity score between 0 and 1
    """
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def duration_match(duration_ms: int, video_duration: int, tolerance: float = 0.1) -> bool:
    """
    Check if video duration matches expected duration.
    
    Args:
        duration_ms: Expected duration in milliseconds
        video_duration: Video duration in seconds
        tolerance: Acceptable difference as fraction (default 10%)
    
    Returns:
        True if durations match within tolerance
    """
    expected_seconds = duration_ms / 1000
    difference = abs(expected_seconds - video_duration)
    max_difference = expected_seconds * tolerance
    
    return difference <= max_difference
