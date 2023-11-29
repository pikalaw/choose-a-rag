import asyncio
from llama_index import (
    LLMPredictor,
    VectorStoreIndex,
)
from llama_index.llms.base import LLM
import llama_index.vector_stores.google.generativeai.genai_extension as genaix
from llama_index.vector_stores.google.generativeai import (
    GoogleVectorStore,
    google_service_context,
)
from llama_index.indices.query.base import BaseQueryEngine
from llama_index.indices.query.query_transform.base import (
    StepDecomposeQueryTransform,
)
from llama_index.prompts.base import PromptTemplate
from llama_index.query_engine.multistep_query_engine import (
    MultiStepQueryEngine,
)
from llama_index.response.schema import Response
import logging
from openai._types import FileContent
from pydantic import BaseModel, PrivateAttr
from tempfile import SpooledTemporaryFile
from typing import Iterable, List, Literal
from ..base_rag import AttributedAnswer, BaseRag, build_response_synthesizer
from ..chunkers import chunk_unstructured


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


class ConversationMessage(BaseModel):
  role: Literal["assistant", "user"]
  message: AttributedAnswer


DEFAULT_CORPUS_ID = "ltsang-unstructured"
_STEP_DECOMPOSE_QUERY_TRANSFORM_TMPL = (
    "The original question is as follows: {query_str}\n"
    "We have an opportunity to answer some, or all of the question from a "
    "knowledge source. "
    "Context information for the knowledge source is provided below, as "
    "well as previous reasoning steps.\n"
    "Given the context and previous reasoning, return a question that can "
    "be answered from "
    "the context. This question can be the same as the original question, "
    "or this question can represent a subcomponent of the overall question."
    "It should not be irrelevant to the original question.\n"
    "If we are confident that we already have enough information to answer "
    "the original question, provide 'None' as the answer. "
    "On the other hand, if you do not have enough information to answer the "
    "original question, you must not provide 'None' as the answer. "
    "Instead, you must ask a new question!\n\n"
    "Some examples are given below: "
    "\n\n"
    "Question: How many Grand Slam titles does the winner of the 2020 Australian "
    "Open have?\n"
    "Knowledge source context: Provides names of the winners of the 2020 "
    "Australian Open\n"
    "Previous reasoning: None\n"
    "Next question: Who was the winner of the 2020 Australian Open? "
    "\n\n"
    "Question: Who was the winner of the 2020 Australian Open?\n"
    "Knowledge source context: Provides names of the winners of the 2020 "
    "Australian Open\n"
    "Previous reasoning: None.\n"
    "New question: Who was the winner of the 2020 Australian Open? "
    "\n\n"
    "Question: How many Grand Slam titles does the winner of the 2020 Australian "
    "Open have?\n"
    "Knowledge source context: Provides information about the winners of the 2020 "
    "Australian Open\n"
    "Previous reasoning:\n"
    "- Who was the winner of the 2020 Australian Open? \n"
    "- The winner of the 2020 Australian Open was Novak Djokovic.\n"
    "New question: None"
    "\n\n"
    "Question: How many Grand Slam titles does the winner of the 2020 Australian "
    "Open have?\n"
    "Knowledge source context: Provides information about the winners of the 2020 "
    "Australian Open - includes biographical information for each winner\n"
    "Previous reasoning:\n"
    "- Who was the winner of the 2020 Australian Open? \n"
    "- The winner of the 2020 Australian Open was Novak Djokovic.\n"
    "New question: How many Grand Slam titles does Novak Djokovic have? "
    "\n\n"
    "Question: {query_str}\n"
    "Knowledge source context: {context_str}\n"
    "Previous reasoning: {prev_reasoning}\n"
    "New question: "
)
_STEP_DECOMPOSE_QUERY_TRANSFORM_PROMPT = PromptTemplate(
  _STEP_DECOMPOSE_QUERY_TRANSFORM_TMPL)

class MultiQueryBaseRag(BaseRag):
  _store: GoogleVectorStore = PrivateAttr()
  _query_engine: BaseQueryEngine = PrivateAttr()

  conversation: List[ConversationMessage] = []

  def __init__(self, *, store: GoogleVectorStore, llm: LLM) -> None:
    super().__init__()

    index = VectorStoreIndex.from_vector_store(
        vector_store=store,
        service_context=google_service_context)
    response_synthesizer = build_response_synthesizer()
    single_step_query_engine = index.as_query_engine(
        response_synthesizer=response_synthesizer)
    step_decompose_transform = StepDecomposeQueryTransform(
        LLMPredictor(llm=llm),
        step_decompose_query_prompt=_STEP_DECOMPOSE_QUERY_TRANSFORM_PROMPT,
        verbose=True)
    query_engine = MultiStepQueryEngine(
        query_engine=single_step_query_engine,
        query_transform=step_decompose_transform,
        response_synthesizer=response_synthesizer,
        index_summary="Ask me anything.",
        num_steps=6)

    self._store = store
    self._query_engine = query_engine

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
    response = self._query_engine.query(message)
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
