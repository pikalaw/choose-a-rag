from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import logging
from pydantic import BaseModel
from typing import List
from .base_rag import AttributedAnswer
from .google_rag import GoogleRag
from .openai_rag import OpenaiRag


app = FastAPI()
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


# CORS.
origins = [
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Hello World'}


class UserMessage(BaseModel):
    text: str


# openai
openai: OpenaiRag | None


@app.post('/openai/new')
async def openai_new() -> None:
  global openai
  # We just reuse an existing one.
  openai = await OpenaiRag.get()


@app.get('/openai/list-files')
async def openai_list_file() -> List[str]:
  if openai is None:
    raise RuntimeError("OpenAI assistant hasn't loaded yet")
  return list(await openai.list_files())


@app.post('/openai/add-files')
async def openai_add_file(files: List[UploadFile]) -> None:
  if openai is None:
    raise RuntimeError("OpenAI assistant hasn't loaded yet")
  for file in files:
    assert file.filename is not None
    assert file.content_type is not None
    await openai.add_file(
        filename=file.filename,
        content=file.file,
        content_type=file.content_type)


@app.post('/openai/clear-files')
async def openai_clear_files() -> None:
  if openai is None:
    raise RuntimeError("OpenAI assistant hasn't loaded yet")
  await openai.clear_files()


@app.post('/openai/add-conversation')
async def openai_add_conversation(message: UserMessage) -> List[AttributedAnswer]:
  if openai is None:
    raise RuntimeError("OpenAI assistant hasn't loaded yet")
  return list(await openai.add_conversation(message.text))


@app.post('/openai/clear-conversation')
async def openai_clear_conversation() -> None:
  if openai is None:
    raise RuntimeError("OpenAI assistant hasn't loaded yet")
  await openai.clear_conversation()


# openai
google: GoogleRag | None


@app.post('/google/new')
async def google_new() -> None:
  global google
  # Try to reuse an existing one.
  google = await GoogleRag.get()


@app.get('/google/list-files')
async def google_list_file() -> List[str]:
  if google is None:
    raise RuntimeError("Google assistant hasn't loaded yet")
  return list(await google.list_files())


@app.post('/google/add-files')
async def google_add_file(files: List[UploadFile]) -> None:
  if google is None:
    raise RuntimeError("Google assistant hasn't loaded yet")
  for file in files:
    assert file.filename is not None
    assert file.content_type is not None
    await google.add_file(
        filename=file.filename,
        content=file.file,
        content_type=file.content_type)


@app.post('/google/clear-files')
async def google_clear_files() -> None:
  if google is None:
    raise RuntimeError("Google assistant hasn't loaded yet")
  await google.clear_files()


@app.post('/google/add-conversation')
async def google_add_conversation(message: UserMessage) -> List[AttributedAnswer]:
  if google is None:
    raise RuntimeError("Google assistant hasn't loaded yet")
  return list(await google.add_conversation(message.text))


@app.post('/google/clear-conversation')
async def google_clear_conversation() -> None:
  if google is None:
    raise RuntimeError("Google assistant hasn't loaded yet")
  await google.clear_conversation()
