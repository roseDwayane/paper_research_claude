"""
Base classes for Research Agent tools.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


@dataclass
class ToolResult(Generic[T]):
    """Result wrapper for tool execution."""

    success: bool
    data: T | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def ok(cls, data: T, **metadata) -> "ToolResult[T]":
        return cls(success=True, data=data, metadata=metadata or None)

    @classmethod
    def fail(cls, error: str, **metadata) -> "ToolResult[T]":
        return cls(success=False, error=error, metadata=metadata or None)


class BaseTool(ABC):
    """Base class for all tools."""

    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    def get_schema(self) -> dict:
        """Get the tool's parameter schema for LLM function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema(),
        }

    @abstractmethod
    def _get_parameters_schema(self) -> dict:
        """Return the JSON schema for tool parameters."""
        pass
