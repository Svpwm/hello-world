"""Conversation memory utilities for the driver assistant agent."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, Iterable, List, Literal, Optional


@dataclass
class ConversationTurn:
    """Single turn within the driver conversation."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime


class ConversationMemory:
    """Ring-buffer conversation memory keeping the latest interaction turns."""

    def __init__(self, max_turns: int = 12) -> None:
        self.max_turns = max_turns
        self._turns: Deque[ConversationTurn] = deque(maxlen=max_turns)

    def add_turn(
        self,
        role: Literal["user", "assistant"],
        content: str,
        *,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Append a new turn to the memory, trimming old entries if necessary."""

        self._turns.append(
            ConversationTurn(
                role=role,
                content=content,
                timestamp=timestamp or datetime.utcnow(),
            )
        )

    def history(self) -> List[ConversationTurn]:
        """Return the stored turns as a list in chronological order."""

        return list(self._turns)

    def __iter__(self) -> Iterable[ConversationTurn]:
        return iter(self._turns)

    def summary(self) -> str:
        """Generate a compact textual summary of the stored turns."""

        return " | ".join(f"{turn.role}: {turn.content}" for turn in self._turns)
