import google.ai.generativelanguage as genai
from typing import Iterable


def list_models() -> Iterable[genai.Model]:
  service = genai.ModelServiceClient()
  models = service.list_models(
      request=genai.ListModelsRequest()
  )
  return [model for model in models]


def generate_text(model: str, prompt: str) -> str:
  service = genai.TextServiceClient()
  response = service.generate_text(
      request=genai.GenerateTextRequest(
          model=model,
          prompt=genai.TextPrompt(
              text=prompt)))
  return response.candidates[0].output
