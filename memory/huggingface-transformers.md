# HuggingFace Transformers — Quick Start

> Created: 2026-03-06

HuggingFace Transformers is the go-to library for working with pretrained language models.

---

## Installation

```bash
pip install transformers torch
```

For Apple Silicon:
```bash
pip install transformers torch
```

---

## Quick Start

### Load a Model

```python
from transformers import AutoModel, AutoTokenizer

# Load BERT
model = AutoModel.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokenize
text = "Hello, world!"
inputs = tokenizer(text, return_tensors="pt")

# Forward pass
outputs = model(**inputs)
last_hidden_state = outputs.last_hidden_state
```

### Popular Models

| Model | Use Case |
|-------|----------|
| **bert-base-uncased** | NER, classification |
| **gpt2** | Text generation |
| **t5-small** | Summarization, translation |
| **llama3** | Chat, generation |
| **claude** | (Use Anthropic API) |

---

## Common Tasks

### Text Classification

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("I love learning about AI!")
# [{'label': 'POSITIVE', 'score': 0.99}]
```

### Named Entity Recognition

```python
ner = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
result = ner("Mark is at Stanford University in California")
# [{'entity': 'B-PER', 'word': 'Mark', ...}]
```

### Summarization

```python
summarizer = pipeline("summarization")
result = summarizer("Long text here...")
```

### Text Generation

```python
generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50)
```

---

## Fine-Tuning

```python
from transformers import Trainer, TrainingArguments

# Prepare dataset
train_dataset = ...  # Your data

# Fine-tune
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

---

## Key Classes

| Class | Purpose |
|-------|---------|
| `AutoModel` | Load any pretrained model |
| `AutoTokenizer` | Load any tokenizer |
| `pipeline` | Quick task execution |
| `Trainer` | Fine-tuning wrapper |
| `TrainingArguments` | Training configuration |

---

## Next Steps

- Explore HuggingFace Hub (10k+ models)
- Try fine-tuning on your data
- Deploy with 🤗 Accelerate

---

*HuggingFace makes AI accessible.* ✨
