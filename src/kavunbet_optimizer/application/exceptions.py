class OptimizationResultErrors:
    """Namespace for optimization-result persistence errors."""

    class OptimizationResultError(Exception):
        """Base error for optimization results."""

    class OptimizationResultNotFoundError(OptimizationResultError):
        """Raised when an optimization result does not exist."""

    class OptimizationResultAlreadyExistsError(OptimizationResultError):
        """Raised when an optimization result ID already exists."""

    class JobResultAlreadyExistsError(OptimizationResultError):
        """Raised when an optimization job already has a result."""


class ReelArtifactErrors:
    """Namespace for reel-artifact storage errors."""

    class ReelArtifactStoreError(Exception):
        """Base error for reel artifact storage."""

    class ReelArtifactNotFoundError(ReelArtifactStoreError):
        """Raised when a reel artifact does not exist."""

    class ReelArtifactConflictError(ReelArtifactStoreError):
        """Raised when a storage key already contains different content."""
