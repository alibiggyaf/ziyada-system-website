import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function ThreeBackground({ theme = "dark", muted = false }) {
  const mountRef = useRef(null);
  const themeRef = useRef(theme);
  const mutedRef = useRef(muted);
  themeRef.current = theme;
  mutedRef.current = muted;

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    /* ── Renderer ── */
    const W = window.innerWidth, H = window.innerHeight;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(W, H);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);

    /* ── Scene & Camera ── */
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 1000);
    camera.position.z = 30;

    /* ── Mouse tracking ── */
    const mouse   = { x: 0, y: 0 };
    const target  = { x: 0, y: 0 };
    // scroll: track normalized scroll progress (0-1)
    let scrollY   = 0;
    let targetScrollY = 0;

    const onMouseMove = (e) => {
      target.x = (e.clientX / window.innerWidth  - 0.5) * 2;
      target.y = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    const onScroll = () => {
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      targetScrollY = maxScroll > 0 ? window.scrollY / maxScroll : 0;
    };
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("scroll", onScroll, { passive: true });

    /* ── Custom cursor (desktop pointer devices only) ── */
    const isTouchDevice = window.matchMedia("(pointer: coarse)").matches;
    const makeCursorEl = (id, css) => {
      if (document.getElementById(id)) document.getElementById(id).remove();
      const el = document.createElement("div");
      el.id = id; el.style.cssText = css;
      document.body.appendChild(el);
      return el;
    };
    let dot = null, ring = null;
    let cx = W / 2, cy = H / 2, rx = cx, ry = cy;
    let onMouseMoveDOM = null;
    let mutObs = null;

    if (!isTouchDevice) {
      dot = makeCursorEl("z-cursor-dot", `
        position:fixed;pointer-events:none;z-index:9999;
        width:7px;height:7px;border-radius:50%;
        background:#3b82f6;transform:translate(-50%,-50%);top:0;left:0;
        box-shadow:0 0 10px rgba(59,130,246,.9),0 0 22px rgba(59,130,246,.5);
        transition:width .18s,height .18s,background .18s,box-shadow .18s;
      `);
      ring = makeCursorEl("z-cursor-ring", `
        position:fixed;pointer-events:none;z-index:9998;
        width:32px;height:32px;border-radius:50%;
        border:1.5px solid rgba(59,130,246,.55);
        transform:translate(-50%,-50%);top:0;left:0;
        transition:width .14s,height .14s,border-color .14s;
      `);

      onMouseMoveDOM = (e) => { cx = e.clientX; cy = e.clientY; };
      window.addEventListener("mousemove", onMouseMoveDOM);

      const onEnter = () => {
        dot.style.width="14px"; dot.style.height="14px";
        dot.style.background="#8b5cf6";
        dot.style.boxShadow="0 0 14px rgba(139,92,246,.9),0 0 28px rgba(139,92,246,.5)";
        ring.style.width="52px"; ring.style.height="52px";
        ring.style.borderColor="rgba(139,92,246,.6)";
      };
      const onLeave = () => {
        dot.style.width="7px"; dot.style.height="7px";
        dot.style.background="#3b82f6";
        dot.style.boxShadow="0 0 10px rgba(59,130,246,.9),0 0 22px rgba(59,130,246,.5)";
        ring.style.width="32px"; ring.style.height="32px";
        ring.style.borderColor="rgba(59,130,246,.55)";
      };
      const attachCursor = () => {
        document.querySelectorAll("a,button,[role=button],input,textarea,select").forEach(el => {
          el.removeEventListener("mouseenter", onEnter);
          el.removeEventListener("mouseleave", onLeave);
          el.addEventListener("mouseenter", onEnter);
          el.addEventListener("mouseleave", onLeave);
        });
      };
      attachCursor();
      mutObs = new MutationObserver(attachCursor);
      mutObs.observe(document.body, { childList: true, subtree: true });
    }

    /* ══ 3-D SCENE ══ */
    const BLUE   = 0x3b82f6;
    const PURPLE = 0x8b5cf6;

    // Brain core
    const coreGeo = new THREE.IcosahedronGeometry(4, 1);
    const coreMat = new THREE.MeshBasicMaterial({ color: BLUE, wireframe: true, transparent: true, opacity: 0.30 });
    const core = new THREE.Mesh(coreGeo, coreMat);
    scene.add(core);

    // Outer ring — TorusKnot (scroll-linked)
    const tkGeo = new THREE.TorusKnotGeometry(8, 2, 128, 16, 2, 3);
    const tkMat = new THREE.MeshBasicMaterial({ color: PURPLE, wireframe: true, transparent: true, opacity: 0.20 });
    const tk = new THREE.Mesh(tkGeo, tkMat);
    scene.add(tk);

    // 900 particles
    const PARTICLE_COUNT = 500;
    const pPos = new Float32Array(PARTICLE_COUNT * 3);
    for (let i = 0; i < PARTICLE_COUNT * 3; i++) pPos[i] = (Math.random() - 0.5) * 45;
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
    const pMat = new THREE.PointsMaterial({ color: BLUE, size: 0.08, transparent: true, opacity: 0.6 });
    const particles = new THREE.Points(pGeo, pMat);
    scene.add(particles);

    /* ── Animation loop ── */
    let raf;
    const clock = new THREE.Clock();

    const animate = () => {
      raf = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      // Smooth mouse lerp
      mouse.x += (target.x - mouse.x) * 0.05;
      mouse.y += (target.y - mouse.y) * 0.05;

      // Smooth scroll lerp
      scrollY += (targetScrollY - scrollY) * 0.04;

      // DOM cursor (desktop only)
      if (dot) { dot.style.left = cx + "px"; dot.style.top = cy + "px"; }
      if (ring) { rx += (cx - rx) * 0.1; ry += (cy - ry) * 0.1; ring.style.left = rx + "px"; ring.style.top = ry + "px"; }

      // Core — mouse-responsive + gentle floating
      const floatY = Math.sin(elapsed * 0.3) * 0.5;
      core.rotation.x = elapsed * 0.04 + mouse.y * 0.08;
      core.rotation.y = elapsed * 0.05 + mouse.x * 0.08;
      core.position.y = floatY;

      // TorusKnot — cursor drag + slow scroll offset + floating
      tk.rotation.x = elapsed * 0.025 + mouse.y * 0.06 + scrollY * Math.PI * 0.08;
      tk.rotation.y = elapsed * 0.03 + mouse.x * 0.06 + scrollY * Math.PI * 0.05;
      tk.rotation.z = scrollY * Math.PI * 0.1;
      tk.position.y = floatY;

      // Subtle scale on scroll
      const scaleTK = 1 + scrollY * 0.03;
      tk.scale.set(scaleTK, scaleTK, scaleTK);

      particles.rotation.y = elapsed * 0.008 + scrollY * 0.2;
      particles.rotation.x = scrollY * 0.1;

      // Theme opacity — nearly invisible in light mode
      const dark = themeRef.current !== "light";
      const baseCore = dark ? 0.34 : 0.07;
      const baseKnot = dark ? 0.24 : 0.05;
      const baseParticles = dark ? 0.30 : 0.09;
      const factor = mutedRef.current ? 0.55 : 1;

      coreMat.opacity = baseCore * factor;
      tkMat.opacity   = baseKnot * factor;
      pMat.opacity    = baseParticles * factor;

      renderer.render(scene, camera);
    };
    animate();

    const onResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMouseMove);
      if (onMouseMoveDOM) window.removeEventListener("mousemove", onMouseMoveDOM);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
      if (mutObs) mutObs.disconnect();
      ["z-cursor-dot", "z-cursor-ring"].forEach(id => document.getElementById(id)?.remove());
      if (mount.contains(renderer.domElement)) mount.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, []);

  return (
    <div ref={mountRef} style={{ position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none" }} />
  );
}