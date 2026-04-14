"""
TransformerDataLoader — Custom PyTorch DataLoader for transformer training.

Features:
- Masked Language Modeling (MLM) with [MASK] token handling
- Dynamic padding (pad to batch max, or fixed max_length)
- Attention mask generation (1 for real tokens, 0 for padding)
- Token type segment IDs (for BERT-style models)
- Position encoding support (absolute + relative)
- Batched sequence packing with efficient collation

Author: Astra | Automa Dynamics
"""

from __future__ import annotations

import torch
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Callable, Dict, Any
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer


@dataclass
class TransformerBatch:
    """Container for a single batch of transformer inputs."""
    input_ids: torch.Tensor          # [batch_size, seq_len]
    attention_mask: torch.Tensor      # [batch_size, seq_len] — 1 for tokens, 0 for padding
    token_type_ids: Optional[torch.Tensor] = None  # [batch_size, seq_len] — segment ids
    position_ids: Optional[torch.Tensor] = None    # [batch_size, seq_len] — position indices
    labels: Optional[torch.Tensor] = None           # [batch_size, seq_len] — for MLM

    def to(self, device: torch.device) -> "TransformerBatch":
        return TransformerBatch(
            input_ids=self.input_ids.to(device),
            attention_mask=self.attention_mask.to(device),
            token_type_ids=self.token_type_ids.to(device).to(device) if self.token_type_ids is not None else None,
            position_ids=self.position_ids.to(device) if self.position_ids is not None else None,
            labels=self.labels.to(device) if self.labels is not None else None,
        )


@dataclass
class DataLoaderConfig:
    """Configuration for TransformerDataLoader."""
    tokenizer: str = "bert-base-uncased"
    max_length: int = 512
    pad_to_multiple_of: Optional[int] = None  # e.g., 8 for tensor core optimization
    mask_prob: float = 0.15  # Probability of replacing a token with [MASK]
    random_prob: float = 0.1  # Of masked tokens, % replaced with random token
    keep_prob: float = 0.1    # Of masked tokens, % kept as-is
    label_all_tokens: bool = False  # For token classification (NER, etc.)
    use_fast_tokenizer: bool = True


class MLMCollator:
    """
    Collate function for Masked Language Modeling (BERT-style training).
    
    Given raw token IDs, applies random masking and produces:
    - input_ids: tokens with some replaced by [MASK]
    - labels: original tokens (cross-entropy loss ignores -100 padding)
    - attention_mask: 1 for real, 0 for padding
    - token_type_ids: all 0s (single segment)
    """

    def __init__(
        self,
        tokenizer: AutoTokenizer,
        max_length: int = 512,
        mask_prob: float = 0.15,
        random_prob: float = 0.1,
        keep_prob: float = 0.1,
        pad_to_multiple_of: Optional[int] = None,
        label_ignore_index: int = -100,
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.mask_prob = mask_prob
        self.random_prob = random_prob
        self.keep_prob = keep_prob
        self.pad_to_multiple_of = pad_to_multiple_of
        self.label_ignore_index = label_ignore_index

        # Token IDs
        self.mask_token_id = tokenizer.mask_token_id
        self.pad_token_id = tokenizer.pad_token_id
        self.cls_token_id = tokenizer.cls_token_id
        self.sep_token_id = tokenizer.sep_token_id

    def __call__(self, batch: List[Dict[str, Any]]) -> TransformerBatch:
        """
        Args:
            batch: List of dicts, each with at least 'input_ids' or 'text'
        Returns:
            TransformerBatch with MLM fields populated
        """
        # Tokenize if raw text provided
        if "input_ids" not in batch[0]:
            texts = [item["text"] for item in batch]
            encoded = self.tokenizer(
                texts,
                max_length=self.max_length,
                padding="longest",  # Dynamic padding per batch
                truncation=True,
                return_tensors="pt",
            )
            input_ids = encoded["input_ids"]
            attention_mask = encoded["attention_mask"]
            token_type_ids = encoded.get("token_type_ids")
        else:
            input_ids = torch.stack([torch.tensor(item["input_ids"]) for item in batch])
            attention_mask = torch.stack([
                torch.tensor(item.get("attention_mask", [1] * len(item["input_ids"]))) 
                for item in batch
            ])
            token_type_ids = None
            if "token_type_ids" in batch[0]:
                token_type_ids = torch.stack([
                    torch.tensor(item["token_type_ids"]) for item in batch
                ])

        # Apply random masking
        masked_input_ids, labels = self._apply_mask(input_ids)

        # Dynamic padding to max length in batch (or fixed)
        if self.pad_to_multiple_of:
            pad_len = self.pad_to_multiple_of - (masked_input_ids.size(1) % self.pad_to_multiple_of)
            if pad_len != self.pad_to_multiple_of:
                padded = torch.full(
                    (masked_input_ids.size(0), masked_input_ids.size(1) + pad_len),
                    self.pad_token_id,
                    dtype=masked_input_ids.dtype,
                )
                padded[:, :masked_input_ids.size(1)] = masked_input_ids
                masked_input_ids = padded

                padded_labels = torch.full(
                    (labels.size(0), labels.size(1) + pad_len),
                    self.label_ignore_index,
                    dtype=labels.dtype,
                )
                padded_labels[:, :labels.size(1)] = labels
                labels = padded_labels

                padded_mask = torch.zeros_like(padded)
                padded_mask[:, :attention_mask.size(1)] = attention_mask
                attention_mask = padded_mask

        # Position IDs
        position_ids = torch.arange(
            masked_input_ids.size(1), dtype=torch.long
        ).unsqueeze(0).expand(masked_input_ids.size(0), -1)

        return TransformerBatch(
            input_ids=masked_input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            labels=labels,
        )

    def _apply_mask(self, input_ids: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Apply random masking to input_ids.
        
        Returns:
            masked_input_ids: input with some tokens replaced
            labels: original tokens at masked positions, -100 elsewhere
        """
        labels = input_ids.clone()
        
        # Probability matrix for masking
        probability_matrix = torch.full(input_ids.shape, self.mask_prob)
        
        # Don't mask special tokens (cls, sep, pad)
        special_tokens_mask = (
            (input_ids == self.cls_token_id) |
            (input_ids == self.sep_token_id) |
            (input_ids == self.pad_token_id)
        )
        probability_matrix.masked_fill_(special_tokens_mask, value=0.0)

        # Sample masking
        masked_indices = torch.bernoulli(probability_matrix).bool()
        labels[~masked_indices] = self.label_ignore_index  # Only compute loss on masked

        # Of masked tokens: 80% [MASK], 10% random, 10% original
        masked_input_ids = input_ids.clone()
        
        mask_token_mask = masked_indices & (torch.rand(input_ids.shape) < 0.8)
        random_token_mask = masked_indices & ~mask_token_mask & (torch.rand(input_ids.shape) < (self.random_prob / (self.random_prob + self.keep_prob)))
        keep_mask = masked_indices & ~mask_token_mask & ~random_token_mask

        # Apply [MASK]
        masked_input_ids[mask_token_mask] = self.mask_token_id

        # Apply random token
        vocab_size = self.tokenizer.vocab_size
        random_mask = random_token_mask.nonzero(as_tuple=True)[0]
        if len(random_mask) > 0:
            random_tokens = torch.randint(0, vocab_size, (len(random_mask),), dtype=torch.long)
            masked_input_ids[random_token_mask] = random_tokens

        return masked_input_ids, labels


class TextDataset(Dataset):
    """
    Simple text dataset for transformer training.
    
    Pass raw strings, gets tokenized on-the-fly by the collator.
    For large datasets, pre-tokenize and store token IDs instead.
    """

    def __init__(self, texts: List[str], tokenizer: Optional[str] = None):
        self.texts = texts
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        return {"text": self.texts[idx]}


def create_mlm_dataloader(
    texts: List[str],
    tokenizer: str = "bert-base-uncased",
    batch_size: int = 8,
    max_length: int = 512,
    mask_prob: float = 0.15,
    shuffle: bool = True,
    num_workers: int = 2,
    pin_memory: bool = True,
) -> DataLoader:
    """
    Factory function to create an MLM DataLoader.
    
    Usage:
        dataloader = create_mlm_dataloader(
            texts=corpus,
            tokenizer="bert-base-uncased",
            batch_size=16,
            max_length=256,
        )
        
        for batch in dataloader:
            # batch.input_ids, batch.labels, batch.attention_mask
            loss = model(**batch).loss
            loss.backward()
    """
    from transformers import AutoTokenizer
    
    tok = AutoTokenizer.from_pretrained(tokenizer)
    
    dataset = TextDataset(texts)
    collator = MLMCollator(
        tokenizer=tok,
        max_length=max_length,
        mask_prob=mask_prob,
    )
    
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collator,
        pin_memory=pin_memory,
        drop_last=True,  # Avoid partial batches during training
    )


# =============================================================================
# Example usage
# =============================================================================
if __name__ == "__main__":
    # Demo corpus
    corpus = [
        "The quick brown fox jumps over the lazy dog.",
        "Deep learning transformers have revolutionized natural language processing.",
        "PyTorch makes building neural networks intuitive and flexible.",
        "Attention mechanisms allow models to focus on relevant context.",
        "Large language models can generate coherent and diverse text.",
    ]

    print("Creating MLM DataLoader...")
    dataloader = create_mlm_dataloader(
        texts=corpus,
        tokenizer="bert-base-uncased",
        batch_size=2,
        max_length=64,
        mask_prob=0.15,
        shuffle=True,
    )

    print(f"Dataset: {len(dataloader.dataset)} sentences")
    print(f"Batches per epoch: {len(dataloader)}")
    print()

    # Inspect first batch
    for batch in dataloader:
        print("=== MLM Batch ===")
        print(f"input_ids shape:      {batch.input_ids.shape}")
        print(f"attention_mask shape: {batch.attention_mask.shape}")
        print(f"labels shape:         {batch.labels.shape}")
        
        # Decode a sample
        decoded = dataloader.collate_fn.tokenizer.decode(batch.input_ids[0])
        print(f"\nDecoded (first seq):\n  {decoded}")
        
        # Show masked positions
        mask_token_id = dataloader.collate_fn.mask_token_id
        masked_positions = (batch.input_ids[0] == mask_token_id).nonzero(as_tuple=True)[0]
        if len(masked_positions) > 0:
            masked_tokens = batch.input_ids[0][masked_positions].tolist()
            original = batch.labels[0][masked_positions].tolist()
            print(f"\n[MASK] positions at indices: {masked_positions.tolist()}")
            print(f"  Masked with [MASK] token")
            print(f"  Original labels: {[dataloader.collate_fn.tokenizer.decode([l]) for l in original]}")
        break