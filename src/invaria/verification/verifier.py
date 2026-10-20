import re
from .report import VerificationReport
from .contract import PreservationContract
from ..ir.models import SemanticGraph


class VerificationEngine:
    def __init__(self, contract: PreservationContract):
        self.contract = contract

    @staticmethod
    def _contains_exact_token(text: str, token: str) -> bool:
        escaped = re.escape(token)
        # Ensure alphanumeric boundaries are respected so '15' doesn't match '1500'
        prefix = r"(?<![A-Za-z0-9_])" if token[0].isalnum() else ""
        suffix = r"(?![A-Za-z0-9_])" if token[-1].isalnum() else ""
        pattern = f"{prefix}{escaped}{suffix}"
        return re.search(pattern, text) is not None

    def verify(self, original_ir: SemanticGraph, candidate_text: str) -> VerificationReport:
        failures = []
        preserved = []
        missing = []

        for node_id, node in original_ir.nodes.items():
            val_str = str(node.value)
            if self._contains_exact_token(candidate_text, val_str):
                preserved.append(node)
            else:
                failures.append(f"Missing invariant ({node.type}): {val_str}")
                missing.append(node)

        passed = len(failures) == 0

        return VerificationReport(
            passed=passed,
            critical_failures=failures,
            preserved_invariants=preserved,
            missing_invariants=missing,
        )