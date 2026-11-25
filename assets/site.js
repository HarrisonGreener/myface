// My Face mascot: drag to spin through the turnaround frames, click to say hi.
(function () {
  var m = document.getElementById('mascot'), btn = document.getElementById('avatarBtn'),
      bubble = document.getElementById('bubble');
  if (!m || !btn) return;

  var FRAMES = 7, frame = 0;
  var lines = ['hiii! what are we getting done today?', 'stop spinning me lol', 'book in, i dare u x',
               'fresh set? new colour? another piercing?', 'rawr means book now in emo'];
  var li = 0;

  function show(f) {
    frame = ((Math.round(f) % FRAMES) + FRAMES) % FRAMES;
    m.style.backgroundPositionX = (frame * 100 / (FRAMES - 1)) + '%';
  }
  function say(t) { if (bubble) bubble.textContent = t; }

  // Drag (mouse or touch) to spin
  var startX = null, startFrame = 0, moved = false;
  btn.addEventListener('pointerdown', function (e) {
    startX = e.clientX; startFrame = frame; moved = false;
    btn.setPointerCapture(e.pointerId);
  });
  btn.addEventListener('pointermove', function (e) {
    if (startX === null) return;
    var dx = e.clientX - startX;
    if (Math.abs(dx) > 6) moved = true;
    show(startFrame - dx / 28);
  });
  function end() { startX = null; }
  btn.addEventListener('pointerup', end);
  btn.addEventListener('pointercancel', end);

  // Click (without dragging) or Enter/Space: turn to face you, hop and talk
  btn.addEventListener('click', function () {
    if (moved) { moved = false; return; }
    show(0);
    li = (li + 1) % lines.length; say(lines[li]);
    btn.classList.remove('hop'); void btn.offsetWidth; btn.classList.add('hop');
  });
  // Arrow keys spin her when focused
  btn.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { show(frame - 1); e.preventDefault(); }
    if (e.key === 'ArrowRight') { show(frame + 1); e.preventDefault(); }
  });

  // Option pills change what she says
  document.querySelectorAll('.pill[data-say]').forEach(function (p) {
    p.addEventListener('mouseenter', function () { say(p.getAttribute('data-say')); });
    p.addEventListener('focus', function () { say(p.getAttribute('data-say')); });
  });

  // One slow spin on load to show she's 3D
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var i = 0, t = setInterval(function () {
      i++; show(i);
      if (i >= FRAMES) { clearInterval(t); show(0); }
    }, 170);
  }
})();
