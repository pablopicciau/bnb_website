// B&B Merì — interazioni minime (menu mobile, galleria foto camere)
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
// cartella: niente nomi obbligatori. Senza foto resta l'illustrazione.
(function () {
  var REPO = 'pablopicciau/bnb_website';
  var BRANCH = 'main';
  var IMAGE = /\.(jpe?g|png|webp|gif)$/i;

  document.querySelectorAll('[data-gallery]').forEach(function (fig) {
    var folder = fig.getAttribute('data-gallery');   // percorso nel repo
    var base = fig.getAttribute('data-gallery-base'); // percorso relativo alla pagina
    var img = fig.querySelector('img');
    if (!img || !window.fetch) return;

    fetch('https://api.github.com/repos/' + REPO + '/contents/' + folder + '?ref=' + BRANCH)
      .then(function (res) { return res.ok ? res.json() : []; })
      .then(function (files) {
        var photos = (Array.isArray(files) ? files : [])
          .filter(function (f) { return f.type === 'file' && IMAGE.test(f.name); })
          .map(function (f) { return f.name; })
          .sort(function (a, b) { return a.localeCompare(b, undefined, { numeric: true }); })
          .map(function (name) { return base + encodeURIComponent(name); });
        if (photos.length) start(fig, img, photos);
      })
      .catch(function () { /* resta l'illustrazione */ });
  });

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
        b.setAttribute('aria-label', dir === 'prev' ? 'Foto precedente' : 'Foto successiva');
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
