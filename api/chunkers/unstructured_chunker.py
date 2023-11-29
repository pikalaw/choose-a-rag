from llama_index.schema import NodeRelationship, RelatedNodeInfo, TextNode
from openai._types import FileContent
from tempfile import SpooledTemporaryFile
from typing import Iterable
import uuid
from unstructured.partition.auto import partition  # type: ignore
from .base import MAX_CHUNK_SIZE


def chunk_unstructured(
    filename: str, content: FileContent, content_type: str
) -> Iterable[TextNode]:
    assert isinstance(content, SpooledTemporaryFile)
    elements = partition(file=content, content_type=content_type)
    text_chunks = [" ".join(str(el).split()) for el in elements]

    doc_id = str(uuid.uuid4())

    for chunk in text_chunks:
        for chunklet in split_chunk(chunk):
            yield TextNode(
                text=chunklet,
                relationships={
                    NodeRelationship.SOURCE: RelatedNodeInfo(
                        node_id=doc_id,
                        metadata={"file_name": filename},
                    )
                },
            )


def split_chunk(chunk: str) -> Iterable[str]:
    i = 0
    while i < len(chunk):
        yield chunk[i:i+MAX_CHUNK_SIZE]
        i += MAX_CHUNK_SIZE
