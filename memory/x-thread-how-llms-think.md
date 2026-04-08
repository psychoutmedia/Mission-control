# X Thread: How LLMs Actually Think

> Pillar 5: Visibility | Created: 2026-03-06
> For posting on @timecode1260 or @automadynamics

---

## Thread Draft

**1/ 🧵 How LLMs Actually "Think" — A thread**

Everyone talks about AI "thinking" and "reasoning."

But what's *actually* happening inside GPT-4, Claude, or Llama when you ask it a question?

Let me break it down. No PhD required. 👇

---

**2/ First: LLMs don't think. They predict.**

Their entire job is answering one question:

"Given everything I've seen so far, what word comes next?"

That's it. Next token prediction. Everything else emerges from this.

---

**3/ Step 1: Tokenization**

Your text gets chopped into pieces called "tokens."

"Hello world" → ["Hello", " world"]
"unbelievable" → ["un", "believ", "able"]

GPT-4 has ~100K possible tokens. Each gets a number.

"Hello" = 9906
" world" = 1917

---

**4/ Step 2: Embeddings**

Each token number becomes a vector — a list of ~4,000 numbers.

These numbers encode *meaning*.

"king" and "queen" have similar vectors.
"king" - "man" + "woman" ≈ "queen"

This is where semantics live.

---

**5/ Step 3: Attention (the magic)**

Here's where it gets wild.

The model asks: "For each word, which OTHER words should I pay attention to?"

In "The cat sat on the mat because it was tired"

When processing "it" → attention focuses on "cat" (not "mat")

---

**6/ The attention formula (simplified):**

1. Each token asks a Question: "What am I looking for?"
2. Each token offers a Key: "Here's what I contain"
3. Questions match Keys → attention weights
4. Weighted sum of Values → new representation

Q, K, V. That's the transformer secret.

---

**7/ Step 4: Layers upon layers**

This attention process repeats 80-100 times.

Each layer builds more abstract understanding:
- Layer 1-10: Grammar, syntax
- Layer 20-40: Facts, entities
- Layer 60+: Reasoning, planning

Like a neural assembly line.

---

**8/ Step 5: Prediction**

After all layers, the final vector gets projected to vocabulary size (100K options).

Softmax gives probabilities:
- "Paris" = 0.92
- "London" = 0.03
- "Berlin" = 0.02
- ...

Sample from this. That's your next token.

---

**9/ The "thinking" illusion**

When Claude writes a careful analysis, it's not planning ahead.

It's just... very good at predicting what a "careful analysis" looks like, one word at a time.

The reasoning emerges from the pattern completion.

---

**10/ Why this matters:**

Understanding this changes how you prompt.

- LLMs are pattern matchers, not reasoners
- They predict "what would a good answer look like"
- Chain-of-thought works because it matches "thinking" patterns
- They can be confidently wrong (hallucinations)

---

**11/ The wild part?**

This simple mechanism — next token prediction — trained on internet text...

Somehow learns:
- Multiple languages
- Math (kinda)
- Code
- Reasoning (sometimes)
- World knowledge

From just "predict the next word."

---

**12/ TL;DR**

1. Text → tokens → numbers
2. Numbers → vectors (embeddings)
3. Attention figures out context
4. 80+ layers refine understanding
5. Predict next token probabilities
6. Sample and repeat

No magic. Just math at scale.

But the emergent capabilities? That's where it gets interesting.

---

**13/ Want to go deeper?**

- "Attention Is All You Need" (2017) — the paper that started it
- Anthropic's transformer circuits research
- 3Blue1Brown's neural network series

Or just ask me. I'm building AI agents and learning this stuff daily.

/end 🧵

---

## Posting Notes

- **Best time**: 9-11am or 1-3pm ET (US tech audience)
- **Images**: Could add simple diagrams for tokenization, attention
- **Engagement**: End with a question? "What surprised you most?"
- **Account**: Probably @automadynamics (AI-focused) or @timecode1260 (main)

## Hashtags (use sparingly)
#AI #LLM #MachineLearning #DeepLearning #Transformers

---

## Quick Stats
- 13 tweets
- ~280 words total
- Technical but accessible
- Builds authority in AI space
