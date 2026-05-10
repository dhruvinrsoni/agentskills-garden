(function () {
  // ── Theme toggle ───────────────────────────────────────────────────────
  var toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var current = document.documentElement.dataset.theme;
      if (!current) {
        // No explicit theme: derive current effective theme from media query.
        current = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      var next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  // ── Filter bar (only present on home page) ─────────────────────────────
  var bar = document.querySelector('[data-filter-bar]');
  var grid = document.querySelector('[data-card-grid]');
  if (!bar || !grid) return;

  var selects = bar.querySelectorAll('select[data-filter]');
  var search = bar.querySelector('[data-filter-search]');
  var clear = document.querySelector('[data-filter-clear]');
  var counter = document.querySelector('[data-filter-count]');
  var noResults = document.querySelector('[data-no-results]');
  var cards = grid.querySelectorAll('[data-skill]');
  var totalCards = cards.length;

  function applyFilters() {
    var filters = {};
    selects.forEach(function (sel) {
      var v = sel.value;
      if (v) filters[sel.dataset.filter] = v;
    });
    var q = (search && search.value || '').trim().toLowerCase();

    var visible = 0;
    cards.forEach(function (card) {
      var ok = true;
      for (var axis in filters) {
        var values = (card.dataset[axis] || '').split(/\s+/);
        if (values.indexOf(filters[axis]) === -1) { ok = false; break; }
      }
      if (ok && q) {
        var text = (card.dataset.text || '').toLowerCase();
        if (text.indexOf(q) === -1) ok = false;
      }
      card.hidden = !ok;
      if (ok) visible++;
    });

    if (counter) {
      counter.textContent = visible === totalCards
        ? totalCards + ' skills'
        : visible + ' of ' + totalCards + ' skills';
    }
    if (noResults) noResults.hidden = visible !== 0;
  }

  selects.forEach(function (sel) { sel.addEventListener('change', applyFilters); });
  if (search) search.addEventListener('input', applyFilters);
  if (clear) clear.addEventListener('click', function () {
    selects.forEach(function (sel) { sel.value = ''; });
    if (search) search.value = '';
    applyFilters();
  });
})();
