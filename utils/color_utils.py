"""
Utility functions for color calculations and other helpers.
"""

from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color code to RGB tuple.

    Args:
        hex_color: Hex color code (e.g., "#ff0000")

    Returns:
        Tuple of (r, g, b) values (0-255)
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """
    Convert RGB tuple to hex color code.

    Args:
        rgb: Tuple of (r, g, b) values (0-255)

    Returns:
        Hex color code (e.g., "#ff0000")
    """
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def interpolate_color(probability: float | None) -> str:
    """
    Interpolate between red and green based on probability.

    Args:
        probability: Value between 0 and 1

    Returns:
        Hex color code
    """
    if probability is None:
        return "#808080"  # Gray for unknown probabilities

    # Ensure probability is within bounds
    probability = max(0, min(1, probability))

    # Red (low probability) to Green (high probability)
    r = int(255 * (1 - probability))
    g = int(255 * probability)
    b = 0

    return rgb_to_hex((r, g, b))


def format_probability(probability: float | None, decimal_places: int = 4) -> str:
    """
    Format probability value for display.

    Args:
        probability: Probability value
        decimal_places: Number of decimal places to show

    Returns:
        Formatted probability string
    """
    if probability is None:
        return "N/A"

    return f"{probability:.{decimal_places}f}"
