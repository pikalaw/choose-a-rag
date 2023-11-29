from llama_index.schema import NodeRelationship, RelatedNodeInfo, TextNode
import logging
from typing import Iterable, List, TypeAlias
import uuid
from .base import MAX_CHUNK_SIZE


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
        yield from stack_to_text_node(stack, filename=filename, doc_id=doc_id)
      add_to_stack(stack, line)
    else:
      add_to_last_section(stack, line)
  if len(stack) > 0:
    yield from stack_to_text_node(stack, filename=filename, doc_id=doc_id)


def stack_to_text_node(
    stack: Stack, *, filename: str, doc_id: str
) -> Iterable[TextNode]:
  context_sections = stack[:-1]
  last_section = stack[-1]

  context = "\n".join(
      ["\n".join(section)[:MAX_CHUNK_SIZE] for section in context_sections]
  )
  for chunk in chunk_section(last_section):
    yield TextNode(
        text="\n".join([context, chunk]),
        relationships={
            NodeRelationship.SOURCE: RelatedNodeInfo(
                node_id=doc_id,
                metadata={"file_name": filename},
            )
        },
    )


def chunk_section(section: Section) -> Iterable[str]:
  text: List[str] = [section[0]]
  text_len = sum([len(line) for line in text])
  for line in section[1:]:
    line_len = len(line)
    if text_len + line_len < MAX_CHUNK_SIZE:
      text.append(line)
      text_len += line_len
      continue
    yield "\n".join(text)[:MAX_CHUNK_SIZE]
    text = [section[0], line]
    text_len = sum([len(line) for line in text])
  if len(text) > 0:
    yield "\n".join(text)[:MAX_CHUNK_SIZE]


def add_to_stack(stack: Stack, line: str) -> None:
  assert line.startswith("#")
  line_depth = compute_header_depth(line)

  while True:
    if len(stack) == 0:
      stack.append([line])
      break

    section = stack[-1]
    header = section[0]

    assert header.startswith("#")
    header_depth = compute_header_depth(header)

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

  last_section = stack[-1]
  last_section.append(line)
