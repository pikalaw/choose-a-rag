from abc import ABC, abstractmethod
import google.ai.generativelanguage as genai
from llama_index.response_synthesizers.google.generativeai import (
    GoogleTextSynthesizer,
)
from openai._types import FileContent
from pydantic import BaseModel
from typing import Iterable


class AttributedAnswer(BaseModel):
  answer: str
  citations: Iterable[str] | None = None
  score: float | None = None


class BaseRag(BaseModel, ABC):
  @classmethod
  @abstractmethod
  async def get_default(cls) -> "BaseRag":
    ...

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


def build_response_synthesizer() -> GoogleTextSynthesizer:
    return GoogleTextSynthesizer.create(
        temperature=0.8,
        answer_style=genai.GenerateAnswerRequest.AnswerStyle.ABSTRACTIVE,
        safety_setting=[
            genai.SafetySetting(
                category=category,
                threshold=genai.SafetySetting.HarmBlockThreshold.BLOCK_NONE,
            )
            for category in [
                genai.HarmCategory.HARM_CATEGORY_DEROGATORY,
                genai.HarmCategory.HARM_CATEGORY_TOXICITY,
                genai.HarmCategory.HARM_CATEGORY_VIOLENCE,
                genai.HarmCategory.HARM_CATEGORY_SEXUAL,
                genai.HarmCategory.HARM_CATEGORY_MEDICAL,
                genai.HarmCategory.HARM_CATEGORY_DANGEROUS,
            ]
        ]
    )
