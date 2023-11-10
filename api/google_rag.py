import asyncio
import llama_index.vector_stores.google.generativeai.genai_extension as genaix
from llama_index.indices.managed.google.generativeai import GoogleIndex
from llama_index.indices.query.base import BaseQueryEngine
from llama_index.response.schema import Response
from llama_index.schema import NodeRelationship, NodeWithScore, RelatedNodeInfo, TextNode
import logging
import math
from openai._types import FileContent
from typing import IO, Iterable, List, Literal
from pydantic import BaseModel, PrivateAttr
from unstructured.partition.auto import partition  # type: ignore
from .base_rag import AttributedAnswer, BaseRag


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


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
    self._query_engine = client.as_query_engine()

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
  async def get(
      cls, *, corpus_id: str = "ltsang-rag-comparision"
  ) -> "GoogleRag":
    return await asyncio.to_thread(lambda: cls._get(corpus_id=corpus_id))

  @classmethod
  def _get(cls, *, corpus_id: str) -> "GoogleRag":
    try:
      return cls(GoogleIndex.from_corpus(corpus_id=corpus_id))
    except Exception as e:
      _logger.warning(f"Cannot find corpus {corpus_id}: {e}. Creating it.")
      return GoogleRag._create(
          corpus_id=corpus_id, display_name="RAG comparision corpus")

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
    assert type(content) is IO[bytes]
    elements = partition(filename=filename, file=content, content_type=content_type)
    text_chunks = [" ".join(str(el).split()) for el in elements]

    doc_id = str(hash(filename))
    self._client.insert_nodes(
        [
            TextNode(
                text=chunk,
                relationships={
                    NodeRelationship.SOURCE: RelatedNodeInfo(
                        node_id=doc_id,
                        metadata={"file_name": filename},
                    )
                },)
            for chunk in text_chunks
        ]
    )

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
        citations=[node.text for node in response.source_nodes],
        score=_max_score(response.source_nodes),
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


def _max_score(nodes: List[NodeWithScore]) -> float | None:
  score = max([-math.inf] + [node.score or -math.inf for node in nodes])
  return score if score > -math.inf else None
