class MovieNotFoundError(ValueError):
    """Raised when an operation targets a movie that is not in the catalog."""


class MovieAlreadySavedError(ValueError):
    """Raised when a movie is already present in the catalog."""


class MovieApiConfigurationError(RuntimeError):
    """Raised when the OMDb client is used without an API key."""
