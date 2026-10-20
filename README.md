# Invaria — Universal LLM Context Compiler

> **Compress less. Preserve more. Prove everything.**

Invaria does not ask which tokens are safe to delete. It searches for the cheapest representation that satisfies a verifiable preservation contract.

## Core Idea
Instead of blindly deleting tokens based on attention scores, Invaria compiles context into structured representations, generates multiple compression candidates, verifies their preservation contract, and selects the cheapest representation that can be proven safe for the requested guarantee.

## Compiler Architecture
```
COMPILE → OPTIMIZE → VERIFY → EMIT
```

## Quickstart
```python
from invaria import Invaria

compiler = Invaria()

result = compiler.compress(
    "Your text here",
    mode="invariant"
)

print(result.text)
print(result.original_tokens)
print(result.compressed_tokens)
print(result.proof)
```
