# MIT Paper Summary: State of LLMs 2025 (Sebastian Raschka)

*Source: Sebastian Raschka (MIT) - https://magazine.sebastianraschka.com/p/state-of-llms-2025*

## Key Takeaways

### DeepSeek R1 & RLVR
- **Reinforcement Learning with Verifiable Rewards (RLVR)** + **GRPO** algorithm
- Enables post-training LLMs on large amounts of data without expensive human labels
- Verifiable rewards = math + code (deterministic correctness)
- Training cost: ~$5M (vs previous $50-500M estimates)

### LLM Development Focus by Year
| Year | Focus |
|------|-------|
| 2022 | RLHF + PPO |
| 2023 | LoRA SFT |
| 2024 | Mid-Training |
| 2025 | RLVR + GRPO |

### Inference-Time Scaling (2026 Priority)
- Spend more compute at inference for better accuracy
- Trade-off: latency/cost vs accuracy
- Techniques: self-consistency, self-refinement
- DeepSeekV2-Math: pushed to gold-level on math competition benchmark

### What's Next (2026-2027)
- **2026**: RLVR extensions + more inference-time scaling
- **2027**: Continual learning (catastrophic forgetting challenge)

### GRPO Improvements (from 2025 literature)
- Zero gradient signal filtering (DAPO)
- Active sampling
- Token-level loss
- No KL loss
- Clip higher
- Off-policy sequence masking

## Why This Matters for LLM Engineering
1. RLVR is THE hot topic for post-training reasoning models
2. Inference-time scaling = practical skill for optimizing LLM apps
3. Understanding GRPO variants = valuable for alignment/finetuning work
4. Continual learning = future of LLM adaptation

---
*Read: March 8, 2026*
