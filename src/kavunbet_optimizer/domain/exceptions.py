class ConfigResourceError(Exception):
    """Base error for configuration resources."""


class ConfigResourceNotFoundError(ConfigResourceError):
    """Raised when a requested configuration resource does not exist."""


class ConfigResourceAlreadyExistsError(ConfigResourceError):
    """Raised when a configuration resource identity already exists."""


class ConfigResourceIdentityMismatchError(ConfigResourceError):
    """Raised when a request body identity differs from its URL identity."""


class ConfigVersionConflictError(ConfigResourceError):
    """Raised when a configuration was changed after it was read."""


class OptimizationJobErrors:
    """Namespace for optimization-job persistence and submission errors."""

    class OptimizationJobError(Exception):
        """Base error for optimization jobs."""

    class OptimizationJobNotFoundError(OptimizationJobError):
        """Raised when an optimization job does not exist."""

    class OptimizationJobAlreadyExistsError(OptimizationJobError):
        """Raised when an optimization job ID already exists."""

    class IdempotencyKeyConflictError(OptimizationJobError):
        """Raised when an idempotency key is already assigned."""
