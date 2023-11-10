import {
  getElement,
  loadTemplate,
  htmlToElement,
  markdown,
} from './common/view_model.js';
import './flashing_dots.js';

/// query event.
export const queryEventName = 'query';
export interface QueryEvent {
  text: string;
}

export class ChatBox extends HTMLElement {
  constructor() {
    super();
    loadTemplate('#chat-box', {into: this});

    const query = getElement<HTMLInputElement>('.query', {from: this});
    query.addEventListener('keyup', event => {
      if (!(event.code === 'Enter' && event.shiftKey === false)) return;
      const text = query.value.trim();
      if (text === '') return;

      query.value = '';
      this.dispatchEvent(
        new CustomEvent<QueryEvent>(queryEventName, {detail: {text}})
      );
    });
  }

  turnFlashingDots({host, mode}: {host: string; mode: 'visible' | 'hidden'}) {
    const dots = getElement(`.host.${host} .flashing-dots`, {from: this});
    dots.style.visibility = mode;
  }

  turnQueryBox(mode: 'enabled' | 'disabled', placeholder = 'Chat with me') {
    const input: HTMLTextAreaElement = getElement('.query', {from: this});
    const enabled = mode === 'enabled';
    input.disabled = !enabled;
    input.placeholder = placeholder;

    if (mode === 'enabled') {
      input.focus();
    }
  }

  addMyMessage({
    host,
    sender,
    message,
  }: {
    host: string;
    sender: string;
    message: string;
  }) {
    const li = document.createElement(
      'chat-box-my-message'
    ) as ChatBoxMyMessage;

    li.sender = sender;
    li.message = message;

    const ul = getElement(`.host.${host} .messages`, {from: this});
    ul.appendChild(li);
  }

  addTheirMessage({
    host,
    sender,
    message,
  }: {
    host: string;
    sender: string;
    message: string;
  }) {
    const li = document.createElement(
      'chat-box-their-message'
    ) as ChatBoxTheirMessage;

    li.sender = sender;
    li.message = message;

    const ul = getElement(`.host.${host} .messages`, {from: this});
    ul.appendChild(li);
  }
}
customElements.define('chat-box', ChatBox);

export class ChatBoxMessage extends HTMLElement {
  constructor(templateSelector: string) {
    super();
    loadTemplate(templateSelector, {into: this});
  }

  set sender(name: string) {
    const div = getElement('.sender', {from: this});
    div!.textContent = name;
  }

  set message(text: string) {
    const div = getElement('.message', {from: this});
    div!.replaceChildren(htmlToElement(markdown(text)));
  }
}

export class ChatBoxMyMessage extends ChatBoxMessage {
  constructor() {
    super('#chat-box-my-message');
  }
}
customElements.define('chat-box-my-message', ChatBoxMyMessage);

export class ChatBoxTheirMessage extends ChatBoxMessage {
  constructor() {
    super('#chat-box-their-message');
  }
}
customElements.define('chat-box-their-message', ChatBoxTheirMessage);
