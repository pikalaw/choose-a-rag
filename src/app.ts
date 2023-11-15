import './chat_box.js';
import {ChatBox, QueryEvent, queryEventName} from './chat_box.js';
import {getElement} from './common/view_model.js';
import * as api from './api.js';

const welcomeMessage = 'How can I help?';

const chatBox = getElement<ChatBox>('.chat-box', {from: document});

chatBox.turnQueryBox('enabled', welcomeMessage);
chatBox.turnFlashingDots('hidden');

chatBox.addEventListener(queryEventName, async event => {
  chatBox.turnQueryBox('disabled', 'Running...');

  const query = (event as CustomEvent<QueryEvent>).detail.text;
  await Promise.all([
    ask({stack: 'google', query}),
    ask({stack: 'llama', query}),
    ask({stack: 'openai', query}),
  ]);

  chatBox.turnQueryBox('enabled', welcomeMessage);
});

async function ask({
  stack,
  query,
}: {
  stack: api.Stack;
  query: string;
}): Promise<void> {
  const chatBoxStack = chatBox.getStack(stack)!;
  chatBoxStack.turnFlashingDots('visible');
  chatBoxStack.addMyMessage({sender: 'User', message: query});
  try {
    const answers = await api.addConversation({
      stack,
      message: query,
    });
    for (const answer of answers) {
      chatBoxStack.addTheirMessage({
        sender: 'Google',
        message: answer.answer,
      });
      /*
      if (
        answer.citations !== undefined &&
        answer.citations !== null &&
        answer.citations.length > 0
      ) {
        chatBoxStack.addTheirMessage({
          sender: 'Citations',
          message: answer.citations.map(c => `* ${c}`).join('\n'),
        });
      }
      if (answer.score !== undefined && answer.score !== null) {
        chatBoxStack.addTheirMessage({
          sender: 'Answerability score',
          message: String(answer.score),
        });
      }
      */
    }
  } catch (error) {
    console.error(error);
    if (error instanceof Error) {
      chatBoxStack.addTheirMessage({
        sender: 'SYSTEM',
        message: error.message,
      });
    }
  }
  chatBoxStack.turnFlashingDots('hidden');
}

function updateFileList({
  host,
  filenames,
}: {
  host: string;
  filenames: string[];
}) {
  const div = getElement<HTMLElement>(`.file-list.${host}`, {from: document});
  div.innerHTML = filenames
    .sort((a, b) => {
      const lowerCaseA = a.toLowerCase();
      const lowerCaseB = b.toLowerCase();
      if (lowerCaseA < lowerCaseB) {
        return -1;
      }
      if (lowerCaseA > lowerCaseB) {
        return 1;
      }
      return 0;
    })
    .map(fn => `<li>${fn}</li>`)
    .join('\n');
}

async function startAll() {
  chatBox.turnQueryBox('disabled', 'Starting...');
  await Promise.all([start('google'), start('llama'), start('openai')]);
  chatBox.turnQueryBox('enabled', welcomeMessage);
}

async function start(stack: api.Stack) {
  const chatBoxStack = chatBox.getStack(stack)!;
  chatBoxStack.turnFlashingDots('visible');
  try {
    await api.get({stack});
  } catch (error) {
    console.error(error);
    if (error instanceof Error) {
      chatBoxStack.addTheirMessage({
        sender: 'SYSTEM',
        message: error.message,
      });
    }
  }
  chatBoxStack.turnFlashingDots('hidden');
}

startAll();
