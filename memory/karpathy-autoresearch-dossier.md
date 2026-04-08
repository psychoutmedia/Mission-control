# Andrej Karpathy's AutoResearch — Full Briefing Dossier

> **Repo:** https://github.com/karpathy/autoresearch
> **Released:** March 7, 2026
> **Stars:** 53.5k+ | **Forks:** 7.4k+
> **Core idea:** Give an AI agent a real LLM training setup. Let it experiment autonomously overnight. Wake up to a log of validated improvements.

---

## What It Is

AutoResearch is a minimal, self-contained autonomous research framework. You point an AI coding agent (Claude, Codex, etc.) at the repo, edit a single file (`train.py`), and let it run experiments while you sleep.

Each experiment runs for a **fixed 5-minute time budget**. The agent modifies the training code, runs the experiment, checks if validation bits-per-byte (`val_bpb`) improved, and either keeps or discards the change. By morning, you have a git history of incremental improvements and a full experiment log.

**Karpathy's own words:**
> *"One day, frontier AI research used to be done by meat computers in between eating, sleeping, having other fun, and synchronizing once in a while using sound wave interconnect in the ritual of 'group meeting'. That era is long gone. Research is now entirely the domain of autonomous swarms of AI agents... This repo is the story of how it all began."*

---

## Architecture — Three Files That Matter

| File | Role | Agent Modifies? |
|------|------|-----------------|
| `prepare.py` | Data prep, tokenizer, dataloader, evaluation harness. **Fixed.** | ❌ No |
| `train.py` | GPT model, MuonAdamW optimizer, training loop. **Everything fair game.** | ✅ Yes |
| `program.md` | Agent instructions / prompt engineering. Human iterates on this. | ✅ Yes (human) |

### What the Agent Can Modify in `train.py`
- Model architecture (depth, width, head count, KV heads, window pattern)
- Optimizer choice and hyperparameters (LR, betas, weight decay)
- Batch sizes (device, total, gradient accumulation)
- Learning rate schedule (warmup, warmdown, final LR fraction)
- Model size scaling (via `DEPTH`, `ASPECT_RATIO`, `HEAD_DIM`)
- Activation functions, normalization, attention patterns
- Initialization strategies
- Anything in the training loop

### What the Agent CANNOT Do
- Touch `prepare.py`
- Install new packages or modify `pyproject.toml`
- Change the evaluation metric (bits-per-byte, lower = better)
- Run experiments longer than 5 minutes

### Key Design Decisions
- **Fixed time budget** → All experiments are directly comparable regardless of what the agent changes. Autoresearch finds the most optimal model for *your specific hardware* within that budget.
- **Single file scope** → Keeps diffs reviewable and the problem space manageable.
- **Single GPU** → Deliberately minimal. No distributed training complexity.
- **Self-contained** → No external dependencies beyond PyTorch and a few small packages.
- **Simplicity criterion** — *"All else being equal, simpler is better."* Deleting code and getting equal/better results is a win.

---

## The Baseline Model

The starting point (`train.py` as-is):

| Metric | Value |
|--------|-------|
| val_bpb | ~0.9979 |
| Parameters | ~50.3M |
| Depth | 8 layers |
| Vocab size | 32,768 |
| Sequence length | 2,048 |
| Window pattern | SSSL (Short, Short, Short, Long — repeating) |
| Optimizer | MuonAdamW (Muon for matrices, AdamW for embeddings/scalars) |
| Time budget | 5 minutes |
| Tokens trained | ~500M |
| GPU | Single NVIDIA (tested on H100) |
| Peak VRAM | ~45GB |
| MFU (Model FLOPs Utilization) | ~39.8% |

### Notable Technical Features in the Baseline
- **ResFormer (Value Residual):** Each attention layer has a value embedding that gets mixed in via an input-dependent gate. The gate is a learned linear projection from a small slice of the hidden state.
- **Rotary Embeddings (RoPE):** Precomputed up to `sequence_len * 10`, cast to bf16.
- **Sliding Window Attention (SSSL pattern):** Alternating short (half-context) and long (full-context) attention windows for memory efficiency.
- **Muon optimizer:** Newton-Schulz iteration (Polar Express) for orthogonalization + Nesterov momentum + variance reduction. Specifically designed for training 2D matrix parameters (linear layers).
- **Per-layer scalars:** `resid_lambdas` and `x0_lambdas` — learned scalars that control how much each layer mixes residual and initial signals.
- **Soft-capped logits:** `softcap = 15` with `tanh` to prevent extreme logits.
- **LR warmup=0%, warmdown=50%:** Cooldown half the schedule to final LR fraction.
- **Weight decay decays linearly** from initial value to 0 over training.

---

## Setup Tutorial

### Prerequisites
- Single NVIDIA GPU (tested on H100; works on A100, 3090, 4090 with tuning)
- Python 3.10+
- `uv` package manager

### Step 1 — Clone the Repo

```bash
git clone https://github.com/karpathy/autoresearch.git
cd autoresearch
```

### Step 2 — Install `uv` (if you don't have it)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 3 — Install Dependencies

```bash
uv sync
```

### Step 4 — One-Time Data Prep (~2 minutes)

```bash
uv run prepare.py
```

This downloads the training data, trains a BPE tokenizer, and sets up data loaders. Output goes to `~/.cache/autoresearch/`.

### Step 5 — Manual Baseline Run (~5 minutes)

```bash
uv run train.py
```

You should see output like:

```
val_bpb:          0.997900
training_seconds: 300.1
total_seconds:    325.9
peak_vram_mb:     45060.2
mfu_percent:      39.80
total_tokens_M:   499.6
num_steps:        953
num_params_M:     50.3
depth:            8
```

If this works, your setup is verified. ✅

### Step 6 — Autonomous Research Mode

Now spin up your favorite AI coding agent in the repo directory. Karpathy suggests:

> *"Hi, have a look at program.md and let's kick off a new experiment! Let's do the setup first."*

Disable all permissions in the agent (no asking for confirmation, no human-in-the-loop).

The agent will:
1. Create a dated branch: `git checkout -b autoresearch/mar30`
2. Create `results.tsv` with headers
3. Run the baseline
4. Begin the loop: edit → commit → train → eval → keep/discard → repeat

**The agent runs until you manually stop it.** It will not pause to ask permission.

### How to Monitor Progress

```bash
# Watch experiment results as they accumulate
cat results.tsv

# Check the git log of experiments
git log --oneline

# Watch the raw training output
tail -f run.log
```

---

## program.md — The Research Agent's Brain

`program.md` is the most important file for getting good results. It's essentially a **prompt/skill** that defines the agent's entire research behavior. The baseline is deliberately minimal — the key to getting better results is iterating on this file.

Key sections in `program.md`:

- **Setup:** Create dated branch, verify data exists, init `results.tsv`
- **Scope:** Only modify `train.py`. Never touch `prepare.py`.
- **Constraints:** No new packages. Fixed 5-min time budget. VRAM is a soft constraint.
- **Simplicity criterion:** Small improvements that add complexity are not worth it. Deleting code for equal/better results is a win.
- **Loop:** Edit → commit → `uv run train.py > run.log 2>&1` → grep results → log to TSV → keep if val_bpb improved, revert if not.
- **Crash handling:** Easy fixes → re-run. Fundamentally broken ideas → skip, log as "crash", move on.
- **NEVER STOP:** Do not ask the human if you should continue. Run until manually stopped.

### Iterating on program.md (For Humans)

Since `program.md` is the only thing the human directly controls, optimizing it is the meta-research problem. Ideas for iteration:

- Add specific architecture hints (e.g., "try Grouped Query Attention")
- Add optimizer suggestions (e.g., "try decreasing weight decay by 0.05 per experiment")
- Add references to papers the agent should read
- Refine the simplicity criterion thresholds
- Add "exploration vs exploitation" strategies
- Add constraints based on your hardware (e.g., max VRAM)

---

## Fork Recommendations for Non-H100 Hardware

Autoresearch was designed for H100-scale GPUs. For smaller hardware:

### Official Forks
| Fork | Platform | Link |
|------|----------|------|
| miolini/autoresearch-macos | MacOS | GitHub |
| trevin-creator/autoresearch-mlx | MacOS (MLX) | GitHub |
| jsegov/autoresearch-win-rtx | Windows (RTX) | GitHub |
| andyluo7/autoresearch | AMD | GitHub |

### Tuning Guide for Small Hardware (MacBooks, etc.)

If running on a MacBook or consumer GPU, Karpathy recommends:

1. **Dataset:** Use [TinyStories](https://huggingface.co/datasets/karpathy/tinystories-gpt4-clean) instead — much less entropy, good results with smaller models.
2. **Vocab size:** Decrease from 8192 → 4096 → 2048 → 1024 → 256 (byte-level).
3. **Sequence length:** Lower `MAX_SEQ_LEN` in `prepare.py` — even down to 256 on very small devices.
4. **Depth:** Lower `DEPTH` in `train.py` from 8 → 4 or lower.
5. **Window pattern:** Use `"L"` (full attention) instead of `"SSSL"` — banded attention may be inefficient on small hardware.
6. **Batch size:** Lower `TOTAL_BATCH_SIZE`, keep powers of 2 (e.g., down to `2**14` ~16K).
7. **Eval tokens:** Lower `EVAL_TOKENS` in `prepare.py` to reduce eval time.

---

## Key Hyperparameters to Understand

| Hyperparameter | Default | What It Controls |
|----------------|---------|------------------|
| `DEPTH` | 8 | Model depth (n_layer) |
| `ASPECT_RATIO` | 64 | `model_dim = depth * aspect_ratio` |
| `HEAD_DIM` | 128 | Attention head dimension |
| `WINDOW_PATTERN` | "SSSL" | Sliding window pattern (L=full, S=half) |
| `TOTAL_BATCH_SIZE` | 2^19 (~524K) | Tokens per optimizer step |
| `DEVICE_BATCH_SIZE` | 128 | Per-GPU batch size |
| `EMBEDDING_LR` | 0.6 | LR for token embeddings (Adam) |
| `UNEMBEDDING_LR` | 0.004 | LR for lm_head (Adam) |
| `MATRIX_LR` | 0.04 | LR for linear layers (Muon) |
| `SCALAR_LR` | 0.5 | LR for per-layer scalars |
| `WEIGHT_DECAY` | 0.2 | Muon weight decay (decays to 0) |
| `WARMUP_RATIO` | 0.0 | LR warmup fraction (0 = no warmup) |
| `WARMDOWN_RATIO` | 0.5 | LR warmdown fraction |
| `FINAL_LR_FRAC` | 0.0 | Final LR as fraction of initial |

---

## 20 Use Case Ideas

### Architecture Exploration
1. **GQA Search** — Have the agent try different `n_kv_head` ratios (e.g., 1, 2, 4 KV heads vs 6 query heads). Find the optimal KV head count for your hardware.
2. **Window Pattern Evolution** — Test SSSL, SSLL, SLSL, SL, LLLL, and novel patterns. Discover which attention sparsity pattern works best for your data.
3. **Depth vs Width Sweep** — Systematically explore depth/width tradeoffs by varying `DEPTH` and `ASPECT_RATIO` together. Find the optimal model shape for your time budget.
4. **Activation Function Hunt** — Try SwiGLU, GeLU, SiLU, ReLU, GeGLU, etc. Discover which works best with Muon.
5. **Initialization Strategy** — Experiment with different weight init schemes (zero-init, small-init, scaled-init). Some interact very differently with Muon.

### Optimization & Training
6. **Learning Rate Landscape** — Sweep embedding LR, matrix LR, and unembedding LR. Find optimal LR scaling for your hardware.
7. **Weight Decay Trajectory** — Try different `WEIGHT_DECAY` values and warmdown schedules. Muon is sensitive to weight decay.
8. **Batch Size Scaling** — Test larger/smaller `DEVICE_BATCH_SIZE` + `TOTAL_BATCH_SIZE` combos. Larger = fewer steps, smaller = more steps in the same time.
9. **Muon Momentum Tuning** — The optimizer uses Nesterov momentum. Explore momentum schedules beyond the built-in `get_muon_momentum()`.
10. **Warmup/Warmdown Ratios** — Try adding LR warmup (default is 0%). Find optimal schedules for different model sizes.

### Model Capabilities
11. **Context Length Scaling** — Modify `MAX_SEQ_LEN` (requires re-running `prepare.py`) and see how the agent adapts architecture for longer contexts.
12. **Vocabulary Engineering** — Experiment with vocab size (lower = more compression, higher = less compression). Try byte-level (256) vs BPE.
13. **Value Embedding Variations** — The ResFormer value embeddings are a unique feature. Try different `ve_gate_channels` sizes or gate architectures.
14. **Per-Layer Scalar Tuning** — The `resid_lambdas` and `x0_lambdas` are learnable. Explore whether constraining or freezing them helps.
15. **Softmax vs Alternatives** — Try different attention softmax temperatures or alternatives like softmax/kernel methods.

### Research Infrastructure
16. **program.md Meta-Optimization** — This is the meta-use-case: iterate on the agent's instructions to make it a better researcher. Add paper references, refine the simplicity criterion, add exploration strategies.
17. **Multi-Objective Search** — Modify the evaluation to weigh val_bpb + VRAM usage + FLOPs. Find Pareto-optimal architectures.
18. **Dataset-Specific Tuning** — Point autoresearch at different datasets (TinyStories, Shakespeare, code, math) and discover what architectures work best for each domain.
19. **Distributed Autoresearch (Multi-GPU)** — Fork and extend to multi-GPU. Have agents collaborate on finding optimal shard/distribution strategies.
20. **Agent Team Research** — Run multiple agents with different `program.md` personalities (conservative vs radical, architecture-focused vs optimizer-focused) and compare their research trajectories.

### Fun/Beyond-Baseline
- **No-Op Baseline Experiments** — Try deleting half the MLP layers, removing value embeddings, or ablating attention heads. See what actually matters.
- **Weird Architecture Ideas** — Let the agent try things humans might not think of: non-standard depth/width ratios, mixed head dimensions, hybrid attention patterns.
- **Overnight Benchmarking** — Run autoresearch for 8 hours (~96 experiments) and plot the val_bpb curve. Watch the agent discover diminishing returns.
- **Branch Archaeology** — Use `git log --oneline` to trace which changes the agent kept vs discarded. Learn what actually helps vs what looked promising but didn't.

---

## What Makes This Interesting (For LLM Engineers)

### It's a Skill, Not a Framework

`program.md` is essentially a **skill definition** — a natural language description of a task that an AI agent executes. This is the same pattern as OpenClaw skills. The entire "research org" fits in a markdown file.

### The Agentic Loop is Clean

```
EDIT train.py → GIT COMMIT → TRAIN (5 min) → EVAL → LOG →
KEEP (val_bpb improved) or REVERT (val_bpb worse) → REPEAT
```

No complex multi-agent orchestration. No external orchestration. Just: edit, test, keep/discard.

### The 5-Minute Budget is Elegant

By fixing the time budget instead of the number of steps, architectural changes are fairly compared. A larger model that trains slower but converges better in 5 minutes can be compared to a smaller model that trains faster. The agent discovers what's optimal for *your specific hardware*.

### Simplicity as a Loss Term

The explicit simplicity criterion — *"small improvement + complexity = discard"* — is a form of regularization. It's encoding the principle that elegance matters, not just raw performance.

### Karpathy's Vision: SETI@home for AI Research

> *"The next step for autoresearch is that it has to be asynchronously massively collaborative for agents (think: SETI@home style). The goal is not to emulate a single PhD student, it's to emulate a research community of them."*

The next evolution is distributed: many agents across many GPUs, all exploring different branches of the architecture/optimizer space, accumulating commits, with a community-wide "fleet registry" of patterns that work.

---

## File Structure

```
autoresearch/
├── README.md          # Overview + setup
├── prepare.py         # Data prep, tokenizer, eval harness (DO NOT MODIFY)
├── train.py           # Model, optimizer, training loop (AGENT MODIFIES)
├── program.md         # Agent instructions (HUMAN ITERATES)
├── pyproject.toml     # Dependencies
├── kernels/           # Flash Attention kernels
└── .cache/autoresearch/  # Training data + tokenizer (generated by prepare.py)
```

---

## References

- **Repo:** https://github.com/karpathy/autoresearch
- **Karpathy's launch tweet:** https://x.com/karpathy/status/2029701092347630069
- **Follow-up on multi-agent vision:** https://x.com/karpathy/status/2031135152349524125
- **Community guide:** https://openrepoguide.com/
- **DataCamp tutorial:** https://www.datacamp.com/tutorial/guide-to-autoresearch
- **nanochat (parent repo):** https://github.com/karpathy/nanochat
- **TinyStories dataset (for small hardware):** https://huggingface.co/datasets/karpathy/tinystories-gpt4-clean

---

*Generated: 2026-03-30*
