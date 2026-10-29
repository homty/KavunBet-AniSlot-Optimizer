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
