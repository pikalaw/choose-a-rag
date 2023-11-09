from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Iterable


class AttributedAnswer(BaseModel):
  answer: str
  citations: Iterable[str] | None = None


class BaseRag(BaseModel, ABC):
  @abstractmethod
  async def add_pdf(self, filename: str, content: bytes) -> None:
    ...

  @abstractmethod
  async def ask_question(self, question: str) -> Iterable[AttributedAnswer]:
    ...
