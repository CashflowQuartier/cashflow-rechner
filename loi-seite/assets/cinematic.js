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

  /* ---------- Zahlen-Bühne: hochzählende Kennzahlen, Mahnwesen-Vergleich, Mieterhöhungs-Rechner ---------- */
  const anchor = document.querySelector(".gains2");
  if (anchor) {
    const sec = document.createElement("section");
    sec.className = "nums";
    sec.innerHTML = `
    <div class="wrap">
      <h2>Die Zahlen hinter der Plattform</h2>
      <p class="lead2">Aus unserem eigenen Bestand. Genau so läuft es auch für deinen.</p>
      <div class="ngrid">
        <div class="ntile"><div class="nval"><span data-to="1000" data-fmt="int">0</span><small>+</small></div><div class="nlab">Einheiten verwalten wir selbst über die Plattform</div></div>
        <div class="ntile"><div class="nval"><span data-to="200" data-fmt="int">0</span><small>+</small></div><div class="nlab">Immobilien pro Jahr vermarktet und selbst verwaltet</div></div>
        <div class="ntile"><div class="nval"><span data-from="60" data-to="1" data-fmt="int">60</span><small> Lauf</small></div><div class="nlab">pro Monat für alle Mieterhöhungen, statt rund 60 Arbeitstagen bei 3.000 Einheiten</div></div>
        <div class="ntile"><div class="nval"><span data-from="100" data-to="20" data-fmt="int">100</span><small> %</small></div><div class="nlab">des früheren Verwaltungsaufwands, bei doppelter Qualität</div></div>
      </div>
      <div class="nrow">
        <div class="panel">
          <h3>Weniger Mietausfall</h3>
          <p class="s">Wie lange es dauert, bis ein Rückstand auffällt und gemahnt wird.</p>
          <div class="cmpbar"><div class="bl"><span>Klassische Verwaltung</span><b>Wochen</b></div><div class="track"><div class="fill old" data-w="100"></div></div></div>
          <div class="cmpbar"><div class="bl"><span>CQPM-Plattform</span><b>Tage</b></div><div class="track"><div class="fill new" data-w="18"></div></div></div>
          <div class="cmpbar"><div class="bl"><span>Mieterhöhungen: manuell</span><b>~60 Arbeitstage</b></div><div class="track"><div class="fill old" data-w="100"></div></div></div>
          <div class="cmpbar"><div class="bl"><span>Mieterhöhungen: Plattform</span><b>1 Lauf / Monat</b></div><div class="track"><div class="fill new" data-w="4"></div></div></div>
          <p class="fine">Werte aus unserem Bestand; Mieterhöhungen bezogen auf 3.000 Einheiten.</p>
        </div>
        <div class="panel calc">
          <h3>Mehr Mietertrag: rechne es für deinen Bestand</h3>
          <p class="s">Beispielrechnung mit deinen Annahmen.</p>
          <label for="c-we">Wohnungen <b id="c-we-v"></b></label><input type="range" id="c-we" min="10" max="3000" step="10" value="250">
          <label for="c-qm">Ø Wohnfläche <b id="c-qm-v"></b></label><input type="range" id="c-qm" min="30" max="120" step="1" value="65">
          <label for="c-eur">Ø mögliche Erhöhung je m² und Monat <b id="c-eur-v"></b></label><input type="range" id="c-eur" min="0.10" max="2.00" step="0.05" value="0.50">
          <label for="c-ant">Anteil Wohnungen mit Potenzial <b id="c-ant-v"></b></label><input type="range" id="c-ant" min="5" max="100" step="5" value="40">
          <div class="result"><div class="nval"><span id="c-out">0</span><small> € / Jahr</small></div><div class="nlab">zusätzliche Jahresmiete, wenn das Potenzial genutzt wird</div></div>
          <p class="fine">Ob und wie viel erhöht werden darf, prüft die KI je Wohnung (Kappungsgrenze, Mietspiegel). Beispielrechnung, keine Zusage.</p>
        </div>
      </div>
    </div>`;
    anchor.after(sec);

    const de = n => Math.round(n).toLocaleString("de-DE");
    function tween(el, from, to, ms, fmt) {
      if (reduce) { el.textContent = fmt(to); return; }
      const t0 = performance.now();
      (function step(now) {
        const k = Math.min(1, (now - t0) / ms), e = 1 - Math.pow(1 - k, 3);
        el.textContent = fmt(from + (to - from) * e);
        if (k < 1) requestAnimationFrame(step);
      })(t0);
    }
    function run() {
      sec.querySelectorAll("[data-to]").forEach(el => tween(el, +(el.dataset.from || 0), +el.dataset.to, 1800, de));
      sec.querySelectorAll(".ntile").forEach((t, i) => setTimeout(() => t.classList.add("run"), i * 120));
      sec.querySelectorAll(".fill").forEach((f, i) => setTimeout(() => f.style.width = f.dataset.w + "%", 200 + i * 180));
      calc(true);
    }
    // Rechner
    const g = id => document.getElementById(id);
    let last = 0;
    function calc(animate) {
      const we = +g("c-we").value, qm = +g("c-qm").value, eur = +g("c-eur").value, ant = +g("c-ant").value;
      g("c-we-v").textContent = de(we);
      g("c-qm-v").textContent = qm + " m²";
      g("c-eur-v").textContent = eur.toLocaleString("de-DE", { minimumFractionDigits: 2 }) + " €";
      g("c-ant-v").textContent = ant + " %";
      const val = we * (ant / 100) * qm * eur * 12;
      tween(g("c-out"), animate ? 0 : last, val, animate ? 1800 : 450, de); last = val;
    }
    ["c-we", "c-qm", "c-eur", "c-ant"].forEach(id => g(id).addEventListener("input", () => calc(false)));
    // Startwerte sofort sichtbar (auch ohne Scroll), Animation beim Hineinscrollen
    sec.querySelectorAll("[data-to]").forEach(el => el.textContent = de(+el.dataset.to));
    sec.querySelectorAll(".fill").forEach(f => f.style.width = f.dataset.w + "%");
    calc(false);
    if ("IntersectionObserver" in window && !reduce) {
      sec.querySelectorAll(".fill").forEach(f => f.style.width = "0");
      const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { run(); io.disconnect(); } }, { threshold: .25 });
      io.observe(sec);
    }
  }

  // Abschnitte beim Hineinscrollen einblenden
  const els = document.querySelectorAll(".gains-box,.vrow > div,.team figure,.team > div,.t,.services .card,.cta-line");
  els.forEach(e => e.classList.add("reveal"));
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .2 });
    els.forEach(e => io.observe(e));
  }
})();
