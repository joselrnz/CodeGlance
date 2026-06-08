# Training

How to optimize a [[Transformers]] model end to end.

## Objective
Next-token prediction with a cross-entropy loss.

## Optimizer
AdamW with a warmup schedule; relies on [[Attention]] gradients flowing cleanly.
