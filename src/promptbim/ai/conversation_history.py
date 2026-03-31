"""ConversationHistory — Manages dialogue context for AI interactions.

Maintains a rolling window of conversation messages with
automatic trimming to stay within token budget.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from promptbim.debug import get_logger

logger = get_logger("ai.conversation_history")


@dataclass
class Message:
    """A single conversation message."""
    role: str  # "user", "assistant", "system"
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_api_dict(self) -> dict:
        """Convert to Anthropic API message format."""
        return {"role": self.role, "content": self.content}


class ConversationHistory:
    """Rolling conversation history with token-aware trimming.

    Keeps the most recent messages within max_messages and
    estimates tokens to stay under max_tokens budget.
    """

    # Rough estimate: 1 token ≈ 4 characters for English, 2 for CJK
    CHARS_PER_TOKEN = 3

    def __init__(
        self,
        max_messages: int = 20,
        max_tokens: int = 4000,
        system_message: str | None = None,
    ) -> None:
        self._messages: list[Message] = []
        self._max_messages = max_messages
        self._max_tokens = max_tokens
        self._system_message = system_message

    @property
    def system_message(self) -> str | None:
        return self._system_message

    @system_message.setter
    def system_message(self, value: str) -> None:
        self._system_message = value

    def add_user(self, content: str, **metadata: Any) -> None:
        """Add a user message."""
        self._messages.append(Message(role="user", content=content, metadata=metadata))
        self._trim()

    def add_assistant(self, content: str, **metadata: Any) -> None:
        """Add an assistant response."""
        self._messages.append(Message(role="assistant", content=content, metadata=metadata))
        self._trim()

    def add_system_context(self, content: str) -> None:
        """Add a system context message (injected as user message with context prefix)."""
        self._messages.append(Message(
            role="user",
            content=f"[System Context] {content}",
            metadata={"is_context": True},
        ))
        self._trim()

    def get_messages(self) -> list[dict]:
        """Return messages in Anthropic API format."""
        return [m.to_api_dict() for m in self._messages]

    def get_last_n(self, n: int) -> list[dict]:
        """Return the last N messages."""
        return [m.to_api_dict() for m in self._messages[-n:]]

    def clear(self) -> None:
        """Clear all messages."""
        self._messages.clear()

    @property
    def message_count(self) -> int:
        return len(self._messages)

    @property
    def estimated_tokens(self) -> int:
        """Estimate total tokens in the history."""
        total_chars = sum(len(m.content) for m in self._messages)
        if self._system_message:
            total_chars += len(self._system_message)
        return total_chars // self.CHARS_PER_TOKEN

    def _trim(self) -> None:
        """Trim history to stay within limits."""
        # Trim by message count
        while len(self._messages) > self._max_messages:
            self._messages.pop(0)

        # Trim by estimated tokens
        while self.estimated_tokens > self._max_tokens and len(self._messages) > 2:
            self._messages.pop(0)

    def get_summary(self) -> str:
        """Return a brief summary of conversation state."""
        return (
            f"History: {self.message_count} messages, "
            f"~{self.estimated_tokens} tokens"
        )
