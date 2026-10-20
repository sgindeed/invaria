import hashlib
import json
import re
from typing import List, Dict, Any
from pydantic import BaseModel

from ..config import InvariaConfig
from ..ir.models import (
    SemanticGraph,
    Entity,
    NumericalInvariant,
    SourceSpan,
)
from ..compressors.lexical import LexicalCompressor
from ..verification.verifier import VerificationEngine
from ..verification.contract import PreservationContract
from ..verification.report import CompressionProof
from ..optimizer.search import Optimizer


class CompressionResult(BaseModel):
    text: str
    original_tokens: int
    compressed_tokens: int
    token_reduction: int
    compression_ratio: float
    mode: str
    representation: str
    proof: CompressionProof
    invariants: List[Any]
    warnings: List[str]
    metadata: Dict[str, Any]


class CompilerPipeline:
    # Matches words, numbers with currency/units/decimals, times, emails, and identifiers
    _TOKEN_PATTERN = re.compile(
        r"[A-Za-z0-9_$%+-]+(?:[@.:/-][A-Za-z0-9_$%+-]+)*"
    )

    def __init__(self, config: InvariaConfig):
        self.config = config
        self.compressors = [LexicalCompressor()]
        self.contract = PreservationContract(strictness=config.mode)
        self.verifier = VerificationEngine(self.contract)
        self.optimizer = Optimizer(config)
        self._compressor_map = {c.name: c for c in self.compressors}

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _hash_ir(ir: SemanticGraph) -> str:
        payload = json.dumps(
            {k: v.model_dump() for k, v in sorted(ir.nodes.items())},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def extract_invariants(self, text: str) -> SemanticGraph:
        graph = SemanticGraph()
        # Only treat short ALL-CAPS words as acronyms if the text itself isn't shouting in ALL CAPS
        text_has_lowercase = any(c.islower() for c in text)

        for idx, match in enumerate(self._TOKEN_PATTERN.finditer(text)):
            raw_token = match.group(0)
            clean_token = raw_token.strip(".,!?:;\"'()[]{}-")
            if not clean_token:
                continue

            start, end = match.span()
            span = SourceSpan(start_char=start, end_char=end, text=raw_token)

            has_digit = any(ch.isdigit() for ch in clean_token)
            has_alpha = any(ch.isalpha() for ch in clean_token)

            # 1. Numerical / Quantitative Invariants (pure numbers, currency, percentages, versions, times)
            if has_digit and not has_alpha:
                unit = None
                if clean_token.startswith(("$", "€", "£", "₹")):
                    unit = clean_token[0]
                elif clean_token.endswith("%"):
                    unit = "%"
                node_id = f"num_{idx}"
                graph.nodes[node_id] = NumericalInvariant(
                    id=node_id,
                    value=clean_token,
                    normalized_value=clean_token,
                    unit=unit,
                    source_span=span,
                )

            # 2. Mixed Alphanumeric Identifiers & Quantities (e.g., S3, AI302, 500mg, 15th)
            elif has_digit and has_alpha:
                if clean_token[0].isdigit():
                    node_id = f"num_{idx}"
                    graph.nodes[node_id] = NumericalInvariant(
                        id=node_id,
                        value=clean_token,
                        normalized_value=clean_token,
                        source_span=span,
                    )
                else:
                    node_id = f"ent_{idx}"
                    graph.nodes[node_id] = Entity(
                        id=node_id,
                        value=clean_token,
                        normalized_value=clean_token,
                        source_span=span,
                    )

            # 3. Structured Identifiers (e.g., emails or domain-like tokens containing '@')
            elif "@" in clean_token:
                node_id = f"ent_{idx}"
                graph.nodes[node_id] = Entity(
                    id=node_id,
                    value=clean_token,
                    normalized_value=clean_token,
                    source_span=span,
                )

            # 4. Lexical Entities: Proper Nouns, CamelCase/PascalCase, and Acronyms
            elif len(clean_token) >= 2:
                is_camel_or_pascal = (
                    any(c.isupper() for c in clean_token[1:])
                    and any(c.islower() for c in clean_token)
                )
                is_capitalized_word = (
                    clean_token[0].isupper()
                    and clean_token[1:].islower()
                    and len(clean_token) > 2
                )
                is_acronym = (
                    text_has_lowercase
                    and clean_token.isupper()
                    and 2 <= len(clean_token) <= 5
                )

                if is_camel_or_pascal or is_capitalized_word or is_acronym:
                    node_id = f"ent_{idx}"
                    graph.nodes[node_id] = Entity(
                        id=node_id,
                        value=clean_token,
                        normalized_value=clean_token.lower(),
                        source_span=span,
                    )

        return graph

    def compile(self, text: str) -> SemanticGraph:
        return self.extract_invariants(text)

    def compress(self, text: str) -> CompressionResult:
        original_tokens = len(text)
        orig_hash = self._hash_text(text)

        # 1. COMPILE
        ir = self.compile(text)
        inv_hash = self._hash_ir(ir)

        # 2. GENERATE CANDIDATES
        all_candidates = []
        for comp in self.compressors:
            if comp.can_handle(text, ir, self.config):
                candidates = comp.generate_candidates(text, ir, self.config)
                for cand in candidates:
                    all_candidates.append((comp.name, cand))

        # 3. VERIFY
        valid_candidates = []
        costs = []
        proofs = []

        for comp_name, cand in all_candidates:
            report = self.verifier.verify(ir, cand)
            if report.passed:
                valid_candidates.append(cand)
                # 4. MEASURE COST using the specific compressor that generated the candidate
                comp_instance = self._compressor_map[comp_name]
                cost = comp_instance.estimate_cost(cand, self.config)
                costs.append(cost)

                proof = CompressionProof(
                    original_hash=orig_hash,
                    invariant_hash=inv_hash,
                    candidate_hash=self._hash_text(cand),
                    verified=True,
                    exact_reconstruction=(cand == text),
                    preservation_contract=self.config.mode,
                    preserved=len(report.preserved_invariants),
                    changed=len(report.changed_invariants),
                    warnings=report.warnings,
                    compressor_chain=[comp_name],
                )
                proofs.append(proof)

        # FAIL-SAFE
        if not valid_candidates:
            return CompressionResult(
                text=text,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                token_reduction=0,
                compression_ratio=1.0,
                mode=self.config.mode,
                representation="original",
                proof=CompressionProof(
                    original_hash=orig_hash,
                    invariant_hash=inv_hash,
                    candidate_hash=orig_hash,
                    verified=True,
                    exact_reconstruction=True,
                    preservation_contract=self.config.mode,
                    preserved=len(ir.nodes),
                    changed=0,
                ),
                invariants=list(ir.nodes.values()),
                warnings=["Fallback to original text"],
                metadata={},
            )

        # 5. OPTIMIZE & SELECT
        best_cand = self.optimizer.select_best(valid_candidates, costs)
        best_idx = valid_candidates.index(best_cand)
        best_proof = proofs[best_idx]

        comp_tokens = len(best_cand)

        # 6. RETURN
        return CompressionResult(
            text=best_cand,
            original_tokens=original_tokens,
            compressed_tokens=comp_tokens,
            token_reduction=original_tokens - comp_tokens,
            compression_ratio=original_tokens / comp_tokens if comp_tokens > 0 else 0.0,
            mode=self.config.mode,
            representation=best_proof.compressor_chain[0],
            proof=best_proof,
            invariants=list(ir.nodes.values()),
            warnings=best_proof.warnings,
            metadata={},
        )