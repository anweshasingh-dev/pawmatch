const loadingRoot = document.documentElement;
loadingRoot.dataset.uiReady = 'true';
const mainContent = document.querySelector('#main');
const pendingForms = new Map();
// A normal destination ends a failed or cancelled search instead of carrying it on.
if (!/\/matches\/\d+\/?$/.test(location.pathname)) {
  try { sessionStorage.removeItem('pawmatch.matchSearch'); } catch (_) {}
}

function beginMatchSearch(destination) {
  // Start processing now. Only presentation waits for the three-second minimum.
  try {
    sessionStorage.setItem('pawmatch.matchSearch', JSON.stringify({
      startedAt: Date.now(), destination
    }));
  } catch (_) { /* The results page enforces its own minimum without storage. */ }
  loadingRoot.dataset.loading = 'matches';
  mainContent.setAttribute('aria-busy', 'true');
}

if (loadingRoot.dataset.matchResultsPending) {
  mainContent.setAttribute('aria-busy', 'true');
}

window.addEventListener('pageshow', (event) => {
  // Back/forward restores an existing page, rather than starting a new search.
  if (event.persisted) {
    delete loadingRoot.dataset.loading;
    delete loadingRoot.dataset.matchResultsPending;
    mainContent.removeAttribute('aria-busy');
    try { sessionStorage.removeItem('pawmatch.matchSearch'); } catch (_) {}
  }
  pendingForms.forEach((buttons, form) => {
    form.removeAttribute('aria-busy');
    buttons.forEach(({ button, disabled }) => { button.disabled = disabled; });
    const status = form.querySelector('.submission-status');
    if (status) status.hidden = true;
  });
  pendingForms.clear();
});

document.addEventListener('click', (event) => {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const link = event.target.closest('a[href]');
  if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
  const destination = new URL(link.href, location.href);
  if (destination.origin === location.origin && /\/matches\/\d+\/?$/.test(destination.pathname)) {
    beginMatchSearch(destination.pathname);
  }
});

document.addEventListener('submit', (event) => {
  const form = event.target;
  if (event.defaultPrevented || form.method === 'dialog' || (form.target && form.target !== '_self')) return;
  if (form.matches('[data-report-form]')) beginMatchSearch('report');
  form.setAttribute('aria-busy', 'true');
  const buttons = [...form.querySelectorAll('button[type="submit"], input[type="submit"]')].map((button) => ({ button, disabled: button.disabled }));
  pendingForms.set(form, buttons);
  // Named submit buttons must retain their contribution to the submitted data.
  buttons.forEach(({ button }) => { if (!button.name) button.disabled = true; });
  const status = form.querySelector('.submission-status');
  if (status) status.hidden = false;
});

document.querySelectorAll('.report-photo').forEach((image) => {
  const wrapper = image.closest('[data-photo-state]');
  const ready = () => { image.hidden = false; wrapper.dataset.photoState = 'ready'; };
  const fallback = () => { image.hidden = true; wrapper.dataset.photoState = 'missing'; };
  image.addEventListener('load', ready);
  image.addEventListener('error', fallback);
  if (image.complete) image.naturalWidth === 0 ? fallback() : ready();
});

const upload = document.querySelector('#image');
let previewUrl;
let previewVersion = 0;
if (upload) upload.addEventListener('change', () => {
  const preview = document.querySelector('#photo-preview');
  const hint = document.querySelector('#upload-hint');
  const zone = document.querySelector('.upload-zone');
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  const version = ++previewVersion;
  const file = upload.files[0];
  preview.hidden = true;
  hint.textContent = file ? file.name : 'Choose a photo from your device.';
  zone.removeAttribute('aria-busy');
  if (file) {
    zone.setAttribute('aria-busy', 'true');
    previewUrl = URL.createObjectURL(file);
    preview.onload = () => {
      if (version !== previewVersion) return;
      preview.hidden = false;

      zone.removeAttribute('aria-busy');
    };
    preview.onerror = () => {
      if (version !== previewVersion) return;

      zone.removeAttribute('aria-busy');
      hint.textContent = 'Preview unavailable. Please choose a valid JPG, PNG, or WebP image.';
    };
    preview.src = previewUrl;
  }
});
