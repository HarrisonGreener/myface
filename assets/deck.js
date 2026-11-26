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

function cable(points, radius = 0.014, color = C.pink) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  return new THREE.Mesh(new THREE.TubeGeometry(curve, 80, radius, 8, false), mat(color, { roughness: 0.45 }));
}

function buildDeck() {
  const deck = new THREE.Group();
  const leds = [];

  // --- base unit
  const base = new THREE.Mesh(new RoundedBoxGeometry(1.25, 0.24, 1.0, 4, 0.04), mat(C.cream));
  base.position.y = 0.12; deck.add(base);
  const slot = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.025, 0.02), mat(C.chip));
  slot.position.set(0.28, 0.14, 0.505); deck.add(slot);
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.02, 0.01), mat(C.pink));
  stripe.position.set(0, 0.05, 0.503); deck.add(stripe);
  for (let i = 0; i < 3; i++) {
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.014, 12, 8), new THREE.MeshBasicMaterial({ color: i === 1 ? C.cyan : C.pinkHot }));
    led.position.set(-0.48 + i * 0.06, 0.15, 0.505); deck.add(led); leds.push(led);
  }
  // swivel
  const swivel = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.36, 0.08, 32), mat(C.creamDk));
  swivel.position.y = 0.28; deck.add(swivel);

  // --- monitor
  const mon = new THREE.Group(); mon.position.y = 0.75; deck.add(mon);
  const front = new THREE.Mesh(new RoundedBoxGeometry(1.12, 0.92, 0.16, 5, 0.06), mat(C.cream));
  front.position.z = 0.32; mon.add(front);
  const tube = new THREE.Mesh(frustum(1.02, 0.84, 0.72, { x: 0.62, y: 0.6, dy: 0.04 }), mat(C.cream));
  tube.position.z = -0.12; mon.add(tube);
  // vents on top of the tube
  for (let i = 0; i < 7; i++) {
    const v = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.006, 0.025), mat(C.creamDk));
    v.position.set(0, 0.4, -0.02 - i * 0.07); v.rotation.x = -0.12; mon.add(v);
  }
  // bezel + screen
  const bezel = new THREE.Mesh(new RoundedBoxGeometry(0.9, 0.7, 0.04, 4, 0.04), mat(C.bezel, { roughness: 0.4 }));
  bezel.position.set(0, 0.03, 0.39); mon.add(bezel);
  const scr = screenTexture();
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 0.6), new THREE.MeshBasicMaterial({ map: scr.tex, toneMapped: false }));
  screen.position.set(0, 0.03, 0.412); mon.add(screen);
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 0.6), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.08, roughness: 0.05, clearcoat: 1 }));
  glass.position.set(0, 0.03, 0.415); mon.add(glass);
  const glow = new THREE.PointLight(0x9bffe0, 0.6, 1.6); glow.position.set(0, 0.03, 0.7); mon.add(glow);
  // power button + pink badge
  const pwr = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.02, 20), mat(C.pink));
  pwr.rotation.x = Math.PI / 2; pwr.position.set(0.44, -0.38, 0.405); mon.add(pwr);
  // side clips (pink tabs like the render)
  [[-0.565, 0.25], [-0.565, -0.2], [0.565, 0.25], [0.565, -0.2]].forEach(([x, y]) => {
    const t = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.1, 0.06), mat(C.pink)); t.position.set(x, y, 0.3); mon.add(t);
  });

  // --- exposed electronics on the back
  const back = new THREE.Group(); back.position.set(0, 0.04, -0.49); back.rotation.y = Math.PI; mon.add(back);
  const pcb = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.42, 0.015), mat(C.pcb, { roughness: 0.5 }));
  back.add(pcb);
  for (let i = 0; i < 9; i++) {
    const chip = new THREE.Mesh(new THREE.BoxGeometry(0.06 + (i % 3) * 0.02, 0.05, 0.02), mat(C.chip));
    chip.position.set(-0.17 + (i % 3) * 0.15, 0.13 - Math.floor(i / 3) * 0.12, 0.016); back.add(chip);
  }
  for (let i = 0; i < 9; i++) {      // heatsink fins
    const fin = new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.14, 0.07), mat(C.metal, { metalness: 0.7, roughness: 0.3 }));
    fin.position.set(-0.05 + i * 0.018, -0.12, 0.045); back.add(fin);
  }
  for (let i = 0; i < 4; i++) {
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.012, 10, 8), new THREE.MeshBasicMaterial({ color: i % 2 ? C.cyan : C.pinkHot }));
    led.position.set(0.19, 0.16 - i * 0.05, 0.02); back.add(led); leds.push(led);
  }
  // bigger heatsink block
  for (let i = 0; i < 12; i++) {
    const fin = new THREE.Mesh(new THREE.BoxGeometry(0.01, 0.16, 0.1), mat(C.metal, { metalness: 0.75, roughness: 0.28 }));
    fin.position.set(0.02 + i * 0.016, 0.06, 0.06); back.add(fin);
  }
  // glowing module
  const mod = new THREE.Mesh(new RoundedBoxGeometry(0.1, 0.14, 0.05, 2, 0.01), new THREE.MeshStandardMaterial({ color: 0x9dffd8, emissive: 0x4dffc0, emissiveIntensity: 0.6, roughness: 0.3 }));
  mod.position.set(-0.17, -0.1, 0.04); back.add(mod);
  // fan
  const fanRing = new THREE.Mesh(new THREE.TorusGeometry(0.075, 0.012, 10, 32), mat(C.pink));
  fanRing.position.set(0.12, -0.14, 0.04); back.add(fanRing);
  const blades = new THREE.Group(); blades.position.copy(fanRing.position); back.add(blades);
  for (let i = 0; i < 5; i++) {
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.018, 0.005), mat(C.chip));
    b.position.x = 0.032; const p = new THREE.Group(); p.rotation.z = i * Math.PI * 2 / 5; p.add(b); blades.add(p);
  }
  // coiled cable across the board
  const coil = []; for (let i = 0; i <= 40; i++) { const a = i / 40 * Math.PI * 6; coil.push([-0.22 + i * 0.011, 0.19 + Math.sin(a) * 0.025, 0.04 + Math.cos(a) * 0.025]); }
  const coilMesh = cable(coil, 0.007, C.pinkHot); back.add(coilMesh);
  // vents on the back panel edge
  for (let i = 0; i < 6; i++) {
    const v = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.008, 0.01), mat(C.creamDk));
    v.position.set(0, -0.24 - i * 0.015, 0.0); back.add(v);
  }

  // --- cables
  deck.add(cable([[0.2, 1.1, -0.55], [0.45, 1.05, -0.35], [0.6, 0.8, -0.1], [0.62, 0.5, 0.1], [0.5, 0.3, 0.3]]));
  deck.add(cable([[-0.15, 1.0, -0.56], [-0.5, 0.95, -0.4], [-0.62, 0.6, -0.2], [-0.6, 0.27, 0.0], [-0.7, 0.03, 0.35], [-0.55, 0.02, 0.8]], 0.012, C.lilac));
  deck.add(cable([[0.0, 0.62, -0.56], [0.15, 0.4, -0.6], [0.35, 0.25, -0.52], [0.65, 0.12, -0.3], [0.85, 0.02, 0.1], [0.9, 0.02, 0.7]]));
  deck.add(cable([[-0.1, 0.9, -0.56], [0.1, 0.95, -0.62], [0.25, 0.75, -0.6], [0.1, 0.55, -0.6], [-0.15, 0.62, -0.58]], 0.01, C.pinkHot));

  // --- keyboard
  const kb = new THREE.Group(); kb.position.set(-0.05, 0.03, 0.95); kb.rotation.x = 0.06; deck.add(kb);
  kb.add(new THREE.Mesh(new RoundedBoxGeometry(1.05, 0.05, 0.36, 3, 0.02), mat(C.cream)));
  const keyGeo = new RoundedBoxGeometry(0.052, 0.03, 0.052, 2, 0.008);
  const keys = new THREE.InstancedMesh(keyGeo, mat(0xffffff, { roughness: 0.5 }), 15 * 5);
  const m4 = new THREE.Matrix4(), col = new THREE.Color();
  let k = 0;
  for (let r = 0; r < 5; r++) for (let c = 0; c < 15; c++) {
    m4.makeTranslation(-0.455 + c * 0.065, 0.035, -0.13 + r * 0.065); keys.setMatrixAt(k, m4);
    keys.setColorAt(k, col.set((c + r) % 4 === 0 ? C.cream : C.pink)); k++;
  }
  kb.add(keys);

  // --- mouse
  const mouse = new THREE.Mesh(new THREE.SphereGeometry(0.1, 24, 16), mat(C.pink, { roughness: 0.4 }));
  mouse.scale.set(0.6, 0.35, 1); mouse.position.set(0.75, 0.035, 0.95); deck.add(mouse);
  deck.add(cable([[0.75, 0.04, 0.85], [0.8, 0.03, 0.6], [0.7, 0.05, 0.45]], 0.008));

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
  const home = new THREE.Vector3(2.6, 1.9, 3.6);
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
  controls.target.set(0, 0.62, 0.2);
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
