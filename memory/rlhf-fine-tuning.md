# RLHF and Fine-Tuning Basics

> Created: 2026-03-06

Reinforcement Learning from Human Feedback (RLHF) and fine-tuning fundamentals.

---

## What is Fine-Tuning?

Fine-tuning = taking a pretrained model and training it further on your specific data.

```
Pretrained Model (GPT, BERT) → Fine-tune on your data → Specialized Model
```

**vs Prompt Engineering:**
- Prompting: Model stays the same, you optimize input
- Fine-tuning: Model changes, learns your patterns

---

## When to Fine-Tune

| Approach | When to Use |
|---------|-------------|
| Prompting | General tasks, quick experiments |
| Fine-tuning | Domain-specific patterns, style, low-latency |
| RLHF | Alignment, complex preferences |

---

## Types of Fine-Tuning

### 1. Full Fine-Tuning
```python
# Update ALL parameters
model = AutoModel.from_pretrained("bert-base")
model.train()
# Gradients flow through entire model
```

### 2. LoRA (Low-Rank Adaptation)
```python
# Only update small adapter matrices
from peft import LoraConfig, get_peft_model

config = LoraConfig(r=8, lora_alpha=16, target_modules=["q_proj", "v_proj"])
model = get_peft_model(base_model, config)
# Train 1-2% of original parameters!
```

### 3. QLoRA
```python
# Quantized + LoRA = even smaller
# 4-bit quantization + LoRA adapters
```

---

## RLHF Overview

```
Step 1: Pretrain on large corpus
         ↓
Step 2: Supervised Fine-Tuning (SFT)
         ↓
Step 3: Reward Model (RM) training
         ↓
Step 4: PPO (Proximal Policy Optimization)
         ↓
Aligned Model
```

### Step 1: Pretraining
Massive text corpus → base model learns language

### Step 2: SFT (Supervised Fine-Tuning)
Human-written Q&A pairs → model learns to respond

### Step 3: Reward Model
- Collect human preferences (A vs B)
- Train model to predict which response humans prefer

### Step 4: PPO
- Use RM to score model outputs
- Reinforcement learning optimizes for high scores

---

## Code: LoRA Fine-Tuning with PEFT

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType

# Load base model
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Configure LoRA
lora_config = LoraConfig(
    r=8,                    # Rank
    lora_alpha=16,           # Scaling
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    task_type=TaskType.CAUSAL_LM
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Output: trainable params: 0.08% of all parameters
```

### Training
```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=3e-4,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

### Save and Load
```python
# Save adapters only
model.save_pretrained("./lora_weights")

# Load later
from peft import PeftModel
model = PeftModel.from_pretrained(base_model, "./lora_weights")
```

---

## DPO (Direct Preference Optimization)

Newer, simpler than RLHF:

```python
from trl import DPOTrainer

dpo_trainer = DPOTrainer(
    model=model,
    train_dataset=preference_dataset,  # (chosen, rejected) pairs
)
dpo_trainer.train()
```

---

## Tools

| Tool | What it does |
|-----|-------------|
| **PEFT** | Parameter-Efficient Fine-Tuning (LoRA, etc.) |
| **TRL** | Transformer Reinforcement Learning (SFT, DPO, PPO) |
| **QLoRA** | Quantized LoRA |
| **Axolotl** | All-in-one fine-tuning script |

---

## When to Use What

| Scenario | Approach |
|---------|----------|
| Learn new style | LoRA |
| Learn new domain | Full fine-tune |
| Align with preferences | RLHF/DPO |
| Quick + cheap | LoRA |
| Best quality | Full fine-tune + RLHF |

---

## Next Steps

1. Try fine-tuning a small model (gpt2) on your data
2. Experiment with LoRA rank (r=8 vs r=16)
3. Explore DPO for preference learning

---

*Fine-tuning is how you make models yours.* ✨
