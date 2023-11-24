from llama_index.schema import NodeRelationship, RelatedNodeInfo, TextNode
import logging
from tempfile import SpooledTemporaryFile
from typing import Iterable, List, Literal, TypeAlias
import uuid


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


Section: TypeAlias = List[str]
Stack: TypeAlias = List[Section]


def chunk_markdown(
    filename: str, content: SpooledTemporaryFile[bytes]
) -> Iterable[TextNode]:
  doc_id = str(uuid.uuid4())
  stack: Stack = []
  for raw_line in content:
    line = raw_line.decode('utf-8').strip()
    if line.startswith("#"):
      yield stack_to_text_node(stack, filename=filename, doc_id=doc_id)
      add_to_stack(stack, line)
    else:
      add_to_last_section(stack, line)
  if len(stack) > 0:
    yield stack_to_text_node(stack, filename=filename, doc_id=doc_id)


def stack_to_text_node(stack: Stack, *, filename: str, doc_id: str) -> TextNode:
  # TODO
  return TextNode(
      text="",
      relationships={
          NodeRelationship.SOURCE: RelatedNodeInfo(
              node_id=doc_id,
              metadata={"file_name": filename},
          )
      },
  )


def add_to_stack(stack: Stack, line: str) -> None:
  # TODO
  ...


def add_to_last_section(stack: Stack, line: str) -> None:
  # TODO
  ...
