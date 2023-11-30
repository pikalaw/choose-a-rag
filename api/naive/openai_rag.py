import asyncio
import logging
from openai import AsyncOpenAI
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import MessageContentText
from openai._types import FileContent, NOT_GIVEN, NotGiven
from pydantic import PrivateAttr
from typing import Iterable, List
from ..base_rag import AttributedAnswer, BaseRag
from ..debugging import pretty


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


class OpenaiRag(BaseRag):
  _client: AsyncOpenAI = PrivateAttr()
  _assistant: Assistant = PrivateAttr()
  _thread: Thread = PrivateAttr()
  _after: str | NotGiven = PrivateAttr(NOT_GIVEN)

  def __init__(self, client: AsyncOpenAI, assistant: Assistant, thread: Thread) -> None:
    super().__init__()
    self._client = client
    self._assistant = assistant
    self._thread = thread

  @classmethod
  async def get_default(cls) -> "BaseRag":
    return await cls.get(assistant_id="asst_4It75FJXgCNPyLn5I4nul0LG")

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

  @classmethod
  async def get(cls, *, assistant_id: str) -> "OpenaiRag":
    client = AsyncOpenAI()
    assistant = await client.beta.assistants.retrieve(assistant_id)
    thread = await client.beta.threads.create()
    return cls(client, assistant, thread)

  async def list_files(self) -> Iterable[str]:
    filenames: List[str] = []
    async for file in self._client.files.list():
      if file.id in self._assistant.file_ids:
        filenames.append(file.filename)
    return filenames

  async def add_file(
      self, *, filename: str, content: FileContent, content_type: str
  ) -> None:
    new_file = await self._client.files.create(
      file=(filename, content, content_type),
      purpose='assistants'
    )
    new_file = await self._client.files.wait_for_processing(new_file.id)

    self._assistant = await self._client.beta.assistants.update(
      self._assistant.id,
      file_ids=self._assistant.file_ids + [new_file.id]
    )

  async def clear_files(self) -> None:
    for file_id in self._assistant.file_ids:
      await self._client.files.delete(file_id)

    self._assistant = await self._client.beta.assistants.update(
      self._assistant.id,
      file_ids=[],
    )

  async def add_conversation(self, message: str) -> Iterable[AttributedAnswer]:
    await self._client.beta.threads.messages.create(
        thread_id=self._thread.id,
        role="user",
        content=message)

    await self._run_thread()
    return await self._get_new_messages()

  async def clear_conversation(self) -> None:
    # Don't actually delete the thread for future reference.
    self._thread = await self._client.beta.threads.create()

  async def _run_thread(self) -> None:
    run = await self._client.beta.threads.runs.create(
        thread_id=self._thread.id,
        assistant_id=self._assistant.id)
    while True:
      # _logger.info(pretty(run))
      match run.status:
        case "queued" | "in_progress":
          await asyncio.sleep(1) 
        case "failed" | "expired":
          raise RuntimeError(run.last_error)
        case "completed":
          return
        case "requires_action" | "cancelling" | "cancelled" | _:
          raise NotImplementedError(f"Run state {run.status} not supported")
      run = await self._client.beta.threads.runs.retrieve(
          run.id,
          thread_id=self._thread.id)

  async def _get_new_messages(self) -> Iterable[AttributedAnswer]:
    attributed_answers: List[AttributedAnswer] = []
    async for message in self._client.beta.threads.messages.list(
        thread_id=self._thread.id,
        after=self._after,
        order="asc",
    ):
      if message.role != 'assistant':
        continue
      # _logger.info(pretty(message))
      for content in message.content:
        if not isinstance(content, MessageContentText):
          _logger.warn(f"Content unexpected: {content}")
          continue
        attributed_answers.append(
          AttributedAnswer(
              answer=content.text.value,
              citations=[str(annotation)
                           for annotation in content.text.annotations],
          )
        )
      # Remember the last message processed so that the next iteration can begin
      # after this message.
      self._after = message.id

    return attributed_answers
