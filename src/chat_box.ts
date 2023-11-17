import {
  getElement,
  getElementAll,
  loadTemplate,
  htmlToElement,
  markdown,
} from './common/view_model.js';
import './flashing_dots.js';
import * as api from './api.js';

/// query event.
export const queryEventName = 'query';
export interface QueryEvent {
  text: string;
}

/// stack change event.
export const stackChangeEventName = 'stack-change';
export interface StackChangeEvent {
  new_stack: api.Stack | undefined;
  target: ChatBoxStack;
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

  get stacks(): ChatBoxStack[] {
    return [...getElementAll<ChatBoxStack>('.stack', {from: this})];
  }

  turnFlashingDots(mode: 'visible' | 'hidden') {
    for (const stack of this.stacks) {
      stack.turnFlashingDots(mode);
    }
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

  addMyMessage({sender, message}: {sender: string; message: string}) {
    for (const stack of this.stacks) {
      stack.addMyMessage({sender, message});
    }
  }

  addTheirMessage({sender, message}: {sender: string; message: string}) {
    for (const stack of this.stacks) {
      stack.addTheirMessage({sender, message});
    }
  }

  clearMessage() {
    for (const stack of this.stacks) {
      stack.clearMessage();
    }
  }
}
customElements.define('chat-box', ChatBox);

/// Events: RatingEvent, StackChangeEvent.
export class ChatBoxStack extends HTMLElement {
  constructor() {
    super();
    loadTemplate('#chat-box-stack', {into: this});

    this.buildStackOptions();

    const stack = this.getAttribute('stack');
    if (stack !== null) {
      this.stack = stack as api.Stack;
    }

    const select = getElement<HTMLInputElement>('.stack-options', {from: this});
    select.addEventListener('change', () => {
      this.dispatchEvent(
        new CustomEvent<StackChangeEvent>(stackChangeEventName, {
          detail: {new_stack: this.stack, target: this},
          bubbles: true,
          composed: true,
        })
      );
    });
  }

  get stack(): api.Stack | undefined {
    const stack = getElement<HTMLInputElement>('.stack-options', {from: this});
    if (stack.value === '') return undefined;
    return stack.value as api.Stack;
  }

  set stack(s: api.Stack | undefined) {
    const stack = getElement<HTMLInputElement>('.stack-options', {from: this});
    if (s === undefined) stack.value = '';
    stack.value = s as string;
  }

  turnFlashingDots(mode: 'visible' | 'hidden') {
    const dots = getElement('.flashing-dots', {from: this});
    dots.style.visibility = mode;
  }

  addMyMessage({sender, message}: {sender: string; message: string}) {
    const li = document.createElement(
      'chat-box-my-message'
    ) as ChatBoxMyMessage;

    li.sender = sender;
    li.message = message;

    const ul = getElement('.messages', {from: this});
    ul.appendChild(li);
  }

  addTheirMessage({sender, message}: {sender: string; message: string}) {
    const li = document.createElement(
      'chat-box-their-message'
    ) as ChatBoxTheirMessage;

    li.sender = sender;
    li.message = message;

    const ul = getElement('.messages', {from: this});
    ul.appendChild(li);
  }

  clearMessage() {
    const ul = getElement('.messages', {from: this});
    ul.innerHTML = '';
  }

  updateFileList(filenames: string[]) {
    const div = getElement<HTMLElement>('.file-list', {from: this});
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

  private buildStackOptions() {
    const select = getElement<HTMLInputElement>('.stack-options', {from: this});
    for (const stack of api.stacks) {
      const option = document.createElement('option') as HTMLOptionElement;
      option.value = stack as string;
      option.text = api.stackNames[stack];

      select.appendChild(option);
    }
  }
}
customElements.define('chat-box-stack', ChatBoxStack);

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
