export async function getWelcome(): Promise<string> {
  const response = await fetch('http://localhost:8001/');
  const message = await response.json();
  return message.message;
}

export async function openaiGet(): Promise<void> {
  await fetch('http://localhost:8001/openai/new', {
    method: 'POST',
  });
}

export async function openaiClearFiles(): Promise<void> {
  await fetch('http://localhost:8001/openai/clear-files', {
    method: 'POST',
  });
}

export interface AttributedAnswer {
  answer: string;
  citations?: string[];
}

export async function openaiAddConversation(
  message: string
): Promise<AttributedAnswer[]> {
  const response = await fetch(
    'http://localhost:8001/openai/add-conversation',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({text: message}),
    }
  );
  const answers: AttributedAnswer[] = await response.json();
  return answers;
}

export async function openaiClearConversation(): Promise<void> {
  await fetch('http://localhost:8001/openai/clear-conversation', {
    method: 'POST',
  });
}
