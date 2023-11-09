from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from .base_rag import AttributedAnswer
from .openai_rag import OpenaiRag


app = FastAPI()


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


openai: OpenaiRag | None


class UserMessage(BaseModel):
    text: str


@app.post('/openai/new')
async def openai_new() -> None:
  global openai
  # We just reuse an existing one.
  openai = await OpenaiRag.get()


@app.post('/openai/add_file')
async def openai_add_file(file: UploadFile) -> None:
  if openai is None:
    raise RuntimeError("OpenAI assistant hasn't loaded yet")
  assert file.filename is not None
  assert file.content_type is not None
  await openai.add_file(
      filename=file.filename, content=file.file, content_type=file.content_type)


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
