// My Face: the vintage computer on the homepage.
(function () {
  var screen = document.getElementById('screen');
  if (!screen) return;
  var power = document.getElementById('power'), led = document.getElementById('led'),
      boot = document.getElementById('boot'), log = document.getElementById('bootlog');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var on = false;

  // ---- power + boot
  var LINES = ['MYFACE BIOS v2.001', 'checking lashes........ ok', 'checking nails......... ok',
               'loading glitter.drv.... ok', 'mounting /hair /piercing /filler', '', 'welcome x'];
  function booted() {
    on = true; screen.classList.add('booted'); led.classList.add('on');
    power.setAttribute('aria-label', 'Power off');
    try { sessionStorage.setItem('mf-on', '1'); } catch (e) {}
    var first = screen.querySelector('.app'); if (first && document.activeElement === power) first.focus();
  }
  function start() {
    if (on) return;
    if (reduce) return booted();
    boot.classList.add('booting'); led.classList.add('on');
    var i = 0;
    (function next() {
      if (i >= LINES.length) return setTimeout(booted, 350);
      log.textContent += LINES[i++] + '\n';
      setTimeout(next, 170);
    })();
  }
  function stop() {
    on = false; closeAll(); screen.classList.remove('booted'); led.classList.remove('on');
    boot.classList.remove('booting'); log.textContent = '';
    power.setAttribute('aria-label', 'Power on');
    try { sessionStorage.removeItem('mf-on'); } catch (e) {}
  }
  power.addEventListener('click', function () { on ? stop() : start(); });
  boot.addEventListener('click', start);
  try { if (sessionStorage.getItem('mf-on')) booted(); } catch (e) {}

  // ---- clock
  var clock = document.getElementById('clock');
  function tick() { var d = new Date(); clock.textContent = ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
  tick(); setInterval(tick, 20000);

  // ---- windows
  var lastIcon = null;
  function closeAll() {
    screen.querySelectorAll('.app-win').forEach(function (w) { w.hidden = true; });
    screen.querySelectorAll('.app.open').forEach(function (a) { a.classList.remove('open'); });
  }
  screen.querySelectorAll('.app').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      var w = document.getElementById('win-' + a.dataset.app);
      if (!w) return;            // no window: follow the link
      ev.preventDefault();
      closeAll(); w.hidden = false; a.classList.add('open'); lastIcon = a;
      w.querySelector('.close').focus();
    });
  });
  screen.querySelectorAll('.app-win .close').forEach(function (b) {
    b.addEventListener('click', function () { closeAll(); if (lastIcon) lastIcon.focus(); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && screen.querySelector('.app-win:not([hidden])')) { closeAll(); if (lastIcon) lastIcon.focus(); }
  });

  // ---- her.exe: drag to spin through the 7 turnaround frames
  var m = document.getElementById('mascot'), btn = document.getElementById('avatarBtn'), bubble = document.getElementById('bubble');
  if (!m || !btn) return;
  var FR = 7, frame = 0, sx = null, sf = 0, moved = false, li = 0;
  var lines = ['drag me round x', 'stop spinning me lol', 'book in, i dare u', 'rawr means book now in emo'];
  function show(f) { frame = ((Math.round(f) % FR) + FR) % FR; m.style.backgroundPositionX = (frame * 100 / (FR - 1)) + '%'; }
  btn.addEventListener('pointerdown', function (e) { sx = e.clientX; sf = frame; moved = false; btn.setPointerCapture(e.pointerId); });
  btn.addEventListener('pointermove', function (e) { if (sx === null) return; var dx = e.clientX - sx; if (Math.abs(dx) > 5) moved = true; show(sf - dx / 22); });
  btn.addEventListener('pointerup', function () { sx = null; });
  btn.addEventListener('pointercancel', function () { sx = null; });
  btn.addEventListener('click', function () {
    if (moved) { moved = false; return; }
    show(0); li = (li + 1) % lines.length; bubble.textContent = lines[li];
    btn.classList.remove('hop'); void btn.offsetWidth; btn.classList.add('hop');
  });
  btn.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { show(frame - 1); e.preventDefault(); }
    if (e.key === 'ArrowRight') { show(frame + 1); e.preventDefault(); }
  });
})();
