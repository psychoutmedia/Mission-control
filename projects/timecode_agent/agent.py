"""
Timecode Analysis Agent for @timecode1260
Analyzes biblical prophecy timecodes and generates content insights.
"""

import re
from dataclasses import dataclass
from typing import Optional
from parser import ProphecyParser
from references import BIBLICAL_REFERENCES, TIME_UNITS, SYMBOLIC_NUMBERS
from generator import ThreadGenerator


@dataclass
class ProphecyAnalysis:
    timecode: str
    raw_value: Optional[int]
    unit: str
    references: list
    symbolic_meaning: Optional[str]
    correlations: list
    thread_draft: str


class TimecodeAgent:
    """Agent for analyzing biblical prophecy timecodes."""

    def __init__(self):
        self.parser = ProphecyParser()
        self.generator = ThreadGenerator()
        self.references = BIBLICAL_REFERENCES
        self.symbolic = SYMBOLIC_NUMBERS

    def analyze_prophecy(
        self,
        timecode: str,
        book: Optional[str] = None,
        theme: Optional[str] = None
    ) -> ProphecyAnalysis:
        """
        Analyze a prophetic timecode.
        
        Args:
            timecode: The time reference (e.g., "1260 days", "time times and half")
            book: Specific biblical book to focus on
            theme: Prophecy theme to explore
            
        Returns:
            ProphecyAnalysis with full breakdown
        """
        # Parse the timecode
        parsed = self.parser.parse(timecode)
        
        # Find references
        refs = self._find_references(parsed, book)
        
        # Get symbolic meaning
        symbolic = self._get_symbolic_meaning(parsed.get("normalized_value"))
        
        # Find correlations
        correlations = self._find_correlations(parsed, theme)
        
        # Generate thread draft
        thread = self.generator.generate_thread(
            timecode=timecode,
            parsed=parsed,
            references=refs,
            symbolic=symbolic,
            correlations=correlations
        )
        
        return ProphecyAnalysis(
            timecode=timecode,
            raw_value=parsed.get("value"),
            unit=parsed.get("unit", "unknown"),
            references=refs,
            symbolic_meaning=symbolic,
            correlations=correlations,
            thread_draft=thread
        )

    def _find_references(self, parsed: dict, book: Optional[str] = None) -> list:
        """Find biblical references matching the timecode."""
        value = parsed.get("value")
        unit = parsed.get("unit")
        matches = []
        
        if not value:
            return matches
            
        for ref in self.references:
            if ref["value"] == value or ref.get("equivalent_days") == self._to_days(value, unit):
                if book is None or book.lower() in ref["reference"].lower():
                    matches.append(ref)
                    
        return matches

    def _to_days(self, value: int, unit: str) -> int:
        """Convert value to days."""
        conversions = {
            "days": 1,
            "months": 30,
            "years": 365,
            "weeks": 7,
            "hours": 1/24
        }
        return value * conversions.get(unit, 1)

    def _get_symbolic_meaning(self, value: Optional[int]) -> Optional[str]:
        """Get symbolic meaning of a number."""
        if not value:
            return None
        return self.symbolic.get(value)

    def _find_correlations(self, parsed: dict, theme: Optional[str] = None) -> list:
        """Find historical/modern correlations to the timecode."""
        value = parsed.get("value")
        correlations = []
        
        # Predefined correlations for key numbers
        correlation_db = {
            1260: [
                "42 months of tribulation period",
                "1,260 days = 3.5 years (half of 7)",
                "1260 BC: Traditional date for Trojan War",
                "Period from temple desecration to cleansing (Hasmonean)",
            ],
            2520: [
                "7 * 360 = 2,520 (complete prophetic cycle)",
                "From 607 BCE to 1914 CE (traditional JW calculation)",
                "Longest prophetic period in scripture",
            ],
            144: [
                "12 * 12 = 144 (elect × elect)",
                "Revelation 14:1 - 144,000 sealed",
                "Perfect government (12 tribes × 12 apostles)",
            ],
            40: [
                "Testing period (flood, wilderness, temptation)",
                "Jesus fasted 40 days",
                "Flood lasted 40 days and nights",
            ],
            7: [
                "Perfection/completion (7 days of creation)",
                "7 seals, 7 trumpets, 7 bowls",
                "70 weeks of Daniel",
            ],
            70: [
                "Weeks of Daniel (490 years)",
                "Nations divided at Babel (70)",
                "70 AD: Temple destruction",
            ],
            42: [
                "Months of beast's authority (Revelation 13:5)",
                "42 generations in Matthew's genealogy",
                "Wilderness stops (Numbers 33)",
            ],
            390: [
                "Ezekiel's prophecy of 390 days (Ezekiel 4:6)",
                "Represents years of Israel's apostasy",
            ],
            1290: [
                "Daniel 12:11 - from temple desecration",
                "30 days beyond 1,260",
            ],
            1335: [
                "Daniel 12:12 - blessed is he who waits",
                "45 days beyond 1,290",
            ],
        }
        
        if value:
            correlations = correlation_db.get(value, [])
            
        return correlations

    def get_theme_analysis(self, theme: str) -> dict:
        """
        Get analysis of a prophecy theme across scripture.
        
        Args:
            theme: Theme to analyze (e.g., "beast", "temple", "rapture")
            
        Returns:
            Dict with theme references and patterns
        """
        theme_map = {
            "beast": [
                "Revelation 13:1-10 (first beast)",
                "Revelation 13:11-18 (second beast)",
                "Daniel 7:19-27 (fourth beast)",
                "Daniel 8:23-27 (little horn)",
            ],
            "temple": [
                "Daniel 9:24-27 (70 weeks)",
                "Revelation 11:1-2 (temple measurement)",
                "Ezekiel 40-48 (future temple)",
                "Matthew 24:15 (abomination of desolation)",
            ],
            "return": [
                "Acts 1:11 (Jesus returns)",
                "Zechariah 14:4 (feet on Mount of Olives)",
                "Revelation 19:11-16 (the rider on white horse)",
                "Matthew 24:30 (sign of Son of Man)",
            ],
            "timecodes": [
                "1260 days - Revelation 12:6, 12:14",
                "42 months - Revelation 13:5",
                "time, times, half - Daniel 7:25, 12:7",
                "2300 evenings/mornings - Daniel 8:14",
                "70 weeks - Daniel 9:24-27",
            ],
        }
        
        theme_lower = theme.lower()
        for key in theme_map:
            if key in theme_lower:
                return {
                    "theme": theme,
                    "references": theme_map[key],
                    "pattern": self._analyze_theme_pattern(theme_map[key])
                }
                
        return {"theme": theme, "references": [], "pattern": "No pattern found"}

    def _analyze_theme_pattern(self, references: list) -> str:
        """Analyze patterns across theme references."""
        return f"{len(references)} references found. Common threads: divine judgment, end-times events, prophetic symbolism."

    def analyze_prophecy_relationship(self, code1: str, code2: str) -> dict:
        """Compare two timecodes for relationships."""
        p1 = self.parser.parse(code1)
        p2 = self.parser.parse(code2)
        
        v1 = p1.get("value", 0)
        v2 = p2.get("value", 0)
        
        # Check relationships
        relationships = []
        
        if v1 and v2:
            if v2 > v1:
                relationships.append(f"{code2} extends {code1} by {v2 - v1}")
            if v1 > v2:
                relationships.append(f"{code1} extends {code2} by {v1 - v2}")
            if v2 == v1 * 2:
                relationships.append(f"{code2} is double {code1}")
            if v2 == v1 * 3.5:
                relationships.append(f"{code2} is 3.5× {code1} (half of 7)")
                
        return {
            "code1": code1,
            "code2": code2,
            "parsed1": p1,
            "parsed2": p2,
            "relationships": relationships
        }


if __name__ == "__main__":
    agent = TimecodeAgent()
    
    # Example: Analyze 1260 days
    result = agent.analyze_prophecy("1260 days", book="Revelation")
    print(f"Timecode: {result.timecode}")
    print(f"Value: {result.raw_value} {result.unit}")
    print(f"Symbolic: {result.symbolic_meaning}")
    print(f"References: {len(result.references)}")
    for ref in result.references:
        print(f"  - {ref['reference']}")
    print(f"\nThread Draft:\n{result.thread_draft}")
