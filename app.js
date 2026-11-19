'use strict';

document.documentElement.classList.add('js');
const english = document.documentElement.lang === 'en';
const say = (ko, en) => english ? en : ko;

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
function closeMenu(restoreFocus = false) {
  navigation?.classList.remove('is-open');
  menuButton?.setAttribute('aria-expanded', 'false');
  if (restoreFocus) menuButton?.focus();
}
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('is-open', open);
});
navigation?.addEventListener('click', event => {
  if (event.target.closest('a')) closeMenu();
});
document.addEventListener('click', event => {
  if (!event.target.closest('.site-header')) closeMenu();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') closeMenu(true);
});
window.matchMedia('(min-width: 851px)').addEventListener('change', () => closeMenu());

// Keep the visitor on the equivalent page, section, and gallery/game filter.
document.querySelectorAll('.languages a').forEach(link => {
  if (link.getAttribute('hreflang') === document.documentElement.lang) return;
  link.addEventListener('click', () => {
    const url = new URL(link.href);
    url.search = window.location.search;
    url.hash = window.location.hash;
    link.href = url.href;
  });
});

document.querySelectorAll('[data-filter-group]').forEach(group => {
  const gallery = group.dataset.filterGroup === 'gallery';
  const cards = Array.from(document.querySelectorAll(gallery ? '.gallery-card' : '.game-card'));
  const buttons = Array.from(group.querySelectorAll('button'));
  const status = document.querySelector('[data-filter-status]');
  group.hidden = false;
  function filter(value, updateUrl) {
    const selected = buttons.find(button => button.dataset.filter === value) ? value : 'all';
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === selected)));
    cards.forEach(card => { card.hidden = selected !== 'all' && card.dataset.category !== selected; });
    if (status) status.textContent = say(`${cards.filter(card => !card.hidden).length}개의 화면`, `${cards.filter(card => !card.hidden).length} screens`);
    if (updateUrl) {
      const url = new URL(window.location.href);
      if (selected === 'all') url.searchParams.delete('filter');
      else url.searchParams.set('filter', selected);
      // file:// previews can reject history updates. Filtering still works.
      try { window.history.replaceState(null, '', url); } catch { /* no persistence needed */ }
    }
  }
  buttons.forEach(button => button.addEventListener('click', () => filter(button.dataset.filter, true)));
  filter(new URL(window.location.href).searchParams.get('filter') || 'all', false);
});

const dialog = document.querySelector('#lightbox');
const lightboxImage = document.querySelector('#lightbox-image');
let activeImages = [];
let imageIndex = 0;
let imageTrigger = null;
function showImage(index) {
  imageIndex = (index + activeImages.length) % activeImages.length;
  const link = activeImages[imageIndex];
  lightboxImage.src = link.dataset.preview;
  lightboxImage.alt = link.querySelector('img').alt;
  document.querySelector('#lightbox-title').textContent = link.dataset.title;
  document.querySelector('#original-image').href = link.href;
  document.querySelector('#image-position').textContent = `${imageIndex + 1} / ${activeImages.length}`;
  document.querySelector('#previous-image').disabled = activeImages.length < 2;
  document.querySelector('#next-image').disabled = activeImages.length < 2;
}
document.querySelectorAll('[data-lightbox]').forEach(link => {
  link.addEventListener('click', event => {
    if (typeof dialog?.showModal !== 'function' || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    imageTrigger = link;
    activeImages = Array.from(document.querySelectorAll('[data-lightbox]')).filter(item => !item.closest('[hidden]'));
    showImage(activeImages.indexOf(link));
    dialog.showModal();
    document.body.classList.add('dialog-open');
    document.querySelector('#close-lightbox').focus();
  });
});
document.querySelector('#close-lightbox')?.addEventListener('click', () => dialog.close());
document.querySelector('#previous-image')?.addEventListener('click', () => showImage(imageIndex - 1));
document.querySelector('#next-image')?.addEventListener('click', () => showImage(imageIndex + 1));
dialog?.addEventListener('close', () => {
  document.body.classList.remove('dialog-open');
  lightboxImage.removeAttribute('src');
  imageTrigger?.focus();
});
dialog?.addEventListener('keydown', event => {
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault();
    showImage(imageIndex + (event.key === 'ArrowLeft' ? -1 : 1));
  }
});
dialog?.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const box = dialog.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
});

document.querySelectorAll('[data-print]').forEach(button => {
  button.hidden = false;
  button.addEventListener('click', () => window.print());
});

const supportForm = document.querySelector('#support-form');
if (supportForm?.dataset.email) supportForm.querySelector('button[type="submit"]').disabled = false;
supportForm?.addEventListener('submit', event => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.dataset.email || !form.reportValidity()) return;
  const subject = say('[리멤픽] ', '[RememPic] ') + document.querySelector('#topic').value;
  const body = document.querySelector('#message').value.trim();
  if (!body) return;
  const draft = `mailto:${form.dataset.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  window.location.href = draft;
  document.querySelector('#form-status').textContent = say(
    '이메일 앱에서 내용을 확인하고 직접 전송해 주세요. 앱이 열리지 않으면 위 주소로 직접 메일을 보내주세요. 이 사이트에는 접수되지 않았습니다.',
    'Review and send the draft in your email app. If it did not open, write directly to the address above. Nothing has been submitted to this website.'
  );
});
