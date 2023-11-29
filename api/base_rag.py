from abc import ABC, abstractmethod
import google.ai.generativelanguage as genai
from llama_index.response_synthesizers.google.generativeai import (
    GoogleTextSynthesizer,
)
from openai._types import FileContent
from pydantic import BaseModel
from typing import Iterable
from .llms import PaLM


TEMPERATURE = 0.8
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


def build_palm() -> PaLM:
    """Choices:
    models/ai-village-001
    models/bard-factual
    models/chat-bard-001
    models/chat-bard-002
    models/chat-bard-003
    models/chat-bard-004
    models/chat-bard-005
    models/chat-bard-006
    models/chat-bard-007
    models/chat-bard-008
    models/chat-bard-009
    models/chat-bard-010
    models/chat-bard-013
    models/chat-bard-014
    models/chat-bard-015
    models/chat-bard-016
    models/chat-bard-017
    models/chat-bard-018
    models/chat-bard-019
    models/chat-bard-020
    models/chat-bison-001
    models/chat-ulm-factual-001
    models/chat-ulm-latest
    models/g-001
    models/g-002
    models/g-003
    models/g-004
    models/g-005
    models/g-006
    models/lamda-api-000
    models/lamda-api-001
    models/lamda-api-eval
    models/meena2-dialog
    models/text-bison-001
    models/text-bison-canary-001
    models/text-eval-m-001
    models/text-eval-m-231019
    models/text-eval-s-001
    models/text-gemini-m-llmit
    models/text-llmit-24b-sax-074
    models/text-unicorn-001
    models/embedding-001
    models/embedding-gecko-001
    models/embedding-gecko-002
    models/gemini-pro
    models/gemini-pro-vision
    models/gemini-ultra
    models/multimodal-eval-231122
    models/text-eval-231121
    models/xl-eval-231122
    models/embedding-001
    """
    return PaLM(model_name="models/text-bison-001")
    