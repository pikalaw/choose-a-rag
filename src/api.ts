export async function getWelcome(): Promise<string> {
  const response = await fetch('http://localhost:8001/');
  const message = await response.json();
  return message.message;
}

export interface AttributedAnswer {
  answer: string;
  citations?: string[];
}

// openai
export async function openaiGet(): Promise<void> {
  await fetch('http://localhost:8001/openai/new', {
    method: 'POST',
  });
}

export async function openaiListFiles(): Promise<string[]> {
  const response = await fetch('http://localhost:8001/openai/list-files', {
    method: 'GET',
  });
  return await response.json();
}

export async function openaiClearFiles(): Promise<void> {
  await fetch('http://localhost:8001/openai/clear-files', {
    method: 'POST',
  });
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

// google
export async function googleGet(): Promise<void> {
  await fetch('http://localhost:8001/google/new', {
    method: 'POST',
  });
}

export async function googleListFiles(): Promise<string[]> {
  const response = await fetch('http://localhost:8001/google/list-files', {
    method: 'GET',
  });
  return await response.json();
}

export async function googleClearFiles(): Promise<void> {
  await fetch('http://localhost:8001/google/clear-files', {
    method: 'POST',
  });
}

export async function googleAddConversation(
  message: string
): Promise<AttributedAnswer[]> {
  const response = await fetch(
    'http://localhost:8001/google/add-conversation',
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

export async function googleClearConversation(): Promise<void> {
  await fetch('http://localhost:8001/google/clear-conversation', {
    method: 'POST',
  });
}
