import './chat_box.js';
import {
  ChatBox,
  ChatBoxStack,
  QueryEvent,
  queryEventName,
  StackChangeEvent,
  stackChangeEventName,
  StackOrNone,
} from './chat_box.js';
import {getElement} from './common/view_model.js';
import * as api from './api.js';

const welcomeMessage = 'How can I help?';

const chatBox = getElement<ChatBox>('.chat-box', {from: document});

chatBox.turnQueryBox('enabled', welcomeMessage);
chatBox.turnFlashingDots('hidden');

chatBox.addEventListener(queryEventName, async event => {
  turnControls('disabled', 'Running...');

  const query = (event as CustomEvent<QueryEvent>).detail.text;
  if (query.startsWith('<')) {
    await ask({
      chatBoxStack: chatBox.stacks.at(0)!,
      query: query.substring(1).trim(),
    });
  } else if (query.startsWith('>')) {
    await ask({
      chatBoxStack: chatBox.stacks.at(-1)!,
      query: query.substring(1).trim(),
    });
  } else {
    await Promise.all(
      chatBox.stacks.map(chatBoxStack => ask({chatBoxStack, query}))
    );
  }

  turnControls('enabled', welcomeMessage);
});

async function ask({
  chatBoxStack,
  query,
}: {
  chatBoxStack: ChatBoxStack;
  query: string;
}): Promise<void> {
  const stack = chatBoxStack.stack;
  if (stack === 'none') return;

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
        sender: api.stackNames[stack],
        message: answer.answer,
      });
      if (
        answer.citations !== undefined &&
        answer.citations !== null &&
        answer.citations.length > 0
      ) {
        chatBoxStack.addTheirMessages({
          sender: 'Attribution',
          messages: dedup(answer.citations),
        });
      }
      if (answer.score !== undefined && answer.score !== null) {
        chatBoxStack.addTheirMessage({
          sender: 'Answerability probability',
          message: answer.score.toFixed(4),
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

function dedup(sections: string[]): string[] {
  const seen: Set<string> = new Set();
  const unique: string[] = [];
  for (const section of sections) {
    if (seen.has(section)) {
      continue;
    }
    unique.push(section);
    seen.add(section);
  }
  return unique;
}

chatBox.addEventListener(stackChangeEventName, async event => {
  turnControls('disabled', 'Starting...');

  updateStackInUrl();

  const stack = (event as CustomEvent<StackChangeEvent>).detail.target;
  await start(stack);

  turnControls('enabled', welcomeMessage);
});

function updateStackInUrl() {
  const url = new URL(window.location.href);
  url.searchParams.delete('stack');
  for (const stack of chatBox.stacks) {
    url.searchParams.append('stack', stack.stack as string);
  }
  window.history.pushState({}, '', url);
}

const fileUpload = getElement<HTMLInputElement>('#files', {from: document});
fileUpload.addEventListener('change', async () => {
  turnControls('disabled', 'Ingesting files...');

  const files = fileUpload.files;
  if (files !== null) {
    for (const chatBoxStack of chatBox.stacks) {
      if (chatBoxStack.enabledForLoading) {
        await uploadFile(chatBoxStack, files);
      }
    }
  }

  turnControls('enabled', welcomeMessage);
});

async function uploadFile(
  chatBoxStack: ChatBoxStack,
  files: FileList
): Promise<void> {
  const stack = chatBoxStack.stack;
  if (stack === 'none') return;

  chatBoxStack.turnFlashingDots('visible');

  try {
    const newFiles = await getNewFiles(stack, files);
    if (newFiles.length > 0) {
      await api.addFiles({stack, files: newFiles});
    }
    // Always update the file list in case a previous stack has updated
    // this stack's storage.
    chatBoxStack.updateFileList(await api.listFiles({stack}));
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

async function getNewFiles(stack: api.Stack, files: FileList): Promise<File[]> {
  const existingFiles = await api.listFiles({stack});

  const newFiles: File[] = [];
  for (const file of files) {
    if (existingFiles.includes(file.name)) {
      console.warn(
        `Stack ${stack} already has file ${file.name}. Skip loading it again.`
      );
      continue;
    }
    newFiles.push(file);
  }
  return newFiles;
}

const deleteFilesButton = getElement<HTMLInputElement>('.delete-files-button', {
  from: document,
});
deleteFilesButton.addEventListener('click', async () => {
  if (!confirm('Are you sure you want to delete all files?')) {
    return;
  }
  turnControls('disabled', 'Clearing files...');

  for (const chatBoxStack of chatBox.stacks) {
    if (chatBoxStack.enabledForLoading) {
      await clearFiles(chatBoxStack);
    }
  }

  turnControls('enabled', welcomeMessage);
});

async function clearFiles(chatBoxStack: ChatBoxStack) {
  const stack = chatBoxStack.stack;
  if (stack === 'none') return;

  chatBoxStack.turnFlashingDots('visible');
  try {
    await api.clearFiles({stack});
    chatBoxStack.updateFileList(await api.listFiles({stack}));
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

function turnControls(mode: 'enabled' | 'disabled', placeholder: string) {
  const enabled = mode === 'enabled';

  chatBox.turnControls(mode, placeholder);
  fileUpload.disabled = !enabled;
  deleteFilesButton.disabled = !enabled;
}

async function startAll() {
  turnControls('disabled', 'Starting...');

  setChatBoxStacksFromUrl();
  await Promise.all(chatBox.stacks.map(chatBoxStack => start(chatBoxStack)));

  turnControls('enabled', welcomeMessage);
}

function setChatBoxStacksFromUrl() {
  const url = new URL(window.location.href);
  const stackIds = url.searchParams.getAll('stack');
  for (let i = 0; i < chatBox.stacks.length; i++) {
    if (i >= stackIds.length) break;
    chatBox.stacks[i].stack = stackIds[i] as StackOrNone;
  }
}

async function start(chatBoxStack: ChatBoxStack) {
  chatBoxStack.clearMessage();
  chatBoxStack.updateFileList([]);

  const stack = chatBoxStack.stack;
  if (stack === 'none') {
    return;
  }

  chatBoxStack.turnFlashingDots('visible');
  try {
    await api.get({stack});
    chatBoxStack.updateFileList(await api.listFiles({stack}));
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
