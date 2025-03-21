from fastapi import FastAPI, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
from pydantic import BaseModel
from typing import Any, cast, List, Literal, Type
from .base_rag import AttributedAnswer, BaseRag
from .naive import GoogleRag, OpenaiRag, PalmRag
from .hyde import (
    HydeGpt4Rag,
    HydeGeminiProRag,
    HydeGeminiUltraRag,
)
from .multi_query import (
    MultiQueryGpt4Rag,
    MultiQueryGeminiProRag,
    MultiQueryGeminiUltraRag,
)
from .reranker import (
    RerankerGpt4Rag,
    RerankerGeminiProRag,
    RerankerGeminiUltraRag,
)
from .window import WindowGoogleRag
from .everything import (
    EverythingGpt4Rag,
    EverythingGeminiProRag,
    EverythingGeminiUltraRag,
)


app = FastAPI()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Any) -> JSONResponse:
    if hasattr(exc, "message"):
      message = exc.message
    else:
      message = str(exc)

    return JSONResponse(
        status_code=500,
        content={"message": message},
        headers={
            "Access-Control-Allow-Origin": "*",
        }
    )


class UserMessage(BaseModel):
    text: str


StackId = Literal[
    "openai",
    "google-aqa",
    "palm",
    "hyde-gpt4",
    "hyde-gemini-pro",
    "hyde-gemini-ultra",
    "multi-query-gpt4",
    "multi-query-gemini-pro",
    "multi-query-gemini-ultra",
    "reranker-gpt4",
    "reranker-gemini-pro",
    "reranker-gemini-ultra",
    "window-google",
    "everything-gpt4",
    "everything-gemini-pro",
    "everything-gemini-ultra",
]
stack_types: dict[StackId, Type[BaseRag]] = {
  "openai": OpenaiRag,
  "google-aqa": GoogleRag,
  "palm": PalmRag,
  "hyde-gpt4": HydeGpt4Rag,
  "hyde-gemini-pro": HydeGeminiProRag,
  "hyde-gemini-ultra": HydeGeminiUltraRag,
  "multi-query-gpt4": MultiQueryGpt4Rag,
  "multi-query-gemini-pro": MultiQueryGeminiProRag,
  "multi-query-gemini-ultra": MultiQueryGeminiUltraRag,
  "reranker-gpt4": RerankerGpt4Rag,
  "reranker-gemini-pro": RerankerGeminiProRag,
  "reranker-gemini-ultra": RerankerGeminiUltraRag,
  "window-google": WindowGoogleRag,
  "everything-gpt4": EverythingGpt4Rag,
  "everything-gemini-pro": EverythingGeminiProRag,
  "everything-gemini-ultra": EverythingGeminiUltraRag,
}
stacks: dict[StackId, BaseRag | None] = {
  stack: None for stack in stack_types.keys()
}


def get_stack(stack: str) -> BaseRag:
  s = stacks[cast(StackId, stack)]
  if s is None:
    raise RuntimeError(f"Stack {stack} hasn't been loaded yet")
  return s


def set_stack(stack: str, instance: BaseRag) -> None:
  stacks[cast(StackId, stack)] = instance


@app.post('/api/{stack}/new')
async def new_stack(stack: str) -> None:
  s = cast(StackId, stack)
  t = stack_types[s]
  if t is None:
    raise RuntimeError(f"Stack type {stack} is unknown")

  # We just reuse an existing one.
  stacks[s] = await t.get_default()


@app.get('/api/{stack}/list-files')
async def list_file(stack: str) -> List[str]:
  return list(await get_stack(stack).list_files())


@app.post('/api/{stack}/add-files')
async def add_file(stack: str, files: List[UploadFile]) -> None:
  for file in files:
    assert file.filename is not None
    assert file.content_type is not None
    await get_stack(stack).add_file(
        filename=file.filename,
        content=file.file,
        content_type=file.content_type)


@app.post('/api/{stack}/clear-files')
async def clear_files(stack: str) -> None:
  await get_stack(stack).clear_files()


@app.post('/api/{stack}/add-conversation')
async def add_conversation(stack: str, message: UserMessage) -> List[AttributedAnswer]:
  return list(await get_stack(stack).add_conversation(message.text))


@app.post('/api/{stack}/clear-conversation')
async def clear_conversation(stack: str) -> None:
  await get_stack(stack).clear_conversation()


app.mount("/", StaticFiles(directory="dist", html=True), name="webapp")
