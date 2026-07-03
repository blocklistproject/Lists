"""Custom exceptions for blocklist operations."""


class BlocklistError(Exception):
    """Base exception for blocklist operations."""



class ConfigurationError(BlocklistError):
    """Configuration file or settings error."""



class ValidationError(BlocklistError):
    """Domain validation error."""



class BuildError(BlocklistError):
    """List building error."""



class DomainNotFoundError(BlocklistError):
    """Domain not found in lists."""



class NetworkError(BlocklistError):
    """Network operation error."""



class FileFormatError(BlocklistError):
    """Invalid file format error."""

