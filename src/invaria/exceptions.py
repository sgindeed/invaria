class InvariaError(Exception):
    """Base exception for all Invaria errors."""
    pass

class ParsingError(InvariaError):
    """Raised when parsing context fails."""
    pass

class UnsupportedContentError(InvariaError):
    """Raised when content type is not supported."""
    pass

class CompressionError(InvariaError):
    """Raised when compression process fails."""
    pass

class VerificationError(InvariaError):
    """Raised when a candidate fails verification checks."""
    pass

class InvariantViolation(VerificationError):
    """Raised when a required invariant is violated."""
    pass

class ReconstructionError(VerificationError):
    """Raised when exact reversible reconstruction fails."""
    pass

class ConfigurationError(InvariaError):
    """Raised when configuration is invalid."""
    pass

class ProviderError(InvariaError):
    """Raised when interacting with an LLM provider fails."""
    pass

class TokenizerError(InvariaError):
    """Raised when tokenization fails."""
    pass

class RenderingError(InvariaError):
    """Raised when rendering a candidate fails."""
    pass

class OptimizationError(InvariaError):
    """Raised when the optimization engine fails to find a valid representation."""
    pass
