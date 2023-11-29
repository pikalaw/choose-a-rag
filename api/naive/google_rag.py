import asyncio
import llama_index.vector_stores.google.generativeai.genai_extension as genaix
from llama_index.indices.managed.google.generativeai import GoogleIndex
from llama_index.vector_stores.google.generativeai.base import NoSuchCorpusException
from llama_index.indices.query.base import BaseQueryEngine
from llama_index.response.schema import Response
import logging
from openai._types import FileContent
from pydantic import BaseModel, PrivateAttr
from tempfile import SpooledTemporaryFile
from typing import Iterable, List, Literal
from ..base_rag import (
    ANSWER_STYLE,
    AttributedAnswer,
    BaseRag,
    SAFETY_SETTING,
    TEMPERATURE,
)
from ..chunkers import chunk_unstructured


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


DEFAULT_CORPUS_ID = "ltsang-unstructured"


class ConversationMessage(BaseModel):
  role: Literal["assistant", "user"]
  message: AttributedAnswer


class GoogleRag(BaseRag):
  _client: GoogleIndex = PrivateAttr()
  _query_engine: BaseQueryEngine = PrivateAttr()

  conversation: List[ConversationMessage] = []

  def __init__(self, client: GoogleIndex) -> None:
    super().__init__()
    self._client = client
    self._query_engine = client.as_query_engine(
        temperature=TEMPERATURE,
        answer_style=ANSWER_STYLE,
        safety_setting=SAFETY_SETTING,
    )

  @classmethod
  async def get_default(cls) -> "BaseRag":
    default_corpus_id = DEFAULT_CORPUS_ID
    try:
      return await cls.get(corpus_id=default_corpus_id)
    except NoSuchCorpusException:
      _logger.warning(f"Cannot find corpus {default_corpus_id}. Creating it.")
      return await GoogleRag.create(
          corpus_id=default_corpus_id,
          display_name="RAG comparision with plain Google")

  @classmethod
  async def create(cls, *, corpus_id: str, display_name: str) -> "GoogleRag":
    return await asyncio.to_thread(
        lambda: cls._create(
            corpus_id=corpus_id, display_name=display_name))

  @classmethod
  def _create(cls, *, corpus_id: str, display_name: str) -> "GoogleRag":
    return cls(GoogleIndex.create_corpus(
        corpus_id=corpus_id, display_name=display_name))

  @classmethod
  async def get(cls, *, corpus_id: str) -> "GoogleRag":
    return await asyncio.to_thread(lambda: cls._get(corpus_id=corpus_id))

  @classmethod
  def _get(cls, *, corpus_id: str) -> "GoogleRag":
    return cls(GoogleIndex.from_corpus(corpus_id=corpus_id))

  async def list_files(self) -> Iterable[str]:
    return await asyncio.to_thread(lambda: self._list_files())

  def _list_files(self) -> Iterable[str]:
    return [
      document.display_name or "?"
      for document in genaix.list_documents(corpus_id=self._client.corpus_id)]

  async def add_file(
      self, *, filename: str, content: FileContent, content_type: str
  ) -> None:
    return await asyncio.to_thread(
        lambda: self._add_file(
            filename=filename, content=content, content_type=content_type))

  def _add_file(
      self, *, filename: str, content: FileContent, content_type: str
  ) -> None:
    assert isinstance(content, SpooledTemporaryFile)
    self._client.insert_nodes(
        list(chunk_unstructured(filename, content, content_type)))

  async def clear_files(self) -> None:
    return await asyncio.to_thread(lambda: self._clear_files())

  def _clear_files(self) -> None:
    for document in genaix.list_documents(corpus_id=self._client.corpus_id):
      genaix.delete_document(
          corpus_id=self._client.corpus_id,
          document_id=document.document_id)

  async def add_conversation(self, message: str) -> Iterable[AttributedAnswer]:
    return await asyncio.to_thread(lambda: self._add_conversation(message))

  def _add_conversation(self, message: str) -> Iterable[AttributedAnswer]:
    response = self._query_engine.query(message)
    assert isinstance(response, Response)

    assistant_message = AttributedAnswer(
        answer=response.response or '',
        citations=[node.text
                   for node in response.source_nodes if node.score is None],
        score=_get_answerable_probability(response),
    )

    self.conversation.extend([
      ConversationMessage(
        role="user",
        message=AttributedAnswer(
          answer=message,
        )
      ),
      ConversationMessage(
        role="assistant",
        message=assistant_message,
      ),
    ])

    return [assistant_message]

  async def clear_conversation(self) -> None:
    self.conversation = []


def _get_answerable_probability(response: Response) -> float | None:
  if response.metadata is None:
    return None
  value = response.metadata.get("answerable_probability", None)
  if value is None:
    return None
  return float(value)
