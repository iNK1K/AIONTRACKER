// Lecture d'une capture de la reserve d'Aion 2 : grille d'icones -> ressources de recolte + quantites.
// Tout se passe dans le navigateur, sans rien envoyer : les icones sont comparees aux icones officielles
// (window.GATHER), les chiffres a des modeles appris sur des captures du jeu (DIGIT_MODELS).
// Reglages mesures sur 3 captures reelles (2 tailles d'interface) : 95 ressources sur 97 reconnues, 0 objet pris a
// tort ; quantites : 90 % justes sur une capture jamais vue, 95 % une fois apprise.
(function () {
  const S = 24;                               // cote des vignettes comparees
  const ZONE = [0.06, 0.06, 0.88, 0.88];      // zone de l'icone comparee (x, y, l, h en fraction de la case)
  const INSET = 0.06;                         // marge ajoutee autour des icones de reference
  const BAND = [0.74, 0.96], DIGX = [0.25, 0.97];   // bande du nombre (en bas a droite de la case)
  const DIGIT_MODELS = {"0":[0.0,0.753,0.945,0.068,0.0,0.5,0.654,0.543,0.502,0.071,1.0,0.314,0.07,0.933,0.333,1.0,0.071,0.0,0.851,0.649,1.0,0.071,0.0,0.748,0.801,1.0,0.071,0.0,0.826,0.73,1.0,0.165,0.007,0.929,0.39,0.5,0.594,0.507,0.714,0.104,0.0,0.929,1.0,0.499,0.066,0.607],"1":[0.004,0.029,0.043,0.425,0.809,0.025,0.262,0.495,0.695,0.893,0.493,0.49,0.489,0.742,0.987,0.486,0.254,0.024,0.504,0.989,0.022,0.018,0.011,0.494,0.987,0.015,0.013,0.006,0.491,0.986,0.014,0.01,0.0,0.491,0.986,0.012,0.006,0.0,0.491,0.986,0.006,0.002,0.0,0.491,0.984,0.386],"2":[0.046,0.692,0.949,0.332,0.015,0.487,0.418,0.581,0.649,0.043,0.464,0.072,0.107,0.963,0.198,0.013,0.008,0.018,0.942,0.19,0.019,0.016,0.491,0.502,0.028,0.007,0.482,0.572,0.048,0.001,0.482,0.897,0.123,0.013,0.0,0.964,0.912,0.524,0.505,0.5,0.964,0.977,1.0,1.0,1.0,0.637],"3":[0.437,0.86,0.909,0.367,0.045,0.49,0.435,0.57,0.668,0.057,0.272,0.029,0.164,0.937,0.053,0.0,0.285,0.533,0.543,0.035,0.0,0.43,0.916,0.531,0.047,0.0,0.169,0.431,0.923,0.389,0.0,0.0,0.0,0.966,0.556,0.5,0.5,0.5,0.77,0.217,1.0,1.0,1.0,0.575,0.038,0.625],"4":[0.0,0.0,0.077,0.506,0.429,0.0,0.021,0.3,0.744,0.465,0.015,0.265,0.627,0.87,0.5,0.114,0.446,0.469,0.629,0.5,0.347,0.45,0.103,0.5,0.5,0.683,0.742,0.493,0.747,0.746,0.435,0.494,0.581,0.834,0.744,0.0,0.0,0.088,0.583,0.495,0.0,0.0,0.0,0.492,0.492,0.759],"5":[0.852,0.831,0.805,0.806,0.0,0.926,0.688,0.435,0.435,0.0,1.0,0.297,0.057,0.045,0.0,0.975,0.5,0.507,0.27,0.003,0.475,0.475,0.629,0.757,0.07,0.0,0.0,0.147,1.0,0.339,0.0,0.0,0.025,1.0,0.272,0.49,0.5,0.525,0.677,0.0,0.979,1.0,1.0,0.353,0.0,0.629],"6":[0.119,0.193,0.498,0.801,0.062,0.412,0.497,0.264,0.401,0.031,0.852,0.451,0.109,0.094,0.0,1.0,0.218,0.49,0.594,0.089,1.0,0.222,0.398,0.984,0.407,1.0,0.07,0.001,0.791,0.782,1.0,0.124,0.003,0.791,0.693,0.5,0.592,0.503,0.879,0.254,0.0,0.969,1.0,0.788,0.049,0.634],"7":[0.844,0.844,0.844,0.844,0.704,0.435,0.435,0.44,0.874,0.725,0.013,0.013,0.018,0.902,0.473,0.0,0.0,0.243,0.926,0.2,0.0,0.0,0.693,0.526,0.1,0.0,0.135,0.914,0.1,0.0,0.0,0.585,0.601,0.059,0.0,0.029,0.903,0.187,0.009,0.0,0.057,0.906,0.1,0.0,0.0,0.6],"8":[0.0,0.838,0.99,0.349,0.045,0.5,0.554,0.503,0.633,0.106,1.0,0.176,0.008,0.917,0.167,0.551,0.504,0.5,0.692,0.115,0.389,0.944,0.919,0.701,0.104,0.837,0.523,0.419,0.871,0.423,0.996,0.081,0.0,0.853,0.686,0.794,0.517,0.494,0.869,0.394,0.594,0.953,0.988,0.842,0.117,0.604],"9":[0.043,0.772,0.775,0.075,0.0,0.499,0.578,0.465,0.49,0.027,0.975,0.209,0.082,0.936,0.296,0.995,0.049,0.024,0.954,0.695,0.99,0.503,0.493,0.908,0.777,0.514,0.493,0.493,0.876,0.455,0.022,0.022,0.196,0.93,0.117,0.47,0.469,0.542,0.505,0.013,0.962,0.96,0.744,0.025,0.0,0.618]};
  let refs = null;

  function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
  function pixels(img) {
    const W = img.naturalWidth, H = img.naturalHeight, c = canvas(W, H), g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0);
    return { W, H, d: g.getImageData(0, 0, W, H).data };
  }
  function loadImg(src) {
    return new Promise((ok, ko) => { const i = new Image(); i.onload = () => ok(i); i.onerror = ko; i.src = src; });
  }

  // ---------------------------------------------------------------- icones
  function thumb(img, x, y, w, h) {
    // la zone peut deborder de la capture (case coupee) : on ne garde que la partie visible, sans la deformer
    const sx = x + ZONE[0] * w, sy = y + ZONE[1] * h, sw = ZONE[2] * w, sh = ZONE[3] * h;
    const W = img.naturalWidth, H = img.naturalHeight;
    const x0 = Math.max(0, sx), y0 = Math.max(0, sy), x1 = Math.min(W, sx + sw), y1 = Math.min(H, sy + sh);
    const c = canvas(S, S), g = c.getContext('2d', { willReadFrequently: true });
    g.imageSmoothingQuality = 'high';
    if (x1 > x0 && y1 > y0) g.drawImage(img, x0, y0, x1 - x0, y1 - y0, (x0 - sx) / sw * S, (y0 - sy) / sh * S, (x1 - x0) / sw * S, (y1 - y0) / sh * S);
    const d = g.getImageData(0, 0, S, S).data;
    d.mask = [Math.ceil((x0 - sx) / sw * S), Math.ceil((y0 - sy) / sh * S), Math.floor((x1 - sx) / sw * S), Math.floor((y1 - sy) / sh * S)];
    return d;
  }
  function dist(a, b) {                       // ecart moyen par canal, sur la partie visible de a
    const [mx0, my0, mx1, my1] = a.mask;
    let d = 0, n = 0;
    for (let y = my0; y < my1; y++) for (let x = mx0; x < mx1; x++) {
      const i = (y * S + x) * 4;
      d += Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]); n += 3;
    }
    return n ? d / n : 999;
  }
  function spread(t) {                        // contraste de la vignette : une case vide est presque uniforme
    let s = 0, s2 = 0, n = 0;
    for (let i = 0; i < t.length; i += 4) { const l = (t[i] + t[i + 1] + t[i + 2]) / 3; s += l; s2 += l * l; n++; }
    return Math.sqrt(Math.max(0, s2 / n - (s / n) ** 2));
  }
  // famille d'une ressource : son nom sans la qualite (les qualites d'une meme ressource se ressemblent forcement)
  const family = n => n.replace(/ (d'une grande pureté|pure?s?|éclatante?s?|fraîches?|frais)$/, '');
  async function references() {
    if (refs) return refs;
    refs = [];
    for (const r of window.GATHER || []) {
      try {
        const img = await loadImg(r.s), w = img.naturalWidth, h = img.naturalHeight;
        refs.push({ n: r.n, t: thumb(img, -INSET * w, -INSET * h, w * (1 + 2 * INSET), h * (1 + 2 * INSET)) });
      } catch (e) { /* icone absente : ignoree */ }
    }
    return refs;
  }

  // ---------------------------------------------------------------- grille
  // les cases sont separees par de fines lignes sombres : on cherche, axe par axe, le pas (au 1/20 de pixel) et le
  // decalage qui font tomber le plus de lignes sur les zones sombres du profil de luminosite
  function period(prof, min, max) {
    // autocorrelation du profil ; un multiple du pas (2, 3 cases…) correle presque aussi bien quand la capture
    // contient un titre ou des marges : on garde le plus petit pas qui correle au moins 80 % aussi bien
    const n = prof.length, m = prof.reduce((a, b) => a + b, 0) / n, p = prof.map(v => v - m), ac = [];
    for (let lag = 0; lag <= Math.min(max + 2, n - 1); lag++) {
      let s = 0;
      for (let i = 0; i + lag < n; i++) s += p[i] * p[i + lag];
      ac[lag] = s / (n - lag);
    }
    let best = min;
    for (let lag = min; lag <= Math.min(max, n - 1); lag++) if (ac[lag] > ac[best]) best = lag;
    for (let k = 4; k >= 2; k--) {
      const c = Math.round(best / k);
      if (c < min) continue;
      let loc = c;
      for (let lag = Math.max(min, c - 2); lag <= c + 2; lag++) if (ac[lag] > ac[loc]) loc = lag;
      if (ac[loc] >= 0.8 * ac[best]) return loc;
    }
    return best;
  }
  function fitLines(prof, lag) {
    const n = prof.length;
    const at = v => { const i = Math.round(v); return i >= 0 && i < n ? Math.min(prof[i], prof[Math.max(0, i - 1)], prof[Math.min(n - 1, i + 1)]) : null; };
    let best = null;
    for (let p = lag - 2; p <= lag + 2; p += 0.05) for (let o = 0; o < p; o += 0.5) {
      let s = 0, k = 0;
      for (let v = o; v < n; v += p) { const a = at(v); if (a !== null) { s += a; k++; } }
      if (k >= 2 && (!best || s / k < best.s)) best = { s: s / k, p, o };
    }
    return best;
  }
  function cellsOn(o, p, n) {                 // cases visibles a 75 % au moins le long d'un axe
    const out = [];
    for (let v = o - p; v < n; v += p) if (v >= -0.25 * p && v + p <= n + 0.25 * p) out.push(v);
    return out;
  }
  function grid(P) {
    const { W, H, d } = P, px = new Array(W).fill(0), py = new Array(H).fill(0);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4, l = d[i] + d[i + 1] + d[i + 2];
      px[x] += l / H; py[y] += l / W;
    }
    // pas mesure sur chaque axe (les cases sont presque carrees : on garde le plus fiable des deux pour l'autre)
    const lx = period(px, 24, Math.min(200, Math.floor(W / 2))), ly = period(py, 24, Math.min(200, Math.floor(H / 2)));
    const lag = Math.abs(lx - ly) <= 0.15 * Math.min(lx, ly) ? null : Math.min(lx, ly);
    const fy = fitLines(py, lag || ly), fx = fitLines(px, lag || lx);
    const xs = cellsOn(fx.o, fx.p, W), ys = cellsOn(fy.o, fy.p, H);
    return { xs, ys, px: fx.p, py: fy.p, cols: xs.length, rows: ys.length, W, H };
  }

  // ---------------------------------------------------------------- nombres
  // texte blanc a contour sombre, aligne a droite dans une bande fixe. On decoupe la bande en colonnes d'encre,
  // puis on lit de droite a gauche tant que le morceau ressemble a un chiffre (seul ou fusionne avec son voisin).
  function inkAt(d, i) {
    const r = d[i], g = d[i + 1], b = d[i + 2], s = Math.max(r, g, b) - Math.min(r, g, b);
    return s < 80 ? Math.max(0, Math.min(1, ((r + g + b) / 3 - 140) / 90)) : 0;
  }
  function vec(M, a, b) {                     // glyphe -> 5 x 9 valeurs (part d'encre) + rapport largeur/hauteur
    const sub = M.map(row => row.slice(a, b)), rows = [];
    sub.forEach((row, k) => { if (row.some(v => v > 0.5)) rows.push(k); });
    if (!rows.length) return null;
    const g = sub.slice(rows[0], rows[rows.length - 1] + 1), h = g.length, w = b - a, v = [];
    for (let yy = 0; yy < 9; yy++) for (let xx = 0; xx < 5; xx++) {
      const ya = yy * h / 9, yb = (yy + 1) * h / 9, xa = xx * w / 5, xb = (xx + 1) * w / 5;
      let s = 0, t = 0;
      for (let y = Math.floor(ya); y < Math.max(Math.floor(ya) + 1, Math.ceil(yb)); y++)
        for (let x = Math.floor(xa); x < Math.max(Math.floor(xa) + 1, Math.ceil(xb)); x++)
          if (y < h && x < w) { s += g[y][x]; t++; }
      v.push(t ? s / t : 0);
    }
    v.push(Math.min(1, w / h));
    return v;
  }
  function nearest(v) {
    let best = null;
    for (const [digit, m] of Object.entries(DIGIT_MODELS)) {
      let e = 0;
      for (let i = 0; i < m.length; i++) e += (v[i] - m[i]) ** 2;
      e /= m.length;
      if (!best || e < best.e) best = { digit, e };
    }
    return best;
  }
  function readNumber(P, x, y, G) {
    const { W, H, d } = P;
    const y0 = Math.max(0, Math.round(y + BAND[0] * G.py)), y1 = Math.min(H, Math.round(y + BAND[1] * G.py));
    const x0 = Math.max(0, Math.round(x + DIGX[0] * G.px)), x1 = Math.min(W, Math.round(x + DIGX[1] * G.px));
    if (y1 - y0 < 4 || x1 - x0 < 3) return { qty: null, err: 1 };
    const M = [];
    for (let yy = y0; yy < y1; yy++) { const row = []; for (let xx = x0; xx < x1; xx++) row.push(inkAt(d, (yy * W + xx) * 4)); M.push(row); }
    const col = i => M.reduce((n, row) => n + (row[i] > 0.5 ? 1 : 0), 0), segs = [];
    for (let i = 0; i < x1 - x0;) {
      while (i < x1 - x0 && !col(i)) i++;
      let j = i; while (j < x1 - x0 && col(j)) j++;
      if (j > i) segs.push([i, j]);
      i = j;
    }
    let i = segs.length - 1, txt = '', worst = 0;
    while (i >= 0 && txt.length < 5) {
      const cands = [];
      const one = vec(M, segs[i][0], segs[i][1]);
      if (one) cands.push({ r: nearest(one), n: 1 });
      if (i >= 1 && segs[i][0] - segs[i - 1][1] <= 1 && segs[i][1] - segs[i - 1][0] <= 7) {
        const two = vec(M, segs[i - 1][0], segs[i][1]);
        if (two) cands.push({ r: nearest(two), n: 2 });
      }
      if (!cands.length) break;
      const best = cands.sort((a, b) => a.r.e - b.r.e)[0];
      if (best.r.e > 0.11) break;
      txt = best.r.digit + txt; worst = Math.max(worst, best.r.e); i -= best.n;
      if (i >= 0 && segs[i + 1][0] - segs[i][1] > 3) break;
    }
    return { qty: txt ? parseInt(txt, 10) : null, err: txt ? worst : 1 };
  }

  // ---------------------------------------------------------------- lecture complete
  // img : image de la capture. Retourne la grille, les cases (ressource reconnue ou non, quantite) et le total.
  window.scanReserve = async function (img, opts) {
    opts = opts || {};
    const progress = opts.progress || (() => {});
    const P = pixels(img), G = grid(P);
    progress(`Grille : ${G.cols} colonnes × ${G.rows} rangées. Comparaison des icônes…`);
    const list = await references(), cells = [];
    for (let r = 0; r < G.rows; r++) for (let c = 0; c < G.cols; c++) {
      const x = G.xs[c], y = G.ys[r], t = thumb(img, x, y, G.px, G.py), sd = spread(t);
      const scored = list.map(ref => ({ n: ref.n, d: dist(t, ref.t) })).sort((a, b) => a.d - b.d);
      const best = scored[0], other = best && scored.find(s => family(s.n) !== family(best.n));
      const famGap = best && other ? other.d - best.d : 99;
      // reconnue : case non vide, icone proche, nettement plus proche que toute ressource d'une autre famille
      const sure = best && sd >= 16 && best.d <= 29 && famGap >= 6;
      const cell = { r, c, x, y, name: sure ? best.n : null, d: best ? best.d : null,
                     cutRight: x + G.px > G.W + 1, cutBottom: y + G.py > G.H + 1 };
      if (cell.name) Object.assign(cell, readNumber(P, x, y, G));
      cell.checkQty = cell.name && (cell.qty == null || cell.err > 0.09 || cell.cutRight || cell.cutBottom);
      cells.push(cell);
    }
    return { grid: G, cells };
  };
})();

// Capture -> texte « Nom quantite » pret a coller (les quantites incertaines a part) + vignettes des cases a verifier.
window.reserveToList = async function (img, progress) {
  const res = await scanReserve(img, { progress });
  const total = {}, check = [];
  for (const c of res.cells) {
    if (!c.name) continue;
    if (c.checkQty) check.push(c); else total[c.name] = (total[c.name] || 0) + c.qty;
  }
  const lines = Object.entries(total).sort((a, b) => a[0].localeCompare(b[0], 'fr')).map(([n, q]) => `${n} ${q}`);
  if (check.length) {
    lines.push('# --- à vérifier : quantité lue incertaine, corrige si besoin ---');
    check.forEach(c => lines.push(c.qty == null ? `# ${c.name} : quantité illisible, à saisir` : `${c.name} ${c.qty}`));
  }
  const thumbs = res.cells.filter(c => c.name).map(c => {
    const cv = document.createElement('canvas');
    cv.width = cv.height = 44;
    cv.getContext('2d').drawImage(img, c.x, c.y, res.grid.px, res.grid.py, 0, 0, 44, 44);
    return { cv, c };
  });
  return { text: lines.join('\n'), found: res.cells.filter(c => c.name).length,
           ignored: res.cells.filter(c => !c.name).length, thumbs };
};
