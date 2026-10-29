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

// Galleria: mostra tutte le foto presenti nella cartella indicata da
// data-gallery (es. assets/img/camera-matrimoniale/). L'elenco dei file
// arriva dall'API pubblica di GitHub, quindi basta caricare le foto nella
// cartella: niente nomi obbligatori. L'ordine si decide in ordine.txt
// nella stessa cartella. Senza foto resta l'illustrazione.
(function () {
  var REPO = 'pablopicciau/bnb_website';
  var BRANCH = 'main';
  var IMAGE = /\.(jpe?g|png|webp|gif)$/i;
  var LABELS = {
    it: ['Foto precedente', 'Foto successiva'],
    en: ['Previous photo', 'Next photo'],
    fr: ['Photo précédente', 'Photo suivante'],
    es: ['Foto anterior', 'Foto siguiente']
  }[document.documentElement.lang] || ['Foto precedente', 'Foto successiva'];

  document.querySelectorAll('[data-gallery]').forEach(function (fig) {
    var folder = fig.getAttribute('data-gallery');   // percorso nel repo
    var base = fig.getAttribute('data-gallery-base'); // percorso relativo alla pagina
    var img = fig.querySelector('img');
    if (!img || !window.fetch) return;

    var list = fetch('https://api.github.com/repos/' + REPO + '/contents/' + folder + '?ref=' + BRANCH)
      .then(function (res) { return res.ok ? res.json() : []; });
    // ordine.txt (facoltativo): un nome di file per riga, nell'ordine voluto;
    // quello dopo "#" e' un commento. Il parametro evita la versione in cache.
    var order = fetch(base + 'ordine.txt?t=' + Date.now())
      .then(function (res) { return res.ok ? res.text() : ''; })
      .catch(function () { return ''; });

    Promise.all([list, order])
      .then(function (r) {
        var files = r[0], wanted = parseOrder(r[1]);
        var names = (Array.isArray(files) ? files : [])
          .filter(function (f) { return f.type === 'file' && IMAGE.test(f.name); })
          .map(function (f) { return f.name; })
          .sort(function (a, b) {
            var ia = rank(wanted, a), ib = rank(wanted, b);
            return ia !== ib ? ia - ib : a.localeCompare(b, undefined, { numeric: true });
          });
        var photos = names.map(function (name) { return base + encodeURIComponent(name); });
        if (photos.length) start(fig, img, photos);
      })
      .catch(function () { /* resta l'illustrazione */ });
  });

  // Nomi elencati in ordine.txt, in minuscolo (le maiuscole non contano)
  function parseOrder(text) {
    return text.split(/\r?\n/)
      .map(function (line) { return line.split('#')[0].trim().toLowerCase(); })
      .filter(Boolean);
  }

  // Posizione nell'elenco; le foto non elencate vanno in fondo
  function rank(wanted, name) {
    var i = wanted.indexOf(name.toLowerCase());
    return i === -1 ? wanted.length : i;
  }

  function start(fig, img, photos) {
    var i = 0;
    var fallback = img.getAttribute('src');
    var count = document.createElement('span');
    count.className = 'gallery-count';

    function show(n) {
      i = (n + photos.length) % photos.length;
      img.src = photos[i];
      count.textContent = (i + 1) + ' / ' + photos.length;
    }

    // Se una foto non si carica (es. appena caricata, sito non ancora aggiornato), la salta
    img.addEventListener('error', function onError() {
      photos.splice(i, 1);
      if (photos.length) return show(i);
      img.removeEventListener('error', onError);
      img.src = fallback;
      fig.querySelectorAll('.gallery-btn, .gallery-count').forEach(function (el) { el.remove(); });
    });

    if (photos.length > 1) {
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
    }
    show(0);
  }
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
