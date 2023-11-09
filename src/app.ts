import './chat_box.js';
import {ChatBox, QueryEvent, queryEventName} from './chat_box.js';
import {getElement} from './common/view_model.js';
import * as api from './api.js';

const welcomeMessage = 'How can I help?';

const chatBox = getElement<ChatBox>('chat-box', {from: document});
chatBox.turnQueryBox('enabled', welcomeMessage);
chatBox.turnFlashingDots('hidden');
chatBox.addEventListener(queryEventName, async event => {
  chatBox.turnQueryBox('disabled', 'Thinking...');
  chatBox.turnFlashingDots('visible');

  const query = (event as CustomEvent<QueryEvent>).detail.text;
  chatBox.addMyMessage({sender: 'User', message: query});

  try {
    const answers = await api.openaiAddConversation(query);
    for (const answer of answers) {
      chatBox.addTheirMessage({sender: 'GPT', message: answer.answer});
      chatBox.addTheirMessage({
        sender: 'GPT-citations',
        message: answer.citations?.join('\n') ?? '-',
      });
    }
  } catch (error) {
    chatBox.addTheirMessage({sender: 'SYSTEM', message: String(error)});
  }

  chatBox.turnQueryBox('enabled', welcomeMessage);
  chatBox.turnFlashingDots('hidden');
});

async function start() {
  await api.openaiGet();
}
start();
