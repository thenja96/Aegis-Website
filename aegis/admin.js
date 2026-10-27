// Content admin: text editor behaviour and confirmations.
(function () {
  var form = document.getElementById('editor');
  var dirty = 0;

  function mark(item) {
    if (item.classList.contains('is-dirty')) return;
    item.classList.add('is-dirty');
    dirty++;
    var s = document.getElementById('status');
    if (s) s.textContent = dirty + ' unsaved change' + (dirty > 1 ? 's' : '');
  }

  if (form) {
    form.querySelectorAll('.field[contenteditable]').forEach(function (f) {
      var input = f.nextElementSibling;
      var start = f.innerHTML;
      f.addEventListener('input', function () {
        input.value = f.innerHTML === start ? '' : f.innerHTML;
        mark(f.closest('.item'));
      });
      // one box is one heading, line or list item: Enter does nothing, Shift+Enter adds a line break
      f.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          if (e.shiftKey) document.execCommand('insertLineBreak');
        }
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault();
          var url = window.prompt('Link address, for example contact.html or https://…');
          if (url) document.execCommand('createLink', false, url.trim());
        }
      });
      // paste as plain text so formatting from Word or email does not come along
      f.addEventListener('paste', function (e) {
        e.preventDefault();
        var t = (e.clipboardData || window.clipboardData).getData('text/plain');
        document.execCommand('insertText', false, t.replace(/\s*\n\s*/g, ' '));
      });
    });
    form.querySelectorAll('input[type=checkbox], input[name^=meta], textarea[name^=meta]').forEach(function (c) {
      c.addEventListener('input', function () { mark(c.closest('.item, .group')); });
      c.addEventListener('change', function () {
        mark(c.closest('.item, .group'));
        if (c.name.indexOf('hide[') === 0) c.closest('.item').classList.toggle('is-hidden', c.checked);
      });
    });
    form.addEventListener('submit', function () { dirty = 0; document.getElementById('save').disabled = true; });
    window.addEventListener('beforeunload', function (e) { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
  }

  // phones: the menu scrolls sideways, so bring the current page's link into view
  var on = document.querySelector('.side nav a.on');
  if (on && on.parentNode.scrollWidth > on.parentNode.clientWidth) on.parentNode.scrollLeft = on.offsetLeft - 16;

  // Design screen: keep colour pickers and code boxes in step, and update the preview live
  var design = document.getElementById('design');
  if (design) {
    var hex = /^#[0-9a-f]{6}$/i;
    function mix(c, t, a) { var n = parseInt(c.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255; return 'rgb(' + [r, g, b].map(function (v) { return Math.round(v + (t - v) * a); }).join(',') + ')'; }
    function paint() {
      var pv = document.getElementById('preview'), v = {};
      ['navy', 'blue', 'teal'].forEach(function (k) { v[k] = design.querySelector('input[name=' + k + ']').value; });
      if (hex.test(v.navy)) pv.style.setProperty('--pv-navy', v.navy);
      if (hex.test(v.blue)) pv.style.setProperty('--pv-blue', v.blue);
      if (hex.test(v.teal)) pv.style.setProperty('--pv-tealtext', mix(v.teal, 0, .42));
      if (hex.test(v.teal) && hex.test(v.blue)) pv.style.setProperty('--pv-grad', 'linear-gradient(90deg,' + mix(v.teal, 0, .2) + ',' + v.blue + ')');
      var r = design.querySelector('input[name=buttons]:checked');
      pv.style.setProperty('--pv-radius', r && r.value === 'rounded' ? '10px' : '4px');
    }
    design.querySelectorAll('input[type=color]').forEach(function (c) {
      var t = design.querySelector('input[name=' + c.dataset.for + ']');
      c.addEventListener('input', function () { t.value = c.value.toUpperCase(); paint(); });
      t.addEventListener('input', function () { if (hex.test(t.value)) c.value = t.value; paint(); });
    });
    design.querySelectorAll('input[type=radio]').forEach(function (r) { r.addEventListener('change', paint); });
    design.querySelectorAll('[data-confirm-click]').forEach(function (b) {
      b.addEventListener('click', function (e) { if (!window.confirm(b.getAttribute('data-confirm-click'))) e.preventDefault(); });
    });
    paint();
  }

  document.querySelectorAll('form[data-confirm]').forEach(function (f) {
    f.addEventListener('submit', function (e) { if (!window.confirm(f.getAttribute('data-confirm'))) e.preventDefault(); });
  });
})();
