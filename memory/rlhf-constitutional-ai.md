# RLHF & Constitutional AI — Training Alignment Techniques

## TL;DR

RLHF (Reinforcement Learning from Human Feedback) and Constitutional AI (CAI) are the core techniques for making LLMs helpful, harmless, and honest. RLHF uses human preference data + RL; CAI uses AI-generated principles + self-critique. DPO has largely replaced PPO as the go-to method due to simplicity and stability.

---

## The Alignment Problem

LLMs are trained to predict the next token — they don't inherently know what humans *want*. They need to be shaped:

```
Pretrained LLM → follows statistics, not intent
         ↓
SFT (Supervised Fine-Tuning) → imitates human demonstrations
         ↓
RLHF / DPO / CAI → aligns with human preferences and values
```

---

## Traditional RLHF (3-Stage Pipeline)

### Stage 1: Supervised Fine-Tuning (SFT)

Fine-tune base model on high-quality human demonstrations.

```python
# Example: SFT with HuggingFace
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8b")
trainer = SFTTrainer(
    model=model,
    train_dataset=demonstrations,  # (prompt, response) pairs
    args=TrainingArguments(learning_rate=1e-5, epochs=3),
)
trainer.train()
```

### Stage 2: Reward Model Training

Train a separate model to predict human preferences.

**Data format:** Pairs of responses (A, B) with human preference label

```python
# Reward model: takes (prompt, response) → scalar score
class RewardModel(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.base = base_model
        self.reward_head = nn.Linear(hidden_size, 1)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.base(input_ids, attention_mask)
        # Use last token's hidden state for reward
        hidden = outputs.last_hidden_state[:, -1, :]
        return self.reward_head(hidden).squeeze(-1)
```

**Training:** Minimize cross-entropy loss on preference pairs — higher reward for preferred response.

### Stage 3: RL Fine-Tuning with PPO

Use the reward model to fine-tune the SFT model via Proximal Policy Optimization (PPO).

```python
# PPO update rule (simplified)
policy_ratio = π_new(a|s) / π_old(a|s)  # probability ratio
clipped_ratio = clip(policy_ratio, 1 - ε, 1 + ε)  # PPO clip
policy_loss = -min(policy_ratio * advantage, clipped_ratio * advantage)
```

**Problem with PPO:**
- Complex: requires separate reward model, value function, KL divergence penalty
- Unstable: reward hacking, mode collapse
- Expensive: requires two model copies (policy + old policy)

---

## DPO (Direct Preference Optimization)

**Insight:** Skip the reward model entirely. Formulate alignment as a classification/contrastive objective.

### The DPO Loss

```python
def dpo_loss(policy_logits, ref_logits, chosen_rewards, rejected_rewards, beta=0.1):
    """
    policy_logits: policy model log probs (batch_size, seq_len, vocab)
    ref_logits: reference (SFT) model log probs
    chosen_rewards, rejected_rewards: scalar rewards from reward model
    
    Simplified — we only use final logits for the "response" portion
    """
    # Compute log probs for policy and reference
    pi_logps = log_softmax(policy_logits)  # per token
    ref_logps = log_softmax(ref_logits)
    
    # Compute per-token advantage via KL divergence
    pi_lps = pi_logps.sum(dim=-1)  # sequence-level
    ref_lps = ref_logps.sum(dim=-1)
    
    # DPO contrastive loss
    # Policy should assign higher prob to chosen vs rejected, relative to reference
    loss = -log_sigmoid(beta * (pi_lps[chosen] - ref_lps[chosen]) 
                          - beta * (pi_lps[rejected] - ref_lps[rejected]))
    return loss.mean()
```

### Why DPO > PPO

| Aspect | PPO-RLHF | DPO |
|--------|----------|-----|
| Models needed | 3 (SFT, reward, value) | 2 (SFT + policy) |
| Stability | Sensitive to hyperparameters | More stable |
| Complexity | ~2000 lines HF impl | ~200 lines |
| KL penalty | Explicit penalty term | Implicit via reference |
| Memory | High (needs old policy) | Lower |
| Performance | Good | Often better |

**Llama 4 (2025):** Uses combination of SFT → rejection sampling → PPO → DPO across multiple rounds.

---

## Constitutional AI (Anthropic, 2022)

**Key idea:** Instead of humans providing all feedback, use AI to critique and revise responses based on a "constitution" of principles.

### Two-Phase Process

**Phase 1: Critique & Revision (SL)**

1. Sample response from model
2. Ask model to critique based on a constitutional principle
3. Ask model to revise response to address critique
4. Fine-tune on (original → revised) pairs

**Example constitutional principle:**
> "Choose the response that is less likely to contain harmful or unethical content. Prefer responses that are more honest and don't manipulate the user."

**Phase 2: RLAIF (RL from AI Feedback)**

1. Use a helpful-only model to generate preference rankings over responses
2. Apply DPO or PPO using AI preferences instead of human preferences
3. Result: model learns from AI-generated feedback (RLAIF)

```python
# CAI critique prompt example
critique_prompt = """Review the following response and identify any ways it could be:
- Harmful or unethical
- Dishonest or manipulative
- Ineffective at being helpful

Response: {response}

Critique:"""

revision_prompt = """Revise the following response to address the critique:

Original: {response}
Critique: {critique}

Revised:"""
```

---

## GRPO (Group Relative Policy Optimization)

**DeepSeek's approach (2025):** Simplifies DPO by generating multiple responses and using group-relative scoring.

```python
# GRPO: instead of pairwise DPO, use group
def grpo_loss(model, prompts, responses_per_prompt=8, beta=0.1):
    """
    For each prompt, generate G responses.
    Score them with a reward model.
    Use relative ranking within group for policy gradient.
    """
    losses = []
    for prompt in prompts:
        # Generate G responses
        response_group = [generate(model, prompt) for _ in range(G)]
        
        # Score each
        rewards = [reward_model(prompt, resp) for resp in response_group]
        
        # Compute relative advantages within group
        baseline = mean(rewards)
        advantages = [r - baseline for r in rewards]
        
        # Policy gradient loss on group-relative advantages
        loss = -sum(advantages * log_probs) / G
        losses.append(loss)
    
    return mean(losses)
```

**Advantage:** Doesn't need a separate reference model — uses previous policy as implicit baseline.

---

## Comparison of Alignment Methods

| Method | Feedback Source | Complexity | Stability | Scalability |
|--------|---------------|------------|-----------|-------------|
| **SFT** | Human demos | Low | High | Good |
| **RLHF (PPO)** | Human preferences | Very High | Medium | Poor |
| **DPO** | Human preferences | Medium | High | Good |
| **RLAIF** | AI preferences | Medium | High | Excellent |
| **CAI** | AI + Constitution | Medium | High | Excellent |
| **GRPO** | AI rewards (group) | Low | High | Excellent |

---

## Practical Implementation

### Tooling

- **Trlx** — Language model RL library (supports PPO, DPO)
- **RL4LMs** — RL for language models (PPO, A2C, etc.)
- **RLHF-PyTorch** — Custom PyTorch RLHF implementation
- **Axolotl** — Fine-tuning with DPO, LoRA support
- **HuggingFace TRL** — Transformer Reinforcement Learning (DPO, PPO)
- **DeepSeek-R1** — GRPO implementation open-sourced

### Example: DPO with TRL

```python
from trl import DPOTrainer

dpo_trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    beta=0.1,
    train_dataset=preference_dataset,  # (prompt, chosen, rejected)
)

dpo_trainer.train()
```

### Example: CAI with Self-Critique Loop

```python
def constitutional_revision(model, prompt, constitution, num_revisions=2):
    response = generate(model, prompt)
    
    for _ in range(num_revisions):
        # Critique
        critique = generate(
            model,
            f"Critique: {response}\n\nPrinciple: {constitution}"
        )
        
        # Revise
        response = generate(
            model,
            f"Original: {response}\nCritique: {critique}\nRevised:"
        )
    
    return response
```

---

## Common Pitfalls

1. **Reward hacking** — Model exploits reward model instead of genuine helpfulness
2. **KL collapse** — Policy drifts too far from reference, loses diversity
3. **Sycophancy** — Model learns to agree with users rather than being genuinely helpful
4. **Length bias** — Longer responses get higher rewards even if less helpful
5. **Preference labeling inconsistency** — Human labelers disagree, leading to noisy signal

**Mitigations:**
- Use Constitutional AI critiques to reduce reliance on human labels
- Apply KL penalty to keep policy close to reference
- Include "honesty" principles alongside helpfulness
- Use大军 diverse preference datasets

---

## For Automa Dynamics (Helios-1 Agent)

**Alignment strategy for autonomous robots:**

1. **Base model:** Fine-tune on teleoperation data (human operators controlling robot)
2. **RLHF:** Collect human preference data on robot behavior (which actions preferred)
3. **Constitutional principles:** Define safety constraints as constitutional principles
4. **Online RL:** Continuously update from real-world feedback

**Key principles for Helios:**
- Safety first: Constitutional principle — "If action could harm humans, prefer inaction"
- Transparency: Robot should explain its reasoning
- Fallback to teleoperation: When uncertain, yield to human control

---

## Next Steps

- Set up DPO training pipeline with TRL for fine-tuning experiments
- Explore GRPO as simpler alternative to PPO
- Research reward model training for domain-specific alignment (robotics)
- Build constitutional principle set for Helios-1

---

## Resources

- [DeepSeek-R1 GRPO paper](https://arxiv.org/abs/2501.12599)
- [Constitutional AI (Anthropic 2022)](https://arxiv.org/abs/2212.08073)
- [DPO paper (Meta 2023)](https://arxiv.org/abs/2305.18290)
- [HuggingFace TRL library](https://huggingface.co/docs/trl)
- [Llama 4 alignment process](https://intuitionlabs.ai/articles/reinforcement-learning-human-feedback)
