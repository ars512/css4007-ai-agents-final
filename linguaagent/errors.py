"""Application-level errors, so callers never see raw provider exceptions."""


class LinguaAgentError(Exception):
    """Base class for all expected application errors."""


class ConfigError(LinguaAgentError):
    """Missing or invalid configuration (for example no API key)."""


class InvalidInputError(LinguaAgentError):
    """The user's input is empty, too long or otherwise unusable."""


class LLMError(LinguaAgentError):
    """The model call failed (network, rate limit, bad response, timeout)."""


class ToolError(LinguaAgentError):
    """Base class for failures inside a tool. `kind` is returned to the caller."""

    kind = "tool_error"


class ToolInputError(ToolError):
    """The tool arguments are invalid (checked before anything is executed)."""

    kind = "invalid_input"


class NotFoundError(ToolError):
    """The requested information does not exist (for example an unknown word)."""

    kind = "not_found"


class ToolUnavailableError(ToolError):
    """An external service or the local store failed (network, quota, bad data)."""

    kind = "unavailable"
