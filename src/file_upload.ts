import {getElement, loadTemplate} from './common/view_model.js';

/// files event.
export const fileUploadEventName = 'file-upload';
export interface FileUploadEvent {
  status: 'uploading' | 'not-uploading';
}

export class FileUpload extends HTMLElement {
  static observedAttributes = ['url'];

  url: string | undefined;

  constructor() {
    super();
    loadTemplate('#file-upload', {into: this});

    const fileInput = getElement<HTMLInputElement>('#files', {from: this});
    fileInput.addEventListener('change', async () => {
      this.dispatchFileUploadEvent('uploading');
      await this.uploadFiles(fileInput);
      this.dispatchFileUploadEvent('not-uploading');
    });
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string) {
    if (name !== 'url') return;
    if (oldValue === newValue) return;
    this.url = newValue;
  }

  private async uploadFiles(fileInput: HTMLInputElement) {
    if (this.url === undefined) throw new Error('url is not set');

    const files = fileInput.files;
    if (files === null) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      formData.append('files', file, file.name);
    }

    await fetch(this.url, {
      method: 'POST',
      body: formData,
    });
  }

  private dispatchFileUploadEvent(status: 'uploading' | 'not-uploading') {
    this.dispatchEvent(
      new CustomEvent<FileUploadEvent>(fileUploadEventName, {
        detail: {
          status,
        },
      })
    );
  }
}
customElements.define('file-upload', FileUpload);
