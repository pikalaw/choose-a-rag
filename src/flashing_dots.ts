import {loadTemplate} from './common/view_model.js';

export class FlashingDots extends HTMLElement {
  constructor() {
    super();
    loadTemplate('#flashing-dots', {into: this});
  }
}
customElements.define('flashing-dots', FlashingDots);
