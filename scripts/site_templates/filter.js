(function () {
  // ── Theme toggle ───────────────────────────────────────────────────────
  var toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var current = document.documentElement.dataset.theme;
      if (!current) {
        current = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      var next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  // ── Home: search + filter + virtualized render ─────────────────────────
  // Driven by /search-index.json so the home page stays a constant size no
  // matter how many skills exist. The server renders the first ~60 cards as a
  // no-JS / slow-network fallback; once the index loads we take over rendering.
  var grid = document.querySelector('[data-card-grid]');
  var bar = document.querySelector('[data-filter-bar]');
  if (!grid) return;

  var baseUrl = grid.dataset.baseUrl || '';
  var searchUrl = grid.dataset.searchUrl || (baseUrl + '/search-index.json');
  var pageSize = parseInt(grid.dataset.pageSize, 10) || 60;

  var selects = bar ? bar.querySelectorAll('select[data-filter]') : [];
  var search = bar ? bar.querySelector('[data-filter-search]') : null;
  var clear = document.querySelector('[data-filter-clear]');
  var counter = document.querySelector('[data-filter-count]');
  var noResults = document.querySelector('[data-no-results]');
  var sentinel = document.querySelector('[data-load-sentinel]');

  var SCOPE = { core: 1, category: 1, master: 1, meta: 1 };
  var all = [];
  var filtered = [];
  var shown = 0;
  var observer = null;

  fetch(searchUrl)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      all = data;
      grid.innerHTML = '';            // replace server fallback with JS render
      wire();
      setupObserver();
      apply();
    })
    .catch(function () { /* keep server-rendered fallback cards */ });

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function cardHtml(s) {
    var tags = (s.tags || []).map(function (t) {
      var cls = 'tag' + (SCOPE[t] ? ' tag-scope' : '')
        + (t === 'safety-critical' ? ' tag-risk-safety-critical'
          : t === 'irreversible' ? ' tag-risk-irreversible' : '');
      return '<a class="' + cls + '" href="' + baseUrl + '/tags/' + encodeURIComponent(t)
        + '/">' + esc(t) + '</a>';
    }).join('');
    return '<article class="card">'
      + '<h3 class="card-title"><a href="' + esc(s.url) + '">' + esc(s.name) + '</a></h3>'
      + '<p class="card-desc">' + esc(s.description) + '</p>'
      + '<div class="card-meta">' + tags + '</div>'
      + '<div class="card-footer"><span>' + esc(s.reasoning_mode || '')
      + '</span><span>v' + esc(s.version || '') + '</span></div>'
      + '</article>';
  }

  // Lightweight dependency-free fuzzy match: every query token must appear as a
  // substring or in-order subsequence of the haystack. Score rewards name hits.
  function haystack(s) {
    return (s.name + ' ' + s.description + ' ' + (s.keywords || []).join(' ')
      + ' ' + (s.tags || []).join(' ')).toLowerCase();
  }
  function subseq(token, text) {
    var i = 0;
    for (var j = 0; j < text.length && i < token.length; j++) {
      if (text[j] === token[i]) i++;
    }
    return i === token.length;
  }
  function score(tokens, s) {
    var hay = haystack(s);
    var name = s.name.toLowerCase();
    var total = 0;
    for (var k = 0; k < tokens.length; k++) {
      var t = tokens[k];
      if (hay.indexOf(t) !== -1) total += (name.indexOf(t) !== -1 ? 3 : 2);
      else if (subseq(t, hay)) total += 1;
      else return -1; // every token must match somehow
    }
    return total;
  }

  function apply() {
    var sel = {};
    selects.forEach(function (s) { if (s.value) sel[s.dataset.filter] = s.value; });
    var q = (search && search.value || '').trim().toLowerCase();
    var tokens = q ? q.split(/\s+/) : [];

    var rows = all.filter(function (s) {
      var tags = s.tags || [];
      for (var axis in sel) { if (tags.indexOf(sel[axis]) === -1) return false; }
      return true;
    });

    if (tokens.length) {
      rows = rows
        .map(function (s) { return { s: s, sc: score(tokens, s) }; })
        .filter(function (x) { return x.sc >= 0; })
        .sort(function (a, b) { return b.sc - a.sc || a.s.name.localeCompare(b.s.name); })
        .map(function (x) { return x.s; });
    }

    filtered = rows;
    shown = 0;
    grid.innerHTML = '';
    renderMore();

    if (counter) {
      counter.textContent = filtered.length === all.length
        ? all.length + ' skills'
        : filtered.length + ' of ' + all.length + ' skills';
    }
    if (noResults) noResults.hidden = filtered.length !== 0;
  }

  function renderMore() {
    if (shown >= filtered.length) return;
    var next = filtered.slice(shown, shown + pageSize);
    grid.insertAdjacentHTML('beforeend', next.map(cardHtml).join(''));
    shown += next.length;
  }

  function setupObserver() {
    if (!sentinel || !('IntersectionObserver' in window)) return;
    observer = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) renderMore();
    }, { rootMargin: '400px' });
    observer.observe(sentinel);
  }

  function wire() {
    selects.forEach(function (s) { s.addEventListener('change', apply); });
    if (search) search.addEventListener('input', apply);
    if (clear) clear.addEventListener('click', function () {
      selects.forEach(function (s) { s.value = ''; });
      if (search) search.value = '';
      apply();
    });
  }
})();

// ── Scroll FABs — runs on every page (long docs/skill pages too) ───────────
//   #scroll-bottom: jumps to the bottom; hidden once you're near it.
//   #scroll-top:    appears after scrolling down a little; jumps back to top.
(function () {
  var toTop = document.getElementById('scroll-top');
  var toBottom = document.getElementById('scroll-bottom');
  if (!toTop && !toBottom) return;

  function update() {
    var doc = document.documentElement;
    var total = doc.scrollHeight;
    var seen = window.scrollY + window.innerHeight;
    if (toTop) {
      toTop.classList.toggle('visible', window.scrollY > 400);
    }
    if (toBottom) {
      var hasRoom = total > window.innerHeight + 200;
      var nearBottom = total - seen < 120;
      toBottom.classList.toggle('visible', hasRoom && !nearBottom);
    }
  }

  if (toTop) toTop.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  if (toBottom) toBottom.addEventListener('click', function () {
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
  });
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  requestAnimationFrame(update);
})();
