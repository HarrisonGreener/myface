// MyFace site script.
// ---- Tagline runs exactly from the start of the m to the end of the E (measured once fonts load)
(function () {
  function fit() {
    document.querySelectorAll('.brand').forEach(function (b) {
      var u = b.querySelector('.logo-svg use'), t = b.querySelector('.tag-svg .tt');
      if (!u || !t) return;
      var bb = u.getBBox(); if (bb.width < 50) return;
      var L = 13, R = 7;   // trim the empty corners the tilted m and E add to their boxes
      t.setAttribute('x', bb.x + L); t.setAttribute('textLength', bb.width - L - R);
    });
  }
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(fit);
})();
// ---- Captcha intro (homepage, once per visit)
(function () {
  var cap = document.getElementById('captcha');
  if (!cap) return;
  var seen = false; try { seen = sessionStorage.getItem('mf-human'); } catch (e) {}
  if (seen) { cap.hidden = true; return; }
  var check = document.getElementById('capCheck'), letters = document.querySelector('#capLetters use');
  document.body.style.overflow = 'hidden';
  setTimeout(function () { check.focus(); }, 50);
  function pass() {
    try { sessionStorage.setItem('mf-human', '1'); } catch (e) {}
    cap.classList.add('done'); document.body.style.overflow = '';
    setTimeout(function () { cap.hidden = true; }, 450);
  }
  check.addEventListener('click', function () {
    if (check.classList.contains('loading') || check.classList.contains('ok')) return;
    check.classList.add('loading');
    setTimeout(function () {
      check.classList.remove('loading'); check.classList.add('ok'); check.setAttribute('aria-checked', 'true');
      setTimeout(pass, 650);
    }, 900);
  });
  document.getElementById('capSkip').addEventListener('click', function (e) { e.preventDefault(); pass(); });
  // refresh: re-roll the wobble
  var seed = 7;
  document.getElementById('capShuffle').addEventListener('click', function () {
    seed = (seed * 7 + 3) % 97;
    var t = document.querySelector('#mf-wob-big feTurbulence'); if (t) t.setAttribute('seed', seed);
  });
  // audio: say it out loud where the browser supports speech
  document.getElementById('capAudio').addEventListener('click', function () {
    if (window.speechSynthesis) { var u = new SpeechSynthesisUtterance('my face. customise your avatar.'); u.rate = 0.85; speechSynthesis.speak(u); }
  });
})();

(function () {
  // ---- Back buttons on inner pages: go back if we came from this site, else go to the parent page
  document.querySelectorAll('a[data-back]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var ref = document.referrer;
      if (ref && ref.indexOf(location.origin) === 0 && history.length > 1) { e.preventDefault(); history.back(); }
    });
  });

  var topBar = document.querySelector('.top');
  function setTopH() { if (topBar) document.documentElement.style.setProperty('--top-h', topBar.offsetHeight + 'px'); }
  setTopH(); window.addEventListener('resize', setTopH);
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
  // the 3D computer (assets/deck.js) takes over from the CSS one once three.js has loaded
  var deckBox = document.getElementById('deck3d'), D = null;

  function fit() { return Math.min(1, (scene.clientWidth - 24) / (scene.clientWidth < 600 ? 900 : 820), scene.clientHeight / 620); }
  function rest() { rig.style.transform = 'scale(' + fit() + ') rotateX(' + rx + 'deg) rotateY(' + ry + 'deg)'; }
  rest();
  window.addEventListener('resize', function () { if (!zoomed) rest(); });

  // ---- Drag to spin the computer 360°, click (without dragging) to turn it on
  var down = null, moved = false;
  scene.addEventListener('pointerdown', function (e) {
    if (zoomed || busy || e.button > 0) return;
    if (D) { down = { x: e.clientX, y: e.clientY }; moved = false; return; }
    e.preventDefault();                                     // no text/sticker selection while spinning
    down = { x: e.clientX, y: e.clientY, rx: rx, ry: ry }; moved = false;
    scene.setPointerCapture(e.pointerId); rig.classList.add('drag');
  });
  scene.addEventListener('pointermove', function (e) {
    if (!down) return;
    var dx = e.clientX - down.x, dy = e.clientY - down.y;
    if (Math.abs(dx) + Math.abs(dy) > 6) moved = true;
    if (D) return;
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
  // the zoomed-in view is the same monitor front, scaled up to fill the window (desktop),
  // or a full-screen frame on phones
  var zvMon = document.getElementById('zvMon');
  function bigScale() { return Math.min(window.innerWidth / 500, window.innerHeight / 420) * 0.98; }
  function phone() { return window.innerWidth <= 620; }
  function sizeZoom() { zvMon.style.setProperty('--S', phone() ? 1 : bigScale()); zv.classList.toggle('phone', phone()); zv.classList.add('full'); }
  window.addEventListener('resize', function () {
    if (!zoomed) return;
    sizeZoom();
    if (D) D.snapIn();
  });
  function showDesktop(instant) {
    sizeZoom();
    zvScreen.insertBefore(os, zvScreen.firstChild); os.inert = false;
    zv.hidden = false;
    if (instant) zv.classList.add('show'); else requestAnimationFrame(function () { zv.classList.add('show'); });
    document.body.style.overflow = 'hidden'; document.body.classList.add('mf-zoomed');
    zoomed = true; busy = false; store.set('mf-in', '1');
  }
  function clearScreen() { zvScreen.removeAttribute('style'); os.style.transform = ''; }
  function deckFull(on) {
    var r = deckBox.getBoundingClientRect();
    deckBox.classList.toggle('full', on); D.resize(); return r;
  }
  function zoomIn() {
    if (zoomed || busy) return;
    if (D) {
      busy = true; scene.parentNode.classList.add('zooming');
      var from = deckFull(true);
      D.flyIn(function () {
        showDesktop(false); bootUp();
      }, from, reduce ? 0 : 1100);
      return;
    }
    busy = true; scene.parentNode.classList.add('zooming');
    ry = ((ry % 360) + 540) % 360 - 180; rest();             // take the short way back round
    var s = fit(), vw = window.innerWidth, vh = window.innerHeight;
    var k, yOff;
    if (vw <= 620) { k = Math.max((vw - 20) / (432 * s), (vh - 50) / (324 * s)); yOff = -15 + 90 * s; }
    else { k = bigScale() / s; yOff = 70 * s; }               // whole monitor front fills the window
    var z = P * (1 - 1 / k) - 150 * s;
    var r = scene.getBoundingClientRect(), dy = (vh / 2) - (r.top + r.height / 2);
    requestAnimationFrame(function () {
      rig.style.transform = 'translate3d(0,' + (dy + yOff) + 'px,' + z + 'px) scale(' + s + ') rotateX(0deg) rotateY(0deg)';
    });
    setTimeout(function () { showDesktop(false); bootUp(); }, reduce ? 0 : 1000);
  }
  function zoomOut() {
    if (!zoomed || busy) return;
    if (D) {
      busy = true; zv.classList.remove('show'); closeAll(); closeStart(); store.set('mf-in', '');
      setTimeout(function () {
        zv.hidden = true; zv.classList.remove('deck'); clearScreen();
        screen.insertBefore(os, screen.firstChild); os.inert = true;
        document.body.style.overflow = ''; document.body.classList.remove('mf-zoomed');
        var to = deckBox.parentNode.getBoundingClientRect();
        D.flyOut(function () {
          deckFull(false); scene.parentNode.classList.remove('zooming');
          zoomed = false; busy = false; D.canvas.focus();
        }, to, reduce ? 0 : 900);
      }, reduce ? 0 : 350);
      return;
    }
    busy = true; zv.classList.remove('show'); closeAll(); closeStart(); store.set('mf-in', '');
    setTimeout(function () {
      zv.hidden = true; screen.insertBefore(os, screen.firstChild); os.inert = true;
      document.body.style.overflow = ''; document.body.classList.remove('mf-zoomed');
      rx = RX; ry = RY; rest(); scene.parentNode.classList.remove('zooming');
      setTimeout(function () { zoomed = false; busy = false; zoomBtn.focus(); }, reduce ? 0 : 1000);
    }, reduce ? 0 : 350);
  }
  document.querySelectorAll('.logoff-btn').forEach(function (b) { b.addEventListener('click', zoomOut); });

  function useDeck(d) {
    D = d; scene.classList.add('has-deck');
    var c = D.canvas;
    c.tabIndex = 0; c.setAttribute('role', 'button'); c.setAttribute('aria-label', 'Turn on the computer (drag to spin it)');
    c.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); zoomIn(); } });
    if (zoomed) {                                           // already on the desktop (came back from another page)
      deckFull(true); D.snapIn();
    }
  }
  if (window.MFDeck) useDeck(window.MFDeck);
  else window.addEventListener('mfdeck', function () { useDeck(window.MFDeck); }, { once: true });

  // ---- Boot text the first time you turn it on
  var hasBooted = false;
  // straight into the desktop (no boot text)
  function bootUp() { hasBooted = true; var first = os.querySelector('.app'); if (first) first.focus({ preventScroll: true }); }

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
      var r = w.getBoundingClientRect(), o = os.getBoundingClientRect(), sc = o.width / os.offsetWidth;
      var l = (r.left - o.left) / sc, t = (r.top - o.top) / sc;
      w.classList.add('dragged'); w.style.left = l + 'px'; w.style.top = t + 'px';
      drag = { x: e.clientX, y: e.clientY, l: l, t: t, sc: sc }; e.preventDefault();
      document.addEventListener('pointermove', move); document.addEventListener('pointerup', stop, { once: true });
    });
    function stop() { drag = null; document.removeEventListener('pointermove', move); }
    function move(e) {
      if (!drag) return;
      var maxL = os.clientWidth - 80, maxT = os.clientHeight - 36 - 34;
      w.style.left = Math.min(maxL, Math.max(80 - w.offsetWidth, drag.l + (e.clientX - drag.x) / drag.sc)) + 'px';
      w.style.top = Math.min(maxT, Math.max(0, drag.t + (e.clientY - drag.y) / drag.sc)) + 'px';
    }
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
    var lines = ['hiya! welcome to myface x', 'what are we booking today?', 'nails, lashes, hair or piercings?', 'pick a treatment x'];
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
