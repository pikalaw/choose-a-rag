import {getElement, loadTemplate} from './common/view_model.js';

export type Rating = 'up' | 'down';

export const ratingEventName = 'rating';
export interface RatingEvent {
  thumb: Rating;
}

export class RatingThumbs extends HTMLElement {
  constructor() {
    super();
    loadTemplate('#rating-thumbs', {into: this});

    const thumb = getElement('.fa', {from: this});
    thumb.addEventListener('click', () => {
      if (this.rating === 'up') {
        this.turnRatingThumb('down');
      } else if (this.rating === 'down') {
        this.turnRatingThumb('up');
      }

      this.dispatchEvent(
        new CustomEvent<RatingEvent>(ratingEventName, {
          detail: {thumb: this.rating},
          bubbles: true,
          composed: true,
        })
      );
    });
  }

  get rating(): Rating {
    const thumb = getElement('.fa', {from: this});
    if (thumb.classList.contains('fa-thumbs-up')) {
      return 'up';
    }
    return 'down';
  }

  turnRatingThumb(mode: Rating) {
    const thumb = getElement('.fa', {from: this});
    if (mode === 'up') {
      thumb.classList.add('fa-thumbs-up');
      thumb.classList.remove('fa-thumbs-down');
    } else {
      thumb.classList.add('fa-thumbs-down');
      thumb.classList.remove('fa-thumbs-up');
    }
  }
}
customElements.define('rating-thumbs', RatingThumbs);
