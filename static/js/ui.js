/**
 * Toasts, confirm modal, prompt modal — replaces alert/confirm/prompt.
 */
(function () {
  'use strict';

  function ensureToastHost() {
    let el = document.getElementById('toast-host');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toast-host';
      el.className = 'dp-toast-host';
      el.setAttribute('aria-live', 'polite');
      document.body.appendChild(el);
    }
    return el;
  }

  function ensureModalHost() {
    let el = document.getElementById('dp-modal-host');
    if (!el) {
      el = document.createElement('div');
      el.id = 'dp-modal-host';
      document.body.appendChild(el);
    }
    return el;
  }

  window.DPToast = function (message, opts) {
    opts = opts || {};
    var type = opts.type || 'info';
    var ms = opts.duration === undefined ? 4200 : opts.duration;
    var host = ensureToastHost();
    var t = document.createElement('div');
    t.className = 'dp-toast dp-toast-' + type;
    t.setAttribute('role', 'status');
    t.textContent = message;
    host.appendChild(t);
    requestAnimationFrame(function () {
      t.classList.add('dp-toast-show');
    });
    if (ms > 0) {
      setTimeout(function () {
        t.classList.remove('dp-toast-show');
        setTimeout(function () {
          t.remove();
        }, 300);
      }, ms);
    }
  };

  window.DPConfirm = function (message, title) {
    return new Promise(function (resolve) {
      var host = ensureModalHost();
      var backdrop = document.createElement('div');
      backdrop.className = 'dp-modal-backdrop';
      backdrop.setAttribute('role', 'dialog');
      backdrop.setAttribute('aria-modal', 'true');
      backdrop.setAttribute('aria-labelledby', 'dp-confirm-title');
      backdrop.innerHTML =
        '<div class="dp-modal">' +
        '<h2 id="dp-confirm-title" class="dp-modal-title">' +
        (title || 'Confirm') +
        '</h2>' +
        '<p class="dp-modal-body"></p>' +
        '<div class="dp-modal-actions">' +
        '<button type="button" class="dp-btn dp-btn-secondary" data-act="cancel">Cancel</button>' +
        '<button type="button" class="dp-btn dp-btn-danger" data-act="ok">OK</button>' +
        '</div></div>';
      backdrop.querySelector('.dp-modal-body').textContent = message;
      host.appendChild(backdrop);

      function cleanup(v) {
        backdrop.remove();
        document.removeEventListener('keydown', onKey);
        resolve(v);
      }
      function onKey(e) {
        if (e.key === 'Escape') cleanup(false);
      }
      document.addEventListener('keydown', onKey);
      backdrop.addEventListener('click', function (e) {
        if (e.target === backdrop) cleanup(false);
      });
      backdrop.querySelector('[data-act="cancel"]').addEventListener('click', function () {
        cleanup(false);
      });
      backdrop.querySelector('[data-act="ok"]').addEventListener('click', function () {
        cleanup(true);
      });
      backdrop.querySelector('[data-act="ok"]').focus();
    });
  };

  window.DPPrompt = function (message, defaultValue, title) {
    return new Promise(function (resolve) {
      var host = ensureModalHost();
      var backdrop = document.createElement('div');
      backdrop.className = 'dp-modal-backdrop';
      backdrop.setAttribute('role', 'dialog');
      backdrop.setAttribute('aria-modal', 'true');
      backdrop.innerHTML =
        '<div class="dp-modal">' +
        '<h2 class="dp-modal-title">' +
        (title || 'Input') +
        '</h2>' +
        '<p class="dp-modal-body"></p>' +
        '<input type="text" class="dp-modal-input" />' +
        '<div class="dp-modal-actions">' +
        '<button type="button" class="dp-btn dp-btn-secondary" data-act="cancel">Cancel</button>' +
        '<button type="button" class="dp-btn dp-btn-primary" data-act="ok">OK</button>' +
        '</div></div>';
      backdrop.querySelector('.dp-modal-body').textContent = message;
      var inp = backdrop.querySelector('.dp-modal-input');
      inp.value = defaultValue != null ? String(defaultValue) : '';

      function cleanup(v) {
        backdrop.remove();
        document.removeEventListener('keydown', onKey);
        resolve(v);
      }
      function onKey(e) {
        if (e.key === 'Escape') cleanup(null);
        if (e.key === 'Enter') cleanup(inp.value);
      }
      document.addEventListener('keydown', onKey);
      backdrop.addEventListener('click', function (e) {
        if (e.target === backdrop) cleanup(null);
      });
      backdrop.querySelector('[data-act="cancel"]').addEventListener('click', function () {
        cleanup(null);
      });
      backdrop.querySelector('[data-act="ok"]').addEventListener('click', function () {
        cleanup(inp.value);
      });
      host.appendChild(backdrop);
      inp.focus();
      inp.select();
    });
  };

  window.DPSetLoading = function (buttonEl, loading, labelBusy) {
    if (!buttonEl) return;
    if (loading) {
      buttonEl.dataset.dpOriginal = buttonEl.innerHTML;
      buttonEl.disabled = true;
      buttonEl.classList.add('dp-btn-loading');
      buttonEl.innerHTML =
        '<span class="dp-spinner" aria-hidden="true"></span> ' + (labelBusy || 'Please wait…');
    } else {
      buttonEl.disabled = false;
      buttonEl.classList.remove('dp-btn-loading');
      if (buttonEl.dataset.dpOriginal) buttonEl.innerHTML = buttonEl.dataset.dpOriginal;
    }
  };
})();
