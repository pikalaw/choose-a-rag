import './chat_box.js';
import {ChatBox, QueryEvent, queryEventName} from './chat_box.js';
import {getElement} from './common/view_model.js';
import * as api from './api.js';

const welcomeMessage = 'How can I help?';
const GOOGLE = 'google';
const OPENAI = 'openai';

const chatBox = getElement<ChatBox>('.chat-box', {from: document});

chatBox.turnQueryBox('enabled', welcomeMessage);
chatBox.turnFlashingDots({host: GOOGLE, mode: 'hidden'});
chatBox.turnFlashingDots({host: OPENAI, mode: 'hidden'});

chatBox.addEventListener(queryEventName, async event => {
  chatBox.turnQueryBox('disabled', 'Running...');

  const query = (event as CustomEvent<QueryEvent>).detail.text;
  if (query.startsWith('<')) {
    await queryOpenai(query.slice(1));
  } else if (query.startsWith('>')) {
    await queryGoogle(query.slice(1));
  } else {
    await Promise.all([queryGoogle(query), queryOpenai(query)]);
  }

  chatBox.turnQueryBox('enabled', welcomeMessage);
});

async function queryGoogle(query: string): Promise<void> {
  chatBox.turnFlashingDots({host: GOOGLE, mode: 'visible'});
  chatBox.addMyMessage({host: GOOGLE, sender: 'User', message: query});
  try {
    const answers = await api.googleAddConversation(query);
    for (const answer of answers) {
      chatBox.addTheirMessage({
        host: GOOGLE,
        sender: 'Google',
        message: answer.answer,
      });
      if (answer.citations?.length ?? 0 > 0) {
        chatBox.addTheirMessage({
          host: GOOGLE,
          sender: 'Citations',
          message: answer.citations?.join('\n') ?? '-',
        });
      }
    }
  } catch (error) {
    chatBox.addTheirMessage({
      host: GOOGLE,
      sender: 'SYSTEM',
      message: String(error),
    });
  }
  chatBox.turnFlashingDots({host: GOOGLE, mode: 'hidden'});
}

async function queryOpenai(query: string): Promise<void> {
  chatBox.turnFlashingDots({host: OPENAI, mode: 'visible'});
  chatBox.addMyMessage({host: OPENAI, sender: 'User', message: query});
  try {
    const answers = await api.openaiAddConversation(query);
    for (const answer of answers) {
      chatBox.addTheirMessage({
        host: OPENAI,
        sender: 'OpenAI',
        message: answer.answer,
      });
      if (answer.citations?.length ?? 0 > 0) {
        chatBox.addTheirMessage({
          host: OPENAI,
          sender: 'Citations',
          message: answer.citations?.join('\n') ?? '-',
        });
      }
    }
  } catch (error) {
    chatBox.addTheirMessage({
      host: OPENAI,
      sender: 'SYSTEM',
      message: String(error),
    });
  }
  chatBox.turnFlashingDots({host: OPENAI, mode: 'hidden'});
}

const fileUpload = getElement<HTMLInputElement>('#files', {from: document});
fileUpload.addEventListener('change', async () => {
  chatBox.turnQueryBox('disabled', 'Ingesting files...');

  const files = fileUpload.files;
  if (files !== null) {
    await Promise.all([googleFileUpload(files), openaiFileUpload(files)]);
  }

  chatBox.turnQueryBox('enabled', welcomeMessage);
});

async function googleFileUpload(files: FileList): Promise<void> {
  chatBox.turnFlashingDots({host: GOOGLE, mode: 'visible'});
  await api.googleAddFiles(files);
  updateFileList({host: GOOGLE, filenames: await api.googleListFiles()});
  chatBox.turnFlashingDots({host: GOOGLE, mode: 'hidden'});
}

async function openaiFileUpload(files: FileList): Promise<void> {
  chatBox.turnFlashingDots({host: OPENAI, mode: 'visible'});
  await api.openaiAddFiles(files);
  updateFileList({host: OPENAI, filenames: await api.openaiListFiles()});
  chatBox.turnFlashingDots({host: OPENAI, mode: 'hidden'});
}

function updateFileList({
  host,
  filenames,
}: {
  host: string;
  filenames: string[];
}) {
  const div = getElement<HTMLElement>(`.file-list.${host}`, {from: document});
  div.innerHTML = filenames.map(fn => `<li>${fn}</li>`).join('\n');
}

async function startAll() {
  chatBox.turnQueryBox('disabled', 'Starting...');
  await Promise.all([startGoogle(), startOpenai()]);
  chatBox.turnQueryBox('enabled', welcomeMessage);
}

async function startGoogle() {
  chatBox.turnFlashingDots({host: GOOGLE, mode: 'visible'});
  await api.googleGet();
  updateFileList({host: GOOGLE, filenames: await api.googleListFiles()});
  chatBox.turnFlashingDots({host: GOOGLE, mode: 'hidden'});
}

async function startOpenai() {
  chatBox.turnFlashingDots({host: OPENAI, mode: 'visible'});
  await api.openaiGet();
  updateFileList({host: OPENAI, filenames: await api.openaiListFiles()});
  chatBox.turnFlashingDots({host: OPENAI, mode: 'hidden'});
}

startAll();
