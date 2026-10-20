# Invaria — Universal LLM Context Compiler

> **Compress less. Preserve more. Prove everything.**

[![PyPI version](https://img.shields.io/pypi/v/invaria.svg)](https://pypi.org/project/invaria/)
[![Python versions](https://img.shields.io/pypi/pyversions/invaria.svg)](https://pypi.org/project/invaria/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Invaria** is a deterministic, rule-based context compiler for Large Language Models. 

Instead of blindly dropping tokens based on probabilistic attention scores (which often leads to hallucinated numbers, broken URLs, or lost named entities), Invaria treats your prompt as source code. It compiles the context into an intermediate representation (IR), generates compression candidates, **verifies** that strict preservation contracts are met, and emits the cheapest safe representation.

---

## Why Invaria?

Most prompt compressors use smaller ML models to guess which words are "unimportant." This is dangerous for enterprise use cases where missing a "NOT", dropping a crucial ID, or altering a currency amount is catastrophic.

Invaria introduces a **Verification Engine**. It mathematically guarantees that:
*   ✅ **Numerical Invariants** (e.g., `$5000`, `99%`, `0.001`) are preserved.
*   ✅ **Lexical Entities** (Proper nouns, CamelCase, Acronyms) are untouched.
*   ✅ **Structured Identifiers** (URLs, Email addresses, API Keys, UUIDs) are safely retained.
*   ✅ **Formatting** (Markdown tables, JSON structures, code blocks) remains syntactically valid.

If a compressed candidate drops a required invariant, Invaria rejects it.

---

## Installation

Install via pip. Invaria `v0.1.0` is extremely lightweight and relies primarily on `pydantic`.

```bash
pip install invaria
```

*Note: Optional dependencies for ML-based semantic compression (`openai`, `anthropic`, `google`) will be utilized in upcoming releases.*

---

## Python API Quickstart

Invaria is designed to be easily integrated into your existing LLM pipelines, RAG systems, or agent frameworks.

```python
from invaria import Invaria

# Initialize the compiler
compiler = Invaria(mode="invariant")

text = """
User Alice transferred $5,000 to Bob on Monday... 
Please do not delete the backup files!!! They are stored in Amazon S3.
"""

# Compress the context
result = compiler.compress(text)

# The compressed text
print(result.text)
# Output: "User Alice transferred $5,000 to Bob on Monday. Please do not delete the backup files! They are stored in Amazon S3."

# Access detailed metrics
print(f"Original Tokens:   {result.original_tokens}")
print(f"Compressed Tokens: {result.compressed_tokens}")
print(f"Token Reduction:   {result.token_reduction}")
print(f"Compression Ratio: {result.compression_ratio:.2f}x")

# Cryptographic proof of preservation
print(f"Verified Safe:     {result.proof.verified}")
print(f"Preserved Entities:{result.proof.preserved}")
```

### Inspecting Extracted Invariants

You can also use Invaria just to parse and inspect the semantic constraints within a prompt without compressing it:

```python
ir = compiler.compile("Contact Support at help@example.com if Stripe webhooks fail.")

for node_id, node in ir.nodes.items():
    print(f"Type: {node.type} | Value: {node.value}")
# Type: entity | Value: Contact
# Type: entity | Value: Support
# Type: entity | Value: help@example.com
# Type: entity | Value: Stripe
```

---

## CLI Usage

Invaria comes with a built-in Command Line Interface for quickly compressing files or verifying external compressions in your CI/CD pipelines.

### Compress a File
```bash
invaria compress prompt.txt --mode invariant
```
*Outputs the compression metrics, the cryptographic proof status, and the compressed text.*

### Verify a Compression
If you have an original context and a compressed version, Invaria can verify if the compressed version safely retained all necessary invariants from the original:
```bash
invaria verify original.txt compressed.txt
```
*Outputs `Verification Passed: True` or `False`.*

---

## Compiler Architecture

Invaria operates similarly to a traditional programming language compiler:

```mermaid
graph LR
    A[Text Input] --> B(COMPILE)
    B -->|Semantic IR| C(OPTIMIZE)
    C -->|Generate Candidates| D(VERIFY)
    D -->|Check Constraints| E(EMIT)
    E --> F[Verified Compressed Text]
```

1.  **Compile (Extract Invariants):** Scans the text to build a `SemanticGraph` (IR) identifying all Entities, Numerical Invariants, Dates, and Instructions.
2.  **Optimize (Generate Candidates):** Applies active compressors (like `LexicalCompressor` for whitespace/punctuation normalization).
3.  **Verify (Preservation Contract):** The `VerificationEngine` checks the candidate string against the Semantic IR to ensure zero critical tokens were lost or mutated.
4.  **Emit:** Computes SHA-256 hashes for the proof, calculates token reductions, and returns a `CompressionResult`.

---

## Roadmap

*   **v0.1.x (Current):** Deterministic Lexical Compression, Entity/Numerical Invariant Extraction, Core Verification Engine, CLI.
*   **v0.2.x:** Syntactic Compression (safe removal of filler phrases, stop words) and Tiktoken integration for exact token pricing.
*   **v0.3.x:** Abstractive Semantic Compression using LLM providers (`openai`, `anthropic`, `google`) backed by Invaria's deterministic `VerificationEngine` to prevent LLM hallucinations during summarization.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Supratim Ghosh (sgindeed).
