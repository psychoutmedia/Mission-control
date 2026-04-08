"""
X Thread Generator for @timecode1260
Generates compelling thread drafts from prophecy analysis.
"""


class ThreadGenerator:
    """Generates X thread content from prophecy analysis."""

    def __init__(self):
        self.max_thread_length = 25  # X limits
        self.max_chars = 280  # Per tweet

    def generate_thread(
        self,
        timecode: str,
        parsed: dict,
        references: list,
        symbolic: str = None,
        correlations: list = None
    ) -> str:
        """
        Generate a thread draft from analysis.
        
        Args:
            timecode: The prophetic timecode
            parsed: Parser output
            references: Biblical references found
            symbolic: Symbolic meaning of the number
            correlations: Historical/modern correlations
            
        Returns:
            Formatted thread as string
        """
        lines = []
        lines.append(self._hook(timecode, parsed))
        
        # Add references
        if references:
            lines.append(self._references_section(references))
            
        # Add symbolic meaning
        if symbolic:
            lines.append(self._symbolic_section(symbolic, parsed))
            
        # Add correlations
        if correlations:
            lines.append(self._correlations_section(correlations))
            
        # Add thread end
        lines.append(self._cta())
        
        return "\n\n".join(lines)

    def _hook(self, timecode: str, parsed: dict) -> str:
        """Generate engaging hook for the thread."""
        hooks = {
            1260: f"""THREAD: The most mysterious number in Bible prophecy.

1,260.

It appears in Revelation 12, Daniel 7, and Daniel 12.
Always connected to the same 3.5-year period.

Why 1,260? Why does God use this number repeatedly?

Let me explain 👇""",

            42: f"""THREAD: Why does the Beast get exactly 42 months?

Not 41. Not 43. Exactly 42.

Revelation 13 says the beast makes war for 42 months.
Daniel 7 mentions "a time, times, and half a time."

There's a pattern here most people miss.

🧵""",

            144: f"""THREAD: 144,000 is the most misunderstood number in Revelation.

Everyone has theories about who they are.
But the number itself reveals something profound.

It's not about who is saved.
It's about the PATTERN God uses.

Let me show you 👇""",

            7: f"""THREAD: Why does God use 7 everywhere?

7 seals. 7 trumpets. 7 bowls.
7 churches. 7 spirits before the throne.

It's not just symbolic repetition.
There's a mathematical precision beneath it.

Here's what's really happening 👇""",

            70: f"""THREAD: Daniel's 70 weeks prophecy changed history.

490 years. Decreed for one purpose:
To reveal the Messiah to the world.

And it happened. Right on time.

Here's how we know 👇""",
        }
        
        default_hook = f"""THREAD: Breaking down {timecode}

Numbers in Bible prophecy aren't random.
Each has a purpose, a pattern, a revelation.

Let's decode {timecode} 👇"""
        
        value = parsed.get("value")
        return hooks.get(value, default_hook)

    def _references_section(self, references: list) -> str:
        """Format references for the thread."""
        lines = ["📜 WHERE IT APPEARS:\n"]
        
        for ref in references[:4]:  # Limit to 4 refs
            ref_text = ref.get("reference", "")
            context = ref.get("context", "")
            lines.append(f"• {ref_text}")
            if context:
                lines.append(f"  Context: {context[:80]}...")
                
        return "\n".join(lines)

    def _symbolic_section(self, symbolic: str, parsed: dict) -> str:
        """Add symbolic meaning section."""
        value = parsed.get("value")
        
        return f"""
🔢 THE NUMBER MEANS:

{value} = {symbolic}

This isn't coincidence.
God encodes meaning into the very structure of prophecy.

The number IS the message."""

    def _correlations_section(self, correlations: list) -> str:
        """Add historical correlations."""
        lines = ["\n⏰ HISTORICAL CORRELATIONS:\n"]
        
        for corr in correlations[:3]:
            lines.append(f"→ {corr}")
            
        return "\n".join(lines)

    def _cta(self) -> str:
        """Call to action."""
        return """
---

Follow @timecode1260 for weekly deep-dives into biblical prophecy, timecodes, and the hidden mathematics of scripture.

What timecode should I decode next? 👇"""

    def generate_theme_thread(self, theme: str, theme_data: dict) -> str:
        """Generate a thread about a prophecy theme."""
        references = theme_data.get("references", [])
        pattern = theme_data.get("pattern", "")
        
        lines = [
            f"THREAD: {theme.upper()} IN BIBLE PROPHECY\n",
            f"The theme of {theme} appears throughout scripture.",
            f"\nFrom Genesis to Revelation, God weaves this pattern.\n",
            "📜 KEY REFERENCES:\n"
        ]
        
        for ref in references[:5]:
            lines.append(f"• {ref}")
            
        lines.append(f"\n🔗 THE PATTERN:\n{pattern}")
        lines.append("\nFollow @timecode1260 for more prophecy breakdowns 👆")
        
        return "\n".join(lines)

    def generate_comparison_thread(self, code1: str, code2: str, comparison: dict) -> str:
        """Generate thread comparing two timecodes."""
        rels = comparison.get("relationships", [])
        
        lines = [
            f"THREAD: {code1} vs {code2}\n",
            "Prophetic timecodes interlock in fascinating ways.",
            "Let's look at how these two connect:\n"
        ]
        
        for rel in rels:
            lines.append(f"→ {rel}")
            
        lines.append("\nFollow @timecode1260 for more prophecy deep-dives 👆")
        
        return "\n".join(lines)

    def format_as_thread(self, content: str) -> list:
        """
        Format content as proper thread tweets.
        
        Returns:
            List of tweet strings, each under 280 chars
        """
        tweets = []
        lines = content.split("\n")
        current_tweet = ""
        
        for line in lines:
            # Check if adding this line exceeds limit
            test_tweet = current_tweet + "\n" + line if current_tweet else line
            
            if len(test_tweet) <= self.max_chars:
                current_tweet = test_tweet
            else:
                # Save current and start new
                if current_tweet:
                    tweets.append(current_tweet.strip())
                current_tweet = line
                
        # Don't forget last tweet
        if current_tweet:
            tweets.append(current_tweet.strip())
            
        # Add thread numbers if multiple tweets
        if len(tweets) > 1:
            numbered = []
            for i, tweet in enumerate(tweets, 1):
                numbered.append(f"({i}/{len(tweets)}) {tweet}")
            tweets = numbered
            
        return tweets
