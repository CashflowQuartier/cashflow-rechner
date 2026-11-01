/* Cinematic-/Sci-Fi-Variante: Bühne (Sterne, Raster, Daten-Globus), HUD-Elemente, Einblendungen. */
(() => {
  const $ = (s, el = document) => el.querySelector(s), $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.body.classList.add("cine");

  /* ---------- HUD-Elemente ---------- */
  const header = $("header");
  if (header) {
    const t = document.createElement("div"); t.className = "hud-ticker"; t.setAttribute("aria-hidden", "true");
    const msg = "SYSTEM ONLINE   ·   KI-PRÜFUNG: JEDE WOHNUNG, JEDEN MONAT   ·   MAHNWESEN: AKTIV   ·   MIETERKOMMUNIKATION: ALLE SPRACHEN   ·   MIETVERTRAG: PER KLICK   ·   ENERGIEVERSORGER: AUTOMATISCH   ·   HUMAN IN THE LOOP: AKTIV   ·   ";
    t.innerHTML = `<span><i></i>${msg}${msg}</span>`; header.after(t);
  }
  const labels = [[".gains-box h2", "Nutzen"], [".how2 h2", "Systemablauf"], [".services h2", "Module und Richtpreise"], [".loi h2", "Absichtserklärung"]];
  labels.forEach(([sel, txt]) => { const h = $(sel); if (h) { const l = document.createElement("span"); l.className = "hud-label"; l.textContent = txt; h.before(l); } });
  $$(".checks li").forEach(li => { const o = document.createElement("span"); o.className = "ok"; o.textContent = "[ OK ]"; li.prepend(o); });
  const k = $(".kicker"); if (k && !reduce) k.classList.add("glitch");
  const pl = $(".player");
  if (pl) pl.insertAdjacentHTML("afterbegin", '<span class="feed" aria-hidden="true"><b>●</b> LIVE FEED</span><span class="feed feed-r" aria-hidden="true">17:00 MIN</span>');
  addEventListener("pointermove", e => { document.body.style.setProperty("--mx", e.clientX + "px"); document.body.style.setProperty("--my", e.clientY + "px"); }, { passive: true });

  /* ---------- Bühne ---------- */
  const c = document.createElement("canvas"); c.id = "stage"; document.body.prepend(c);
  const x = c.getContext("2d");
  let w, h, dpr, t = 0, stars = [], globe = [];
  function size() {
    dpr = Math.min(devicePixelRatio || 1, 2); w = innerWidth; h = innerHeight;
    c.width = w * dpr; c.height = h * dpr; x.setTransform(dpr, 0, 0, dpr, 0, 0);
    stars = Array.from({ length: Math.round(w / 9) }, () => ({ x: Math.random() * w, y: Math.random() * h, z: Math.random() }));
    globe = []; const n = 520;                              // Punkte auf einer Kugel (Fibonacci-Verteilung)
    for (let i = 0; i < n; i++) { const y = 1 - (i / (n - 1)) * 2, r = Math.sqrt(1 - y * y), a = i * 2.39996; globe.push([Math.cos(a) * r, y, Math.sin(a) * r]); }
  }
  function frame() {
    x.clearRect(0, 0, w, h);
    const sy = scrollY, fade = Math.max(0, 1 - sy / (h * 1.2));
    for (const s of stars) {                                // Sterne mit Tiefe
      const py = (s.y - sy * (.05 + s.z * .15)) % h, yy = py < 0 ? py + h : py;
      x.fillStyle = `rgba(200,225,255,${.15 + s.z * .5})`; x.fillRect(s.x, yy, s.z * 1.6 + .4, s.z * 1.6 + .4);
    }
    const hz = h * .62;                                     // Raster-Boden
    x.lineWidth = 1;
    for (let i = -22; i <= 22; i++) { x.strokeStyle = `rgba(233,179,63,${(.09 - Math.abs(i) * .0035) * (.4 + .6 * fade)})`; x.beginPath(); x.moveTo(w / 2, hz); x.lineTo(w / 2 + i * w / 9, h); x.stroke(); }
    const off = (t * .8) % 1;
    for (let k = 0; k < 14; k++) { const p = Math.pow((k + off) / 14, 2.2), y = hz + p * (h - hz); x.strokeStyle = `rgba(94,231,255,${(.02 + p * .12) * (.4 + .6 * fade)})`; x.beginPath(); x.moveTo(0, y); x.lineTo(w, y); x.stroke(); }
    if (fade > 0 && w > 700) {                              // Daten-Globus rechts im ersten Bildschirm
      const R = Math.min(w, h) * .26, cx = w * .78, cy = h * .4 - sy * .3, ry = t * 1.2, cs = Math.cos(ry), sn = Math.sin(ry), tilt = .35;
      for (const [gx, gy, gz] of globe) {
        const X = gx * cs - gz * sn, Z = gx * sn + gz * cs, Y = gy * Math.cos(tilt) - Z * Math.sin(tilt), Z2 = gy * Math.sin(tilt) + Z * Math.cos(tilt);
        const a = (Z2 + 1) / 2; x.fillStyle = Z2 > 0 ? `rgba(255,217,138,${a * .9 * fade})` : `rgba(94,231,255,${a * .35 * fade})`;
        x.fillRect(cx + X * R, cy + Y * R, 1.6, 1.6);
      }
      x.strokeStyle = `rgba(94,231,255,${.25 * fade})`;
      for (const m of [1.18, 1.32]) { x.beginPath(); x.ellipse(cx, cy, R * m, R * m * .28, -.25, 0, 6.283); x.stroke(); }
      const sat = t * 2.4; x.fillStyle = `rgba(255,217,138,${fade})`;
      x.beginPath(); x.arc(cx + Math.cos(sat) * R * 1.18 * Math.cos(-.25) - Math.sin(sat) * R * 1.18 * .28 * Math.sin(-.25), cy + Math.cos(sat) * R * 1.18 * Math.sin(-.25) + Math.sin(sat) * R * 1.18 * .28 * Math.cos(-.25), 3, 0, 6.283); x.fill();
    }
    t += .004;
    if (!reduce) requestAnimationFrame(frame);
  }
  addEventListener("resize", () => { size(); if (reduce) frame(); }); size(); frame();
  if (!reduce) addEventListener("scroll", () => {}, { passive: true });

  /* ---------- Einblenden beim Scrollen (Inhalt bleibt immer sichtbar) ---------- */
  const els = $$(".gains-box,.vrow > div,.team figure,.team > div,.t,.services .card,.cta-line");
  els.forEach(e => e.classList.add("reveal"));
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .2 });
    els.forEach(e => io.observe(e));
  }
})();
