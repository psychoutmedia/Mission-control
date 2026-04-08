"""
Parser for biblical prophecy timecodes.
Handles various formats: "1260 days", "time times and half", "42 months", etc.
"""

import re
from typing import Dict, Optional


# Unit conversions to days (prophetic calendar)
UNIT_CONVERSIONS = {
    "day": 1,
    "days": 1,
    "month": 30,      # Prophetic month = 30 days
    "months": 30,
    "year": 360,      # Prophetic year = 360 days (12 × 30)
    "years": 360,
    "week": 7,
    "weeks": 7,
    "hour": 1/24,     # Less common
    "hours": 1/24,
    "time": 360,      # "time, times, and half a time" = 1 + 2 + 0.5 = 3.5 years
    "times": 360,
    "half": 180,      # half a time = 0.5 prophetic years
}

# Symbolic/pattern numbers
PATTERN_NUMBERS = {
    3: "Trinity, divine completeness",
    4: "World/earth (4 corners, 4 winds)",
    7: "Perfection/completion",
    10: "Ordinal completeness",
    12: "Divine government (12 tribes, 12 apostles)",
    24: "Priestly divisions (1 Chronicles 24)",
    30: "New beginning (30 days = new month)",
    40: "Testing/trial period",
    42: "Beast's authority (3.5 years)",
    70: "Divine patience/fulfillment",
    144: "Elect × elect (12 × 12)",
    360: "Prophetic year (12 × 30)",
    390: "Years of Israel's apostasy (Ezek 4:6)",
    1260: "3.5 years × 360 (half of 7)",
    2300: "Long duration (Daniel 8:14)",
    2520: "7 × 360 (complete prophetic cycle)",
}


class ProphecyParser:
    """Parser for biblical prophecy timecodes."""

    def parse(self, timecode: str) -> Dict:
        """
        Parse a timecode string into structured data.
        
        Args:
            timecode: String like "1260 days", "time times and half", "42 months"
            
        Returns:
            Dict with parsed values:
            {
                "raw": original input,
                "value": numeric value or None,
                "unit": unit string or None,
                "normalized_value": value in days,
                "pattern_numbers": list of symbolic numbers found
            }
        """
        result = {
            "raw": timecode,
            "value": None,
            "unit": None,
            "normalized_value": None,
            "pattern_numbers": [],
            "is_compound": False,
            "compound_parts": []
        }
        
        # Try direct numeric parsing first
        direct = self._parse_direct(timecode)
        if direct:
            result.update(direct)
            result["pattern_numbers"] = self._find_pattern_numbers(result["value"])
            return result
            
        # Try compound parsing (e.g., "time times and half")
        compound = self._parse_compound(timecode)
        if compound:
            result.update(compound)
            result["pattern_numbers"] = self._find_pattern_numbers(result["value"])
            return result
            
        # Try fraction parsing
        fraction = self._parse_fraction(timecode)
        if fraction:
            result.update(fraction)
            result["pattern_numbers"] = self._find_pattern_numbers(result["value"])
            return result
            
        return result

    def _parse_direct(self, text: str) -> Optional[Dict]:
        """Parse direct number + unit format."""
        text = text.strip().lower()
        
        # Pattern: number + unit
        pattern = r"(\d+(?:,\d{3})*)\s*(days?|months?|years?|weeks?|hours?|hours?)\b"
        match = re.search(pattern, text)
        
        if match:
            value_str = match.group(1).replace(",", "")
            value = int(value_str)
            unit = match.group(2)
            unit_normalized = unit.rstrip("s") if unit.endswith("s") else unit
            
            return {
                "value": value,
                "unit": unit_normalized,
                "normalized_value": value * UNIT_CONVERSIONS.get(unit_normalized, 1),
                "pattern_numbers": []
            }
            
        return None

    def _parse_compound(self, text: str) -> Optional[Dict]:
        """Parse compound expressions like 'time, times, and half a time'."""
        text = text.strip().lower()
        
        # "time, times, and half a time" pattern
        compound_patterns = [
            r"time,\s*times\s*and\s*half\s*a?\s*time",
            r"times?,\s*and\s*half\s*a?\s*time",
            r"a?\s*time\s*and\s*a\s*half",
            r"time\s*and\s*times\s*and\s*half\s*a\s*time",
        ]
        
        for pattern in compound_patterns:
            if re.search(pattern, text):
                # 1 time + 2 times + 0.5 time = 3.5 prophetic years
                total_years = 1 + 2 + 0.5  # = 3.5 years
                total_days = int(total_years * 360)  # = 1260 days
                
                return {
                    "value": 1260,  # The canonical value
                    "unit": "days",
                    "normalized_value": 1260,
                    "is_compound": True,
                    "compound_parts": [
                        {"part": "1 time", "years": 1, "days": 360},
                        {"part": "2 times", "years": 2, "days": 720},
                        {"part": "half a time", "years": 0.5, "days": 180},
                    ],
                    "expression": "time, times, and half a time",
                    "calculation": "1 + 2 + 0.5 = 3.5 prophetic years = 1,260 days"
                }
                
        return None

    def _parse_fraction(self, text: str) -> Optional[Dict]:
        """Parse fractional expressions like 'a day for each year'."""
        text = text.strip().lower()
        
        # "40 days and 40 nights" or "40 days and 40 nights"
        pattern = r"(\d+)\s*days?\s*(?:and|&)\s*(\d+)\s*nights?"
        match = re.search(pattern, text)
        
        if match:
            days = int(match.group(1))
            nights = int(match.group(2))
            total = days + nights
            
            return {
                "value": total,
                "unit": "days",
                "normalized_value": total,
                "is_compound": True,
                "compound_parts": [
                    {"part": f"{days} days", "value": days},
                    {"part": f"{nights} nights", "value": nights}
                ]
            }
            
        return None

    def _find_pattern_numbers(self, value: Optional[int]) -> list:
        """Find pattern/symbolic numbers within the value."""
        if not value:
            return []
            
        found = []
        
        # Check exact matches
        for num in PATTERN_NUMBERS:
            if num == value:
                found.append({
                    "number": num,
                    "meaning": PATTERN_NUMBERS[num],
                    "type": "exact"
                })
                
        # Check for factor relationships
        for num in PATTERN_NUMBERS:
            if value % num == 0 and num != value:
                factor = value // num
                found.append({
                    "number": num,
                    "meaning": PATTERN_NUMBERS[num],
                    "type": "factor",
                    "factor": factor,
                    "relationship": f"{value} = {num} × {factor}"
                })
                
        return found

    def convert_to_equivalent(self, value: int, from_unit: str, to_unit: str) -> int:
        """
        Convert between prophetic time units.
        
        Args:
            value: Numeric value
            from_unit: Source unit (day, month, year, etc.)
            to_unit: Target unit
            
        Returns:
            Converted value
        """
        days = value * UNIT_CONVERSIONS.get(from_unit.rstrip("s"), 1)
        return int(days / UNIT_CONVERSIONS.get(to_unit.rstrip("s"), 1))

    def is_prophetic_calendar(self, value: int, unit: str) -> bool:
        """
        Check if value follows prophetic calendar (360-day year).
        Prophetic months are 30 days, years are 360 days.
        """
        if unit in ("month", "months"):
            return value <= 30  # Prophetic months are exactly 30 days
        if unit in ("year", "years"):
            return value == 360  # Prophetic year
        if unit in ("day", "days"):
            # Values that are multiples of 30 or 360 suggest prophetic calendar
            return value % 30 == 0 or value % 360 == 0
        return False
