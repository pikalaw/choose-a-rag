import {fromEvent, Observable} from 'rxjs';
import {filter, map, startWith} from 'rxjs/operators';
import showdown from 'showdown';

export function getElementAll<T extends HTMLElement>(
  selector: string,
  {from}: {from: HTMLElement | Document}
): NodeListOf<T> {
  const p = from instanceof HTMLElement ? from.shadowRoot : from;
  if (!p) {
    throw new Error(`${selector} has no shadow root`);
  }
  const element = p.querySelectorAll<T>(selector);
  if (element.length === 0) {
    throw new Error(`no element found for ${selector}`);
  }
  return element;
}

export function getElement<T extends HTMLElement>(
  selector: string,
  {from}: {from: HTMLElement | Document}
): T {
  const elements = getElementAll<T>(selector, {from});
  return elements[0];
}

export function loadTemplate(selector: string, {into}: {into: HTMLElement}) {
  into.attachShadow({mode: 'open'});
  const component = cloneTemplate(selector);
  into.shadowRoot!.replaceChildren(component);
}

function cloneTemplate(selector: string): HTMLElement {
  const source = getElement<HTMLTemplateElement>(selector, {from: document});
  return source.content.cloneNode(true) as HTMLElement;
}

export function getChangedValue(selector: string): Observable<string> {
  const element = getElement<HTMLInputElement>(selector, {from: document});
  return fromEvent(element, 'input').pipe(
    map(event => {
      if (!event.target) return undefined;
      const target = event.target as HTMLInputElement;
      return target.value;
    }),
    startWith(element.value),
    filter((value: string | undefined): value is string => !!value)
  );
}

export function htmlToElement(html: string): DocumentFragment {
  const temp = document.createElement('template');
  html = html.trim(); // Never return a space text node as a result
  temp.innerHTML = html;
  return temp.content;
}

export function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function markdown(str: string): string {
  const converter = new showdown.Converter({
    emoji: true,
    literalMidWordUnderscores: true,
    openLinksInNewWindow: true,
    parseImgDimensions: true,
    simplifiedAutoLink: true,
    strikethrough: true,
    tables: true,
  });
  const html = converter.makeHtml(str);
  return html;
}
