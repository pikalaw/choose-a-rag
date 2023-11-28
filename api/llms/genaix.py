import google.ai.generativelanguage as genai
from google.api_core import client_options as client_options_lib
from typing import Iterable


_DEFAULT_API_ENDPOINT = "autopush-generativelanguage.sandbox.googleapis.com"


def list_models() -> Iterable[genai.Model]:
  service = genai.ModelServiceClient(
      client_options=client_options_lib.ClientOptions(
          api_endpoint=_DEFAULT_API_ENDPOINT
      ),
  )
  models = service.list_models(
      request=genai.ListModelsRequest()
  )
  return [model for model in models]


def generate_text(model: str, prompt: str) -> str:
  service = genai.TextServiceClient(
      client_options=client_options_lib.ClientOptions(
          api_endpoint=_DEFAULT_API_ENDPOINT
      ),
  )
  response = service.generate_text(
      request=genai.GenerateTextRequest(
          model=model,
          prompt=genai.TextPrompt(
              text=prompt)))
  candidates = list(response.candidates)
  if len(candidates) == 0:
    return ''
  candidate = candidates[0]
  return str(candidate.output)
