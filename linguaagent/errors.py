"""Application-level errors, so callers never see raw provider exceptions."""


class LinguaAgentError(Exception):
    """Base class for all expected application errors."""


class ConfigError(LinguaAgentError):
    """Missing or invalid configuration (for example no API key)."""


class InvalidInputError(LinguaAgentError):
    """The user's input is empty, too long or otherwise unusable."""


class LLMError(LinguaAgentError):
    """The model call failed (network, rate limit, bad response, timeout)."""
