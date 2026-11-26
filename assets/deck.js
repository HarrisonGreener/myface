// MyFace cyberdeck: a procedural three.js model of a pink cyberpunk CRT computer.
// createDeck(container) mounts it and returns { flyIn(done), flyOut(done), dispose() }.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const C = {
  cream: 0xefe6d6, creamDk: 0xd9cdb8, pink: 0xf4a3c6, pinkHot: 0xff4fa3, lilac: 0xc9a7ff,
  bezel: 0x2a2730, pcb: 0x3c6f55, chip: 0x1b1a20, metal: 0xb9b6c2, cyan: 0x5ff6ff,
};

function mat(color, o = {}) { return new THREE.MeshStandardMaterial({ color, roughness: 0.62, metalness: 0.04, ...o }); }

// procedural grime: yellowed patches, dirt in the corners, specks and scratches
function rnd(seed) { let x = seed; return () => (x = (x * 16807) % 2147483647) / 2147483647; }
function grime(seed, base, tint = [150, 120, 70]) {
  const r = rnd(seed), S = 512;
  const cv = document.createElement('canvas'); cv.width = cv.height = S; const g = cv.getContext('2d');
  const rc = document.createElement('canvas'); rc.width = rc.height = S; const h = rc.getContext('2d');
  g.fillStyle = base; g.fillRect(0, 0, S, S); h.fillStyle = '#9a9a9a'; h.fillRect(0, 0, S, S);
  for (let i = 0; i < 26; i++) {                         // yellowed / dirty blotches
    const x = r() * S, y = r() * S, rad = 30 + r() * 140, a = 0.05 + r() * 0.12;
    const gr = g.createRadialGradient(x, y, 0, x, y, rad);
    gr.addColorStop(0, `rgba(${tint[0]},${tint[1]},${tint[2]},${a})`); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  const edge = g.createRadialGradient(S / 2, S / 2, S * 0.25, S / 2, S / 2, S * 0.75);   // grime in the edges
  edge.addColorStop(0, 'rgba(0,0,0,0)'); edge.addColorStop(1, 'rgba(70,55,40,.32)');
  g.fillStyle = edge; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 4500; i++) {                       // specks
    const x = r() * S, y = r() * S, v = r();
    g.fillStyle = v < .5 ? `rgba(60,45,35,${.08 + r() * .25})` : `rgba(255,250,240,${.1 + r() * .2})`;
    g.fillRect(x, y, 1 + r() * 1.5, 1 + r() * 1.5);
    h.fillStyle = `rgba(${v < .5 ? 255 : 0},${v < .5 ? 255 : 0},${v < .5 ? 255 : 0},.25)`; h.fillRect(x, y, 2, 2);
  }
  g.lineCap = 'round';
  for (let i = 0; i < 55; i++) {                         // scratches
    const x = r() * S, y = r() * S, l = 10 + r() * 70, ang = r() * Math.PI;
    g.strokeStyle = `rgba(90,70,55,${.12 + r() * .25})`; g.lineWidth = .6 + r() * 1.2;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(ang) * l, y + Math.sin(ang) * l); g.stroke();
    h.strokeStyle = 'rgba(255,255,255,.5)'; h.lineWidth = 1.5; h.beginPath(); h.moveTo(x, y); h.lineTo(x + Math.cos(ang) * l, y + Math.sin(ang) * l); h.stroke();
  }
  for (let i = 0; i < 6; i++) {                          // smudges
    const x = r() * S, y = r() * S; g.fillStyle = 'rgba(80,65,55,.07)';
    for (let k = 0; k < 12; k++) { g.beginPath(); g.ellipse(x + r() * 30, y + r() * 30, 10 + r() * 16, 5 + r() * 9, r() * 3, 0, 6.3); g.fill(); }
  }
  const map = new THREE.CanvasTexture(cv); map.colorSpace = THREE.SRGBColorSpace;
  const rough = new THREE.CanvasTexture(rc);
  return { map, rough };
}
function dirty(seed, base, o = {}) {
  const t = grime(seed, base, o.tint);
  return new THREE.MeshStandardMaterial({ map: t.map, roughnessMap: t.rough, bumpMap: t.rough, bumpScale: 0.6, roughness: 0.85, metalness: 0.03, ...o.extra });
}

// a box whose back face is shrunk: the tapered tube of a CRT
function frustum(w, h, d, backScale) {
  const g = new THREE.BoxGeometry(w, h, d, 1, 1, 1).toNonIndexed();
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    if (p.getZ(i) < 0) { p.setX(i, p.getX(i) * backScale.x); p.setY(i, p.getY(i) * backScale.y + backScale.dy); }
  }
  g.computeVertexNormals();
  return g;
}

function screenTexture() {
  const cv = document.createElement('canvas'); cv.width = 768; cv.height = 576;
  const ctx = cv.getContext('2d');
  const lines = [
    'MYFACE OS v4.0 // ella.moore',
    '----------------------------------',
    '> boot sequence ......... OK',
    '> lashes.drv ............ OK',
    '> nails.drv ............. OK',
    '> piercing.drv .......... OK',
    '> filler.drv ............ OK',
    '> location: MANCHESTER',
    '',
    '> customise your avatar',
    '',
  ];
  let blink = true;
  function draw() {
    const g = ctx.createRadialGradient(384, 288, 60, 384, 288, 480);
    g.addColorStop(0, '#1a0f22'); g.addColorStop(1, '#07040a');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 768, 576);
    ctx.font = 'bold 30px "Courier New", monospace';
    lines.forEach((l, i) => {
      ctx.fillStyle = i === 0 ? '#ff7cc0' : (l.startsWith('> customise') ? '#ffffff' : '#7dffd1');
      ctx.shadowColor = ctx.fillStyle; ctx.shadowBlur = 10;
      ctx.fillText(l, 40, 64 + i * 40);
    });
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#ff7cc0';
    ctx.font = 'bold 30px "Courier New", monospace';
    ctx.fillText('> CLICK TO LOG IN' + (blink ? ' _' : ''), 40, 64 + lines.length * 40);
    // scanlines
    ctx.fillStyle = 'rgba(0,0,0,.22)';
    for (let y = 0; y < 576; y += 4) ctx.fillRect(0, y, 768, 2);
    tex.needsUpdate = true;
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  draw();
  const timer = setInterval(() => { blink = !blink; draw(); }, 550);
  return { tex, stop: () => clearInterval(timer) };
}


function plug(pos, dir) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.055, 14), mat(0x2b2830, { roughness: 0.5 }));
  const ring = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.012, 14), mat(C.pink));
  ring.position.y = -0.02; g.add(body, ring);
  g.position.copy(pos); g.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
  return g;
}
// a cable that starts and ends in a plug sitting in a socket
function wire(points, color = C.pink, radius = 0.013) {
  const v = points.map(p => new THREE.Vector3(...p));
  const curve = new THREE.CatmullRomCurve3(v, false, 'centripetal');
  const g = new THREE.Group();
  g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 120, radius, 8, false), dirty(color, '#' + new THREE.Color(color).getHexString(), { tint: [90, 60, 70], extra: { roughness: 0.55 } })));
  g.add(plug(v[0], v[0].clone().sub(v[1])));
  g.add(plug(v[v.length - 1], v[v.length - 1].clone().sub(v[v.length - 2])));
  return g;
}

function buildDeck() {
  const deck = new THREE.Group();
  const leds = [];
  const shell = dirty(11, '#ece2cf'), shell2 = dirty(23, '#e3d8c3'), shell3 = dirty(37, '#d6c9b1');

  // --- base unit: chunky system box with a floppy drive (raised everything by B)
  const B = 0.17;
  deck.position.y = -0.09;
  const base = new THREE.Group(); deck.add(base);
  const body = new THREE.Mesh(new RoundedBoxGeometry(1.0, 0.24, 0.82, 4, 0.035), shell3);
  body.position.y = 0.13; base.add(body);
  [[-0.42, -0.34], [0.42, -0.34], [-0.42, 0.34], [0.42, 0.34]].forEach(([x, z]) => {
    const f = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.04, 0.02, 14), mat(0x2a2629)); f.position.set(x, 0.01, z); base.add(f);
  });
  const F = 0.411; // front face z
  // 3.5" floppy bay with a disk half in it
  const bay = new THREE.Mesh(new RoundedBoxGeometry(0.4, 0.085, 0.02, 2, 0.008), dirty(71, '#bfb197'));
  bay.position.set(-0.2, 0.16, F); base.add(bay);
  const slot = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.014, 0.02), mat(0x0d0c10));
  slot.position.set(-0.22, 0.17, F + 0.005); base.add(slot);
  const disk = new THREE.Group(); disk.position.set(-0.22, 0.17, F + 0.03); disk.rotation.x = -0.04; base.add(disk);
  const dk = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.008, 0.11), mat(C.pinkHot, { roughness: 0.5 })); disk.add(dk);
  const shut = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.0095, 0.05), mat(C.metal, { metalness: 0.8, roughness: 0.35 }));
  shut.position.set(0.0, 0, -0.03); disk.add(shut);
  const lab = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.0092, 0.05), dirty(83, '#f4eee2')); lab.position.set(0, 0, 0.03); disk.add(lab);
  const ej = new THREE.Mesh(new RoundedBoxGeometry(0.04, 0.02, 0.015, 2, 0.005), mat(C.pink)); ej.position.set(-0.05, 0.135, F + 0.012); base.add(ej);
  const act = new THREE.Mesh(new THREE.SphereGeometry(0.009, 10, 8), new THREE.MeshBasicMaterial({ color: 0x6dffb0 })); act.position.set(-0.36, 0.135, F + 0.012); base.add(act); leds.push(act);
  // 5.25" blank bay with a little lever
  const bay2 = new THREE.Mesh(new RoundedBoxGeometry(0.34, 0.085, 0.02, 2, 0.008), dirty(73, '#d0c3a9'));
  bay2.position.set(0.24, 0.16, F); base.add(bay2);
  const lever = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.016, 0.02), mat(0x3a3438)); lever.position.set(0.24, 0.165, F + 0.015); base.add(lever);
  // grille slots, power rocker, LED and a pink trim stripe
  for (let i = 0; i < 9; i++) {
    const g = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.05, 0.01), mat(0x3a3236)); g.position.set(-0.36 + i * 0.03, 0.06, F + 0.001); base.add(g);
  }
  const rock = new THREE.Mesh(new RoundedBoxGeometry(0.06, 0.04, 0.02, 2, 0.006), mat(0x2a2629)); rock.position.set(0.3, 0.065, F + 0.008); base.add(rock);
  const pled = new THREE.Mesh(new THREE.SphereGeometry(0.012, 12, 8), new THREE.MeshBasicMaterial({ color: C.pinkHot })); pled.position.set(0.4, 0.065, F + 0.01); base.add(pled); leds.push(pled);
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.94, 0.012, 0.004), mat(C.pink)); stripe.position.set(0, 0.215, F + 0.002); base.add(stripe);
  for (let i = 0; i < 6; i++) {
    const v = new THREE.Mesh(new THREE.BoxGeometry(0.006, 0.12, 0.05), mat(0x5a5048)); v.position.set(0.502, 0.13, -0.25 + i * 0.07); base.add(v);
    const v2 = v.clone(); v2.position.x = -0.502; base.add(v2);
  }
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.22, 0.26, 28), shell2);
  neck.position.y = 0.2 + B; deck.add(neck);
  // swivel collar + tilt mount: neck runs up into the underside of the case
  const collar = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.035, 28), dirty(61, '#c9bba1'));
  collar.position.y = 0.345 + B; deck.add(collar);
  const mount = new THREE.Mesh(new RoundedBoxGeometry(0.46, 0.16, 0.5, 3, 0.03), shell3);
  mount.position.set(0, 0.42 + B, 0.04); deck.add(mount);

  // --- monitor
  const mon = new THREE.Group(); mon.position.y = 0.74 + B; deck.add(mon);
  const front = new THREE.Mesh(new RoundedBoxGeometry(1.12, 0.92, 0.16, 5, 0.06), shell);
  front.position.z = 0.32; mon.add(front);
  const tube = new THREE.Mesh(frustum(1.02, 0.84, 0.72, { x: 0.62, y: 0.6, dy: 0.04 }), shell2);
  tube.position.z = -0.12; mon.add(tube);
  for (let i = 0; i < 7; i++) {
    const v = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.008, 0.025), mat(0x6b5f52));
    v.position.set(0, 0.405 - i * 0.012, -0.02 - i * 0.07); v.rotation.x = -0.12; mon.add(v);
  }
  const bezel = new THREE.Mesh(new RoundedBoxGeometry(0.9, 0.7, 0.04, 4, 0.04), dirty(51, '#2a2730', { tint: [120, 110, 100] }));
  bezel.position.set(0, 0.03, 0.39); mon.add(bezel);
  const scr = screenTexture();
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 0.6), new THREE.MeshBasicMaterial({ map: scr.tex, toneMapped: false }));
  screen.position.set(0, 0.03, 0.412); mon.add(screen);
  const smudge = grime(77, 'rgba(0,0,0,0)', [255, 255, 255]);
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 0.6), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.1, roughness: 0.25, clearcoat: 1, alphaMap: smudge.rough }));
  glass.position.set(0, 0.03, 0.415); mon.add(glass);
  const glow = new THREE.PointLight(0x9bffe0, 0.6, 1.6); glow.position.set(0, 0.03, 0.7); mon.add(glow);
  const pwr = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.02, 20), mat(C.pink));
  pwr.rotation.x = Math.PI / 2; pwr.position.set(0.44, -0.38, 0.405); mon.add(pwr);
  // side sockets (pink port blocks the wires plug into)
  const sockets = [[-0.575, 0.22], [-0.575, -0.2], [0.575, 0.22], [0.575, -0.2]];
  sockets.forEach(([x, y]) => {
    const t = new THREE.Mesh(new RoundedBoxGeometry(0.04, 0.11, 0.08, 2, 0.01), mat(C.pink)); t.position.set(x, y, 0.3); mon.add(t);
    const hole = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.01, 12), mat(0x111111));
    hole.rotation.z = Math.PI / 2; hole.position.set(x + Math.sign(x) * 0.021, y, 0.3); mon.add(hole);
  });

  // --- exposed electronics on the back
  const back = new THREE.Group(); back.position.set(0, 0.04, -0.49); back.rotation.y = Math.PI; mon.add(back);
  back.add(new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.46, 0.015), dirty(63, '#3c6f55', { tint: [40, 30, 20] })));
  for (let i = 0; i < 6; i++) {
    const chip = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.05, 0.02), mat(C.chip));
    chip.position.set(-0.2 + (i % 3) * 0.08, 0.13 - Math.floor(i / 3) * 0.09, 0.016); back.add(chip);
  }
  for (let i = 0; i < 12; i++) {
    const fin = new THREE.Mesh(new THREE.BoxGeometry(0.01, 0.16, 0.1), mat(C.metal, { metalness: 0.75, roughness: 0.4 }));
    fin.position.set(0.04 + i * 0.016, 0.08, 0.06); back.add(fin);
  }
  const mod = new THREE.Mesh(new RoundedBoxGeometry(0.1, 0.12, 0.05, 2, 0.01), new THREE.MeshStandardMaterial({ color: 0x9dffd8, emissive: 0x4dffc0, emissiveIntensity: 0.6, roughness: 0.4 }));
  mod.position.set(-0.17, -0.1, 0.04); back.add(mod);
  const housing = new THREE.Mesh(new RoundedBoxGeometry(0.19, 0.19, 0.045, 2, 0.012), dirty(91, '#26232a'));
  housing.position.set(0.13, -0.13, 0.03); back.add(housing);
  const fanRing = new THREE.Mesh(new THREE.TorusGeometry(0.075, 0.012, 10, 32), mat(C.pink));
  fanRing.position.set(0.13, -0.13, 0.055); back.add(fanRing);
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.02, 14), mat(C.pink));
  hub.rotation.x = Math.PI / 2; hub.position.set(0.13, -0.13, 0.062); back.add(hub);
  [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, b]) => {
    const sc = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.01, 8), mat(C.metal, { metalness: 0.8 }));
    sc.rotation.x = Math.PI / 2; sc.position.set(0.13 + a * 0.078, -0.13 + b * 0.078, 0.055); back.add(sc);
  });
  const blades = new THREE.Group(); blades.position.copy(fanRing.position); back.add(blades);
  for (let i = 0; i < 5; i++) {
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.018, 0.005), mat(C.chip));
    b.position.x = 0.032; const p = new THREE.Group(); p.rotation.z = i * Math.PI * 2 / 5; p.add(b); blades.add(p);
  }
  for (let i = 0; i < 4; i++) {
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.012, 10, 8), new THREE.MeshBasicMaterial({ color: i % 2 ? C.cyan : C.pinkHot }));
    led.position.set(-0.04, 0.16 - i * 0.045, 0.02); back.add(led); leds.push(led);
  }
  // header sockets on the board edge (where the wires plug in), in monitor space
  const hdr = (x, y) => { const h = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.04, 0.03), mat(0x1c1b21)); h.position.set(-x, y + 0.04, -0.515); mon.add(h); };
  [[0.24, 0.2], [-0.24, 0.2], [0.24, -0.17], [-0.05, -0.2], [-0.24, -0.15]].forEach(([x, y]) => hdr(x, y));

  // --- wires: every one runs from a socket to a socket (monitor space)
  const W = [
    // back board top-right -> over the top -> right side socket
    [[-0.24, 0.24, -0.56], [-0.3, 0.42, -0.5], [-0.42, 0.5, -0.15], [-0.6, 0.38, 0.1], [-0.625, 0.22, 0.3]],
    // back board top-left -> down the side -> left lower socket
    [[0.24, 0.24, -0.56], [0.36, 0.3, -0.45], [0.55, 0.05, -0.2], [0.66, -0.15, 0.1], [0.625, -0.2, 0.3]],
    // back board bottom -> down into the stand
    [[0.05, -0.16, -0.56], [0.1, -0.42, -0.5], [0.12, -0.55, -0.25], [0.0, -0.53, -0.12]],
    // right lower socket -> down to the foot
    [[-0.625, -0.2, 0.3], [-0.72, -0.4, 0.3], [-0.5, -0.66, 0.36], [-0.3, -0.665, 0.36]],
    // jumper loop on the back board
    [[0.24, -0.13, -0.56], [0.1, -0.02, -0.66], [-0.1, 0.05, -0.64], [-0.24, 0.24, -0.56]],
  ];
  const cols = [C.pink, C.lilac, C.pink, C.pinkHot, C.pinkHot];
  W.forEach((pts, i) => mon.add(wire(pts, cols[i], i === 4 ? 0.009 : 0.013)));
  // socket on the foot for the last wire
  const fs = new THREE.Mesh(new RoundedBoxGeometry(0.08, 0.04, 0.05, 2, 0.01), mat(C.pink));
  fs.position.set(-0.3, 0.075 + B, 0.33); deck.add(fs);

  deck.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  return { deck, leds, screen, scr, blades };
}

export function createDeck(container) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(32, 1, 0.05, 50);
  const home = new THREE.Vector3(2.2, 1.5, 3.0);
  camera.position.copy(home);

  scene.add(new THREE.HemisphereLight(0xfff4fb, 0x6b4a73, 1.1));
  const key = new THREE.DirectionalLight(0xffffff, 1.7); key.position.set(2.5, 4, 3); key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024); key.shadow.camera.left = -2; key.shadow.camera.right = 2; key.shadow.camera.top = 2; key.shadow.camera.bottom = -2;
  scene.add(key);
  const pinkRim = new THREE.PointLight(0xff4fa3, 6, 8); pinkRim.position.set(-2.5, 1.6, -1.5); scene.add(pinkRim);
  const cyanRim = new THREE.PointLight(0x5ff6ff, 4, 8); cyanRim.position.set(2.5, 1.2, -2); scene.add(cyanRim);

  const ground = new THREE.Mesh(new THREE.CircleGeometry(2.2, 48), new THREE.ShadowMaterial({ opacity: 0.28 }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);

  const { deck, leds, screen, scr, blades } = buildDeck();
  scene.add(deck);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 0.6, 0);
  controls.enableDamping = true; controls.enablePan = false; controls.enableZoom = false;
  controls.minPolarAngle = 0.5; controls.maxPolarAngle = 1.45;
  controls.autoRotate = true; controls.autoRotateSpeed = 0.9;
  controls.addEventListener('start', () => { controls.autoRotate = false; });
  controls.update();

  let flying = null, raf;
  function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    renderer.setSize(w, h, false); camera.aspect = w / h;
    camera.fov = 32; camera.updateProjectionMatrix();
    const a = w / h, k = a < 1.2 ? Math.pow(1.2 / a, 0.85) : 1;
    if (!flying) { const dir = camera.position.clone().sub(controls.target).normalize(); camera.position.copy(controls.target).add(dir.multiplyScalar(home.length() * 0.92 * k)); }
  }
  resize(); window.addEventListener('resize', resize);

  const clock = new THREE.Clock();
  function tick() {
    const t = clock.getElapsedTime();
    leds.forEach((l, i) => { l.visible = Math.sin(t * (2 + i * 0.7) + i) > -0.3; });
    blades.rotation.z = t * 9;
    if (flying) {
      const k = Math.min(1, (performance.now() - flying.start) / flying.ms);
      const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
      camera.position.lerpVectors(flying.fromPos, flying.toPos, e);
      controls.target.lerpVectors(flying.fromTgt, flying.toTgt, e);
      camera.lookAt(controls.target);
      if (k >= 1) { const d = flying.done; flying = null; d && d(); }
    } else controls.update();
    renderer.render(scene, camera);
    raf = requestAnimationFrame(tick);
  }
  tick();

  const saved = { pos: new THREE.Vector3(), tgt: new THREE.Vector3() };
  function screenView() {
    const c = new THREE.Vector3(); screen.getWorldPosition(c);
    const vFov = THREE.MathUtils.degToRad(camera.fov);
    const fitH = 0.6 / 2 / Math.tan(vFov / 2), fitW = 0.8 / 2 / (Math.tan(vFov / 2) * camera.aspect);
    return { pos: c.clone().add(new THREE.Vector3(0, 0, Math.min(fitH, fitW) * 0.92)), tgt: c };
  }
  function fly(toPos, toTgt, ms, done) {
    controls.enabled = false; controls.autoRotate = false;
    flying = { fromPos: camera.position.clone(), fromTgt: controls.target.clone(), toPos, toTgt, ms, start: performance.now(), done };
  }
  return {
    canvas: renderer.domElement,
    flyIn(done) {
      saved.pos.copy(camera.position); saved.tgt.copy(controls.target);
      const v = screenView(); fly(v.pos, v.tgt, 1100, done);
    },
    flyOut(done) { fly(saved.pos.clone(), saved.tgt.clone(), 900, () => { controls.enabled = true; done && done(); }); },
    dispose() { cancelAnimationFrame(raf); scr.stop(); renderer.dispose(); },
  };
}
