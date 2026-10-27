(() => {
  const root = document.body.dataset.root || './';
  const themeButton = document.getElementById('theme-toggle');
  function setTheme(dark) {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    themeButton.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
    themeButton.setAttribute('title', themeButton.getAttribute('aria-label'));
    themeButton.setAttribute('aria-pressed', String(dark));
    try { localStorage.setItem('labcol1709-theme', dark ? 'dark' : 'light'); } catch (_) {}
  }
  themeButton.addEventListener('click', () => setTheme(document.documentElement.dataset.theme !== 'dark'));
  setTheme(document.documentElement.dataset.theme === 'dark');
  const drawer = document.getElementById('site-navigation');
  const shade = document.getElementById('nav-shade');
  const menu = document.getElementById('menu-toggle');
  const close = document.getElementById('menu-close');
  function setMenu(open) {
    drawer.classList.toggle('open', open); shade.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
    if (open) close.focus();
  }
  menu.addEventListener('click', () => setMenu(!drawer.classList.contains('open')));
  close.addEventListener('click', () => { setMenu(false); menu.focus(); });
  shade.addEventListener('click', () => setMenu(false));
  drawer.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
  const dialog = document.getElementById('search-dialog');
  const search = document.getElementById('guide-search');
  const results = document.getElementById('search-results');
  let index = null;
  let loading = null;
  function message(text) { results.replaceChildren(); const p = document.createElement('p'); p.className = 'search-message'; p.textContent = text; results.append(p); }
  async function loadSearch() {
    if (!loading) loading = fetch(root + 'search-index.json').then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(data => { index = data; return data; });
    return loading;
  }
  async function showSearch() {
    dialog.showModal(); search.focus();
    try { await loadSearch(); runSearch(); } catch (_) { message('Search could not load. Use the navigation to open an exercise.'); loading = null; }
  }
  document.getElementById('search-open').addEventListener('click', showSearch);
  document.getElementById('search-close').addEventListener('click', () => dialog.close());
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { event.preventDefault(); if (!dialog.open) showSearch(); }
    if (event.key === 'Escape' && drawer.classList.contains('open')) { setMenu(false); menu.focus(); }
  });
  function runSearch() {
    if (!index) return;
    const query = search.value.trim().toLowerCase();
    if (!query) { message('Search the guide for a feature, setting, or exercise.'); return; }
    const terms = query.split(/\s+/);
    const matches = index.map(page => {
      const text = (page.title + ' ' + page.text).toLowerCase();
      const score = terms.every(term => text.includes(term)) ? terms.reduce((sum, term) => sum + (page.title.toLowerCase().includes(term) ? 6 : 1), 0) : 0;
      return {page, score};
    }).filter(row => row.score).sort((a,b) => b.score-a.score).slice(0,10);
    results.replaceChildren();
    if (!matches.length) { message('No matching pages. Try a feature name such as captions or translation.'); return; }
    for (const {page} of matches) {
      const link = document.createElement('a'); link.className = 'search-result'; link.href = root + page.path;
      const title = document.createElement('strong'); title.textContent = page.title;
      const snippet = document.createElement('p');
      const position = Math.max(0, page.text.toLowerCase().indexOf(terms[0])-45);
      snippet.textContent = (position ? '…' : '') + page.text.slice(position, position+180) + '…';
      link.append(title, snippet); results.append(link);
    }
  }
  search.addEventListener('input', runSearch);
  document.querySelectorAll('[data-audit-filter]').forEach(button => button.addEventListener('click', () => {
    const filter = button.dataset.auditFilter;
    document.querySelectorAll('[data-audit-filter]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    let count = 0;
    document.querySelectorAll('tr[data-image-status]').forEach(row => { const show = filter === 'all' || row.dataset.imageStatus === filter; row.hidden = !show; if (show) count++; });
    document.getElementById('audit-count').textContent = count + ' source images shown';
  }));
  window.addEventListener('beforeprint', () => {
    document.querySelectorAll('img[loading]').forEach(img => img.loading = 'eager');
    document.querySelectorAll('details.background-reading').forEach(item => item.open = true);
  });
  if (location.hash && !document.getElementById(decodeURIComponent(location.hash.slice(1)))) {
    const oldRoutes = JSON.parse(document.getElementById('legacy-routes').textContent);
    const destination = oldRoutes[location.hash.slice(1)];
    if (destination) location.replace(root + destination + location.hash);
  }
})();
