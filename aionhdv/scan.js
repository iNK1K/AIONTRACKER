// Lecture d'une capture de la reserve d'Aion 2 : grille d'icones -> ressources de recolte + quantites.
// Tout se passe dans le navigateur, sans rien envoyer : les icones sont comparees aux icones officielles
// (window.GATHER), les chiffres a des modeles appris sur des captures du jeu (DIGIT_MODELS).
// Reglages mesures sur 2 captures reelles : 66 ressources sur 66 reconnues, 65 quantites sur 66 (l'erreur signalee).
(function () {
  const S = 24;                               // cote des vignettes comparees
  const ZONE = [0.06, 0.06, 0.88, 0.88];      // zone de l'icone comparee (x, y, l, h en fraction de la case)
  const INSET = 0.06;                         // marge ajoutee autour des icones de reference
  const BAND = [0.765, 0.93], DIGX = [0.25, 0.97];   // bande du nombre (en bas a droite de la case)
  const DIGIT_MODELS = {"0":[0.333,0.915,0.778,0.422,0.0,0.667,0.706,0.5,0.711,0.111,1.0,0.248,0.111,1.0,0.498,1.0,0.0,0.0,1.0,0.883,1.0,0.0,0.0,1.0,0.996,1.0,0.0,0.0,1.0,0.9,1.0,0.211,0.0,1.0,0.4,0.528,0.711,0.5,0.843,0.0,0.056,1.0,1.0,0.685,0.0,0.655],"1":[0.034,0.129,0.225,0.613,1.0,0.189,0.345,0.5,0.75,1.0,0.56,0.474,0.388,0.694,1.0,0.388,0.194,0.0,0.5,1.0,0.002,0.001,0.0,0.5,1.0,0.003,0.002,0.0,0.5,1.0,0.001,0.0,0.0,0.5,1.0,0.0,0.0,0.0,0.5,1.0,0.0,0.0,0.0,0.5,0.999,0.387],"2":[0.342,0.813,0.848,0.611,0.065,0.56,0.541,0.591,0.806,0.16,0.389,0.134,0.167,1.0,0.33,0.0,0.0,0.139,0.9,0.202,0.0,0.028,0.595,0.548,0.0,0.0,0.528,0.68,0.128,0.0,0.528,1.0,0.185,0.0,0.0,1.0,1.0,0.5,0.5,0.5,1.0,1.0,1.0,1.0,1.0,0.651],"3":[0.685,0.77,0.876,0.634,0.034,0.659,0.403,0.624,0.817,0.082,0.317,0.111,0.305,0.917,0.088,0.0,0.459,0.619,0.654,0.022,0.0,0.653,1.0,0.737,0.0,0.0,0.287,0.5,1.0,0.459,0.004,0.0,0.086,1.0,0.748,0.504,0.5,0.586,0.891,0.288,1.0,1.0,1.0,0.783,0.0,0.646],"4":[0.0,0.05,0.294,0.744,0.5,0.014,0.106,0.428,0.836,0.5,0.071,0.347,0.643,0.852,0.5,0.242,0.551,0.467,0.643,0.5,0.448,0.565,0.18,0.539,0.525,0.765,0.775,0.558,0.784,0.775,0.441,0.45,0.607,0.882,0.737,0.0,0.0,0.154,0.654,0.511,0.0,0.0,0.022,0.522,0.5,0.796],"5":[1.0,0.919,0.716,0.717,0.0,1.0,0.698,0.445,0.445,0.0,1.0,0.439,0.287,0.229,0.0,0.8,0.5,0.603,0.556,0.071,0.3,0.3,0.661,0.913,0.25,0.0,0.0,0.258,1.0,0.562,0.057,0.0,0.137,1.0,0.488,0.557,0.5,0.637,0.789,0.104,1.0,1.0,1.0,0.577,0.0,0.661],"6":[0.143,0.343,0.737,0.833,0.0,0.511,0.588,0.429,0.417,0.0,0.94,0.466,0.144,0.083,0.0,1.0,0.319,0.5,0.583,0.069,1.0,0.42,0.417,1.0,0.488,1.0,0.15,0.0,0.928,0.919,1.0,0.206,0.0,0.928,0.822,0.524,0.706,0.5,1.0,0.322,0.048,1.0,1.0,1.0,0.0,0.64],"7":[1.0,1.0,1.0,1.0,0.892,0.625,0.625,0.63,1.0,0.898,0.125,0.125,0.13,1.0,0.452,0.0,0.0,0.382,1.0,0.0,0.0,0.0,0.882,0.533,0.0,0.0,0.262,1.0,0.033,0.0,0.0,0.762,0.708,0.0,0.0,0.14,1.0,0.208,0.0,0.0,0.28,1.0,0.0,0.0,0.0,0.625],"8":[0.226,0.903,0.833,0.588,0.03,0.613,0.626,0.417,0.794,0.085,0.944,0.258,0.083,0.97,0.07,0.652,0.583,0.583,0.817,0.0,0.656,1.0,0.994,0.843,0.0,0.947,0.5,0.494,0.988,0.439,1.0,0.0,0.0,0.985,0.851,0.903,0.5,0.5,0.978,0.412,0.806,1.0,1.0,0.97,0.0,0.64],"9":[0.367,0.793,0.749,0.356,0.041,0.684,0.601,0.493,0.657,0.16,1.0,0.217,0.119,0.956,0.546,0.997,0.21,0.179,0.949,0.873,0.964,0.642,0.619,0.95,0.895,0.467,0.471,0.466,0.947,0.619,0.0,0.0,0.291,0.945,0.199,0.492,0.488,0.744,0.481,0.018,0.983,0.977,0.939,0.01,0.0,0.653]};
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
    const n = prof.length, m = prof.reduce((a, b) => a + b, 0) / n, p = prof.map(v => v - m);
    let best = min, bv = -Infinity;
    for (let lag = min; lag <= Math.min(max, n - 1); lag++) {
      let s = 0;
      for (let i = 0; i + lag < n; i++) s += p[i] * p[i + lag];
      s /= (n - lag);
      if (s > bv) { bv = s; best = lag; }
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
    const lag = period(H >= W ? py : px, 24, Math.min(200, Math.floor(Math.max(W, H) / 2)));
    const fy = fitLines(py, lag), fx = fitLines(px, lag);
    const xs = cellsOn(fx.o, fx.p, W), ys = cellsOn(fy.o, fy.p, H);
    return { xs, ys, px: fx.p, py: fy.p, cols: xs.length, rows: ys.length, W, H };
  }

  // ---------------------------------------------------------------- nombres
  // texte blanc a contour sombre, aligne a droite dans une bande fixe. On decoupe la bande en colonnes d'encre,
  // puis on lit de droite a gauche tant que le morceau ressemble a un chiffre (seul ou fusionne avec son voisin).
  function inkAt(d, i) {
    const r = d[i], g = d[i + 1], b = d[i + 2], s = Math.max(r, g, b) - Math.min(r, g, b);
    return s < 80 ? Math.max(0, Math.min(1, ((r + g + b) / 3 - 120) / 90)) : 0;
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
      const sure = best && sd >= 12 && best.d <= 31 && famGap >= 5.5;
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
  const thumbs = check.map(c => {
    const cv = document.createElement('canvas');
    cv.width = cv.height = 44;
    cv.getContext('2d').drawImage(img, c.x, c.y, res.grid.px, res.grid.py, 0, 0, 44, 44);
    return { cv, c };
  });
  return { text: lines.join('\n'), found: res.cells.filter(c => c.name).length,
           ignored: res.cells.filter(c => !c.name).length, thumbs };
};
