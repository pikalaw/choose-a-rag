from abc import ABC, abstractmethod
from openai._types import FileContent
from pydantic import BaseModel
from typing import Iterable


class AttributedAnswer(BaseModel):
  answer: str
  citations: Iterable[str] | None = None
  score: float | None = None


class BaseRag(BaseModel, ABC):
  @abstractmethod
  async def list_files(self) -> Iterable[str]:
    ...

  @abstractmethod
  async def add_file(
      self, *, filename: str, content: FileContent, content_type: str
  ) -> None:
    ...

  @abstractmethod
  async def clear_files(self) -> None:
    ...

  @abstractmethod
  async def add_conversation(self, message: str) -> Iterable[AttributedAnswer]:
    ...

  @abstractmethod
  async def clear_conversation(self) -> None:
    ...
