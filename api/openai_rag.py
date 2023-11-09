import asyncio
import logging
from openai import AsyncOpenAI
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import MessageContentText
from openai._types import NOT_GIVEN, NotGiven
from pydantic import PrivateAttr
from typing import Iterable, List
from .base_rag import AttributedAnswer, BaseRag


_logger = logging.getLogger(__name__)


class OpenaiRag(BaseRag):
  _client: AsyncOpenAI = PrivateAttr()
  _assistant: Assistant = PrivateAttr()
  _thread: Thread = PrivateAttr()
  _after: str | NotGiven = PrivateAttr(NOT_GIVEN)

  def __init__(self, client: AsyncOpenAI, assistant: Assistant, thread: Thread) -> None:
    self._client = client
    self._assistant = assistant
    self._thread = thread

  @classmethod
  async def create(cls) -> "OpenaiRag":
    client = AsyncOpenAI()
    assistant = await client.beta.assistants.create(
      name="Q&A Expert",
      instructions="You are an expert Q&A assistant. "
          "Always do your research first. "
          "Take a deep breath and explain your line of thoughts step by step. "
          "Then, provide a conclusion of your thoughts.",
      tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
      model="gpt-4-1106-preview",
    )
    thread = await client.beta.threads.create()
    return cls(client, assistant, thread)

  async def add_pdf(self, filename: str, content: bytes) -> None:
    new_file = await self._client.files.create(
      file=(filename, content, "application/pdf"),
      purpose='assistants'
    )
    new_file = await self._client.files.wait_for_processing(new_file.id)
    self._assistant = await self._client.beta.assistants.update(
      self._assistant.id,
      file_ids=self._assistant.file_ids + [new_file.id]
    )

  async def ask_question(self, question: str) -> Iterable[AttributedAnswer]:
    await self._client.beta.threads.messages.create(
        thread_id=self._thread.id,
        role="user",
        content=question)

    await self._run_thread()
    return await self._get_new_messages()

  async def _run_thread(self) -> None:
    while True:
      run = await self._client.beta.threads.runs.create(
          thread_id=self._thread.id,
          assistant_id=self._assistant.id)
      match run.status:
        case "queued" | "in_progress":
          await asyncio.sleep(1) 
        case "failed" | "expired":
          raise RuntimeError(run.last_error)
        case "completed":
          break
        case "requires_action" | "cancelling" | "cancelled" | _:
          raise NotImplementedError(f"Run state {run.status} not supported")

  async def _get_new_messages(self) -> Iterable[AttributedAnswer]:
    attributed_answers: List[AttributedAnswer] = []
    async for message in self._client.beta.threads.messages.list(
        thread_id=self._thread.id,
        after=self._after,
    ):
      assert message.role == "assistant"
      for content in message.content:
        if not isinstance(content, MessageContentText):
          _logger.warn(f"Content unexpected: {content}")
          continue
        attributed_answers.append(
          AttributedAnswer(
              answer = content.text.value,
              citations = [str(annotation)
                           for annotation in content.text.annotations],
          )
        )
      # Remember the last message processed so that the next iteration can begin
      # after this message.
      self._after = message.id

    return attributed_answers
