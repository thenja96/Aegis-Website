(function () {
  var mobile = window.matchMedia('(max-width: 768px)');

  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      document.body.classList.toggle('nav-open', open);
    });
  }
  document.querySelectorAll('.has-sub > a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (mobile.matches) { e.preventDefault(); a.parentNode.classList.toggle('open'); }
    });
  });

  // Active nav item
  var here = location.pathname.replace(/\/index\.html$/, '/');
  document.querySelectorAll('.nav a[href]').forEach(function (a) {
    var href = a.getAttribute('href');
    if (!href || href.indexOf('#') === 0) return;
    var target = new URL(href, location.href).pathname.replace(/\/index\.html$/, '/');
    if (target === here) a.classList.add('active');
  });

  // Scroll reveal
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
  }

  // Stats count-up (pure numbers only, e.g. "17+" and "30+")
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce && 'IntersectionObserver' in window) {
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        so.unobserve(en.target);
        var el = en.target, m = /^(\d+)(\+?)$/.exec(el.textContent.trim());
        if (!m) return;
        var end = parseInt(m[1], 10), suffix = m[2], start = null;
        function tick(ts) {
          if (!start) start = ts;
          var p = Math.min((ts - start) / 900, 1), e = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(end * e) + suffix;
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: .6 });
    document.querySelectorAll('.stat b').forEach(function (b) { so.observe(b); });
  }

  // Sub-navigation scroll spy
  var subnav = document.querySelector('.subnav');
  if (subnav) {
    var links = Array.prototype.slice.call(subnav.querySelectorAll('a[href^="#"]'));
    var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); }).filter(Boolean);
    var current = null;
    function spy() {
      var y = window.scrollY + 160, active = null;
      targets.forEach(function (t) { if (t.offsetTop <= y) active = t; });
      if (active === current) return;
      current = active;
      links.forEach(function (a) {
        var on = active && a.getAttribute('href') === '#' + active.id;
        a.classList.toggle('active', !!on);
        if (on) { var c = subnav.querySelector('.container'); c.scrollTo({ left: a.offsetLeft - c.clientWidth / 2 + a.offsetWidth / 2, behavior: 'smooth' }); }
      });
    }
    window.addEventListener('scroll', spy, { passive: true });
    spy();
  }

  // Back to top
  var top = document.querySelector('.totop');
  if (top) {
    window.addEventListener('scroll', function () { top.classList.toggle('show', window.scrollY > 900); }, { passive: true });
    top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });
  }

  // Logo tooltips from alt text
  document.querySelectorAll('.logo-wall img, .marquee-track img, .logo-strip img').forEach(function (img) {
    if (img.alt && !img.title) img.title = img.alt;
  });

  // Contact form: inline validation, async submit, inline success
  var form = document.querySelector('form.form');
  if (form) {
    var notice = document.querySelector('.notice');
    function fail(field, show) { field.classList.toggle('invalid', show); }
    function validate() {
      var ok = true;
      form.querySelectorAll('[required]').forEach(function (f) {
        var bad = !f.value.trim() || (f.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value));
        fail(f, bad); if (bad) ok = false;
      });
      return ok;
    }
    form.querySelectorAll('[required]').forEach(function (f) {
      f.addEventListener('input', function () { if (f.classList.contains('invalid')) validate(); });
      f.addEventListener('blur', validate);
    });
    form.addEventListener('submit', function (e) {
      if (!validate()) { e.preventDefault(); form.querySelector('.invalid').focus(); return; }
      if (!window.fetch) return; // plain post with redirect fallback
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]'), label = btn.textContent;
      btn.disabled = true; btn.textContent = 'Sending';
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
        .then(function (j) {
          if (!j.ok) throw 0;
          form.reset();
          if (notice) { notice.classList.remove('error'); notice.classList.add('show'); notice.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
        })
        .catch(function () {
          if (notice) { notice.textContent = 'The message could not be sent. Please email aegis@aegiscomm.com.my.'; notice.classList.add('show', 'error'); }
        })
        .finally(function () { btn.disabled = false; btn.textContent = label; });
    });
    if (/[?&]sent=1/.test(location.search) && notice) { notice.classList.add('show'); notice.scrollIntoView({ block: 'center' }); }
    if (/[?&]error=1/.test(location.search) && notice) { notice.textContent = 'Please check the required fields and try again.'; notice.classList.add('show', 'error'); }
  }
})();

// ---- Interaction options S4 B2 A2 A3 V4 V5 ----
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // S4 reading progress bar
  var bar = document.querySelector('.progress');
  if (bar) {
    var upd = function () {
      var h = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = (h > 0 ? Math.min(100, scrollY / h * 100) : 0) + '%';
    };
    addEventListener('scroll', upd, { passive: true }); addEventListener('resize', upd); upd();
  }

  // B2 magnetic buttons (desktop pointers only)
  if (fine && !reduce) {
    document.querySelectorAll('.btn').forEach(function (b) {
      b.classList.add('magnet');
      b.addEventListener('mousemove', function (e) {
        var r = b.getBoundingClientRect(), x = e.clientX - r.left - r.width / 2, y = e.clientY - r.top - r.height / 2;
        b.style.transform = 'translate(' + x * 0.18 + 'px,' + y * 0.28 + 'px)';
      });
      b.addEventListener('mouseleave', function () { b.style.transform = ''; });
    });
  }

  // A2 arrowheads appear once each line has drawn
  document.querySelectorAll('.diagram .d-arrow, .diagram .d-loop').forEach(function (p) {
    p.addEventListener('animationend', function () { p.classList.add('drawn'); });
  });

  // A3 hero headline word reveal (text unchanged, split into spans)
  var h1 = document.querySelector('.hero h1');
  if (h1 && !reduce && !h1.querySelector('*')) {
    var words = h1.textContent.split(/(\s+)/), i = 0;
    h1.textContent = '';
    words.forEach(function (w) {
      if (!w) return;
      if (/^\s+$/.test(w)) { h1.appendChild(document.createTextNode(' ')); return; }
      var s = document.createElement('span'); s.className = 'w'; s.textContent = w; s.style.animationDelay = (0.08 * i++) + 's'; h1.appendChild(s);
    });
  }

  // V4 risk-tier selector, labels taken from the table headings
  var tw = document.querySelector('.tier-wrap');
  if (tw) {
    var ths = Array.prototype.slice.call(tw.querySelectorAll('thead th')).slice(1);
    var tabs = document.createElement('div'); tabs.className = 'tier-tabs'; tabs.setAttribute('role', 'tablist');
    var all = document.createElement('button'); all.type = 'button'; all.textContent = 'All tiers'; all.setAttribute('role', 'tab'); all.setAttribute('aria-selected', 'true'); tabs.appendChild(all);
    ths.forEach(function (th, idx) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = th.textContent; b.setAttribute('role', 'tab'); b.setAttribute('aria-selected', 'false'); b.dataset.tier = String(idx + 1); tabs.appendChild(b);
    });
    tabs.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      tabs.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
      if (b.dataset.tier) tw.dataset.tier = b.dataset.tier; else delete tw.dataset.tier;
    });
    tw.parentNode.insertBefore(tabs, tw);
    if (window.matchMedia('(max-width: 768px)').matches) tabs.querySelector('[data-tier="1"]').click();
  }

  // V5 audience tabs on the home page
  var at = document.querySelector('.aud-tabs');
  if (at) {
    at.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var f = b.dataset.filter;
      at.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
      document.querySelectorAll('[data-aud]').forEach(function (el) {
        el.classList.toggle('dim', f !== 'all' && el.dataset.aud.split(' ').indexOf(f) === -1);
      });
    });
  }
})();

// ---- Audit: Escape closes the mobile menu; open a fold when its sub-nav link is used ----
(function () {
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var nav = document.querySelector('.nav.open'), t = document.querySelector('.nav-toggle');
    if (nav && t) { t.click(); t.focus(); }
  });
  function openFoldFor(hash) {
    if (!hash) return;
    var sec = document.getElementById(hash.slice(1)); if (!sec) return;
    var d = sec.querySelector('details.fold'); if (d) d.open = true;
  }
  document.querySelectorAll('.subnav a[href^="#"]').forEach(function (a) { a.addEventListener('click', function () { openFoldFor(a.getAttribute('href')); }); });
  openFoldFor(location.hash);
  window.addEventListener('hashchange', function () { openFoldFor(location.hash); });
  window.addEventListener('beforeprint', function () { document.querySelectorAll('details.fold').forEach(function (d) { d.open = true; }); });
})();

// ---- Reveal safety: anchors, folds and a timer so nothing stays hidden ----
(function () {
  function revealInView() {
    document.querySelectorAll('.reveal:not(.in)').forEach(function (el) {
      var b = el.getBoundingClientRect();
      if (b.bottom > 0 && b.top < innerHeight * 1.1) el.classList.add('in');
    });
  }
  window.addEventListener('hashchange', function () { setTimeout(revealInView, 50); });
  document.querySelectorAll('details.fold').forEach(function (d) { d.addEventListener('toggle', function () { setTimeout(revealInView, 50); }); });
  if (location.hash) setTimeout(revealInView, 150);
  setTimeout(revealInView, 1200);
  setTimeout(function () { document.querySelectorAll('.reveal:not(.in)').forEach(function (el) { el.classList.add('in'); }); }, 3000);
})();

// ---- Always open a page at the top unless the URL points at a section ----
(function () {
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  function toTop() { if (!location.hash) window.scrollTo(0, 0); }
  toTop();
  window.addEventListener('pageshow', function (e) { if (e.persisted) toTop(); });
  // drop the #section from the address bar once used, so a reload or return opens at the top
  function clearHash() {
    if (location.hash) setTimeout(function () { history.replaceState(null, '', location.pathname + location.search); }, 600);
  }
  if (document.readyState === 'complete') clearHash(); else window.addEventListener('load', clearHash);
  window.addEventListener('hashchange', clearHash);
})();

// ---- IPO roadmap stepper: hover (desktop) or click/keys select a milestone ----
(function () {
  document.querySelectorAll('[data-stepper]').forEach(function (root) {
    root.classList.add('js');
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    var panels = Array.prototype.slice.call(root.querySelectorAll('[role="tabpanel"]'));
    var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    function select(i, focus) {
      tabs.forEach(function (t, k) { var on = k === i; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1; });
      panels.forEach(function (p, k) { p.classList.toggle('is-active', k === i); });
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i); });
      if (fine) t.addEventListener('mouseenter', function () { select(i); });
      t.addEventListener('keydown', function (e) {
        var k = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
        if (k) { e.preventDefault(); select((i + k + tabs.length) % tabs.length, true); }
        if (e.key === 'Home') { e.preventDefault(); select(0, true); }
        if (e.key === 'End') { e.preventDefault(); select(tabs.length - 1, true); }
      });
    });
    select(0);
  });
})();

// ---- Home service filter: show only services for the chosen stage ----
(function () {
  var tabs = document.querySelector('.aud-tabs');
  var grid = document.querySelector('#services .grid');
  if (!tabs || !grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.card[data-aud]'));
  var logos = Array.prototype.slice.call(document.querySelectorAll('.marquee-track [data-aud]'));
  var current = 'all';
  function cols() { return getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length || 1; }
  function layout() {
    var n = cols(), i = 0;
    cards.forEach(function (c) {
      c.classList.remove('col-end', 'row-n');
      if (c.classList.contains('is-hidden')) return;
      if (i % n === n - 1) c.classList.add('col-end');
      if (i >= n) c.classList.add('row-n');
      i++;
    });
    var last = cards.filter(function (c) { return !c.classList.contains('is-hidden'); }).pop();
    if (last) last.classList.add('col-end');
  }
  function apply(f) {
    current = f;
    var match = function (el) { return f === 'all' || el.dataset.aud.split(' ').indexOf(f) !== -1; };
    cards.forEach(function (c) { var on = match(c); c.classList.toggle('is-hidden', !on); c.classList.toggle('is-shown', on); c.classList.remove('dim'); });
    logos.forEach(function (l) { l.classList.toggle('is-hidden', !match(l)); l.classList.remove('dim'); });
    layout();
  }
  grid.classList.add('filtered');
  tabs.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    e.stopImmediatePropagation();
    tabs.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
    apply(b.dataset.filter);
  }, true);
  window.addEventListener('resize', layout);
  apply('all');
})();

// Photo filmstrip: counter and previous/next buttons
(function () {
  document.querySelectorAll('.photo-grid').forEach(function (strip) {
    var items = strip.querySelectorAll('figure'), n = items.length;
    if (n < 2) return;
    strip.setAttribute('tabindex', '0');
    strip.setAttribute('role', 'region');
    strip.setAttribute('aria-label', 'Photos, scroll sideways for more');
    var ctl = document.createElement('div');
    ctl.className = 'film-ctl';
    ctl.innerHTML = '<span class="film-ct" aria-live="polite"></span>' +
      '<button type="button" aria-label="Previous photo">&larr;</button>' +
      '<button type="button" aria-label="Next photo">&rarr;</button>';
    // wrap so the controls stay under the strip inside two-column layouts
    var film = document.createElement('div');
    film.className = 'film';
    strip.parentNode.insertBefore(film, strip);
    film.appendChild(strip);
    film.appendChild(ctl);
    var ct = ctl.querySelector('.film-ct'), prev = ctl.children[1], next = ctl.children[2];
    var pad = function (x) { return (x < 10 ? '0' : '') + x; };
    function step() { return items[1].offsetLeft - items[0].offsetLeft; }
    function update() {
      var max = strip.scrollWidth - strip.clientWidth;
      ctl.hidden = max < 4;
      var atEnd = strip.scrollLeft >= max - 4;
      var i = atEnd ? n : Math.round(strip.scrollLeft / step()) + 1;
      ct.textContent = pad(i) + ' / ' + pad(n);
      prev.disabled = strip.scrollLeft < 4;
      next.disabled = atEnd;
    }
    var still = window.matchMedia('(prefers-reduced-motion: reduce)');
    function go(d) {
      var i = Math.max(0, Math.min(n - 1, Math.round(strip.scrollLeft / step()) + d));
      strip.scrollTo({ left: items[i].offsetLeft - items[0].offsetLeft, behavior: still.matches ? 'auto' : 'smooth' });
    }
    prev.addEventListener('click', function () { go(-1); });
    next.addEventListener('click', function () { go(1); });
    strip.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });
})();

// Home quote: words darken as the quote scrolls up the screen
(function () {
  var q = document.querySelector('[data-fill]');
  if (!q || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  q.innerHTML = q.textContent.split(' ').map(function (w) { return '<span class="w">' + w + '</span>'; }).join(' ');
  var words = q.querySelectorAll('.w'), queued = false;
  function paint() {
    queued = false;
    var r = q.getBoundingClientRect(), vh = innerHeight;
    var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (vh * 0.5)));
    var n = Math.round(p * words.length);
    words.forEach(function (w, i) { w.classList.toggle('on', i < n); });
  }
  addEventListener('scroll', function () { if (!queued) { queued = true; requestAnimationFrame(paint); } }, { passive: true });
  addEventListener('resize', paint);
  paint();
})();

// Page-end contact section: draw its top line once it scrolls into view
(function () {
  var c = document.querySelector('.cta');
  if (!c || !('IntersectionObserver' in window)) { if (c) c.classList.add('in'); return; }
  var io = new IntersectionObserver(function (es) {
    if (es[0].isIntersecting) { c.classList.add('in'); io.disconnect(); }
  }, { threshold: 0.4 });
  io.observe(c);
})();

// Phone contact bar: step aside while the page's own Contact us section or the footer is on screen
(function () {
  var bar = document.querySelector('.mobile-cta');
  var spots = document.querySelectorAll('.cta, .band-cta, .footer');
  if (!bar || !spots.length || !('IntersectionObserver' in window)) return;
  var seen = new Set();
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) seen.add(e.target); else seen.delete(e.target); });
    bar.classList.toggle('is-away', seen.size > 0);
  });
  spots.forEach(function (s) { io.observe(s); });
})();

// Discourage casual image saving: no right-click menu or drag on images (the rest of the page is untouched)
(function () {
  function onImg(e) { return e.target && (e.target.tagName === 'IMG' || (e.target.closest && e.target.closest('picture, .frame, .thumb, .team-hero-img'))); }
  document.addEventListener('contextmenu', function (e) { if (onImg(e)) e.preventDefault(); });
  document.addEventListener('dragstart', function (e) { if (onImg(e)) e.preventDefault(); });
})();

// Jump links: drop links to sections that are switched off in the backend
(function () {
  document.querySelectorAll('.subnav a[href^="#"]').forEach(function (a) {
    var t = document.getElementById(a.getAttribute('href').slice(1));
    if (t && t.closest('[hidden]')) a.remove();
  });
})();
