import './chat_box.js';
import {ChatBox, ChatBoxStack, QueryEvent, queryEventName} from './chat_box.js';
import {getElement} from './common/view_model.js';
import * as api from './api.js';

const welcomeMessage = 'How can I help?';

const chatBox = getElement<ChatBox>('.chat-box', {from: document});

chatBox.turnQueryBox('enabled', welcomeMessage);
chatBox.turnFlashingDots('hidden');

chatBox.addEventListener(queryEventName, async event => {
  chatBox.turnQueryBox('disabled', 'Running...');

  const query = (event as CustomEvent<QueryEvent>).detail.text;
  await Promise.all(
    chatBox.stacks.map(chatBoxStack => ask({chatBoxStack, query}))
  );

  chatBox.turnQueryBox('enabled', welcomeMessage);
});

async function ask({
  chatBoxStack,
  query,
}: {
  chatBoxStack: ChatBoxStack;
  query: string;
}): Promise<void> {
  const stack = chatBoxStack.stack;
  if (stack === undefined) return;

  chatBoxStack.turnFlashingDots('visible');
  chatBoxStack.clearMessage();
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
  await Promise.all(chatBox.stacks.map(chatBoxStack => start(chatBoxStack)));
  chatBox.turnQueryBox('enabled', welcomeMessage);
}

async function start(chatBoxStack: ChatBoxStack) {
  const stack = chatBoxStack.stack;
  if (stack === undefined) return;

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
