import * as THREE from "three";

/** Entrada contínua do mascote: tudo normalizado em -1..1. */
export interface SusanaInput {
  lookX: number;
  lookY: number;
  turn: number;
}

export interface Susana {
  root: THREE.Group;
  update: (dt: number, input: SusanaInput) => void;
  wave: () => void;
  celebrate: () => void;
  think: () => void;
  entranceProgress: () => number;
  dispose: () => void;
}

const WHITE = 0xf3f6fb;
const BLUE = 0x1d4fc4;

const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));
const damp = (cur: number, target: number, lambda: number, dt: number) =>
  cur + (target - cur) * (1 - Math.exp(-lambda * dt));
const easeOutBack = (x: number) => {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
};

/** Ponto na superfície de uma esfera (lon 0 = frente, +z). */
function onSphere(r: number, lon: number, lat: number) {
  return new THREE.Vector3(
    r * Math.cos(lat) * Math.sin(lon),
    r * Math.sin(lat),
    r * Math.cos(lat) * Math.cos(lon),
  );
}

function canvasTexture(w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  draw(c.getContext("2d")!);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

/** Gota: esfera de raio R com ponta a `d` acima do centro, tangente suave. */
function dropProfile(R: number, d: number) {
  const cosA = R / d;
  const a = Math.acos(cosA);
  const pts: THREE.Vector2[] = [];
  const steps = 40;
  for (let i = 0; i <= steps; i++) {
    const th = -Math.PI / 2 + ((Math.PI / 2 - a + Math.PI / 2) * i) / steps;
    pts.push(new THREE.Vector2(Math.max(R * Math.cos(th), 0.0001), R * Math.sin(th)));
  }
  const tx = R * Math.sin(a);
  const ty = R * Math.cos(a);
  const tip = new THREE.Vector2(0.0001, d);
  const ctrl = new THREE.Vector2(tx * 0.42, ty + (d - ty) * 0.55);
  const curve = new THREE.QuadraticBezierCurve(new THREE.Vector2(tx, ty), ctrl, tip);
  curve.getPoints(24).slice(1).forEach((p) => pts.push(p));
  return pts;
}

export function createSusana(): Susana {
  const disposables: { dispose: () => void }[] = [];
  const track = <T extends { dispose: () => void }>(o: T) => {
    disposables.push(o);
    return o;
  };

  const skin = track(
    new THREE.MeshPhysicalMaterial({
      color: WHITE,
      roughness: 0.42,
      clearcoat: 1,
      clearcoatRoughness: 0.28,
      sheen: 0.6,
      sheenColor: new THREE.Color(0xdbeafe),
      sheenRoughness: 0.5,
    }),
  );
  const blueMat = track(new THREE.MeshPhysicalMaterial({ color: BLUE, roughness: 0.35, clearcoat: 0.8 }));

  const mesh = (geo: THREE.BufferGeometry, mat: THREE.Material = skin) => {
    track(geo);
    return new THREE.Mesh(geo, mat);
  };

  const root = new THREE.Group();
  const body = new THREE.Group(); // balança e respira
  root.add(body);

  // ---------- corpo ----------
  const torsoCurve = new THREE.SplineCurve([
    new THREE.Vector2(0.0001, 0.45),
    new THREE.Vector2(0.22, 0.465),
    new THREE.Vector2(0.38, 0.54),
    new THREE.Vector2(0.47, 0.67),
    new THREE.Vector2(0.52, 0.86),
    new THREE.Vector2(0.49, 1.1),
    new THREE.Vector2(0.42, 1.3),
    new THREE.Vector2(0.28, 1.43),
    new THREE.Vector2(0.0001, 1.47),
  ]);
  const torso = mesh(new THREE.LatheGeometry(torsoCurve.getPoints(48), 56));
  body.add(torso);

  // cruz azul
  const cross = new THREE.Shape();
  const a = 0.06;
  const b = 0.17;
  cross.moveTo(-a, -b);
  [
    [a, -b], [a, -a], [b, -a], [b, a], [a, a], [a, b], [-a, b], [-a, a], [-b, a], [-b, -a], [-a, -a],
  ].forEach(([x, y]) => cross.lineTo(x, y));
  cross.closePath();
  const crossMesh = mesh(
    new THREE.ExtrudeGeometry(cross, { depth: 0.02, bevelEnabled: true, bevelSize: 0.01, bevelThickness: 0.01, bevelSegments: 3 }),
    blueMat,
  );
  crossMesh.position.set(0, 0.92, 0.5);
  crossMesh.rotation.x = -0.08;
  body.add(crossMesh);

  // ---------- pernas e pés ----------
  const legGeo = new THREE.CapsuleGeometry(0.17, 0.34, 12, 24);
  const footGeo = new THREE.SphereGeometry(1, 32, 24);
  track(legGeo);
  track(footGeo);
  for (const s of [-1, 1]) {
    const leg = new THREE.Mesh(legGeo, skin);
    leg.position.set(s * 0.2, 0.42, 0);
    root.add(leg);
    const foot = new THREE.Mesh(footGeo, skin);
    foot.scale.set(0.23, 0.13, 0.33);
    foot.position.set(s * 0.21, 0.12, 0.08);
    root.add(foot);
  }

  // ---------- mão ----------
  const fingerGeo = new THREE.CapsuleGeometry(0.03, 0.1, 6, 12);
  track(fingerGeo);
  const palmGeo = new THREE.SphereGeometry(1, 24, 18);
  track(palmGeo);
  const makeHand = (open: boolean) => {
    const hand = new THREE.Group();
    const palm = new THREE.Mesh(palmGeo, skin);
    palm.scale.set(0.115, open ? 0.12 : 0.1, 0.06);
    hand.add(palm);
    if (open) {
      const angles = [0.5, 0.17, -0.12, -0.4];
      const lens = [0.9, 1.15, 1.05, 0.8];
      angles.forEach((ang, i) => {
        const f = new THREE.Mesh(fingerGeo, skin);
        f.scale.set(1, lens[i], 1);
        f.position.set(-Math.sin(ang) * 0.17 + 0.0, Math.cos(ang) * 0.17, 0);
        f.rotation.z = ang;
        hand.add(f);
      });
      const thumb = new THREE.Mesh(fingerGeo, skin);
      thumb.position.set(-0.11, 0.02, 0.02);
      thumb.rotation.z = 1.0;
      hand.add(thumb);
    } else {
      const thumb = new THREE.Mesh(fingerGeo, skin);
      thumb.position.set(0.08, 0.04, 0.03);
      thumb.rotation.z = -0.5;
      thumb.scale.set(1, 0.7, 1);
      hand.add(thumb);
      for (let i = 0; i < 3; i++) {
        const f = new THREE.Mesh(fingerGeo, skin);
        f.scale.set(1, 0.65, 1);
        f.position.set(-0.03 - i * 0.002, -0.1 - i * 0.015, 0.015 - i * 0.02);
        f.rotation.z = 0.15 * i;
        hand.add(f);
      }
    }
    return hand;
  };

  const tube = (pts: THREE.Vector3[], r: number) => {
    const g = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 24, r, 20, false);
    return mesh(g);
  };
  const ball = (r: number) => mesh(new THREE.SphereGeometry(r, 24, 18));

  // braço acenando (lado +x), com cotovelo articulado
  const shoulderR = new THREE.Group();
  shoulderR.position.set(0.4, 1.2, 0.02);
  body.add(shoulderR);
  shoulderR.add(ball(0.125));
  shoulderR.add(tube([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0.16, -0.06, 0.02), new THREE.Vector3(0.34, -0.1, 0.05)], 0.11));
  const elbowR = new THREE.Group();
  elbowR.position.set(0.34, -0.1, 0.05);
  shoulderR.add(elbowR);
  elbowR.add(ball(0.11));
  elbowR.add(tube([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0.07, 0.22, 0.02), new THREE.Vector3(0.1, 0.42, 0.0)], 0.105));
  const wrist = ball(0.105);
  wrist.position.set(0.1, 0.42, 0);
  elbowR.add(wrist);
  const handR = makeHand(true);
  handR.position.set(0.1, 0.5, 0);
  handR.rotation.z = -0.15;
  elbowR.add(handR);

  // braço na cintura (lado -x)
  const shoulderL = new THREE.Group();
  shoulderL.position.set(-0.4, 1.2, 0.02);
  body.add(shoulderL);
  shoulderL.add(ball(0.125));
  shoulderL.add(
    tube(
      [
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(-0.15, -0.12, 0.02),
        new THREE.Vector3(-0.2, -0.34, 0.06),
        new THREE.Vector3(-0.02, -0.5, 0.2),
      ],
      0.108,
    ),
  );
  const handL = makeHand(false);
  handL.position.set(-0.01, -0.52, 0.24);
  handL.rotation.set(0.2, 0.5, 0.5);
  shoulderL.add(handL);

  // ---------- cabeça ----------
  const head = new THREE.Group();
  head.position.set(0, 1.98, 0.02);
  body.add(head);
  const R = 0.64;
  const headMesh = mesh(new THREE.LatheGeometry(dropProfile(R, 1.18), 72));
  head.add(headMesh);

  // cacho em espiral, no plano da superfície frontal da ponta
  const curlPts: THREE.Vector3[] = [];
  for (let i = 0; i <= 80; i++) {
    const t = i / 80;
    const ang = t * Math.PI * 3.4 + 0.3;
    const rad = 0.2 * (1 - t * 0.88);
    curlPts.push(new THREE.Vector3(Math.cos(ang) * rad, Math.sin(ang) * rad, 0));
  }
  const curlGroup = new THREE.Group();
  curlGroup.add(mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(curlPts), 160, 0.058, 16, false)));
  const curlCap = ball(0.058);
  curlCap.position.copy(curlPts[curlPts.length - 1]);
  curlGroup.add(curlCap);
  const curlBase = ball(0.062);
  curlBase.position.copy(curlPts[0]);
  curlGroup.add(curlBase);
  curlGroup.position.set(0.02, 0.68, 0.31);
  curlGroup.rotation.set(-0.5, 0, 0);
  curlGroup.scale.setScalar(1.25);
  head.add(curlGroup);

  // decalque do rosto: sobrancelhas, cílios, bochechas e sorriso
  const faceTex = track(
    canvasTexture(1024, 512, (g) => {
      g.clearRect(0, 0, 1024, 512);
      const cheek = (x: number) => {
        const gr = g.createRadialGradient(x, 300, 4, x, 300, 70);
        gr.addColorStop(0, "rgba(244,143,177,0.55)");
        gr.addColorStop(1, "rgba(244,143,177,0)");
        g.fillStyle = gr;
        g.fillRect(x - 90, 210, 180, 180);
      };
      cheek(310);
      cheek(714);
      g.lineCap = "round";
      g.strokeStyle = "#7b5b4a";
      g.lineWidth = 9;
      g.beginPath();
      g.moveTo(312, 190);
      g.quadraticCurveTo(372, 150, 452, 172);
      g.moveTo(572, 172);
      g.quadraticCurveTo(652, 150, 712, 190);
      g.stroke();
      g.strokeStyle = "#e07a93";
      g.lineWidth = 8;
      g.beginPath();
      g.moveTo(440, 352);
      g.quadraticCurveTo(512, 392, 584, 352);
      g.stroke();
      g.lineWidth = 5;
      g.beginPath();
      g.moveTo(582, 353);
      g.quadraticCurveTo(596, 348, 604, 336);
      g.moveTo(442, 353);
      g.quadraticCurveTo(428, 348, 420, 336);
      g.stroke();
    }),
  );
  const faceGeo = new THREE.SphereGeometry(R + 0.004, 64, 48, 0, Math.PI, 0.7, 1.7);
  // u = 0..1 mapeia longitude -90..+90 graus; rotacionamos para a frente (+z)
  const face = mesh(
    faceGeo,
    track(new THREE.MeshBasicMaterial({ map: faceTex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 })),
  );
  face.rotation.y = 0;
  head.add(face);

  // olhos
  const eyeTex = track(
    canvasTexture(256, 256, (g) => {
      g.clearRect(0, 0, 256, 256);
      g.fillStyle = "#ffffff";
      g.beginPath();
      g.ellipse(128, 128, 110, 118, 0, 0, Math.PI * 2);
      g.fill();
      const iris = g.createRadialGradient(128, 120, 10, 128, 128, 92);
      iris.addColorStop(0, "#0b3d91");
      iris.addColorStop(0.55, "#2f7ff0");
      iris.addColorStop(1, "#7cc0ff");
      g.fillStyle = iris;
      g.beginPath();
      g.arc(128, 132, 88, 0, Math.PI * 2);
      g.fill();
      g.strokeStyle = "#0a2a66";
      g.lineWidth = 7;
      g.stroke();
      g.fillStyle = "#06143a";
      g.beginPath();
      g.arc(128, 134, 40, 0, Math.PI * 2);
      g.fill();
      g.fillStyle = "#ffffff";
      g.beginPath();
      g.arc(98, 98, 22, 0, Math.PI * 2);
      g.fill();
      g.beginPath();
      g.arc(160, 164, 10, 0, Math.PI * 2);
      g.fill();
      // cílios superiores
      g.strokeStyle = "#5a3d33";
      g.lineWidth = 9;
      g.lineCap = "round";
      g.beginPath();
      g.ellipse(128, 128, 112, 120, 0, Math.PI * 1.08, Math.PI * 1.95);
      g.stroke();
    }),
  );
  const eyeMat = track(new THREE.MeshBasicMaterial({ map: eyeTex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4 }));
  const eyes: THREE.Mesh[] = [];
  for (const s of [-1, 1]) {
    const eye = mesh(new THREE.CircleGeometry(0.135, 40), eyeMat);
    const p = onSphere(R + 0.008, s * 0.38, 0.06);
    eye.position.copy(p);
    eye.lookAt(p.clone().multiplyScalar(3));
    eye.scale.set(1, 1.08, 1);
    eyes.push(eye);
    head.add(eye);
  }

  // colar e pingente
  const chainCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-0.3, 1.5, 0.15),
    new THREE.Vector3(-0.18, 1.42, 0.35),
    new THREE.Vector3(0, 1.36, 0.46),
    new THREE.Vector3(0.18, 1.42, 0.35),
    new THREE.Vector3(0.3, 1.5, 0.15),
  ]);
  const chain = mesh(
    new THREE.TubeGeometry(chainCurve, 32, 0.006, 6, false),
    track(new THREE.MeshStandardMaterial({ color: 0xcfd8e6, metalness: 0.7, roughness: 0.3 })),
  );
  body.add(chain);
  const pendant = mesh(
    new THREE.LatheGeometry(dropProfile(0.05, 0.1), 28),
    track(
      new THREE.MeshPhysicalMaterial({
        color: 0x9fd4ff,
        roughness: 0.05,
        transparent: true,
        opacity: 0.88,
        ior: 1.45,
        clearcoat: 1,
        emissive: 0x4aa8ff,
        emissiveIntensity: 0.25,
      }),
    ),
  );
  pendant.position.set(0, 1.27, 0.49);
  pendant.rotation.x = 0.15;
  body.add(pendant);

  // sombra de contato
  const shadowTex = track(
    canvasTexture(256, 256, (g) => {
      const gr = g.createRadialGradient(128, 128, 8, 128, 128, 126);
      gr.addColorStop(0, "rgba(30,64,175,0.38)");
      gr.addColorStop(1, "rgba(30,64,175,0)");
      g.fillStyle = gr;
      g.fillRect(0, 0, 256, 256);
    }),
  );
  const shadow = mesh(new THREE.PlaneGeometry(1.7, 1.7), track(new THREE.MeshBasicMaterial({ map: shadowTex, transparent: true, depthWrite: false })));
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.005;
  root.add(shadow);

  // ---------- animação ----------
  const st = {
    t: 0,
    entrance: 0,
    lookX: 0,
    lookY: 0,
    turn: 0,
    nextBlink: 2.2,
    blink: -1,
    wave: -1,
    jump: -1,
    think: 0,
    thinkTarget: 0,
  };

  const update = (dt: number, input: SusanaInput) => {
    dt = Math.min(dt, 0.05);
    st.t += dt;
    st.entrance = Math.min(1, st.entrance + dt / 0.8);

    // entrada: squash and stretch
    const e = easeOutBack(st.entrance);
    const sq = st.entrance < 1 ? Math.sin(st.entrance * Math.PI) * 0.12 : 0;
    root.scale.set(e * (1 + sq), e * (1 - sq), e * (1 + sq));

    // repouso
    const float = Math.sin((st.t / 5) * Math.PI * 2) * 0.5 + 0.5;
    let y = float * 0.12;
    const breathe = 1 + Math.sin((st.t / 3.6) * Math.PI * 2) * 0.015;

    if (st.jump >= 0) {
      st.jump += dt;
      const j = clamp(st.jump / 0.9, 0, 1);
      y += Math.sin(j * Math.PI) * 0.6;
      if (j >= 1) st.jump = -1;
    }
    body.position.y = y;
    body.scale.set(1, breathe, 1);
    shadow.scale.setScalar(1 - y * 0.35);
    (shadow.material as THREE.MeshBasicMaterial).opacity = 1 - y * 0.5;

    // olhar e giro
    st.lookX = damp(st.lookX, clamp(input.lookX, -1, 1), 6, dt);
    st.lookY = damp(st.lookY, clamp(input.lookY, -1, 1), 6, dt);
    st.turn = damp(st.turn, clamp(input.turn, -1, 1), 3, dt);
    st.think = damp(st.think, st.thinkTarget, 5, dt);
    const rad = Math.PI / 180;
    head.rotation.y = st.lookX * 18 * rad;
    head.rotation.x = -st.lookY * 10 * rad + st.think * 0.05;
    head.rotation.z = st.think * -0.22;
    root.rotation.y = st.turn * 25 * rad;

    // piscar
    st.nextBlink -= dt;
    if (st.nextBlink <= 0 && st.blink < 0) {
      st.blink = 0;
      st.nextBlink = 3 + Math.random() * 3;
    }
    let eyeY = 1.08;
    if (st.blink >= 0) {
      st.blink += dt;
      const b = clamp(st.blink / 0.18, 0, 1);
      eyeY = 1.08 * (1 - Math.sin(b * Math.PI) * 0.92);
      if (b >= 1) st.blink = -1;
    }
    eyes.forEach((m) => (m.scale.y = Math.max(eyeY, 0.06)));

    // aceno: cotovelo oscila; sem aceno, braço relaxado
    let elbow = 0;
    let lift = 0;
    if (st.wave >= 0) {
      st.wave += dt;
      const w = st.wave / 2.4;
      const env = Math.sin(clamp(w, 0, 1) * Math.PI);
      elbow = Math.sin(st.wave * 9) * 0.32 * clamp(env * 2, 0, 1);
      lift = env * 0.15;
      if (w >= 1) st.wave = -1;
    }
    const celebrating = st.jump >= 0;
    const raise = celebrating ? 1 : 0;
    elbowR.rotation.z = elbow + raise * 0.25;
    shoulderR.rotation.z = lift + raise * 0.6;
    shoulderL.rotation.z = 0;
    shoulderL.rotation.x = 0;
  };

  return {
    root,
    update,
    wave: () => {
      if (st.wave < 0) st.wave = 0;
    },
    celebrate: () => {
      if (st.jump < 0) {
        st.jump = 0;
        st.wave = 0;
      }
    },
    entranceProgress: () => st.entrance,
    think: () => {
      st.thinkTarget = st.thinkTarget ? 0 : 1;
    },
    dispose: () => disposables.forEach((d) => d.dispose()),
  };
}
