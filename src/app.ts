import './chat_box.js';
import {ChatBox, QueryEvent, queryEventName} from './chat_box.js';
import {getElement} from './common/view_model.js';

const welcomeMessage = 'How can I help?';

const chatBox = getElement<ChatBox>('chat-box', {from: document});
chatBox.turnQueryBox('enabled', welcomeMessage);
chatBox.turnFlashingDots('hidden');
chatBox.addEventListener(queryEventName, async event => {
  chatBox.turnQueryBox('disabled', 'Thinking...');
  chatBox.turnFlashingDots('visible');

  const query = (event as CustomEvent<QueryEvent>).detail.text;
  window.alert(`got ${query}`);

  chatBox.turnQueryBox('enabled', welcomeMessage);
  chatBox.turnFlashingDots('hidden');
});
