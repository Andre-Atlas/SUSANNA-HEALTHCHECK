"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  /** Imagem oficial exibida antes do 3D, sem WebGL e com movimento reduzido. */
  fallbackSrc: string;
  alt: string;
  className?: string;
  /** Só para laboratório e testes: órbita da câmera em graus. */
  debugYaw?: number;
}

type Status = "poster" | "ready" | "fallback";

function webglAvailable() {
  try {
    const c = document.createElement("canvas");
    return !!(c.getContext("webgl2") || c.getContext("webgl"));
  } catch {
    return false;
  }
}

export default function Mascot3D({ fallbackSrc, alt, className, debugYaw = 0 }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<Status>("poster");

  useEffect(() => {
    const el = host.current;
    if (!el) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !webglAvailable()) {
      queueMicrotask(() => setStatus("fallback"));
      return;
    }

    let disposed = false;
    let raf = 0;
    let cleanup = () => {};

    (async () => {
      const [THREE, { RoomEnvironment }, { createSusana }] = await Promise.all([
        import("three"),
        import("three/examples/jsm/environments/RoomEnvironment.js"),
        import("./buildSusana"),
      ]);
      if (disposed) return;

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.05;
      renderer.setClearColor(0x000000, 0);
      const canvas = renderer.domElement;
      canvas.setAttribute("aria-hidden", "true");
      canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:pan-y";
      el.appendChild(canvas);
      cleanup = () => {
        renderer.dispose();
        canvas.remove();
      };

      const scene = new THREE.Scene();
      const pmrem = new THREE.PMREMGenerator(renderer);
      const room = new RoomEnvironment();
      const envTex = pmrem.fromScene(room, 0.04).texture;
      room.dispose();
      scene.environment = envTex;
      scene.environmentIntensity = 0.75;

      const key = new THREE.DirectionalLight(0xffffff, 2.2);
      key.position.set(2.5, 4, 4);
      const fill = new THREE.DirectionalLight(0xbcd7ff, 0.7);
      fill.position.set(-3, 2, 3);
      const rim = new THREE.DirectionalLight(0x93c5fd, 1.6);
      rim.position.set(-1, 3, -4);
      scene.add(key, fill, rim);

      const camera = new THREE.PerspectiveCamera(28, 1, 0.1, 50);
      const target = new THREE.Vector3(0, 1.55, 0);
      const orbit = (debugYaw * Math.PI) / 180;
      camera.position.set(Math.sin(orbit) * 8, 1.8, Math.cos(orbit) * 8);
      camera.lookAt(target);

      const susana = createSusana();
      scene.add(susana.root);

      const input = { lookX: 0, lookY: 0, turn: 0 };
      const resize = () => {
        const w = el.clientWidth || 1;
        const h = el.clientHeight || 1;
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      };
      resize();
      const ro = new ResizeObserver(resize);
      ro.observe(el);

      const onMove = (e: PointerEvent) => {
        const r = el.getBoundingClientRect();
        const cx = r.left + r.width / 2;
        const cy = r.top + r.height * 0.35;
        input.lookX = Math.max(-1, Math.min(1, (e.clientX - cx) / (window.innerWidth * 0.5)));
        input.lookY = Math.max(-1, Math.min(1, (cy - e.clientY) / (window.innerHeight * 0.5)));
      };
      const onScroll = () => {
        const r = el.getBoundingClientRect();
        const p = (r.top + r.height / 2) / window.innerHeight; // 0..1 na tela
        input.turn = Math.max(-1, Math.min(1, (0.5 - p) * 2.4));
      };
      const onEnter = () => susana.wave();
      const onClick = () => susana.celebrate();
      window.addEventListener("pointermove", onMove, { passive: true });
      window.addEventListener("scroll", onScroll, { passive: true });
      el.addEventListener("pointerenter", onEnter);
      el.addEventListener("click", onClick);
      onScroll();

      let visible = true;
      const io = new IntersectionObserver(([en]) => {
        const was = visible;
        visible = en.isIntersecting;
        if (visible && !was) {
          last = performance.now();
          cancelAnimationFrame(raf);
          raf = requestAnimationFrame(loop);
          susana.wave();
        }
      });
      io.observe(el);

      let last = performance.now();
      let first = true;
      const loop = (now: number) => {
        if (disposed || !visible) return;
        susana.update((now - last) / 1000, input);
        last = now;
        renderer.render(scene, camera);
        if (first && susana.entranceProgress() > 0.5) {
          first = false;
          setStatus("ready");
          window.setTimeout(() => susana.wave(), 900);
        }
        raf = requestAnimationFrame(loop);
      };
      raf = requestAnimationFrame(loop);

      const onContextLost = (e: Event) => {
        e.preventDefault();
        setStatus("fallback");
      };
      canvas.addEventListener("webglcontextlost", onContextLost);

      cleanup = () => {
        cancelAnimationFrame(raf);
        ro.disconnect();
        io.disconnect();
        window.removeEventListener("pointermove", onMove);
        window.removeEventListener("scroll", onScroll);
        el.removeEventListener("pointerenter", onEnter);
        el.removeEventListener("click", onClick);
        canvas.removeEventListener("webglcontextlost", onContextLost);
        susana.dispose();
        envTex.dispose();
        pmrem.dispose();
        renderer.dispose();
        renderer.forceContextLoss();
        canvas.remove();
      };
    })().catch(() => {
      cleanup();
      if (!disposed) setStatus("fallback");
    });

    return () => {
      disposed = true;
      cleanup();
    };
  }, [debugYaw]);

  return (
    <div ref={host} className={className} data-mascot={status} style={{ position: "relative" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={fallbackSrc}
        alt={alt}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "contain",
          opacity: status === "ready" ? 0 : 1,
          transition: "opacity .5s ease",
          pointerEvents: "none",
        }}
      />
    </div>
  );
}
