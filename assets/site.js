// My Face site script.
(function () {
  // ---- Back buttons on inner pages: go back if we came from this site, else go to the parent page
  document.querySelectorAll('a[data-back]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var ref = document.referrer;
      if (ref && ref.indexOf(location.origin) === 0 && history.length > 1) { e.preventDefault(); history.back(); }
    });
  });

  var scene = document.getElementById('scene');
  if (!scene) return;
  var rig = document.getElementById('rig'), screen = document.getElementById('screen'), os = document.getElementById('os'),
      zoomBtn = document.getElementById('zoomBtn'), zv = document.getElementById('zoomview'), zvScreen = document.getElementById('zvScreen'),
      x = 0;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var P = 1600, RX = -10, RY = -30, rx = RX, ry = RY, zoomed = false, busy = false;
  var store = { get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
                set: function (k, v) { try { v ? sessionStorage.setItem(k, v) : sessionStorage.removeItem(k); } catch (e) {} } };

  os.inert = true;

  function fit() { return Math.min(1, (scene.clientWidth - 24) / (scene.clientWidth < 600 ? 900 : 820), scene.clientHeight / 620); }
  function rest() { rig.style.transform = 'scale(' + fit() + ') rotateX(' + rx + 'deg) rotateY(' + ry + 'deg)'; }
  rest();
  window.addEventListener('resize', function () { if (!zoomed) rest(); });

  // ---- Drag to spin the computer 360°, click (without dragging) to turn it on
  var down = null, moved = false;
  scene.addEventListener('pointerdown', function (e) {
    if (zoomed || busy || e.button > 0) return;
    down = { x: e.clientX, y: e.clientY, rx: rx, ry: ry }; moved = false;
    scene.setPointerCapture(e.pointerId); rig.classList.add('drag');
  });
  scene.addEventListener('pointermove', function (e) {
    if (!down) return;
    var dx = e.clientX - down.x, dy = e.clientY - down.y;
    if (Math.abs(dx) + Math.abs(dy) > 6) moved = true;
    ry = down.ry + dx * 0.5;
    rx = Math.max(-40, Math.min(25, down.rx - dy * 0.3));
    rest();
  });
  scene.addEventListener('pointerup', function () {
    if (!down) return;
    down = null; rig.classList.remove('drag');
    if (!moved) zoomIn();
  });
  scene.addEventListener('pointercancel', function () { down = null; rig.classList.remove('drag'); });
  // keyboard: Enter/Space on the button zooms, arrows spin
  zoomBtn.addEventListener('click', function (e) { if (e.detail === 0) zoomIn(); });
  zoomBtn.addEventListener('keydown', function (e) {
    var k = { ArrowLeft: -20, ArrowRight: 20 }[e.key];
    if (k) { ry += k; rest(); e.preventDefault(); }
  });

  // ---- Fly into the screen, then hand over to a full-size copy of the screen
  function showDesktop(instant) {
    zvScreen.appendChild(os); os.inert = false;
    zv.hidden = false;
    if (instant) zv.classList.add('show'); else requestAnimationFrame(function () { zv.classList.add('show'); });
    document.body.style.overflow = 'hidden';
    zoomed = true; busy = false; store.set('mf-in', '1');
  }
  function zoomIn() {
    if (zoomed || busy) return;
    busy = true; scene.parentNode.classList.add('zooming');
    ry = ((ry % 360) + 540) % 360 - 180; rest();             // take the short way back round
    var s = fit(), vw = window.innerWidth, vh = window.innerHeight;
    var fr = vw <= 620 ? [20, 50] : [52, 80];
    var k = Math.max((vw - fr[0]) / (432 * s), (vh - fr[1]) / (324 * s));
    var z = P * (1 - 1 / k) - 150 * s;
    var r = scene.getBoundingClientRect(), dy = (vh / 2) - (r.top + r.height / 2);
    requestAnimationFrame(function () {
      rig.style.transform = 'translate3d(0,' + (dy - (fr[1] - fr[0]) / 2 + 90 * s) + 'px,' + z + 'px) scale(' + s + ') rotateX(0deg) rotateY(0deg)';
    });
    setTimeout(function () { showDesktop(false); bootUp(); }, reduce ? 0 : 1000);
  }
  function zoomOut() {
    if (!zoomed || busy) return;
    busy = true; zv.classList.remove('show'); closeAll(); closeStart(); store.set('mf-in', '');
    setTimeout(function () {
      zv.hidden = true; screen.insertBefore(os, screen.firstChild); os.inert = true;
      document.body.style.overflow = '';
      rx = RX; ry = RY; rest(); scene.parentNode.classList.remove('zooming');
      setTimeout(function () { zoomed = false; busy = false; zoomBtn.focus(); }, reduce ? 0 : 1000);
    }, reduce ? 0 : 350);
  }
  document.querySelectorAll('.logoff-btn').forEach(function (b) { b.addEventListener('click', zoomOut); });

  // ---- Boot text the first time you turn it on
  var boot = document.getElementById('boot'), log = document.getElementById('bootlog'), hasBooted = false;
  var LINES = ['MYFACE BIOS v4.00.950', 'checking lashes........ ok', 'checking nails......... ok',
               'loading glitter.drv.... ok', 'mounting /hair /piercing /filler', '', 'welcome x'];
  function bootUp() {
    var first = os.querySelector('.app');
    if (hasBooted || reduce) { hasBooted = true; first.focus(); return; }
    hasBooted = true; boot.classList.add('on'); log.textContent = '';
    var i = 0;
    (function next() {
      if (i >= LINES.length) return setTimeout(function () {
        boot.classList.add('splashing');
        setTimeout(function () { boot.classList.remove('on', 'splashing'); first.focus(); }, 1500);
      }, 300);
      log.textContent += LINES[i++] + '\n'; setTimeout(next, 150);
    })();
  }

  // ---- Clock
  var clock = document.getElementById('clock');
  function tick() { var d = new Date(); clock.textContent = ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
  tick(); setInterval(tick, 20000);

  // ---- Windows (several can be open; drag by the title bar; minimise and maximise)
  var lastIcon = null, z = 10, tasks = document.getElementById('tasks'), opened = 0;
  function wins() { return Array.prototype.slice.call(os.querySelectorAll('.app-win')); }
  function task(w) { return tasks.querySelector('[data-win="' + w.id + '"]'); }
  function focusWin(w) {
    wins().forEach(function (x) { x.classList.remove('active'); var t = task(x); if (t) t.classList.remove('on'); });
    w.hidden = false; w.style.zIndex = ++z; w.classList.add('active');
    var t = task(w); if (t) t.classList.add('on');
  }
  function closeWin(w) {
    w.hidden = true; w.classList.remove('active', 'maxed');
    var t = task(w); if (t) t.remove();
    var icon = os.querySelector('.app[data-app="' + w.id.slice(4) + '"]'); if (icon) icon.classList.remove('open');
    var top = wins().filter(function (x) { return !x.hidden; }).sort(function (p, q) { return q.style.zIndex - p.style.zIndex; })[0];
    if (top) focusWin(top); else if (lastIcon) lastIcon.focus();
  }
  function closeAll() { wins().forEach(function (w) { if (!w.hidden || task(w)) closeWin(w); }); }
  function openWin(key, from) {
    var w = document.getElementById('win-' + key);
    if (!w) return false;
    closeStart();
    if (!task(w)) {
      var t = document.createElement('button'); t.type = 'button'; t.className = 'task'; t.dataset.win = w.id; t.textContent = w.dataset.label;
      t.addEventListener('click', function () { if (!w.hidden && w.classList.contains('active')) { w.hidden = true; t.classList.remove('on'); } else focusWin(w); });
      tasks.appendChild(t);
      if (!w.classList.contains('dragged') && os.clientWidth > 620) {     // cascade new windows
        var off = (opened++ % 5) * 26;
        w.hidden = false; w.classList.add('dragged');
        w.style.left = Math.max(8, (os.clientWidth - w.offsetWidth) / 2 - 60 + off) + 'px';
        w.style.top = Math.max(8, (os.clientHeight - 36 - w.offsetHeight) / 2 - 30 + off) + 'px';
      }
    }
    focusWin(w);
    var icon = os.querySelector('.app[data-app="' + key + '"]'); if (icon) icon.classList.add('open');
    lastIcon = from || icon; w.querySelector('.back').focus();
    return true;
  }
  function backToDesktop() { var w = os.querySelector('.app-win.active:not([hidden])'); if (w) closeWin(w); }
  os.querySelectorAll('.app').forEach(function (a) {
    a.addEventListener('click', function (ev) { if (zoomed && openWin(a.dataset.app, a)) ev.preventDefault(); });
  });
  wins().forEach(function (w) {
    w.addEventListener('pointerdown', function () { if (!w.classList.contains('active')) focusWin(w); });
    w.querySelector('.close').addEventListener('click', function () { closeWin(w); });
    w.querySelector('.wback').addEventListener('click', function () { closeWin(w); });
    w.querySelector('.min').addEventListener('click', function () { w.hidden = true; w.classList.remove('active'); var t = task(w); if (t) t.classList.remove('on'); });
    w.querySelector('.max').addEventListener('click', function () { w.classList.toggle('maxed'); });
    var bar = w.querySelector('.titlebar'), drag = null;
    bar.addEventListener('dblclick', function (e) { if (!e.target.closest('button')) w.classList.toggle('maxed'); });
    bar.addEventListener('pointerdown', function (e) {
      if (e.target.closest('button') || w.classList.contains('maxed') || os.clientWidth <= 620) return;
      var r = w.getBoundingClientRect(), o = os.getBoundingClientRect();
      w.classList.add('dragged'); w.style.left = (r.left - o.left) + 'px'; w.style.top = (r.top - o.top) + 'px';
      drag = { x: e.clientX, y: e.clientY, l: r.left - o.left, t: r.top - o.top }; bar.setPointerCapture(e.pointerId);
    });
    bar.addEventListener('pointermove', function (e) {
      if (!drag) return;
      var maxL = os.clientWidth - 80, maxT = os.clientHeight - 36 - 34;
      w.style.left = Math.min(maxL, Math.max(80 - w.offsetWidth, drag.l + e.clientX - drag.x)) + 'px';
      w.style.top = Math.min(maxT, Math.max(0, drag.t + e.clientY - drag.y)) + 'px';
    });
    bar.addEventListener('pointerup', function () { drag = null; });
  });
  // single click selects an icon on the desktop background, like a real OS
  os.addEventListener('pointerdown', function (e) {
    os.querySelectorAll('.app.sel').forEach(function (a) { a.classList.remove('sel'); });
    var a = e.target.closest('.app'); if (a) a.classList.add('sel');
  });

  // ---- Start menu
  var startBtn = document.getElementById('startBtn'), startMenu = document.getElementById('startmenu');
  function closeStart() { if (!startMenu) return; startMenu.hidden = true; startBtn.setAttribute('aria-expanded', 'false'); }
  startBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    var open = startMenu.hidden; closeStart();
    if (open) { startMenu.hidden = false; startBtn.setAttribute('aria-expanded', 'true'); startMenu.querySelector('a').focus(); }
  });
  startMenu.querySelectorAll('a[data-app]').forEach(function (a) {
    a.addEventListener('click', function (ev) { if (openWin(a.dataset.app, startBtn)) ev.preventDefault(); });
  });
  document.addEventListener('click', function (e) { if (!startMenu.hidden && !startMenu.contains(e.target)) closeStart(); });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || !zoomed) return;
    if (!startMenu.hidden) { closeStart(); startBtn.focus(); }
    else if (os.querySelector('.app-win.active:not([hidden])')) backToDesktop();
    else zoomOut();
  });

  // Coming back from another page: go straight to the desktop
  // (only when coming back from one of the site's own pages: a fresh visit or a refresh always starts at the computer)
  var nav = (performance.getEntriesByType && performance.getEntriesByType('navigation')[0] || {}).type;
  var fromSite = document.referrer && document.referrer.indexOf(location.origin) === 0 && document.referrer.split('#')[0] !== location.href.split('#')[0];
  if (store.get('mf-in') && nav !== 'reload' && (nav === 'back_forward' || fromSite)) { hasBooted = true; showDesktop(true); }
  else store.set('mf-in', '');

  // ---- her.exe: drag to spin her through the 7 turnaround frames
  var m = document.getElementById('mascot'), btn = document.getElementById('avatarBtn'), bubble = document.getElementById('bubble');
  if (m && btn) {
    var FR = 10, frame = 0, sx = null, sf = 0, mv = false, li = 0;
    var lines = ['hiya! welcome to my face x', 'what are we booking today?', 'nails, lashes, hair or piercings?', 'pick a treatment x'];
    var show = function (f) { frame = ((Math.round(f) % FR) + FR) % FR; m.style.backgroundPositionX = (frame * 100 / (FR - 1)) + '%'; };
    btn.addEventListener('pointerdown', function (e) { sx = e.clientX; sf = frame; mv = false; btn.setPointerCapture(e.pointerId); });
    btn.addEventListener('pointermove', function (e) { if (sx === null) return; var dx = e.clientX - sx; if (Math.abs(dx) > 5) mv = true; show(sf - dx / 20); });
    btn.addEventListener('pointerup', function () { sx = null; });
    btn.addEventListener('pointercancel', function () { sx = null; });
    btn.addEventListener('click', function () {
      if (mv) { mv = false; return; }
      show(0); li = (li + 1) % lines.length; bubble.textContent = lines[li];
      m.classList.remove('hop'); void m.offsetWidth; m.classList.add('hop');
    });
    btn.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { show(frame - 1); e.preventDefault(); }
      if (e.key === 'ArrowRight') { show(frame + 1); e.preventDefault(); }
    });
  }

  // ---- Profile "song"
  var radio = document.getElementById('radio'), np = document.getElementById('np'), on = false;
  if (radio) radio.addEventListener('click', function () {
    on = !on; radio.innerHTML = on ? '&#10074;&#10074;' : '&#9654;'; radio.setAttribute('aria-label', on ? 'Pause' : 'Play');
    np.textContent = on ? 'now playing: [your salon playlist]' : 'press play for salon vibes';
  });
})();
