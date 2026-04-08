"""
Biblical prophecy references database.
Key timecodes from Daniel, Revelation, and related prophetic books.
"""

# Key prophetic timecodes with their references
BIBLICAL_REFERENCES = [
    # === 1260 DAYS ===
    {
        "value": 1260,
        "unit": "days",
        "equivalent_days": 1260,
        "reference": "Revelation 12:6",
        "text": "The woman fled into the wilderness... for 1,260 days",
        "context": "Woman (Israel/Church) in wilderness during tribulation",
        "theme": "protection"
    },
    {
        "value": 1260,
        "unit": "days",
        "equivalent_days": 1260,
        "reference": "Revelation 12:14",
        "text": "The woman was given the two wings... to be nourished for a time, times, and half a time",
        "context": "Same 3.5 year period expressed differently",
        "theme": "protection"
    },
    {
        "value": 1260,
        "unit": "days",
        "equivalent_days": 1260,
        "reference": "Daniel 7:25",
        "text": "He shall speak words against the Most High... and shall wear out the saints for a time, times, and half a time",
        "context": "Little horn's persecution of saints",
        "theme": "persecution"
    },
    {
        "value": 1260,
        "unit": "days",
        "equivalent_days": 1260,
        "reference": "Daniel 12:7",
        "text": "...when the power of the shattering of the holy people has been finished... a time, times, and half a time",
        "context": "End-time tribulation period",
        "theme": "tribulation"
    },
    
    # === 42 MONTHS ===
    {
        "value": 42,
        "unit": "months",
        "equivalent_days": 1260,  # 42 × 30 = 1260
        "reference": "Revelation 13:5",
        "text": "The beast was allowed to make war for 42 months",
        "context": "Beast's authority during tribulation",
        "theme": "judgment"
    },
    {
        "value": 42,
        "unit": "months",
        "equivalent_days": 1260,
        "reference": "Revelation 11:2",
        "text": "The holy city will be trampled for 42 months",
        "context": "Gentile times (Jews out of land)",
        "theme": "gentile dominion"
    },
    
    # === TIME, TIMES, HALF ===
    {
        "value": 1260,
        "unit": "days",
        "equivalent_days": 1260,
        "expression": "time, times, and half a time",
        "reference": "Daniel 7:25",
        "text": "A time, times, and half a time",
        "calculation": "1 + 2 + 0.5 = 3.5 prophetic years = 1,260 days",
        "context": "Three distinct periods totaling 3.5 years",
        "theme": "tribulation"
    },
    
    # === 70 WEEKS (DANIEL) ===
    {
        "value": 70,
        "unit": "weeks",
        "equivalent_days": 490,  # 70 × 7 = 490
        "reference": "Daniel 9:24",
        "text": "70 weeks have been decreed for your people... to finish transgression, put an end to sin, atone for wickedness...",
        "context": "Messianic prophecy - 490 years from decree to Messiah",
        "theme": "messianic"
    },
    {
        "value": 7,
        "unit": "weeks",
        "equivalent_days": 49,  # 7 × 7 = 49
        "reference": "Daniel 9:25",
        "text": "From the going out of the word to restore Jerusalem... 7 weeks",
        "context": "Initial period - rebuilding Jerusalem",
        "theme": "restoration"
    },
    {
        "value": 62,
        "unit": "weeks",
        "equivalent_days": 434,  # 62 × 7 = 434
        "reference": "Daniel 9:25",
        "text": "62 weeks... to the Messiah the Prince",
        "context": "Period from restoration to Messiah",
        "theme": "messianic"
    },
    {
        "value": 1,
        "unit": "week",
        "equivalent_days": 7,
        "reference": "Daniel 9:27",
        "text": "He will confirm a covenant for one week",
        "context": "Final week - 7 years (midweek abomination?)",
        "theme": "covenant"
    },
    
    # === 2300 EVENINGS/MORNINGS ===
    {
        "value": 2300,
        "unit": "evenings/mornings",
        "equivalent_days": 2300,
        "reference": "Daniel 8:14",
        "text": "For 2,300 evenings and mornings; then the sanctuary shall be restored",
        "context": "Desecration to restoration (often interpreted as years)",
        "theme": "restoration"
    },
    
    # === 1290 DAYS ===
    {
        "value": 1290,
        "unit": "days",
        "equivalent_days": 1290,
        "reference": "Daniel 12:11",
        "text": "From the time the regular sacrifice is abolished... 1,290 days",
        "context": "30 days beyond 1,260 - time for judgment/completion",
        "theme": "judgment"
    },
    
    # === 1335 DAYS ===
    {
        "value": 1335,
        "unit": "days",
        "equivalent_days": 1335,
        "reference": "Daniel 12:12",
        "text": "Blessed is he who waits and comes to the 1,335 days",
        "context": "45 days beyond 1,290 - blessing beyond tribulation",
        "theme": "blessing"
    },
    
    # === 2520 DAYS/YEARS ===
    {
        "value": 2520,
        "unit": "days",
        "equivalent_days": 2520,
        "reference": "Calculation: 7 × 360",
        "text": "Complete prophetic cycle (7 prophetic years × 360 days)",
        "context": "Used in various prophetic calculations",
        "theme": "cycle"
    },
    
    # === 40 DAYS ===
    {
        "value": 40,
        "unit": "days",
        "equivalent_days": 40,
        "reference": "Genesis 7:4, 7:17",
        "text": "40 days and 40 nights of flood",
        "context": "Testing/trial period",
        "theme": "testing"
    },
    {
        "value": 40,
        "unit": "days",
        "equivalent_days": 40,
        "reference": "Matthew 4:2",
        "text": "Jesus fasted for 40 days in the wilderness",
        "context": "Temptation/testing of Messiah",
        "theme": "testing"
    },
    {
        "value": 40,
        "unit": "days",
        "equivalent_days": 40,
        "reference": "Numbers 13:25",
        "text": "Spies explored land for 40 days",
        "context": "Testing period before promise",
        "theme": "testing"
    },
    
    # === 144,000 ===
    {
        "value": 144,
        "unit": "thousands",
        "equivalent_days": 144000,
        "reference": "Revelation 7:4",
        "text": "144,000 sealed from the tribes of Israel",
        "context": "Elect/ remnant - 12,000 from each of 12 tribes",
        "theme": "election"
    },
    {
        "value": 144,
        "unit": "thousands",
        "equivalent_days": 144000,
        "reference": "Revelation 14:1",
        "text": "144,000 with the Lamb on Mount Zion",
        "context": "Firstfruits of the redeemed",
        "theme": "redemption"
    },
    
    # === 390 DAYS (EZEKIEL) ===
    {
        "value": 390,
        "unit": "days",
        "equivalent_days": 390,
        "reference": "Ezekiel 4:6",
        "text": "Lie on your side 390 days... each day for a year",
        "context": "Years of Israel's apostasy before restoration",
        "theme": "judgment"
    },
    
    # === 7 SEALS/TRUMPETS/BOWLS ===
    {
        "value": 7,
        "unit": "seals",
        "equivalent_days": 7,
        "reference": "Revelation 5-8",
        "text": "Seven seals are opened, revealing judgment",
        "context": "Sequence of end-time judgments",
        "theme": "judgment"
    },
    {
        "value": 7,
        "unit": "trumpets",
        "equivalent_days": 7,
        "reference": "Revelation 8-11",
        "text": "Seven trumpets announce escalating judgments",
        "context": "Second wave of judgments",
        "theme": "judgment"
    },
    {
        "value": 7,
        "unit": "bowls",
        "equivalent_days": 7,
        "reference": "Revelation 15-16",
        "text": "Seven bowls of God's wrath poured out",
        "context": "Final judgments - third wave",
        "theme": "wrath"
    },
]

# Symbolic meanings of prophetic numbers
SYMBOLIC_NUMBERS = {
    3: "Divine perfection (Trinity)",
    4: "World/creation (4 winds, 4 corners)",
    7: "Completeness/perfection (7 days of creation)",
    10: "Ordinal completeness (10 commandments)",
    12: "Divine government (12 tribes, 12 apostles)",
    24: "Priestly worship (24 divisions)",
    30: "New beginning (30 days = new month)",
    40: "Testing/trial (flood, wilderness, temptation)",
    42: "Beast's authority (3.5 years)",
    70: "Divine fulfillment (70 weeks, 70 × 7)",
    120: "Limit (120 years until flood - Genesis 6:3)",
    144: "Elect × elect (12 × 12)",
    360: "Prophetic year (12 × 30-day months)",
    390: "Years of Israel's apostasy (Ezekiel)",
    490: "70 weeks completed (Daniel)",
    1260: "3.5 years (half of 7) - tribulation period",
    1290: "1,260 + 30 days - time of completion",
    1335: "1,290 + 45 days - blessing awaits",
    1440: "12 × 120 - full election (12 × limit)",
    2300: "Long duration - desecration to restoration",
    2520: "7 × 360 - complete prophetic cycle",
    144000: "Elect sealed - 12 × 12 × 1,000",
}

# Time unit definitions (prophetic calendar)
TIME_UNITS = {
    "day": 1,
    "month": 30,      # Prophetic month = 30 days
    "year": 360,      # Prophetic year = 12 × 30
    "week": 7,        # Standard week
    "time": 360,      # "A time" = 1 prophetic year
}

# Theme categories for cross-referencing
THEMES = {
    "tribulation": [
        "Revelation 12:6,14",
        "Daniel 7:25",
        "Daniel 12:7",
        "Revelation 13:5",
        "Matthew 24:21-22"
    ],
    "judgment": [
        "Revelation 6-18 (seals, trumpets, bowls)",
        "Daniel 2:34-35 (stone cuts mountain)",
        "Joel 3:12-16 (valley of judgment)"
    ],
    "restoration": [
        "Daniel 9:24-27 (70 weeks)",
        "Ezekiel 36-37 (dry bones, restoration)",
        "Isaiah 11:11-12 (gathering of Israel)",
        "Jeremiah 31:31-34 (new covenant)"
    ],
    "messianic": [
        "Daniel 9:24-27 (Messiah cut off)",
        "Isaiah 53 (suffering servant)",
        "Zechariah 9:9-10 (king comes humbly)",
        "Psalm 22 (crucifixion prophecy)"
    ],
    "rapture": [
        "1 Thessalonians 4:13-18",
        "1 Corinthians 15:51-58",
        "John 14:1-3",
        "Revelation 4-5 (throne scene)"
    ],
    "second_coming": [
        "Acts 1:11 (returns the same way)",
        "Zechariah 14:4 (feet on Mount of Olives)",
        "Matthew 24:29-31 (sign of Son of Man)",
        "Revelation 19:11-16 (the rider on white horse)"
    ],
    "beast": [
        "Revelation 13 (first and second beast)",
        "Daniel 7:19-27 (fourth beast - Rome)",
        "Daniel 8:23-27 (little horn)",
        "2 Thessalonians 2:3-12 (lawless one)"
    ],
    "temple": [
        "Daniel 9:27 (abomination of desolation)",
        "Matthew 24:15 (flee when see)",
        "Ezekiel 40-48 (future temple)",
        "Revelation 11:1-2 (temple measured)"
    ],
}


def search_references(query: str) -> list:
    """
    Search references by text content or reference.
    
    Args:
        query: Search term
        
    Returns:
        List of matching references
    """
    query_lower = query.lower()
    results = []
    
    for ref in BIBLICAL_REFERENCES:
        if (query_lower in ref.get("reference", "").lower() or
            query_lower in ref.get("text", "").lower() or
            query_lower in ref.get("context", "").lower()):
            results.append(ref)
            
    return results


def get_references_by_theme(theme: str) -> list:
    """Get all references for a given theme."""
    return THEMES.get(theme.lower(), [])


def get_timecode_references(value: int, unit: str = "days") -> list:
    """Get all references matching a specific timecode."""
    results = []
    
    for ref in BIBLICAL_REFERENCES:
        if ref.get("value") == value and ref.get("unit") == unit:
            results.append(ref)
            
    return results
