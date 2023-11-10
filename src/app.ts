import './chat_box.js';
import './file_upload.js';
import {ChatBox, QueryEvent, queryEventName} from './chat_box.js';
import {getElement} from './common/view_model.js';
import {
  FileUpload,
  FileUploadEvent,
  fileUploadEventName,
} from './file_upload.js';
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
    await processOpenai(query.slice(1));
  } else if (query.startsWith('>')) {
    await processGoogle(query.slice(1));
  } else {
    await Promise.all([processGoogle(query), processOpenai(query)]);
  }

  chatBox.turnQueryBox('enabled', welcomeMessage);
});

async function processGoogle(query: string): Promise<void> {
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

async function processOpenai(query: string): Promise<void> {
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

const fileUpload = getElement<FileUpload>('.file-upload', {from: document});
fileUpload.addEventListener(fileUploadEventName, async event => {
  const status = (event as CustomEvent<FileUploadEvent>).detail.status;
  if (status === 'uploading') {
    chatBox.turnQueryBox('disabled', 'Ingesting files...');
    chatBox.turnFlashingDots({host: OPENAI, mode: 'visible'});
    updateFileList([]);
  } else {
    chatBox.turnQueryBox('enabled', welcomeMessage);
    chatBox.turnFlashingDots({host: OPENAI, mode: 'hidden'});
    updateFileList(await api.openaiListFiles());
  }
});

function updateFileList(filenames: string[]) {
  const div = getElement<HTMLElement>('.file-list', {from: document});
  div.innerHTML = filenames.map(fn => `<li>${fn}</li>`).join('\n');
}

async function start() {
  chatBox.turnQueryBox('disabled', 'Starting...');
  Promise.all([api.googleGet(), api.openaiGet()]);
  updateFileList(await api.openaiListFiles());
  chatBox.turnQueryBox('enabled', welcomeMessage);
}
start();
