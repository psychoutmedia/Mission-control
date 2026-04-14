# MLOps for LLMs — Research Notes

## TL;DR

LLMOps ≠ MLOps. LLMs break traditional MLOps assumptions:
- **Discrete artifact** → continuous foundation model
- **Clear metrics** → fuzzy, multi-dimensional eval
- **One-off training** → RLHF, fine-tuning, prompt iteration loops
- **Model-centric** → data + prompt + infra equally important

---

## The Core LLMOps Stack

### 1. Experiment Tracking

| Tool | Best For | Cost | Self-Host | LLM-Specific |
|------|----------|------|-----------|--------------|
| **MLflow** |通用, open source | Free | ✓ | Via LangChain integration |
| **Weights & Biases** |Research teams | Free tier, $15/user/mo | Limited | ✓ Native LLM monitoring |
| **Neptune** |Structured experiments | Free tier, $99/mo | ✓ | Good for fine-tuning |
| **Aim** |Open-source, local | Free | ✓ | LLM-specific views |
| **ClearML** |Auto ML, pipeline-heavy | Free tier | ✓ | Agent orchestration |
| **Comet** |LLM evals | Free tier | ✓ | Strong for LLM comparison |
| **MLtraq** |High-throughput benchmarks | Free | ✓ | Fastest for large runs |

**Recommendation for personal projects:** MLflow (free, self-hosted) + Aim (local, LLM-native UI)

### 2. Data Versioning

**DVC (Data Version Control)**
- Git-like versioning for data, models, experiments
- Works with S3/GCS/HDFS storage backends
- Integrates with MLflow for pipeline tracking
- Essential for LLM: version training corpora, prompt datasets, eval sets

```bash
pip install dvc
dvc init
dvc remote add -d storage s3://my-llm-bucket
dvc add data/train.jsonl
git add data/train.jsonl.dvc
git commit -m "Add training data v2"
```

**Alternatives:** Pachyderm (K8s-native), Dolt (SQL with versioning), lakeFS (Git for data lakes)

### 3. Model Registry & Artifact Management

**MLflow Model Registry**
- Central hub for model versioning, stage transitions (staging → production)
- Model lineage tracking
- API serving integration

```python
import mlflow

# Log model with metrics
with mlflow.start_run():
    mlflow.log_params({"model": "llama-3", "lr": 2e-5})
    mlflow.log_metrics({"accuracy": 0.92})
    mlflow.pyfunc.log_model("llm_classifier", predict_fn)

# Register and transition
client = mlflow.MlflowClient()
client.register_model("runs:/abc/llm_classifier", "production-v1")
client.transition_model_version_stage("production-v1", stage="Production")
```

### 4. Fine-Tuning Pipelines

**Axolotl** — Multi-framework fine-tuning (LoRA, QLoRA, full fine-tune)
**Unsloth** — 2x faster LoRA fine-tuning, 30% less memory
**PEFT** (HuggingFace) — Parameter-efficient fine-tuning abstractions
**LLaMA Factory** — All-in-one fine-tuning platform

### 5. Prompt Engineering & A/B Testing

**Prompt Management:**
- **PromptLayer** / **Helicone** — Track LLM API calls, version prompts, measure latency
- **Weights & Biases Weave** — LLM evals, trace prompts, structured feedback
- **LangSmith** — Comprehensive LLM app debugging and monitoring

**A/B Testing Prompts:**
```python
# Example: Prompt A/B with tracking
variants = {
    "prompt_v1": "Explain {topic} simply.",
    "prompt_v2": "Explain {topic} to a 10-year-old."
}

for variant_name, prompt_template in variants.items():
    response = llm.invoke(prompt_template.format(topic=topic))
    wandb.log({f"{variant_name}_response": response})
```

### 6. Evaluation & Benchmarks

LLM eval is multi-dimensional — no single metric works:

| Aspect | Tools | Metrics |
|--------|-------|---------|
| **Automated Benchmarks** | lm-evaluation-harness, EleutherAI | MMLU, HellaSwag, TruthfulQA |
| **Human Preference** | Scale AI, Argilla | Win rate, preference score |
| **ROUGE/BLEU** | ragas, langchain-evaluate | N-gram overlap |
| **LLM-as-Judge** | Prometheus, GPTScore | 1-5 rating, pairwise comparison |
| **Custom Evals** | BigRouter, custom harness | Domain-specific tests |

**Key insight:** RAGAS score = faithfulness + answer relevance + context relevance

### 7. Deployment & Inference

| Tool | Use Case | Self-Host |
|------|----------|-----------|
| **vLLM** | High-throughput inference | ✓ |
| **TensorRT-LLM** | Optimized NVIDIA inference | ✓ |
| **Ollama** | Local LLM serving | ✓ |
| **TGI (Text Generation Inference)** | HuggingFace official | ✓ |
| **Anyscale Endpoints** | Managed LLM API | ✗ |
| **SageMaker, Vertex AI** | Enterprise cloud | ✗ |

### 8. Observability & Monitoring

LLM-specific metrics beyond standard ML:

```
- Token usage & cost tracking
- Latency per request / time-to-first-token
- Token throughput (tokens/sec)
- Cache hit rate
- Prompt/response length distributions
- Error rates by model/prompt
- Hallucination detection signals
- User feedback signals (thumbs up/down)
- Drift detection (input distribution shifts)
```

**Tools:** Weights & Biases Weave, LangSmith, Phoenix (Arize), Helicone, PromptLayer

### 9. CI/CD for LLMs

**Continuous Training Triggers:**
- Data drift detected → retrain
- New eval benchmarks released → re-eval
- New base model available → fine-tune comparison

**Pipeline Tools:**
- **Kubeflow** — Full ML pipelines on K8s
- **ZenML** — MLOps framework, stack-agnostic
- **Metaflow** — Netflix's ML framework, great for experiments
- **Prefect** — Python-native workflow orchestration
- **Dagster** — Modern data pipeline, strong type safety

### 10. Infrastructure

| Component | Options |
|-----------|---------|
| **Compute** | Lambda Labs, RunPod, Vast.ai, AWS EC2, GCP |
| **Storage** | S3, GCS, HuggingFace Hub, Weights & Biases artifacts |
| **Container** | Docker, Singularity (for HPC) |
| **Orchestration** | Kubernetes (via Ray, Spark), Slurm |

---

## LLMOps Workflow (2026)

```
1. Data Collection & Versioning
   └─ DVC + HuggingFace Datasets

2. Prompt Experimentation  
   └─ Weights & Biases Weave / LangSmith
   └─ A/B test prompts, track metrics

3. Fine-Tuning Pipeline
   └─ Axolotl / Unsloth + PEFT
   └─ Track with MLflow

4. Evaluation
   └─ lm-evaluation-harness + RAGAS + LLM-as-judge
   └─ Register best model in MLflow Registry

5. Deployment
   └─ vLLM / Ollama / TGI
   └─ Containerize with Docker

6. Monitoring & Feedback
   └─ Helicone + LangSmith
   └─ Collect user feedback → RLHF loop

7. Continuous Improvement
   └─ Argilla for human-in-the-loop labeling
   └─ Trigger fine-tuning on drift/feedback
```

---

## Key Differences: MLOps vs LLMOps

| Aspect | Traditional MLOps | LLMOps |
|--------|-------------------|--------|
| Model Size | MB | GB (上百GB for large models) |
| Training Frequency | Periodic retrain | Continuous prompt tuning |
| Evaluation | Single metric (accuracy) | Multi-dimensional (safety, helpfulness, hallucination) |
| Data | Structured tabular | Unstructured text, multimodal |
| Infrastructure | CPU/GPU | Multi-GPU, tensor parallelism |
| Cost | $100s-1000s | $10,000s-100,000s+ |
| Versioning | Model weights | + Prompts + RAG contexts + RLHF data |

---

## Tool Recommendations by Use Case

**Solo dev / personal projects:**
- MLflow (tracking) + DVC (data) + Ollama (inference) + Weights & Biases (weave for LLM monitoring)
- Total cost: Free (except W&B optional)

**Startup / small team:**
- Weights & Biases (full stack) + Weave (LLM monitoring) + vLLM (inference)
- Axolotl for fine-tuning
- LangSmith for RAG evaluation

**Enterprise:**
- SageMaker / Vertex AI + Kubeflow + MLflow (centralized)
- Weights & Biases Enterprise + Scale AI for labeling
- Vertex AI Agent Builder for RAG

---

## Security Considerations

- **PII scrubbing** before training on user data
- **API key rotation** for LLM provider access
- **Rate limiting** to prevent prompt injection attacks
- **Input/output logging** for compliance (GDPR, etc.)
- **Model access controls** — who can fine-tune vs read-only

---

## Next Steps for Personal Stack

Based on current projects (Ollama + RAG + agent systems):

1. **Install DVC** — add to projects/ for data versioning
2. **Set up MLflow locally** — track all fine-tuning experiments
3. **Add Weights & Biases Weave** — monitor Ollama LLM calls
4. **Integrate lm-evaluation-harness** — standardized LLM benchmarks
5. **Build evaluation pipeline** for timecode_agent and SIAM

---

## Resources

- [MLflow docs](https://mlflow.org/docs/latest/index.html)
- [DVC getting started](https://dvc.org/doc/start)
- [Axolotl fine-tuning](https://github.com/OpenAccess-AI-Collective/axolotl)
- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- [Weights & Biases LLM monitoring](https://wandb.ai/solutions/llm)
- [LLMOps landscape 2026](https://lakefs.io/mlops/mlops-tools/)
