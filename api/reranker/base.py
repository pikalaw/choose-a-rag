import asyncio
import logging
from llama_index import ServiceContext, VectorStoreIndex
from llama_index.core import BaseRetriever
from llama_index.llms.base import LLM
from llama_index.postprocessor import LLMRerank
from llama_index.response.schema import Response
from llama_index.response_synthesizers.google.generativeai import (
    GoogleTextSynthesizer,
)
from llama_index.retrievers import VectorIndexRetriever
from llama_index.schema import QueryBundle
import llama_index.vector_stores.google.generativeai.genai_extension as genaix
from llama_index.vector_stores.google.generativeai import (
    GoogleVectorStore,
    google_service_context,
)
from openai._types import FileContent
from pydantic import BaseModel, PrivateAttr
from tempfile import SpooledTemporaryFile
from typing import Iterable, List, Literal
from ..base_rag import AttributedAnswer, BaseRag, build_response_synthesizer
from ..chunkers import chunk_unstructured


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


DEFAULT_CORPUS_ID = "ltsang-unstructured"


class ConversationMessage(BaseModel):
  role: Literal["assistant", "user"]
  message: AttributedAnswer


class RerankerBaseRag(BaseRag):
  _store: GoogleVectorStore = PrivateAttr()
  _retriever: BaseRetriever = PrivateAttr()
  _reranker: LLMRerank = PrivateAttr()
  _response_synthesizer: GoogleTextSynthesizer = PrivateAttr()

  conversation: List[ConversationMessage] = []

  def __init__(
      self,
      *,
      store: GoogleVectorStore,
      llm: LLM,
      retrieve_top_k: int = 10,
      rerank_top_k: int = 5) -> None:
    super().__init__()

    index = VectorStoreIndex.from_vector_store(
        vector_store=store,
        service_context=google_service_context)
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=retrieve_top_k,
    )
    reranker = LLMRerank(
        choice_batch_size=5,
        top_n=rerank_top_k,
        service_context=ServiceContext.from_defaults(llm=llm),
    )
    response_synthesizer = build_response_synthesizer()

    self._store = store
    self._retriever = retriever
    self._reranker = reranker
    self._response_synthesizer = response_synthesizer

  @classmethod
  async def create(
      cls, *, corpus_id: str, display_name: str, llm: LLM
  ) -> BaseRag:
    return await asyncio.to_thread(
        lambda: cls._create(
            corpus_id=corpus_id, display_name=display_name, llm=llm)
    )

  @classmethod
  def _create(
      cls, *, corpus_id: str, display_name: str, llm: LLM
  ) -> BaseRag:
    return cls(
      store=GoogleVectorStore.create_corpus(
          corpus_id=corpus_id,
          display_name=display_name),
      llm=llm)

  @classmethod
  async def get(cls, *, corpus_id: str, llm: LLM) -> BaseRag:
    return await asyncio.to_thread(
        lambda: cls._get(corpus_id=corpus_id, llm=llm))

  @classmethod
  def _get(cls, *, corpus_id: str, llm: LLM) -> BaseRag:
    return cls(
        store=GoogleVectorStore.from_corpus(corpus_id=corpus_id),
        llm=llm)

  async def list_files(self) -> Iterable[str]:
    return await asyncio.to_thread(lambda: self._list_files())

  def _list_files(self) -> Iterable[str]:
    return [
        document.display_name or "?"
        for document in genaix.list_documents(
            corpus_id=self._store.corpus_id)
    ]

  async def add_file(
      self, *, filename: str, content: FileContent, content_type: str
  ) -> None:
    return await asyncio.to_thread(
        lambda: self._add_file(
            filename=filename, content=content, content_type=content_type
        )
    )

  def _add_file(
      self, *, filename: str, content: FileContent, content_type: str
  ) -> None:
    assert isinstance(content, SpooledTemporaryFile)
    self._store.add(list(chunk_unstructured(filename, content, content_type)))

  async def clear_files(self) -> None:
    return await asyncio.to_thread(lambda: self._clear_files())

  def _clear_files(self) -> None:
    for document in genaix.list_documents(corpus_id=self._store.corpus_id):
      genaix.delete_document(
          corpus_id=self._store.corpus_id, document_id=document.document_id
      )

  async def add_conversation(self, message: str) -> Iterable[AttributedAnswer]:
    return await asyncio.to_thread(lambda: self._add_conversation(message))

  def _add_conversation(self, message: str) -> Iterable[AttributedAnswer]:
    query_bundle = QueryBundle(message)
    retrieved_nodes = self._retriever.retrieve(query_bundle)
    reranked_nodes = self._reranker.postprocess_nodes(
        retrieved_nodes, query_bundle
    )
    response = self._response_synthesizer.synthesize(
        query_bundle,
        reranked_nodes,
    )
    assert isinstance(response, Response)

    assistant_message = AttributedAnswer(
        answer=response.response or '',
        citations=[node.text
                   for node in response.source_nodes if node.score is None],
        score=_get_answerable_probability(response),
    )
    self.conversation.extend(
        [
            ConversationMessage(
                role="user",
                message=AttributedAnswer(
                    answer=message,
                ),
            ),
            ConversationMessage(
                role="assistant",
                message=assistant_message,
            ),
        ]
    )

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
