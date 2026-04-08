# Timecode Analysis Agent

Analyzes biblical prophecy and timecodes for @timecode1260 content.

## Quick Start

```python
from timecode_agent import TimecodeAgent

agent = TimecodeAgent()

# Analyze a prophetic timecode
result = agent.analyze_prophecy("1260 days", book="Revelation")
print(result.thread_draft)

# Get theme analysis
theme_data = agent.get_theme_analysis("beast")
print(theme_data["references"])

# Compare two timecodes
comparison = agent.analyze_prophecy_relationship("1260 days", "42 months")
print(comparison["relationships"])
```

## Features

- **Timecode Parser** — Handles numeric ("1260 days"), compound ("time, times, and half a time"), and symbolic formats
- **Reference Database** — 40+ prophetic passages with context and themes
- **Symbolic Number Analysis** — Understands what numbers mean (7=completion, 12=government, etc.)
- **Theme Clustering** — Groups prophecies by theme (tribulation, judgment, restoration, messianic, etc.)
- **X Thread Generator** — Creates engaging thread drafts ready to post

## Key Timecodes

| Timecode | Equivalent | Key References |
|----------|------------|-----------------|
| 1,260 days | 42 months, 3.5 years | Revelation 12, Daniel 7, Daniel 12 |
| 42 months | 1,260 days | Revelation 11, 13 |
| 70 weeks | 490 days | Daniel 9:24-27 |
| 1,290 days | 1,260 + 30 | Daniel 12:11 |
| 1,335 days | 1,290 + 45 (blessed!) | Daniel 12:12 |
| 144,000 | 12 × 12 × 1,000 | Revelation 7, 14 |

## Symbolic Numbers

- **7** — Completeness/perfection
- **12** — Divine government
- **40** — Testing/trial
- **144** — Elect × elect (12 × 12)
- **360** — Prophetic year (12 × 30)

## Project Structure

```
timecode_agent/
├── agent.py         # Main TimecodeAgent class
├── parser.py        # ProphecyParser for timecode parsing
├── references.py   # Biblical database + helper functions
├── generator.py    # X thread generator
├── __init__.py
├── SPEC.md
└── README.md
```

## Future Enhancements

- [ ] Connect to real Bible API for verse lookup
- [ ] Add date correlation calculator (input date → find prophecy alignment)
- [ ] X API integration for direct posting
- [ ] Visualization of prophecy timelines
- [ ] Cross-reference analysis (trace theme through Bible)

---

Built for @timecode1260 — Biblical prophecy + timecodes.
