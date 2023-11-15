import {
  getElement,
  loadTemplate,
  htmlToElement,
  markdown,
} from './common/view_model.js';
import './flashing_dots.js';
import './rating_thumbs.js';
import type * as api from './api.js';
import {RatingEvent, ratingEventName, RatingThumbs} from './rating_thumbs.js';

/// query event.
export const queryEventName = 'query';
export interface QueryEvent {
  text: string;
}

export class ChatBox extends HTMLElement {
  readonly openai: ChatBoxStack;
  readonly google: ChatBoxStack;
  readonly llama: ChatBoxStack;

  private readonly all: ChatBoxStack[];

  constructor() {
    super();
    loadTemplate('#chat-box', {into: this});

    this.openai = getElement<ChatBoxStack>('.stack.openai', {from: this});
    this.google = getElement<ChatBoxStack>('.stack.google', {from: this});
    this.llama = getElement<ChatBoxStack>('.stack.llama', {from: this});
    this.all = [this.openai, this.google, this.llama];

    this.openai.addEventListener(ratingEventName, event => {
      const rating = (event as CustomEvent<RatingEvent>).detail.thumb;
      if (rating === 'up') {
        this.google.thumb.turnRatingThumb('down');
        this.llama.thumb.turnRatingThumb('down');
      }
    });
    this.google.addEventListener(ratingEventName, event => {
      const rating = (event as CustomEvent<RatingEvent>).detail.thumb;
      if (rating === 'up') {
        this.openai.thumb.turnRatingThumb('down');
        this.llama.thumb.turnRatingThumb('down');
      }
    });
    this.llama.addEventListener(ratingEventName, event => {
      const rating = (event as CustomEvent<RatingEvent>).detail.thumb;
      if (rating === 'up') {
        this.openai.thumb.turnRatingThumb('down');
        this.google.thumb.turnRatingThumb('down');
      }
    });

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

  getStack(stack: api.Stack): ChatBoxStack | undefined {
    switch (stack) {
      case 'openai':
        return this.openai;
      case 'google':
        return this.google;
      case 'llama':
        return this.llama;
      default:
        return undefined;
    }
  }

  shuffleStacks() {
    const newOrder = Array.from(Array(this.all.length), (_, i) => i + 1).map(
      x => String(x)
    );
    shuffleArray(newOrder);

    for (let i = 0; i < newOrder.length; i++) {
      this.all[i].style.order = newOrder[i];
    }
  }

  turnFlashingDots(mode: 'visible' | 'hidden') {
    for (const stack of this.all) {
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
    for (const stack of this.all) {
      stack.addMyMessage({sender, message});
    }
  }

  addTheirMessage({sender, message}: {sender: string; message: string}) {
    for (const stack of this.all) {
      stack.addTheirMessage({sender, message});
    }
  }

  clearMessage() {
    for (const stack of this.all) {
      stack.clearMessage();
    }
  }
}
customElements.define('chat-box', ChatBox);

/// Events: RatingEvent
export class ChatBoxStack extends HTMLElement {
  readonly thumb: RatingThumbs;

  constructor() {
    super();
    loadTemplate('#chat-box-stack', {into: this});

    this.thumb = getElement<RatingThumbs>('.rating', {from: this});
  }

  turnFlashingDots(mode: 'visible' | 'hidden') {
    const dots = getElement('.flashing-dots', {from: this});
    if (mode === 'visible') {
      this.thumb.style.visibility = 'hidden';
    }
    dots.style.visibility = mode;
    if (mode === 'hidden') {
      this.thumb.style.visibility = 'visible';
    }
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

function shuffleArray(array: unknown[]) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}
