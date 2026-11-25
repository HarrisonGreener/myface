// My Face Radio: a tiny play/pause toggle (add an <audio> source if you want real music)
(function () {
  var b = document.getElementById('radio'), np = document.getElementById('np');
  if (!b) return;
  var on = false;
  b.addEventListener('click', function () {
    on = !on;
    b.innerHTML = on ? '&#10074;&#10074;' : '&#9654;';
    b.setAttribute('aria-label', on ? 'Pause' : 'Play');
    np.textContent = on ? 'Now playing: [your salon playlist]' : 'Press play for salon vibes';
  });
})();
