/* Cinematic-Bühne: perspektivisches Raster mit wandernden Lichtpunkten */
(() => {
  document.body.classList.add("cine");
  const c = document.createElement("canvas"); c.id = "stage"; document.body.prepend(c);
  const x = c.getContext("2d"), reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let w, h, dpr, t = 0, pts = [];
  function size() {
    dpr = Math.min(devicePixelRatio || 1, 2); w = innerWidth; h = innerHeight;
    c.width = w * dpr; c.height = h * dpr; x.setTransform(dpr, 0, 0, dpr, 0, 0);
    pts = Array.from({ length: Math.round(w / 18) }, () => ({ x: Math.random() * w, y: Math.random() * h, r: Math.random() * 1.6 + .3, v: Math.random() * .25 + .05 }));
  }
  function frame() {
    x.clearRect(0, 0, w, h);
    const hz = h * .58, g = x.createRadialGradient(w * .5, hz, 0, w * .5, hz, w * .7);
    g.addColorStop(0, "rgba(233,179,63,.10)"); g.addColorStop(1, "rgba(4,6,13,0)");
    x.fillStyle = g; x.fillRect(0, 0, w, h);
    x.lineWidth = 1;
    for (let i = -24; i <= 24; i++) {                       // Fluchtlinien
      x.strokeStyle = `rgba(233,179,63,${.10 - Math.abs(i) * .0035})`;
      x.beginPath(); x.moveTo(w / 2, hz); x.lineTo(w / 2 + i * w / 10, h); x.stroke();
    }
    const off = (t * .6) % 1;                               // Querlinien laufen auf den Betrachter zu
    for (let k = 0; k < 14; k++) {
      const p = Math.pow((k + off) / 14, 2.2), y = hz + p * (h - hz);
      x.strokeStyle = `rgba(233,179,63,${.03 + p * .14})`;
      x.beginPath(); x.moveTo(0, y); x.lineTo(w, y); x.stroke();
    }
    for (const p of pts) {                                  // Datenpunkte
      p.y -= p.v; if (p.y < 0) { p.y = h; p.x = Math.random() * w; }
      x.fillStyle = `rgba(255,217,138,${.25 + .35 * Math.sin(t * 2 + p.x)})`;
      x.beginPath(); x.arc(p.x, p.y, p.r, 0, 6.283); x.fill();
    }
    t += .004;
    if (!reduce) requestAnimationFrame(frame);
  }
  addEventListener("resize", size); size(); frame();
  // Abschnitte beim Hineinscrollen einblenden
  const els = document.querySelectorAll(".gains-box,.vrow > div,.team figure,.team > div,.t,.services .card,.cta-line");
  els.forEach(e => e.classList.add("reveal"));
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .2 });
    els.forEach(e => io.observe(e));
  }
})();
