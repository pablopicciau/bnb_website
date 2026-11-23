// B&B Merì — interazioni minime (menu mobile, galleria foto camere)
// Usato da tutte le lingue (IT, EN, FR, ES).
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var menu = document.getElementById('nav-menu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', function () {
    var open = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // Chiudi il menu quando si clicca una voce
  menu.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') {
      menu.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
})();

// Galleria: le foto sono gia' nella pagina (le mette tools/build_pages.py,
// cosi' le vedono anche Google e gli assistenti AI); qui si aggiungono le
// frecce, il contatore e lo scorrimento col dito. Senza JavaScript si vede
// la prima foto.
(function () {
  var LABELS = {
    it: ['Foto precedente', 'Foto successiva'],
    en: ['Previous photo', 'Next photo'],
    fr: ['Photo précédente', 'Photo suivante'],
    es: ['Foto anterior', 'Foto siguiente']
  }[document.documentElement.lang] || ['Foto precedente', 'Foto successiva'];

  document.querySelectorAll('[data-gallery]').forEach(function (fig) {
    var slides = Array.prototype.slice.call(fig.querySelectorAll('.gallery-slide'));
    if (slides.length < 2) return;
    var i = 0;
    var count = document.createElement('span');
    count.className = 'gallery-count';
    count.setAttribute('aria-live', 'polite');

    // Carica in anticipo la foto successiva, cosi' il cambio e' immediato
    function preload(n) {
      var img = slides[(n + slides.length) % slides.length].querySelector('img');
      if (img) img.loading = 'eager';
    }

    function show(n) {
      slides[i].hidden = true;
      i = (n + slides.length) % slides.length;
      slides[i].hidden = false;
      count.textContent = (i + 1) + ' / ' + slides.length;
      preload(i + 1);
    }

    ['prev', 'next'].forEach(function (dir) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'gallery-btn gallery-' + dir;
      b.setAttribute('aria-label', LABELS[dir === 'prev' ? 0 : 1]);
      b.textContent = dir === 'prev' ? '‹' : '›';
      b.addEventListener('click', function () { show(i + (dir === 'prev' ? -1 : 1)); });
      fig.appendChild(b);
    });
    fig.appendChild(count);

    // Scorrimento col dito su telefono
    var x0 = null;
    fig.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    fig.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1));
      x0 = null;
    });

    // Prima foto visibile; la seconda si prepara solo quando la galleria
    // entra nello schermo
    count.textContent = '1 / ' + slides.length;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries, obs) {
        if (entries[0].isIntersecting) { preload(1); obs.disconnect(); }
      }).observe(fig);
    }
  });
})();

// Pagina parcheggi: schede (gratuiti / a pagamento / ascensori / consigli)
// e mappa che si sposta sul parcheggio scelto. Senza JavaScript si vedono
// tutte le schede una sotto l'altra.
(function () {
  var tablist = document.querySelector('.tabs[role="tablist"]');
  if (!tablist) return;
  var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));
  var panels = tabs.map(function (tab) {
    return document.getElementById(tab.getAttribute('aria-controls'));
  });
  var map = document.getElementById('park-map');
  var mapName = document.getElementById('park-map-name');
  var narrow = window.matchMedia('(max-width: 860px)');

  function activate(id) {
    tabs.forEach(function (tab, i) {
      var on = tab.getAttribute('aria-controls') === id;
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      tab.tabIndex = on ? 0 : -1;
      panels[i].hidden = !on;
    });
  }

  function showOnMap(button, scroll) {
    if (!map || !button) return;
    map.src = button.getAttribute('data-map-src');
    if (mapName) mapName.textContent = button.getAttribute('data-map-name');
    // Su telefono la mappa sta in alto: ci porta lo sguardo
    if (scroll && narrow.matches) map.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function openSpot(key) {
    var card = document.getElementById('spot-' + key);
    if (!card) return;
    activate(card.closest('[role="tabpanel"]').id);
    document.querySelectorAll('.park-card.is-highlighted').forEach(function (c) {
      c.classList.remove('is-highlighted');
    });
    card.classList.add('is-highlighted');
    showOnMap(card.querySelector('[data-map-src]'), false);
    card.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  tablist.hidden = false;
  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function () {
      activate(tab.getAttribute('aria-controls'));
      showOnMap(panels[i].querySelector('[data-map-src]'), false);
    });
    // Frecce sinistra/destra per spostarsi tra le schede da tastiera
    tab.addEventListener('keydown', function (e) {
      var step = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!step) return;
      var next = tabs[(i + step + tabs.length) % tabs.length];
      next.focus();
      next.click();
    });
  });

  document.addEventListener('click', function (e) {
    var mapButton = e.target.closest('[data-map-src]');
    if (mapButton) showOnMap(mapButton, true);
    var pick = e.target.closest('[data-spot]');
    if (pick) {
      e.preventDefault();
      openSpot(pick.getAttribute('data-spot'));
      history.replaceState(null, '', '#spot-' + pick.getAttribute('data-spot'));
    }
  });

  // Scheda iniziale: dal link (#paid, #spot-re_alta...) oppure la prima
  var hash = location.hash.slice(1);
  if (hash.indexOf('spot-') === 0) openSpot(hash.slice(5));
  else activate(panels.some(function (p) { return p.id === hash; }) ? hash : panels[0].id);
})();

// Check-in online: schede degli accompagnatori in base al numero di ospiti,
// controlli prima dell'invio, invio al gestionale e istruzioni a schermo.
(function () {
  var form = document.getElementById('checkin-form');
  if (!form) return;
  var MAX_FILE = 10 * 1024 * 1024;
  var msg = JSON.parse(form.getAttribute('data-messages'));
  var template = document.getElementById('guest-template');
  var extra = document.getElementById('extra-guests');
  var count = form.querySelector('[name="guests_count"]');
  var arrival = form.querySelector('[name="arrival"]');
  var departure = form.querySelector('[name="departure"]');
  var errorBox = document.getElementById('checkin-error');
  var button = form.querySelector('button[type="submit"]');

  // Una scheda per ogni ospite oltre al principale (guests[1], guests[2]...)
  function syncGuests() {
    var wanted = (parseInt(count.value, 10) || 1) - 1;
    while (extra.children.length < wanted) {
      var i = extra.children.length + 1;
      var node = template.content.firstElementChild.cloneNode(true);
      node.querySelector('legend').textContent = msg.s_guest.replace('{n}', i + 1);
      node.querySelectorAll('[name], [id], [for], [aria-describedby]').forEach(function (el) {
        ['name', 'id', 'for', 'aria-describedby'].forEach(function (a) {
          if (el.hasAttribute(a)) el.setAttribute(a, el.getAttribute(a).replace(/__i__/g, i));
        });
      });
      extra.appendChild(node);
    }
    while (extra.children.length > wanted) extra.removeChild(extra.lastElementChild);
  }
  count.addEventListener('change', syncGuests);
  syncGuests();

  // La partenza non puo' essere prima dell'arrivo
  arrival.addEventListener('change', function () { departure.min = arrival.value; });

  function fail(text, field) {
    errorBox.textContent = text;
    errorBox.hidden = false;
    if (field) field.focus();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    errorBox.hidden = true;
    if (!form.checkValidity()) { form.reportValidity(); return; }
    if (departure.value <= arrival.value) return fail(msg.err_dates, departure);
    var files = form.querySelectorAll('input[type="file"]');
    for (var k = 0; k < files.length; k++) {
      var f = files[k].files[0];
      if (f && f.size > MAX_FILE) return fail(msg.err_file.replace('{name}', f.name), files[k]);
    }

    var label = button.textContent;
    button.disabled = true;
    button.textContent = msg.sending;

    fetch(form.getAttribute('data-endpoint'), { method: 'POST', body: new FormData(form) })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok || !data.ok) throw new Error(data.error || res.status);
          return data;
        });
      })
      .then(showResult)
      .catch(function () {
        button.disabled = false;
        button.textContent = label;
        var box = document.getElementById('checkin-failure');
        box.hidden = false;
        box.focus();
        box.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
  });

  // Le istruzioni arrivano dal gestionale come testo semplice: un paragrafo
  // ogni riga vuota. Inserite come testo, mai come HTML.
  function showResult(data) {
    var box = document.getElementById('checkin-result');
    var target = box.querySelector('.checkin-instructions');
    target.textContent = '';
    String(data.instructions || '').split(/\n\s*\n/).forEach(function (part) {
      if (!part.trim()) return;
      var p = document.createElement('p');
      p.textContent = part.trim();
      target.appendChild(p);
    });
    form.hidden = true;
    document.getElementById('checkin-failure').hidden = true;
    box.hidden = false;
    box.focus();
    box.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
})();
