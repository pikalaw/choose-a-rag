import google.ai.generativelanguage as genai
from google.api_core import client_options as client_options_lib
from typing import Iterable


# _DEFAULT_API_ENDPOINT = "autopush-generativelanguage.sandbox.googleapis.com"
_DEFAULT_API_ENDPOINT = None


def list_models() -> Iterable[genai.Model]:
    service = genai.ModelServiceClient(
        client_options=client_options_lib.ClientOptions(
            api_endpoint=_DEFAULT_API_ENDPOINT
        ),
    )
    models = service.list_models(request=genai.ListModelsRequest())
    return [model for model in models]


def generate_text(model: str, prompt: str) -> str:
    service = genai.TextServiceClient(
        client_options=client_options_lib.ClientOptions(
            api_endpoint=_DEFAULT_API_ENDPOINT
        ),
    )
    response = service.generate_text(
        request=genai.GenerateTextRequest(
            model=model, temperature=0.2, prompt=genai.TextPrompt(text=prompt)
        )
    )
    candidates = list(response.candidates)
    if len(candidates) == 0:
        return ""
    candidate = candidates[0]
    return str(candidate.output)


def generate_content(model: str, prompt: str) -> str:
    service = genai.GenerativeServiceClient(
        client_options=client_options_lib.ClientOptions(
            api_endpoint=_DEFAULT_API_ENDPOINT
        ),
    )
    response = service.generate_content(
        request=genai.GenerateContentRequest(
            model=model,
            contents=[
                genai.Content(
                    parts=[
                        genai.Part(text=prompt),
                    ],
                )
            ],
            generation_config=genai.GenerationConfig(
                temperature=0.7,
            ),
        )
    )

    if len(response.candidates) == 0:
        return ""

    candidate = response.candidates[0]

    if len(candidate.content.parts) == 0:
        return ""

    part = candidate.content.parts[0]
    return part.text


def generate_answer(model: str, prompt: str) -> str:
    service = genai.GenerativeServiceClient(
        client_options=client_options_lib.ClientOptions(
            api_endpoint=_DEFAULT_API_ENDPOINT
        ),
    )
    response = service.generate_answer(
        request=genai.GenerateAnswerRequest(
            model=model,
            contents=[
                genai.Content(
                    parts=[
                        genai.Part(text=prompt),
                    ],
                )
            ],
        )
    )
    return response.answer.content.parts[0].text
