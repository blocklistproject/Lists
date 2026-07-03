"""Custom exceptions for blocklist operations."""


class BlocklistError(Exception):
    """Base exception for blocklist operations."""

    pass


class ConfigurationError(BlocklistError):
    """Configuration file or settings error."""

    pass


class ValidationError(BlocklistError):
    """Domain validation error."""

    pass


class BuildError(BlocklistError):
    """List building error."""

    pass


class DomainNotFoundError(BlocklistError):
    """Domain not found in lists."""

    pass


class NetworkError(BlocklistError):
    """Network operation error."""

    pass


class FileFormatError(BlocklistError):
    """Invalid file format error."""

    pass
