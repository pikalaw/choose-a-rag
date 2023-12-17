const api = '/api';

export interface AttributedAnswer {
  answer: string;
  citations?: string[];
  score?: number;
}

export type Stack =
  | 'openai'
  | 'google'
  | 'hyde-gpt4'
  | 'hyde-gemini-pro'
  | 'hyde-gemini-ultra'
  | 'multi-query-gpt4'
  | 'multi-query-gemini-pro'
  | 'multi-query-gemini-ultra'
  | 'reranker-gpt4'
  | 'reranker-gemini-pro'
  | 'reranker-gemini-ultra'
  | 'window-google'
  | 'everything-gpt4'
  | 'everything-gemini-pro'
  | 'everything-gemini-ultra';

export const stackNames: {
  [key in Stack]: string;
} = {
  openai: 'ChatGPT-4 Assistant',
  google: 'Google AQA',
  'hyde-gpt4': 'HyDE + ChatGPT-4',
  'hyde-gemini-pro': 'HyDE + Gemini Pro',
  'hyde-gemini-ultra': 'HyDE + Gemini Ultra',
  'multi-query-gpt4': 'Multi-query + ChatGPT-4',
  'multi-query-gemini-pro': 'Multi-query + Gemini Pro',
  'multi-query-gemini-ultra': 'Multi-query + Gemini Ultra',
  'reranker-gpt4': 'Reranking + ChatGPT-4',
  'reranker-gemini-pro': 'Reranking + Gemini Pro',
  'reranker-gemini-ultra': 'Reranking + Gemini Ultra',
  'window-google': 'Windowed markdown + Google AQA',
  'everything-gpt4': 'Multi-query + Reranking + Windowed markdown + ChatGPT-4',
  'everything-gemini-pro':
    'Multi-query + Reranking + Windowed markdown + Gemini Pro',
  'everything-gemini-ultra':
    'Multi-query + Reranking + Windowed markdown + Gemini Ultra',
};
export const stacks = Object.keys(stackNames).map(n => n as Stack);

export async function get({stack}: {stack: Stack}): Promise<void> {
  const response = await fetch(`${api}/${stack}/new`, {
    method: 'POST',
  });
  if (!response.ok) {
    const message = await response.json();
    throw new Error(message.message);
  }
}

export async function listFiles({stack}: {stack: Stack}): Promise<string[]> {
  const response = await fetch(`${api}/${stack}/list-files`, {
    method: 'GET',
  });
  if (!response.ok) {
    const message = await response.json();
    throw new Error(message.message);
  }
  return await response.json();
}

export async function addFiles({
  stack,
  files,
}: {
  stack: Stack;
  files: FileList | File[];
}): Promise<void> {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    formData.append('files', file, file.name);
  }

  const response = await fetch(`${api}/${stack}/add-files`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const message = await response.json();
    throw new Error(message.message);
  }
}

export async function clearFiles({stack}: {stack: Stack}): Promise<void> {
  const response = await fetch(`${api}/${stack}/clear-files`, {
    method: 'POST',
  });
  if (!response.ok) {
    const message = await response.json();
    throw new Error(message.message);
  }
}

export async function addConversation({
  stack,
  message,
}: {
  stack: Stack;
  message: string;
}): Promise<AttributedAnswer[]> {
  const response = await fetch(`${api}/${stack}/add-conversation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({text: message}),
  });
  if (!response.ok) {
    const message = await response.json();
    throw new Error(message.message);
  }
  const answers: AttributedAnswer[] = await response.json();
  return answers;
}

export async function clearConversation({
  stack,
}: {
  stack: Stack;
}): Promise<void> {
  const response = await fetch(`${api}/${stack}/clear-conversation`, {
    method: 'POST',
  });
  if (!response.ok) {
    const message = await response.json();
    throw new Error(message.message);
  }
}
