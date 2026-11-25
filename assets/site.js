// My Face: 3D computer on the homepage that zooms into a MySpace-style profile.
(function () {
  var scene = document.getElementById('scene');
  if (!scene) return;
  var rig = document.getElementById('rig'), screen = document.getElementById('screen'), os = document.getElementById('os'),
      zoomBtn = document.getElementById('zoomBtn'), zv = document.getElementById('zoomview'), zvScreen = document.getElementById('zvScreen'),
      logoff = document.getElementById('logoff');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var P = 1600, rx = -10, ry = -24, zoomed = false, busy = false;

  os.inert = true;                                   // the small preview isn't tabbable; the zoomed copy is

  function fit() { return Math.min(1, (scene.clientWidth - 24) / (scene.clientWidth < 600 ? 900 : 820), scene.clientHeight / 620); }
  function rest() { rig.style.transform = 'scale(' + fit() + ') rotateX(' + rx + 'deg) rotateY(' + ry + 'deg)'; }
  rest();
  window.addEventListener('resize', function () { if (!zoomed) rest(); });

  // Tilt towards the pointer
  scene.addEventListener('pointermove', function (e) {
    if (zoomed || busy) return;
    var r = scene.getBoundingClientRect();
    var mx = (e.clientX - r.left) / r.width - .5, my = (e.clientY - r.top) / r.height - .5;
    rx = -10 - my * 10; ry = -24 + mx * 30;
    rig.classList.add('follow'); rest();
  });
  scene.addEventListener('pointerleave', function () { if (!zoomed && !busy) { rx = -10; ry = -24; rest(); } });

  // Fly the camera into the screen, then hand over to a full-size copy of the screen
  function zoomIn() {
    if (zoomed || busy) return;
    busy = true; rig.classList.remove('follow'); scene.parentNode.classList.add('zooming');
    var s = fit(), vw = window.innerWidth, vh = window.innerHeight;
    var k = Math.max(vw / (432 * s), vh / (324 * s)) * 1.02;        // how much bigger the screen must look
    var z = P * (1 - 1 / k) - 150 * s;                               // the screen sits 150px in front of the rig centre
    // screen centre is 34+216-250 = 0px across and 28+162-210-70 = -90px up from the rig centre
    var r = scene.getBoundingClientRect(), dy = (vh / 2) - (r.top + r.height / 2);
    rig.style.transform = 'translate3d(0,' + (dy + 90 * s) + 'px,' + z + 'px) scale(' + s + ')';
    setTimeout(function () {
      zvScreen.appendChild(os); os.inert = false;
      zv.hidden = false; requestAnimationFrame(function () { zv.classList.add('show'); });
      document.body.style.overflow = 'hidden';
      zoomed = true; busy = false; bootUp();
    }, reduce ? 0 : 1000);
  }
  function zoomOut() {
    if (!zoomed || busy) return;
    busy = true; zv.classList.remove('show');
    setTimeout(function () {
      zv.hidden = true; closeAll(); screen.insertBefore(os, screen.firstChild); os.inert = true;
      document.body.style.overflow = '';
      rx = -10; ry = -24; rest(); scene.parentNode.classList.remove('zooming');
      setTimeout(function () { zoomed = false; busy = false; zoomBtn.focus(); }, reduce ? 0 : 1000);
    }, reduce ? 0 : 350);
  }
  zoomBtn.addEventListener('click', zoomIn);
  scene.addEventListener('click', zoomIn);
  logoff.addEventListener('click', zoomOut);
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (os.querySelector('.app-win:not([hidden])')) { closeAll(); if (lastIcon) lastIcon.focus(); } else zoomOut();
  });

  // Boot text on the way in (once per visit)
  var boot = document.getElementById('boot'), log = document.getElementById('bootlog'), hasBooted = false;
  var LINES = ['MYFACE BIOS v2.001', 'checking lashes........ ok', 'checking nails......... ok',
               'loading glitter.drv.... ok', 'mounting /hair /piercing /filler', '', 'welcome x'];
  function bootUp() {
    var first = os.querySelector('.app');
    if (hasBooted || reduce) { hasBooted = true; first.focus(); return; }
    hasBooted = true; boot.classList.add('on'); log.textContent = '';
    var i = 0;
    (function next() {
      if (i >= LINES.length) return setTimeout(function () { boot.classList.remove('on'); first.focus(); }, 350);
      log.textContent += LINES[i++] + '\n'; setTimeout(next, 150);
    })();
  }

  // Clock
  var clock = document.getElementById('clock');
  function tick() { var d = new Date(); clock.textContent = ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
  tick(); setInterval(tick, 20000);

  // Desktop windows
  var lastIcon = null;
  function closeAll() {
    os.querySelectorAll('.app-win').forEach(function (w) { w.hidden = true; });
    os.querySelectorAll('.app.open').forEach(function (a) { a.classList.remove('open'); });
  }
  os.querySelectorAll('.app').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      var w = document.getElementById('win-' + a.dataset.app);
      if (!w || !zoomed) return;
      ev.preventDefault();
      closeAll(); w.hidden = false; a.classList.add('open'); lastIcon = a;
      w.querySelector('.close').focus();
    });
  });
  os.querySelectorAll('.app-win .close').forEach(function (b) {
    b.addEventListener('click', function () { closeAll(); if (lastIcon) lastIcon.focus(); });
  });

  // Profile pic: drag to spin her through the 7 turnaround frames, click to hop
  var m = document.getElementById('mascot'), btn = document.getElementById('avatarBtn');
  var bubble = document.getElementById('bubble'), li = 0, lines = ['drag me round x', 'stop spinning me lol', 'book in, i dare u', 'rawr means book now in emo'];
  var FR = 7, frame = 0, sx = null, sf = 0, moved = false;
  function show(f) { frame = ((Math.round(f) % FR) + FR) % FR; m.style.backgroundPositionX = (frame * 100 / (FR - 1)) + '%'; }
  btn.addEventListener('pointerdown', function (e) { sx = e.clientX; sf = frame; moved = false; btn.setPointerCapture(e.pointerId); });
  btn.addEventListener('pointermove', function (e) { if (sx === null) return; var dx = e.clientX - sx; if (Math.abs(dx) > 5) moved = true; show(sf - dx / 20); });
  btn.addEventListener('pointerup', function () { sx = null; });
  btn.addEventListener('pointercancel', function () { sx = null; });
  btn.addEventListener('click', function () {
    if (moved) { moved = false; return; }
    show(0); li = (li + 1) % lines.length; bubble.textContent = lines[li];
    m.classList.remove('hop'); void m.offsetWidth; m.classList.add('hop');
  });
  btn.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { show(frame - 1); e.preventDefault(); }
    if (e.key === 'ArrowRight') { show(frame + 1); e.preventDefault(); }
  });

  // Profile "song"
  var radio = document.getElementById('radio'), np = document.getElementById('np'), on = false;
  radio.addEventListener('click', function () {
    on = !on; radio.innerHTML = on ? '&#10074;&#10074;' : '&#9654;'; radio.setAttribute('aria-label', on ? 'Pause' : 'Play');
    np.textContent = on ? 'now playing: [your salon playlist]' : 'press play for salon vibes';
  });
})();
