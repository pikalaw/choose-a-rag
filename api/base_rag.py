from abc import ABC, abstractmethod
import google.ai.generativelanguage as genai
from llama_index.response_synthesizers.google.generativeai import (
    GoogleTextSynthesizer,
)
from openai._types import FileContent
from pydantic import BaseModel
from typing import Iterable
from .llms import PaLM


TEMPERATURE = 0.2
ANSWER_STYLE = genai.GenerateAnswerRequest.AnswerStyle.ABSTRACTIVE
SAFETY_SETTING = [
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
        genai.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
    ]
]
# Maximum number of passage to use to answer questions.
PASSAGE_COUNT = 3


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
        temperature=TEMPERATURE,
        answer_style=ANSWER_STYLE,
        safety_setting=SAFETY_SETTING,
    )


def build_gemini_pro() -> PaLM:
    return PaLM(model_name="models/gemini-pro")
    

def build_gemini_ultra() -> PaLM:
    return PaLM(model_name="models/gemini-ultra")
    