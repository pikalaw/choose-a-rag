from fastapi import FastAPI, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
from pydantic import BaseModel
from typing import Any, List, Literal, Type
from .base_rag import AttributedAnswer, BaseRag
from .google_rag import GoogleRag
from .llama_rag import LlamaRag
from .openai_rag import OpenaiRag


app = FastAPI()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# CORS.
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Any) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": exc.message},
        headers={
            "Access-Control-Allow-Origin": "*",
        }
    )


class UserMessage(BaseModel):
    text: str


StackId = Literal["openai", "google", "llama"]
stack_types: dict[StackId, Type[BaseRag]] = {
  "openai": OpenaiRag,
  "google": GoogleRag,
  "llama": LlamaRag,
}
stacks: dict[StackId, BaseRag | None] = {
  stack: None for stack in stack_types.keys()
}


def get_stack(stack: str) -> BaseRag:
  s = stacks[stack]
  if s is None:
    raise RuntimeError(f"Stack {stack} hasn't been loaded yet")
  return s


@app.post('/api/{stack}/new')
async def new_stack(stack: str) -> None:
  # We just reuse an existing one.
  stacks[stack] = await stack_types[stack].get_default()


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
