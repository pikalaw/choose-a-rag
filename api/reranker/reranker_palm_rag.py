from llama_index.vector_stores.google.generativeai.base import (
    NoSuchCorpusException,
)
import logging
from .base import DEFAULT_CORPUS_ID, RerankerBaseRag
from ..base_rag import BaseRag
from ..llms import PaLM


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


class RerankerPalmRag(RerankerBaseRag):
    @classmethod
    async def get_default(cls) -> BaseRag:
        default_corpus_id = DEFAULT_CORPUS_ID
        palm = PaLM()
        try:
            return await cls.get(corpus_id=default_corpus_id, llm=palm)
        except NoSuchCorpusException:
            _logger.warning(f"Cannot find corpus {default_corpus_id}. Creating it.")
            return cls._create(
                corpus_id=default_corpus_id,
                display_name="RAG comparision with LlamaIndex",
                llm=palm,
            )
