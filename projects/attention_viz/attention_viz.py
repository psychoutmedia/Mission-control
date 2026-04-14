"""
Attention Visualization Tool
============================
Visualize attention patterns in transformer models.

Supports:
- Hooking into attention layers to capture attention weights
- Heatmap rendering of attention across heads and layers
- Comparison of attention before/after fine-tuning
"""

import torch
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from typing import Optional
import seaborn as sns

sns.set_style("whitegrid")


class AttentionVisualizer:
    """
    Captures and visualizes attention patterns from transformer models.

    Works with any model that uses torch.nn.MultiheadAttention
    or has attention weights accessible via .attentions.
    """

    def __init__(self, model: Optional[torch.nn.Module] = None):
        self.model = model
        self.attention_weights = {}  # layer_idx -> (batch, heads, seq, seq)
        self.tokens = None
        self.hooks = []

    # ─────────────────────────────────────────────────────────
    # Hooking Mechanism
    # ─────────────────────────────────────────────────────────

    def register_hooks(self, layer_indices: Optional[list] = None):
        """
        Register forward hooks on attention layers to capture weights.

        Args:
            layer_indices: Which layers to hook. None = all attention layers.
        """
        if self.model is None:
            raise ValueError("No model set. Pass model to __init__ or set_model().")

        self.hooks = []
        layer_idx = 0

        for name, module in self.model.named_modules():
            if "attention" in name.lower() or "attn" in name.lower():
                if layer_indices is None or layer_idx in layer_indices:
                    hook = module.register_forward_hook(self._hook_fn(layer_idx))
                    self.hooks.append((name, hook))
                layer_idx += 1

        print(f"Registered {len(self.hooks)} attention hooks on layers: "
              f"{[name for name, _ in self.hooks]}")

    def _hook_fn(self, layer_idx: int):
        """Factory for hook functions that capture attention weights."""
        def hook_fn(module, input, output):
            # output is (attn_output, attn_weights) for MultiheadAttention
            # For HuggingFace models: output[1] contains attention weights
            if isinstance(output, tuple) and len(output) > 1:
                attn_weights = output[1]  # (batch, heads, seq, seq)
            else:
                attn_weights = output
            self.attention_weights[layer_idx] = attn_weights.detach().cpu()
        return hook_fn

    def remove_hooks(self):
        """Remove all registered hooks."""
        for name, hook in self.hooks:
            hook.remove()
        self.hooks = []
        self.attention_weights = {}

    # ─────────────────────────────────────────────────────────
    # Forward Pass with Token Tracking
    # ─────────────────────────────────────────────────────────

    @torch.no_grad()
    def run(self, input_ids: torch.LongTensor, tokens: Optional[list] = None):
        """
        Run a forward pass and capture attention weights.

        Args:
            input_ids: Token IDs, shape (batch, seq_len)
            tokens: List of token strings for labeling axes
        """
        if self.model is None:
            raise ValueError("No model set.")

        self.attention_weights = {}
        self.tokens = tokens or [f"tok_{i}" for i in range(input_ids.shape[1])]

        _ = self.model(input_ids)

    # ─────────────────────────────────────────────────────────
    # Visualization
    # ─────────────────────────────────────────────────────────

    def plot_attention_heatmap(
        self,
        layer: int = 0,
        head: Optional[int] = None,
        tokens: Optional[list] = None,
        figsize: tuple = (12, 10),
        cmap: str = "Blues",
        title: Optional[str] = None,
        save_path: Optional[str] = None,
    ):
        """
        Plot attention heatmap for a specific layer (all heads or one head).

        Args:
            layer: Which layer to visualize
            head: Which head to visualize. None = average across heads.
            tokens: Token labels for x/y axes
            figsize: Figure size
            cmap: Colormap
            title: Custom title
            save_path: Where to save the figure
        """
        if layer not in self.attention_weights:
            raise ValueError(f"No attention captured for layer {layer}. Run run() first.")

        # Shape: (batch, heads, seq, seq) → take batch 0
        weights = self.attention_weights[layer][0]  # (heads, seq, seq)

        if head is not None:
            # Single head
            attn = weights[head].numpy()
            label = f"Layer {layer}, Head {head}"
        else:
            # Average across heads
            attn = weights.mean(dim=0).numpy()
            label = f"Layer {layer} (avg across {weights.shape[0]} heads)"

        tokens = tokens or self.tokens or [f"{i}" for i in range(attn.shape[0])]

        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(
            attn,
            xticklabels=tokens,
            yticklabels=tokens,
            cmap=cmap,
            ax=ax,
            cbar_kws={"label": "Attention Weight"},
        )
        ax.set_xlabel("Key Tokens")
        ax.set_ylabel("Query Tokens")
        ax.set_title(title or f"Attention Heatmap — {label}")
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved: {save_path}")

        plt.show()
        return fig

    def plot_all_heads(
        self,
        layer: int = 0,
        tokens: Optional[list] = None,
        figsize: Optional[tuple] = None,
        save_path: Optional[str] = None,
    ):
        """
        Plot a grid of all attention heads for a given layer.

        Each subplot = one attention head.
        """
        if layer not in self.attention_weights:
            raise ValueError(f"No attention captured for layer {layer}. Run run() first.")

        weights = self.attention_weights[layer][0]  # (heads, seq, seq)
        n_heads = weights.shape[0]
        seq_len = weights.shape[1]

        # Auto-size grid
        n_cols = min(4, n_heads)
        n_rows = (n_heads + n_cols - 1) // n_cols
        figsize = figsize or (4 * n_cols, 3.5 * n_rows)

        tokens = tokens or self.tokens or [f"{i}" for i in range(seq_len)]

        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = np.atleast_2d(axes)

        for h in range(n_heads):
            row, col = h // n_cols, h % n_cols
            ax = axes[row, col]
            attn = weights[h].numpy()
            sns.heatmap(
                attn,
                xticklabels=[],
                yticklabels=[],
                cmap="Blues",
                ax=ax,
                cbar=False,
            )
            ax.set_title(f"Head {h}", fontsize=10)

        # Hide empty subplots
        for h in range(n_heads, n_rows * n_cols):
            row, col = h // n_cols, h % n_cols
            axes[row, col].axis("off")

        fig.suptitle(f"Layer {layer} — All {n_heads} Attention Heads", fontsize=14)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved: {save_path}")

        plt.show()
        return fig

    def plot_token_attention(
        self,
        token_idx: int,
        layer: Optional[int] = None,
        tokens: Optional[list] = None,
        figsize: tuple = (10, 6),
        save_path: Optional[str] = None,
    ):
        """
        Plot how a specific token attends to all other tokens across layers/heads.

        Shows attention FROM token_idx TO all other positions.
        Useful for understanding what each token "looks at".
        """
        tokens = tokens or self.tokens or [f"{i}" for i in range(100)]
        n_layers = len(self.attention_weights)

        if layer is not None:
            # Single layer, all heads averaged
            weights = self.attention_weights[layer][0].mean(dim=0).numpy()
            attn_to_plot = weights[token_idx]
            fig, ax = plt.subplots(figsize=figsize)
            ax.bar(range(len(attn_to_plot)), attn_to_plot, color="steelblue")
            ax.set_xlabel("Key Token")
            ax.set_ylabel("Attention Weight")
            ax.set_title(f"Token '{tokens[token_idx]}' attends to (Layer {layer}, avg heads)")
            ax.set_xticks(range(len(tokens)))
            ax.set_xticklabels(tokens, rotation=45, ha="right", fontsize=8)
            plt.tight_layout()
        else:
            # All layers, heads averaged
            fig, axes = plt.subplots(1, n_layers, figsize=(4 * n_layers, 5), sharey=True)
            axes = np.atleast_1d(axes)

            for li, (layer_idx, weights) in enumerate(sorted(self.attention_weights.items())):
                w = weights[0].mean(dim=0).numpy()[token_idx]
                axes[li].bar(range(len(w)), w, color="steelblue")
                axes[li].set_title(f"Layer {layer_idx}")
                axes[li].set_xlabel("Key Token")
                if li == 0:
                    axes[li].set_ylabel("Attention Weight")

            fig.suptitle(f"Token '{tokens[token_idx]}' attends across all layers", fontsize=14)
            plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved: {save_path}")

        plt.show()
        return fig


# ─────────────────────────────────────────────────────────
# Demo with a small transformer
# ─────────────────────────────────────────────────────────

def demo_small_transformer():
    """
    Demo using a tiny custom transformer on a simple sequence.
    Shows how to hook, capture, and visualize attention.
    """
    import torch.nn as nn

    # Tiny transformer for demonstration
    model = nn.TransformerEncoder(
        nn.TransformerEncoderLayer(
            d_model=64,
            nhead=4,
            dim_feedforward=128,
            batch_first=True,
        ),
        num_layers=2,
    )
    model.eval()

    viz = AttentionVisualizer(model)
    viz.register_hooks()

    # Simple sentence
    tokens = ["The", "cat", "sat", "down", "and", "slept", "well", "."]
    seq_len = len(tokens)

    # Dummy token IDs
    input_ids = torch.randint(0, 100, (1, seq_len))

    viz.run(input_ids, tokens=tokens)

    print(f"\nCaptured attention from {len(viz.attention_weights)} layers")
    for layer, w in viz.attention_weights.items():
        print(f"  Layer {layer}: {w.shape} — {w.shape[1]} heads, seq_len={w.shape[2]}")

    # Visualize
    viz.plot_attention_heatmap(layer=0, title="Layer 0 Attention (avg heads)")
    viz.plot_all_heads(layer=0, tokens=tokens)
    viz.plot_token_attention(token_idx=1, tokens=tokens)  # "cat" attends

    viz.remove_hooks()
    return viz


if __name__ == "__main__":
    print("=" * 60)
    print("ATTENTION VISUALIZATION TOOL — Demo")
    print("=" * 60)
    demo_small_transformer()
