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
  // shown when you arrive or refresh, but not when moving between the site's own pages
  var navType = (performance.getEntriesByType && performance.getEntriesByType('navigation')[0] || {}).type;
  var ref = document.referrer, internal = ref && ref.indexOf(location.origin + location.pathname.replace(/[^/]*$/, '')) === 0;   // came from one of the site's pages
  if (!document.documentElement.classList.contains('show-cap')) { cap.hidden = true; return; }
  var check = document.getElementById('capCheck'), letters = document.querySelector('#capLetters use');
  document.body.style.overflow = 'hidden';
  setTimeout(function () { check.focus(); }, 50);
  function pass() {
    try { sessionStorage.setItem('mf-human', '1'); } catch (e) {}
    cap.classList.add('done'); document.body.style.overflow = '';
    window.dispatchEvent(new Event('mf-human'));
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
  var reduce = false;   // the site plays its full animations for everyone (Ella's call)
  var P = 1600, RX = -10, RY = -30, rx = RX, ry = RY, zoomed = false, busy = false;
  var store = { get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
                set: function (k, v) { try { v ? sessionStorage.setItem(k, v) : sessionStorage.removeItem(k); } catch (e) {} } };

  os.inert = true;
  // the 3D computer (assets/deck.js) takes over from the CSS one once three.js has loaded
  var deckBox = document.getElementById('deck3d'), D = null, demoing = false;

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
    if (Math.abs(dx) + Math.abs(dy) > (e.pointerType === 'touch' ? 12 : 6)) moved = true;
    if (D) return;
    ry = down.ry + dx * 0.5;
    rx = Math.max(-40, Math.min(25, down.rx - dy * 0.3));
    rest();
  });
  scene.addEventListener('pointerup', function (e) {
    if (!down) return;
    down = null; rig.classList.remove('drag');
    if (moved) return;
    var hit = D && D.pick ? D.pick(e.clientX, e.clientY) : null;
    if (hit && hit.key) { if (zoomed || busy) return; busy = true; D.press(hit.key, function () { busy = false; zoomIn(hit.app); }); }
    else zoomIn();
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
  function zoomIn(app) {
    if (zoomed || busy) return;
    if (D) {
      busy = true; scene.parentNode.classList.add('zooming');
      var from = deckFull(true);
      D.flyIn(function () {
        showDesktop(false); bootUp();
        if (app) openWin(app);
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
      busy = true; zv.classList.remove('show'); closeAll(); closeStart(); store.set('mf-in', ''); store.set('mf-win', '');
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
    busy = true; zv.classList.remove('show'); closeAll(); closeStart(); store.set('mf-in', ''); store.set('mf-win', '');
    setTimeout(function () {
      zv.hidden = true; screen.insertBefore(os, screen.firstChild); os.inert = true;
      document.body.style.overflow = ''; document.body.classList.remove('mf-zoomed');
      rx = RX; ry = RY; rest(); scene.parentNode.classList.remove('zooming');
      setTimeout(function () { zoomed = false; busy = false; zoomBtn.focus(); }, reduce ? 0 : 1000);
    }, reduce ? 0 : 350);
  }
  document.querySelectorAll('.logoff-btn').forEach(function (b) { b.addEventListener('click', zoomOut); });

  // remember which way the computer was facing when you leave, so Back returns to the same view
  window.addEventListener('pagehide', function () { if (D && D.getView) store.set('mf-view', JSON.stringify(D.getView())); });
  function useDeck(d) {
    D = d; scene.classList.add('has-deck');
    if (D.isPhone) {
      zv.classList.add('flip'); document.documentElement.classList.add('mf-phone');
      // phone furniture: a status bar and an end-call key that logs off back to the 3D phone
      // phone OS: blue-green block wallpaper, a clock home screen, and a big app grid behind "Menu"
      var sc = document.createElement('div'); sc.className = 'ph-scene'; sc.setAttribute('aria-hidden', 'true');
      sc.innerHTML = [[-12, 8, 62, 22, -8], [44, 22, 70, 18, 6], [-6, 44, 58, 16, -4], [52, 58, 60, 20, 10], [8, 74, 70, 16, -6], [30, 36, 40, 12, 14]]
        .map(function (b) { return '<i style="left:' + b[0] + '%;top:' + b[1] + '%;width:' + b[2] + '%;height:' + b[3] + '%;transform:rotate(' + b[4] + 'deg)"></i>'; }).join('');
      os.insertBefore(sc, os.firstChild);
      var st = document.createElement('div'); st.className = 'ph-status'; st.setAttribute('aria-hidden', 'true');
      st.innerHTML = '<span class="ph-sig"><i></i><i></i><i></i><i></i></span><b class="ph-t"></b><span class="ph-bat"><i></i></span>'; os.appendChild(st);
      var home = document.createElement('div'); home.className = 'ph-home';
      home.innerHTML = '<button type="button" class="ph-clockbtn" aria-label="Open the menu"><span class="ph-clock"></span><span class="ph-date"></span><span class="ph-hint">tap to open</span></button>' +
        '<div class="ph-keys"><a class="ph-k" href="#" data-go="book">Book</a><button type="button" class="ph-k ph-menu" aria-label="Menu"><i></i><i></i><i></i><i></i></button><a class="ph-k" href="#" data-go="contact">Contact</a></div>';
      os.appendChild(home);
      var tick = function () { var d = new Date(), t = ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2);
        home.querySelector('.ph-clock').textContent = t; st.querySelector('.ph-t').textContent = t;
        home.querySelector('.ph-date').textContent = d.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'short' }); };
      tick(); setInterval(tick, 20000);
      var openGrid = function () { os.classList.add('ph-grid'); };
      openGrid();   // the 3D phone's screen already shows the clock, so tapping it goes straight to the apps
      home.querySelector('.ph-clockbtn').addEventListener('click', openGrid);
      home.querySelector('.ph-menu').addEventListener('click', openGrid);
      home.querySelectorAll('[data-go]').forEach(function (k) { k.addEventListener('click', function (e) {
        e.preventDefault(); var a = os.querySelector('.app[data-app="' + k.dataset.go + '"]'); if (a) { openGrid(); a.click(); } }); });
      var bar = document.createElement('div'); bar.className = 'ph-gridbar';
      bar.innerHTML = '<button type="button" class="ph-back" aria-label="Back to the clock">&lsaquo; Home</button><b>Menu</b>';
      bar.querySelector('.ph-back').addEventListener('click', function () { os.classList.remove('ph-grid'); });
      os.appendChild(bar);
      var off = document.createElement('button'); off.type = 'button'; off.className = 'ph-logoff';
      off.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v8"/><path d="M6.3 6.6a8 8 0 1 0 11.4 0"/></svg>Log off';
      off.addEventListener('click', zoomOut); os.appendChild(off);
      var pd = document.getElementById('popD'); if (pd) pd.innerHTML = '<b>Your avatar needs customising!</b>Open the phone to customise your avatar and find your treatment x';
    }
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
    if (store.get('mf-win') === w.id.slice(4)) store.set('mf-win', '');
    var t = task(w); if (t) t.remove();
    var icon = os.querySelector('.app[data-app="' + w.id.slice(4) + '"]'); if (icon) icon.classList.remove('open');
    var top = wins().filter(function (x) { return !x.hidden; }).sort(function (p, q) { return q.style.zIndex - p.style.zIndex; })[0];
    if (top) focusWin(top); else if (lastIcon) lastIcon.focus();
  }
  function closeAll() { wins().forEach(function (w) { if (!w.hidden || task(w)) closeWin(w); }); }
  function openWin(key, from) {
    var w = document.getElementById('win-' + key);
    if (!w) return false;
    store.set('mf-win', key);
    if (key === 'avatar') { w.classList.add('maxed'); if (typeof czPreload === 'function') czPreload(); }
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
  if (store.get('mf-in') && nav !== 'reload' && (nav === 'back_forward' || fromSite)) {
    hasBooted = true; showDesktop(true);
    var lastWin = store.get('mf-win'); if (lastWin) openWin(lastWin);           // back to the window you were in
  }
  else store.set('mf-in', ''); store.set('mf-win', '');

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
  // ---- "Show me how": a pretend cursor clicks the computer, then the Customise icon on the desktop
  function showHow(fromEl) {
    if (zoomed || busy) { zoomIn(); return; }
    var cur = document.createElement('div'); cur.className = 'demo-cursor'; cur.setAttribute('aria-hidden', 'true');
    document.body.appendChild(cur);
    var r0 = fromEl.getBoundingClientRect();
    function at(x, y) { cur.style.transform = 'translate(' + x + 'px,' + y + 'px)'; }
    function click(then) {
      cur.classList.add('press');
      var ring = document.createElement('span'); ring.className = 'demo-ring'; cur.appendChild(ring);
      setTimeout(function () { cur.classList.remove('press'); }, 180);
      setTimeout(function () { ring.remove(); then && then(); }, 420);
    }
    cur.style.transition = 'none'; at(r0.left + r0.width / 2, r0.top + r0.height / 2);
    void cur.offsetWidth; cur.style.transition = '';
    // 1) over to the computer's screen
    var sr = D && D.screenRect ? D.screenRect() : document.getElementById('scene').getBoundingClientRect();
    setTimeout(function () { at(sr.left + sr.width * 0.5, sr.top + sr.height * 0.5); }, 60);
    setTimeout(function () {
      click(function () {
        demoing = true; zoomIn();
        // 2) once the desktop is up, over to the Customise icon
        var wait = setInterval(function () {
          if (!zoomed || busy) return;
          clearInterval(wait);
          var icon = os.querySelector('.app[data-app="avatar"]');
          if (!icon) { demoing = false; cur.remove(); openAvatar(); return; }
          setTimeout(function () {
            var ir = icon.getBoundingClientRect();
            cur.classList.add('slow'); at(ir.left + ir.width / 2, ir.top + ir.height * 0.4);
            setTimeout(function () {
              icon.classList.add('sel');                       // hover over the icon a moment...
              setTimeout(function () {
                click(function () {                            // ...then click it
                  icon.classList.add('pressed');
                  setTimeout(function () {
                    demoing = false; icon.classList.remove('sel', 'pressed'); openAvatar();
                    cur.classList.add('bye'); setTimeout(function () { cur.remove(); }, 400);
                  }, 250);
                });
              }, 550);
            }, 1350);
          }, 700);
        }, 80);
      });
    }, 1050);
  }

  // ---- avatar.exe pop-up: an old-Windows warning telling you what to do (once per visit)
  var pop = document.getElementById('avatarPop');
  function showPop() {
    if (!pop || zoomed) return;
    setTimeout(function () {
      if (zoomed) return;
      if (D && D.isPhone) { notifs(); return; }
      // boom boom boom: photos of her work flood the screen, then avatar.exe lands in the middle on top
      photos.forEach(function (w, i) {
        setTimeout(function () { w.hidden = false; requestAnimationFrame(function () { w.classList.add('in'); }); }, i * 110);
      });
      setTimeout(function () {
        pop.hidden = false; requestAnimationFrame(function () { pop.classList.add('in'); });
        pop.querySelector('.pop-go').focus({ preventScroll: true });
      }, photos.length * 110 + 120);
    }, 900);
  }
  var photos = Array.prototype.slice.call(document.querySelectorAll('#popFlood .photo'));
  function hideWin(w) { w.classList.remove('in'); setTimeout(function () { w.hidden = true; }, 180); }
  // closing avatar.exe clears every pop-up at once
  function hidePop() { hideWin(pop); photos.forEach(hideWin); }

  // ---- phones: the same idea as picture messages arriving on the flip phone, stacked like notifications
  function notifs() {
    var wrap = document.createElement('div'); wrap.className = 'nf-stack'; wrap.setAttribute('aria-live', 'polite');
    ['pointerdown', 'pointerup', 'click'].forEach(function (t) { wrap.addEventListener(t, function (e) { e.stopPropagation(); }); });
    scene.appendChild(wrap);
    var bookA = document.querySelector('.pop-book');
    var pin = document.createElement('a'); pin.className = 'nf nf-pin'; pin.href = bookA ? bookA.getAttribute('href') : '#';
    pin.innerHTML = '<span class="nf-ic">&#128197;</span><span class="nf-tx"><small>book_now.exe &middot; now</small><b>Slots are open &mdash; tap to book</b></span><span class="nf-go">BOOK</span>';
    var list = document.createElement('div'); list.className = 'nf-list';
    var clear = document.createElement('button'); clear.type = 'button'; clear.className = 'nf-clear'; clear.textContent = 'Clear all';
    wrap.appendChild(pin); wrap.appendChild(list); wrap.appendChild(clear);
    var gone = function (el) { el.classList.add('out'); setTimeout(function () { el.remove(); if (!list.children.length && !wrap.querySelector('.nf-pin')) wrap.remove(); }, 260); };
    clear.addEventListener('click', function () { [pin].concat([].slice.call(list.children)).forEach(gone); clear.remove(); setTimeout(function () { wrap.remove(); }, 300); });
    // swipe a card sideways to dismiss it
    var swipe = function (el) {
      var x0 = null;
      el.addEventListener('pointerdown', function (e) { x0 = e.clientX; el.setPointerCapture(e.pointerId); el.style.transition = 'none'; });
      el.addEventListener('pointermove', function (e) { if (x0 === null) return; var dx = e.clientX - x0; el.style.transform = 'translateX(' + dx + 'px)'; el.style.opacity = 1 - Math.min(1, Math.abs(dx) / 220); });
      el.addEventListener('pointerup', function (e) {
        if (x0 === null) return; var dx = e.clientX - x0; x0 = null; el.style.transition = '';
        if (Math.abs(dx) > 80) { el.style.transform = 'translateX(' + (dx > 0 ? 120 : -120) + '%)'; el.style.opacity = 0; setTimeout(function () { el.remove(); }, 220); }
        else { el.style.transform = ''; el.style.opacity = ''; if (Math.abs(dx) < 6 && el.dataset.tap) window[el.dataset.tap] && window[el.dataset.tap](); }
      });
    };
    var items = photos.map(function (w) { return { name: w.querySelector('.pop-bar span').textContent, img: w.querySelector('img') }; });
    var buzz = function () { var c = D && D.canvas; if (!c) return; c.classList.remove('nf-buzz'); void c.offsetWidth; c.classList.add('nf-buzz'); try { navigator.vibrate && navigator.vibrate(60); } catch (e) {} };
    setTimeout(function () { pin.classList.add('in'); buzz(); }, 200);
    items.forEach(function (it, i) {
      setTimeout(function () {
        var n = document.createElement('div'); n.className = 'nf';
        n.innerHTML = '<span class="nf-ic">&#9993;</span><span class="nf-tx"><small>Picture message &middot; now</small><b>' + it.name + '</b></span>' +
          '<img src="' + it.img.getAttribute('src') + '" alt="' + it.img.alt + '">';
        list.insertBefore(n, list.firstChild); swipe(n); requestAnimationFrame(function () { n.classList.add('in'); }); buzz();
        while (list.children.length > 3) list.lastChild.remove();       // keep it tidy: only the three newest show
      }, 900 + i * 650);
    });
    setTimeout(function () {
      var n = document.createElement('div'); n.className = 'nf nf-av'; n.dataset.tap = 'mfOpenPhone';
      n.innerHTML = '<span class="nf-ic">&#9888;</span><span class="nf-tx"><small>avatar.exe &middot; now</small><b>Your avatar needs customising! Tap the phone</b></span>';
      list.insertBefore(n, list.firstChild); swipe(n); requestAnimationFrame(function () { n.classList.add('in'); }); buzz();
      while (list.children.length > 3) list.lastChild.remove();
      clear.classList.add('in');
    }, 900 + items.length * 650 + 300);
    window.mfOpenPhone = function () { zoomIn(); };
  }
  photos.forEach(function (w) {
    w.querySelector('.pop-x').addEventListener('click', function () { hideWin(w); });
    ['pointerdown', 'pointerup', 'click'].forEach(function (t) { w.addEventListener(t, function (e) { e.stopPropagation(); }); });
  });
  if (pop) {
    pop.querySelectorAll('.pop-x, .pop-ok').forEach(function (b) { b.addEventListener('click', hidePop); });
    pop.querySelector('.pop-go').addEventListener('click', function (e) { hidePop(); showHow(e.currentTarget); });
    pop.addEventListener('keydown', function (e) { if (e.key === 'Escape') hidePop(); });
    // the pop-up sits over the computer: its clicks must not count as clicking the computer
    ['pointerdown', 'pointerup', 'click'].forEach(function (t) { pop.addEventListener(t, function (e) { e.stopPropagation(); }); });
    var capEl = document.getElementById('captcha');
    if (capEl && !capEl.hidden) window.addEventListener('mf-human', showPop, { once: true });
  }

  // ---- Customise your avatar: spin her round, click a part, get the services for it
  var cz = document.querySelector('.cz'), czFig = document.getElementById('czFig'), czFrame = 0, czSpun = false;
  var CZ_FRAMES = 6;
  function czSet(f) {
    czFrame = ((f % CZ_FRAMES) + CZ_FRAMES) % CZ_FRAMES;
    czFig.style.backgroundPosition = (czFrame * 100 / (CZ_FRAMES - 1)) + '% 0';
    czFig.classList.toggle('front', czFrame === 0);
    var pf = document.getElementById('ptFrame'); if (pf) pf.textContent = (czFrame + 1) + '/' + CZ_FRAMES;
  }
  // clicking a part pops a ring of bubbles out of that spot (same style as the site menu)
  var czRingEl = null;
  function czClose() {
    if (czRingEl) { var r = czRingEl; czRingEl = null; r.classList.remove('open'); setTimeout(function () { r.remove(); }, 180); }
    czFig.querySelectorAll('.hs').forEach(function (h) { h.classList.remove('on'); });
  }
  function czPart(group, hs) {
    czClose();
    if (!group) return;
    var sec = cz.querySelector('.cz-part[data-part="' + group + '"]'); if (!sec) return;
    hs = hs || czFig.querySelector('.hs[data-part="' + group + '"]');
    czFig.querySelectorAll('.hs').forEach(function (h) { h.classList.toggle('on', h.dataset.part === group); });
    var items = Array.prototype.map.call(sec.querySelectorAll('.cz-list a'), function (a) {
      return { label: a.querySelector('b').textContent + '  ' + a.querySelector('em').textContent, href: a.getAttribute('href') };
    });
    var book = sec.querySelector('.cz-book');
    items.unshift({ label: sec.querySelector('h3').textContent, title: true });
    if (book) items.push({ label: 'Book this', href: book.getAttribute('href'), book: true });
    var stage = cz.querySelector('.cz-stage'), sr = stage.getBoundingClientRect(), hr = hs.getBoundingClientRect();
    var ring = document.createElement('div'); ring.className = 'pie cz-pie'; ring.setAttribute('role', 'menu');
    var pin = document.createElement('span'); pin.className = 'pie-pin'; ring.appendChild(pin);
    var top = items.shift(), L = [], R = [], made = [];
    items.forEach(function (it, i) { (i % 2 ? R : L).push(it); });
    function bubble(it, side, x, y, i) {
      var el = document.createElement(it.title ? 'span' : 'a');
      if (!it.title) { el.href = it.href; el.setAttribute('role', 'menuitem'); }
      el.className = 'pie-item ' + side + (it.title ? ' cz-title' : '') + (it.book ? ' cz-bookb' : '');
      el.innerHTML = '<span class="pk"></span><span class="pl"></span>'; el.querySelector('.pl').textContent = it.label;
      el.style.setProperty('--x', x + 'px'); el.style.setProperty('--y', y + 'px'); el.style.transitionDelay = (i * 22) + 'ms';
      ring.appendChild(el); made.push(el);
    }
    var n = 0, rows = Math.max(L.length, R.length);
    bubble(top, 'c', 0, -78, n++);
    for (var i = 0; i < rows; i++) {
      var t = rows === 1 ? 0 : i / (rows - 1), y = -26 + t * Math.max(90, (rows - 1) * 46), x = 34 + Math.sin(t * Math.PI) * 34;
      if (L[i]) bubble(L[i], 'l', -x, y, n++);
      if (R[i]) bubble(R[i], 'r', x, y, n++);
    }
    if (group === 'hair') {                              // hair colour swatches under the hair bubbles
      var row = document.createElement('div'); row.className = 'cz-swatches';
      row.style.setProperty('--y', (-26 + Math.max(90, (rows - 1) * 46) + 54) + 'px');
      CZ_HAIR.forEach(function (c) {
        var b = document.createElement('button'); b.type = 'button'; b.className = 'cz-sw' + (c.key === czHair ? ' on' : '');
        b.style.background = c.sw; b.setAttribute('aria-label', 'Hair colour: ' + c.label); b.title = c.label;
        b.addEventListener('click', function (e) { e.stopPropagation(); czSetHair(c.key); row.querySelectorAll('.cz-sw').forEach(function (x) { x.classList.toggle('on', x === b); }); });
        row.appendChild(b);
      });
      ring.appendChild(row); made.push(row);
    }
    stage.appendChild(ring);
    var cx = hr.left + hr.width / 2 - sr.left, cy = hr.top + hr.height / 2 - sr.top;
    ring.style.left = cx + 'px'; ring.style.top = cy + 'px';
    // keep the whole ring inside the stage (shrink a little on small screens); measure at full size
    ring.classList.add('open', 'nt');
    var o = ring.getBoundingClientRect(), minX = 0, maxX = 0, minY = 0, maxY = 0;
    made.forEach(function (el) { var r = el.getBoundingClientRect();
      minX = Math.min(minX, r.left - o.left); maxX = Math.max(maxX, r.right - o.left); minY = Math.min(minY, r.top - o.top); maxY = Math.max(maxY, r.bottom - o.top); });
    var k = Math.min(1, (sr.width - 16) / (maxX - minX), (sr.height - 16) / (maxY - minY));
    ring.style.setProperty('--k', k);
    var lx = Math.min(Math.max(cx, 8 - minX * k), sr.width - 8 - maxX * k), ly = Math.min(Math.max(cy, 8 - minY * k), sr.height - 8 - maxY * k);
    ring.style.left = lx + 'px'; ring.style.top = ly + 'px';
    czRingEl = ring;
    ring.classList.remove('open'); void ring.offsetWidth; ring.classList.remove('nt'); ring.classList.add('open');            // force a layout so the pop-out animates
    var first = ring.querySelector('a'); if (first) first.focus({ preventScroll: true });
  }
  // hair colours: each one is its own full turnaround, swapped in when picked
  var CZ_HAIR = [
    { key: '', label: 'Black & pink', sw: 'linear-gradient(135deg,#1c1a1e 55%,#ff4fa3 55%)' },
    { key: 'green', label: 'Green', sw: '#7cff3a' }, { key: 'blue', label: 'Ice blue', sw: '#a9cdf2' },
    { key: 'red', label: 'Red', sw: '#c2321c' }, { key: 'blonde', label: 'Blonde', sw: '#f0d48e' }];
  var czHair = store.get('mf-hair') || '';
  function czSetHair(key) {
    czHair = key || ''; store.set('mf-hair', czHair);
    var url = 'url("' + new URL('assets/avatar-turn' + (czHair ? '-' + czHair : '') + '.webp?v=55', document.baseURI).href + '")';   // absolute, so it works from the stylesheet too
    czFig.style.backgroundImage = url; if (cz) cz.style.setProperty('--sprite', url);
    if (cz) cz.querySelectorAll('.pt-hair').forEach(function (b) { b.classList.toggle('on', b.dataset.hair === czHair); });
    var fg = cz && cz.querySelector('.pt-fg'), sw = cz && cz.querySelector('.pt-hair[data-hair="' + czHair + '"]'); if (fg && sw) fg.style.background = sw.style.background;
  }
  var czPreloaded = false;
  function czPreload() { if (czPreloaded) return; czPreloaded = true; CZ_HAIR.forEach(function (c) { if (c.key) new Image().src = 'assets/avatar-turn-' + c.key + '.webp?v=55'; }); }
  function czSpinTo(target, done) {                      // turn frame by frame, like a character select
    if (czFrame === target) { done && done(); return; }
    var step = ((target - czFrame + CZ_FRAMES) % CZ_FRAMES) <= CZ_FRAMES / 2 ? 1 : -1;
    var t = setInterval(function () { czSet(czFrame + step); if (czFrame === target) { clearInterval(t); done && done(); } }, 90);
  }
  function openAvatar() {
    var w = document.getElementById('win-avatar'); if (!w || !cz) return;
    openWin('avatar'); w.classList.add('maxed'); czPreload();
    if (!czSpun && !reduce) { czSpun = true; czSet(1); var n = 0, t = setInterval(function () { czSet(czFrame + 1); if (++n >= CZ_FRAMES - 1) clearInterval(t); }, 110); }
  }
  if (cz) {
    czSet(0); if (czHair) czSetHair(czHair);
    czFig.querySelectorAll('.hs').forEach(function (h) {
      h.addEventListener('click', function (e) { e.stopPropagation(); if (czDragged) return; czPart(h.dataset.part, h); });
    });
    cz.querySelectorAll('.cz-chip').forEach(function (c) {
      c.addEventListener('click', function () { czSpinTo(0, function () { czPart(c.dataset.part); }); });
    });
    // Paint bits: part thumbnails, hair colours, background (star burst) colours
    cz.querySelectorAll('.pt-thumb').forEach(function (t) {
      t.addEventListener('click', function (e) { e.stopPropagation(); czSpinTo(0, function () { czPart(t.dataset.part); }); });
    });
    cz.querySelectorAll('.pt-hair').forEach(function (b) { b.addEventListener('click', function () { czSetHair(b.dataset.hair); }); });
    cz.querySelectorAll('.pt-bg').forEach(function (b) {
      b.addEventListener('click', function () { cz.style.setProperty('--burst', b.dataset.bg); var bc = cz.querySelector('.pt-bgc'); if (bc) bc.style.background = b.dataset.bg; });
    });
    czSetHair(czHair);
    cz.querySelectorAll('.cz-reset').forEach(function (b) { b.addEventListener('click', function () { czPart(''); }); });
    cz.querySelectorAll('.cz-turn').forEach(function (b) { b.addEventListener('click', function () { czClose(); czSet(czFrame + (+b.dataset.d)); }); });
    cz.querySelector('.cz-stage').addEventListener('click', function (e) { if (czRingEl && !czRingEl.contains(e.target)) czClose(); });
    cz.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && czRingEl) { e.stopPropagation(); var on = czFig.querySelector('.hs.on'); czClose(); if (on) on.focus(); }
    });
    var czDown = null, czDragged = false, czStart = 0;
    czFig.addEventListener('pointerdown', function (e) { czDown = e.clientX; czStart = czFrame; czDragged = false; });
    window.addEventListener('pointermove', function (e) {
      if (czDown === null) return;
      var dx = e.clientX - czDown;
      if (Math.abs(dx) > 8) czDragged = true;
      if (czDragged) { czClose(); czSet(czStart - Math.round(dx / 45)); }
    });
    window.addEventListener('pointerup', function () { czDown = null; setTimeout(function () { czDragged = false; }, 0); });
    czFig.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { czSet(czFrame + (e.key === 'ArrowLeft' ? -1 : 1)); e.preventDefault(); }
    });
  }

  // ---- MyFace Radio: 30-second Apple Music previews of The Money Store, track after track
  var radio = document.getElementById('radio'), np = document.getElementById('np'), amLink = document.getElementById('amLink'),
      skip = document.getElementById('radioNext'), audio = null, tracks = null, ti = 0;
  var ALBUM = 515449028;   // Death Grips, The Money Store
  function setBtn(playing) { radio.innerHTML = playing ? '&#10074;&#10074;' : '&#9654;'; radio.setAttribute('aria-label', playing ? 'Pause' : 'Play'); }
  function playTrack(i) {
    if (!tracks || !tracks.length) return;
    ti = (i + tracks.length) % tracks.length;
    var t = tracks[ti];
    audio.src = t.previewUrl; audio.play().catch(function () {});
    np.textContent = (ti + 1) + '. ' + t.trackName + ' — Death Grips';
    if (amLink) amLink.href = t.trackViewUrl;
  }
  function load() {
    np.textContent = 'tuning in...';
    return fetch('https://itunes.apple.com/lookup?id=' + ALBUM + '&entity=song&country=gb')
      .then(function (r) { return r.json(); })
      .then(function (j) { tracks = j.results.filter(function (x) { return x.wrapperType === 'track' && x.previewUrl; }); });
  }
  if (radio) {
    radio.addEventListener('click', function () {
      if (audio && !audio.paused) { audio.pause(); setBtn(false); return; }
      if (!audio) {
        audio = new Audio(); audio.volume = 0.6;
        audio.addEventListener('ended', function () { playTrack(ti + 1); });
        setBtn(true);
        load().then(function () { playTrack(0); }).catch(function () { np.textContent = 'radio is offline x'; setBtn(false); audio = null; });
      } else { audio.play().catch(function () {}); setBtn(true); }
    });
    if (skip) skip.addEventListener('click', function () { if (audio && tracks) { playTrack(ti + 1); setBtn(true); } });
  }
})();

// ---- Bubble menu (replaces the top nav): bubbles fan out round a centre, categories open a second ring
(function () {
  var btn = document.getElementById('menuBtn'), nav = document.getElementById('bubbleNav');
  if (!btn || !nav) return;
  function read(ul) {
    return Array.prototype.map.call(ul.children, function (li) {
      var a = li.querySelector(':scope > a'), sub = li.querySelector(':scope > ul');
      return { label: a.textContent, href: a.getAttribute('href'), cur: a.hasAttribute('aria-current'), sub: sub ? read(sub) : null };
    });
  }
  var ROOT = read(nav.querySelector('ul')), layer = null, ring = null;
  function close() {
    if (!layer) return;
    layer.classList.remove('open'); var l = layer; layer = null; ring = null;
    setTimeout(function () { l.remove(); }, 200);
    btn.setAttribute('aria-expanded', 'false'); document.documentElement.classList.remove('bn-open'); btn.focus();
  }
  var instant = false;
  var ringLabel = '';                                    // which ring is showing ('' = the main one)
  function show(items, nested, label) {
    ringLabel = nested ? (label || '') : '';
    if (!layer) {
      layer = document.createElement('div'); layer.className = 'bn-layer'; layer.setAttribute('role', 'dialog'); layer.setAttribute('aria-label', 'Menu');
      layer.addEventListener('click', function (e) { if (e.target === layer) close(); });
      document.body.appendChild(layer); document.documentElement.classList.add('bn-open');
      if (instant) layer.classList.add('open', 'nt'); else requestAnimationFrame(function () { layer && layer.classList.add('open'); });
      btn.setAttribute('aria-expanded', 'true');
    }
    if (ring) ring.remove();
    ring = document.createElement('div'); ring.className = 'pie';
    var head = document.createElement('span'); head.className = 'pie-head'; head.innerHTML = '<svg aria-hidden="true"><use href="#mf-mono" width="100%" height="100%"/></svg>'; ring.appendChild(head);
    if (nested) ring.dataset.nested = '1';
    var list = items.slice(); if (nested) list.push({ label: 'Back', back: true });
    var top = list.shift(), L = [], R = [], made = [];
    list.forEach(function (it, i) { (i % 2 ? R : L).push(it); });
    function bubble(it, side, x, y, i) {
      var el;
      if (it.act) {
        el = document.createElement('button'); el.type = 'button';
        el.addEventListener('click', function () { close(); setTimeout(it.act, 220); });
      } else if (it.sub || it.back) {
        el = document.createElement('button'); el.type = 'button';
        el.addEventListener('click', function () { it.back ? show(ROOT, false) : show(it.sub, true, it.label); });
      } else {
        el = document.createElement('a'); el.href = it.href; if (it.cur) el.setAttribute('aria-current', 'page');
        // remember the menu was open here, so Back brings you back to it
        el.addEventListener('click', function () { try { sessionStorage.setItem('mf-menu', JSON.stringify({ at: location.pathname, ring: ringLabel })); } catch (err) {} });
      }
      el.className = 'pie-item ' + side;
      el.innerHTML = '<span class="pk"></span><span class="pl"></span>';
      el.querySelector('.pl').textContent = it.label + (it.sub || it.back ? '...' : '');
      el.style.setProperty('--x', x + 'px'); el.style.setProperty('--y', y + 'px'); el.style.transitionDelay = (i * 20) + 'ms';
      ring.appendChild(el); made.push(el);
    }
    var n = 0, rows = Math.max(L.length, R.length);
    bubble(top, 'c', 0, -110, n++);
    for (var i = 0; i < rows; i++) {
      var t = rows === 1 ? 0 : i / (rows - 1), y = -58 + t * Math.max(120, rows * 36), x = 46 + Math.sin(t * Math.PI) * 50;
      if (L[i]) bubble(L[i], 'l', -x, y, n++);
      if (R[i]) bubble(R[i], 'r', x, y, n++);
    }
    layer.appendChild(ring);
    // fit the whole ring on screen (shrinks a little on phones); measure at full size
    ring.classList.add('open', 'nt');
    var minX = 0, maxX = 0, minY = 0, maxY = 0, o = ring.getBoundingClientRect();
    made.forEach(function (el) { var r = el.getBoundingClientRect();
      minX = Math.min(minX, r.left - o.left); maxX = Math.max(maxX, r.right - o.left); minY = Math.min(minY, r.top - o.top); maxY = Math.max(maxY, r.bottom - o.top); });
    var w = maxX - minX, h = maxY - minY, k = Math.min(1, (innerWidth - 20) / w, (innerHeight - 20) / h);
    ring.style.setProperty('--k', k);
    ring.style.left = (innerWidth / 2 - (minX + w / 2) * k) + 'px'; ring.style.top = (innerHeight / 2 - (minY + h / 2) * k) + 'px';
    if (!instant) { ring.classList.remove('open'); void ring.offsetWidth; ring.classList.remove('nt'); ring.classList.add('open'); }
    else setTimeout(function () { ring && ring.classList.remove('nt'); layer && layer.classList.remove('nt'); }, 50);
    made[0].focus({ preventScroll: true });
  }
  btn.addEventListener('click', function () { layer ? close() : show(ROOT, false); });
  // coming back to the page you left from the menu: open the menu again, on the same ring
  function reopen() {
    var m = null; try { m = JSON.parse(sessionStorage.getItem('mf-menu')); } catch (err) {}
    if (!m || m.at !== location.pathname) return;
    try { sessionStorage.removeItem('mf-menu'); } catch (err) {}
    if (layer) return;
    var sub = m.ring && ROOT.filter(function (it) { return it.label === m.ring && it.sub; })[0];
    sub ? show(sub.sub, true, sub.label) : show(ROOT, false);
  }
  // straight away on load (not after), already open, so there's no jump
  (function () {
    var t = (performance.getEntriesByType && performance.getEntriesByType('navigation')[0] || {}).type;
    if (t === 'back_forward' || !document.documentElement.classList.contains('show-cap')) { instant = true; reopen(); instant = false; }
  })();
  window.addEventListener('pageshow', function (e) {
    var navType = (performance.getEntriesByType && performance.getEntriesByType('navigation')[0] || {}).type;
    if (e.persisted || navType === 'back_forward') reopen();
  });
  document.addEventListener('keydown', function (e) {
    if (!layer) return;
    if (e.key === 'Escape') { e.preventDefault(); if (ring.dataset.nested) show(ROOT, false); else close(); }
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].indexOf(e.key) >= 0) {
      var b = Array.prototype.slice.call(ring.querySelectorAll('.pie-item')), i = b.indexOf(document.activeElement);
      i = (i + (e.key === 'ArrowUp' || e.key === 'ArrowLeft' ? -1 : 1) + b.length) % b.length; b[i].focus(); e.preventDefault();
    }
  });
})();

// ---- Site search: same glossy style, searches every page on the site
(function () {
  var btn = document.getElementById('searchBtn');
  if (!btn) return;
  var idx = null, layer = null, input, list, hits = [], sel = 0, root = btn.dataset.root;
  function load() {
    if (idx) return Promise.resolve(idx);
    return fetch(btn.dataset.index).then(function (r) { return r.json(); }).then(function (j) { idx = j; return j; });
  }
  function score(p, terms) {
    var t = p.t.toLowerCase(), d = (p.u ? p.d + ' ' + p.u.replace(/[\/-]/g, ' ') : '').toLowerCase(), s = 0;   // the homepage only matches 'home'
    for (var i = 0; i < terms.length; i++) {
      var w = terms[i];
      if (t.indexOf(w) >= 0) s += t.indexOf(w) === 0 ? 6 : 4;
      else if (d.indexOf(w) >= 0) s += 1;
      else return 0;                                     // every word has to match somewhere
    }
    return s - p.u.split('/').length * 0.1;              // shorter, top-level pages first
  }
  function render() {
    var q = input.value.trim().toLowerCase();
    list.innerHTML = '';
    if (!q || !idx) { hits = []; return; }
    var terms = q.split(/\s+/);
    hits = idx.map(function (p) { return { p: p, s: score(p, terms) }; }).filter(function (h) { return h.s > 0; })
      .sort(function (a, b) { return b.s - a.s; }).slice(0, 8);
    sel = 0;
    if (!hits.length) { var li = document.createElement('li'); li.className = 'sr-none'; li.textContent = 'nothing found x'; list.appendChild(li); return; }
    hits.forEach(function (h, i) {
      var li = document.createElement('li'), a = document.createElement('a');
      a.className = 'sr-item' + (i === sel ? ' on' : ''); a.href = root + h.p.u;
      a.innerHTML = '<span class="pk"></span><b></b><small></small>';
      a.querySelector('b').textContent = h.p.t; a.querySelector('small').textContent = h.p.d;
      li.appendChild(a); list.appendChild(li);
    });
  }
  function mark() { list.querySelectorAll('.sr-item').forEach(function (a, i) { a.classList.toggle('on', i === sel); }); }
  function close() {
    if (!layer) return;
    layer.classList.remove('open'); var l = layer; layer = null;
    setTimeout(function () { l.remove(); }, 200);
    document.documentElement.classList.remove('bn-open'); btn.focus();
  }
  function open() {
    layer = document.createElement('div'); layer.className = 'bn-layer sr-layer'; layer.setAttribute('role', 'dialog'); layer.setAttribute('aria-label', 'Search');
    layer.innerHTML = '<div class="sr-box"><label class="sr-field"><svg class="mg" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6.5"/><path d="M15 15l6 6"/></svg>' +
      '<input type="search" placeholder="search treatments, prices, aftercare..." aria-label="Search the site" autocomplete="off"></label><ul class="sr-list" role="listbox"></ul></div>';
    input = layer.querySelector('input'); list = layer.querySelector('.sr-list');
    layer.addEventListener('click', function (e) { if (e.target === layer) close(); });
    input.addEventListener('input', function () { load().then(render); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { if (!hits.length) return; sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + hits.length) % hits.length; mark(); e.preventDefault(); }
      else if (e.key === 'Enter' && hits[sel]) location.href = root + hits[sel].p.u;
    });
    document.body.appendChild(layer); document.documentElement.classList.add('bn-open');
    requestAnimationFrame(function () { layer && layer.classList.add('open'); input.focus(); });
    load();
  }
  btn.addEventListener('click', function () { layer ? close() : open(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && layer) { e.preventDefault(); close(); }
    if (e.key === '/' && !layer && !/INPUT|TEXTAREA/.test(document.activeElement.tagName) && !document.body.classList.contains('mf-zoomed')) { e.preventDefault(); open(); }
  });
})();

// ---- The sliding type bands carry on from where they were (no restart when you move between pages)
(function () {
  var tracks = document.querySelectorAll('.band .track'); if (!tracks.length) return;
  var t0 = null; try { t0 = +sessionStorage.getItem('mf-bands'); if (!t0) { t0 = Date.now(); sessionStorage.setItem('mf-bands', t0); } } catch (e) { t0 = Date.now(); }
  var ago = (Date.now() - t0) / 1000;
  tracks.forEach(function (t) { t.style.animationDelay = '-' + ago.toFixed(2) + 's'; });
})();

// ---- floating BOOK button: flash lime the instant it's touched (iOS doesn't show :active on its own)
(function () {
  var b = document.querySelector('.fab-book'); if (!b) return;
  b.addEventListener('pointerdown', function () { b.classList.add('tap'); });
  ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (t) { b.addEventListener(t, function () { setTimeout(function () { b.classList.remove('tap'); }, 180); }); });
  document.addEventListener('touchstart', function () {}, { passive: true });
})();
