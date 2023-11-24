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
  | 'hyde-palm'
  | 'multi-query-gpt4'
  | 'multi-query-palm'
  | 'reranker-gpt4'
  | 'reranker-palm';

export const stackNames: {
  [key in Stack]: string;
} = {
  openai: 'ChatGPT-4 Assistant',
  google: 'Google AQA',
  'hyde-gpt4': 'HyDE with ChatGPT-4',
  'hyde-palm': 'HyDE with PaLM',
  'multi-query-gpt4': 'Multi-query with ChatGPT-4',
  'multi-query-palm': 'Multi-query with PaLM',
  'reranker-gpt4': 'Reranking with ChatGPT-4',
  'reranker-palm': 'Reranking with PaLM',
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
