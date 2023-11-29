from llama_index.vector_stores.google.generativeai.base import NoSuchCorpusException
import logging
from openai._types import FileContent
from tempfile import SpooledTemporaryFile
from ..naive import GoogleRag
from ..base_rag import BaseRag
from ..chunkers import chunk_markdown


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


DEFAULT_CORPUS_ID = "ltsang-markdown"


class WindowGoogleRag(GoogleRag):
  @classmethod
  async def get_default(cls) -> BaseRag:
    default_corpus_id = DEFAULT_CORPUS_ID
    try:
      return await cls.get(corpus_id=default_corpus_id)
    except NoSuchCorpusException:
      _logger.warning(f"Cannot find corpus {default_corpus_id}. Creating it.")
      return await GoogleRag.create(
          corpus_id=default_corpus_id,
          display_name="RAG comparision with plain Google")

  def _add_file(
      self, *, filename: str, content: FileContent, content_type: str
  ) -> None:
    if content_type != "text/markdown":
      super()._add_file(
          filename=filename, content=content, content_type=content_type)
      return

    assert isinstance(content, SpooledTemporaryFile)
    self._client.insert_nodes(list(chunk_markdown(filename, content)))
