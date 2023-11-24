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
    filename: str, content: Iterable[bytes]
) -> Iterable[TextNode]:
  doc_id = str(uuid.uuid4())
  stack: Stack = []
  for raw_line in content:
    line = raw_line.decode('utf-8').strip()
    if line.startswith("#"):
      if len(stack) > 0:
        yield stack_to_text_node(stack, filename=filename, doc_id=doc_id)
      add_to_stack(stack, line)
    else:
      add_to_last_section(stack, line)
  if len(stack) > 0:
    yield stack_to_text_node(stack, filename=filename, doc_id=doc_id)


def stack_to_text_node(stack: Stack, *, filename: str, doc_id: str) -> TextNode:
  return TextNode(
      text="\n".join(["\n".join(section) for section in stack]),
      relationships={
          NodeRelationship.SOURCE: RelatedNodeInfo(
              node_id=doc_id,
              metadata={"file_name": filename},
          )
      },
  )


def add_to_stack(stack: Stack, line: str) -> None:
  if len(stack) == 0:
    stack.append([line])
    return

  while True:
    section = stack[-1]
    header = section[0]

    assert header.startswith("#")
    header_depth = compute_header_depth(header)
    assert line.startswith("#")
    line_depth = compute_header_depth(line)

    if line_depth > header_depth:
      stack.append([line])
      return

    del stack[-1]


def compute_header_depth(header: str) -> int:
  count = 0
  for char in header:
    if char == '#':
        count += 1
    else:
        break
  return count



def add_to_last_section(stack: Stack, line: str) -> None:
  # Ignore bare lines with no header.
  if len(stack) == 0:
    return

  stack[-1].append(line)
