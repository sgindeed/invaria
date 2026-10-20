from typing import Optional
from .config import InvariaConfig
from .compiler.pipeline import CompilerPipeline, CompressionResult
from .ir.models import SemanticGraph

class Invaria:
    def __init__(self, **kwargs):
        self.config = InvariaConfig(**kwargs)
        self.pipeline = CompilerPipeline(self.config)

    def compress(self, text: str, **kwargs) -> CompressionResult:
        # Override config optionally for this run
        if kwargs:
            local_config = self.config.model_copy(update=kwargs)
            local_pipeline = CompilerPipeline(local_config)
            return local_pipeline.compress(text)
        return self.pipeline.compress(text)

    def compile(self, text: str) -> SemanticGraph:
        return self.pipeline.compile(text)

    def verify(self, original: str, compressed: str) -> bool:
        ir = self.pipeline.compile(original)
        report = self.pipeline.verifier.verify(ir, compressed)
        return report.passed

    def inspect(self, text: str) -> SemanticGraph:
        return self.pipeline.compile(text)

    def benchmark(self, text: str) -> None:
        raise NotImplementedError("Benchmark framework is not yet initialized.")
