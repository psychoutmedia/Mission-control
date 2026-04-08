"""
Hugging Face Transformers Demo
Load models, run inference, and understand the pipeline

This demonstrates:
- Loading pretrained models
- Tokenization
- Pipeline API
- Model introspection

Run: python projects/hf_transformers_demo.py
"""

from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch


def demo_pipeline():
    """Use the pipeline API - simplest way to run inference"""
    print("=" * 60)
    print("DEMO 1: Pipeline API (easiest)")
    print("=" * 60)
    
    # Sentiment analysis pipeline
    classifier = pipeline("sentiment-analysis")
    result = classifier("I love building AI agents!")[0]
    print(f"Sentiment: {result['label']} (score: {result['score']:.3f})")
    
    # Text generation pipeline
    generator = pipeline("text-generation", model="gpt2")
    result = generator("Once upon a time", max_new_tokens=30, num_return_sequences=1)[0]
    print(f"\nGenerated: {result['generated_text']}")


def demo_tokenizer():
    """Understand tokenization - how text becomes numbers"""
    print("\n" + "=" * 60)
    print("DEMO 2: Tokenization")
    print("=" * 60)
    
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    text = "Hello, world! AI is amazing."
    tokens = tokenizer(text, return_tensors="pt")
    
    print(f"Original text: '{text}'")
    print(f"Token IDs: {tokens['input_ids'].tolist()[0]}")
    print(f"Token count: {tokens['input_ids'].shape[1]}")
    
    # Decode back
    decoded = tokenizer.decode(tokens['input_ids'][0])
    print(f"Decoded: '{decoded}'")


def demo_model_loading():
    """Load model and tokenizer directly"""
    print("\n" + "=" * 60)
    print("DEMO 3: Direct Model Loading")
    print("=" * 60)
    
    model_name = "gpt2"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    print(f"Model: {model_name}")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Model size: ~{sum(p.numel() for p in model.parameters()) * 2 / 1e6:.1f}MB")
    
    # Check device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    model.to(device)


def demo_embeddings():
    """Extract embeddings from a model"""
    print("\n" + "=" * 60)
    print("DEMO 4: Embeddings")
    print("=" * 60)
    
    from transformers import AutoModel
    
    model = AutoModel.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    text = "artificial intelligence"
    inputs = tokenizer(text, return_tensors="pt")
    
    # Get hidden states
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    
    # Last hidden state
    hidden = outputs.last_hidden_state
    print(f"Input: '{text}'")
    print(f"Hidden shape: {hidden.shape} (batch, tokens, hidden_dim)")
    print(f"Embedding dim: {hidden.shape[-1]}")
    
    # Mean pooling
    mean_embed = hidden.mean(dim=1)
    print(f"Mean pooled shape: {mean_embed.shape}")


# ---------------------------------------------------------------------------
# DEMO 5: Fine-tuning with LoRA (Low-Rank Adaptation)
# ---------------------------------------------------------------------------
# LoRA freezes the base model and trains only small adapter matrices.
# This makes fine-tuning feasible on consumer GPUs (or Mac M-series).
# We train a sentiment classifier on a tiny custom dataset.
# ---------------------------------------------------------------------------

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
)
from datasets import load_dataset
import torch


def prepare_sample_dataset():
    """
    Tiny custom dataset for sentiment classification.
    In production you'd load from CSV/JSON/HF Hub.
    """
    from datasets import Dataset

    data = {
        "text": [
            "I love this product, it's amazing!",
            "Terrible experience, would not recommend.",
            "Pretty good overall, satisfied with purchase.",
            "Absolute garbage, worst decision ever.",
            "Decent for the price, does the job.",
            "Mind-blowing quality, exceeded expectations!",
        ],
        "label": [1, 0, 1, 0, 1, 1],  # 1=positive, 0=negative
    }
    return Dataset.from_dict(data)


def demo_lora_finetuning():
    """
    Fine-tune a classifier using LoRA + HuggingFace Trainer.
    This freezes the base model and only trains adapter layers.
    """
    print("\n" + "=" * 60)
    print("DEMO 5: Fine-tuning with LoRA (Low-Rank Adaptation)")
    print("=" * 60)

    model_name = "distilbert-base-uncased"  # Small enough for CPU/Mac
    print(f"Base model: {model_name}")

    # 1. Load model + tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=2
    )

    # 2. Tokenize dataset
    dataset = prepare_sample_dataset()

    def tokenize_fn(examples):
        return tokenizer(
            examples["text"], truncation=True, padding="max_length", max_length=128
        )

    tokenized_ds = dataset.map(tokenize_fn, batched=True)
    tokenized_ds = tokenized_ds.remove_columns(["text"])
    tokenized_ds.set_format("torch")

    # 3. Split into train/eval
    split_ds = tokenized_ds.train_test_split(test_size=0.3, seed=42)
    train_ds = split_ds["train"]
    eval_ds = split_ds["test"]

    # 4. Data collator (handles batching)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # 5. Training arguments — lightweight for demo
    training_args = TrainingArguments(
        output_dir="./hf_finetune_demo",
        eval_strategy="epoch",
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        num_train_epochs=5,
        learning_rate=2e-4,
        logging_steps=2,
        save_strategy="no",  # Don't save checkpoint for demo
        report_to="none",  # Disable wandb/tensorboard
        seed=42,
    )

    # 6. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=data_collator,
    )

    print("\nStarting fine-tuning (5 epochs on 4 samples)...")
    print("(This would take longer on a real dataset)")
    trainer.train()

    # 7. Evaluate
    print("\nEvaluation results:")
    metrics = trainer.evaluate()
    print(f"Eval loss: {metrics['eval_loss']:.4f}")
    print(f"Eval accuracy: {metrics['eval_accuracy']:.4f}")

    # 8. Run inference on new text
    print("\nInference on new samples:")
    test_texts = [
        "This is fantastic, I really enjoy it!",
        "Not great, quite disappointing honestly.",
    ]
    for text in test_texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            logits = model(**inputs).logits
        pred = torch.argmax(logits, dim=-1).item()
        label = "positive" if pred == 1 else "negative"
        print(f"  '{text}' → {label}")


def demo_peft_lora_overview():
    """
    For larger models, use the `peft` library + LoRA.
    Full example (requires `pip install peft`):
    """
    print("\n" + "=" * 60)
    print("DEMO 6: PEFT/LoRA for Large Models (Concept)")
    print("=" * 60)
    print("""
For models like Llama-7B+, full fine-tuning is prohibitive.
Use PEFT (Parameter-Efficient Fine-Tuning) with LoRA:

    from peft import LoraConfig, get_peft_model, TaskType

    lora_config = LoraConfig(
        r=8,                      # rank — higher = more capacity, more params
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],  # which layers to adapt
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.SEQ_CLS,
    )

    base_model = AutoModelForSequenceClassification.from_pretrained(...)
    model = get_peft_model(base_model, lora_config)
    model.print_trainable_parameters()
    # Output: "trainable params: 0.1% of all parameters"

Key insight: LoRA adds small rank-decomposition matrices (A, B)
such that W_new = W + BA. Instead of updating W (billions of params),
you only train A and B (thousands of params).

Typical use cases:
- Instruction tuning (Alpaca, Vicuna style)
- Domain adaptation (legal, medical, finance)
- Task-specific classifiers
- Personality/persona fine-tuning

Resources:
- https://huggingface.co/docs/peft
- https://arxiv.org/abs/2106.09685 (LoRA paper)
""")


if __name__ == "__main__":
    print("Hugging Face Transformers Demo")
    print("=" * 60)
    
    demo_pipeline()
    demo_tokenizer()
    demo_model_loading()
    demo_embeddings()
    
    print("\n" + "=" * 60)
    print("DEMO 5: Fine-tuning (real run)")
    print("=" * 60)
    demo_lora_finetuning()
    demo_peft_lora_overview()
    
    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("""
1. Pipeline API - fastest way to get started
2. Tokenization - text → tokens → IDs → model → IDs → text
3. Models are just large neural networks (~124M params for gpt2)
4. Embeddings - dense vectors representing semantic meaning
5. Auto classes - AutoTokenizer, AutoModel - load any model architecture
6. Fine-tuning - adapt a pretrained model to your task/dataset
   - Full fine-tune: update all params (expensive)
   - LoRA/PEFT: freeze base, train only adapters (cheap, effective)
   - Great for: instruction tuning, domain adaptation, classifiers
    """)
