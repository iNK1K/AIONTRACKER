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

  window.__thumb = thumb; window.__dist = dist; window.__readNumber = readNumber;

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

// ======================================================================== annonces en vente
// Capture de la fenetre « Mes ventes » : une ligne par annonce (icone avec quantite, nom, prix total et unitaire).
// L'objet est reconnu par son icone (window.MARKET_ICONS), la quantite comme dans la reserve, les prix par des
// modeles de chiffres appris sur une capture de cette fenetre (PRICE_MODELS) ; total = unitaire x quantite sert de
// verification.
(function () {
  // chiffres des prix, appris sur une capture reelle (pas encore de 8 : un prix avec un 8 est signale a verifier)
  const PRICE_MODELS = {"0": [0.446, 0.72, 0.709, 0.624, 0.347, 0.781, 0.69, 0.474, 0.674, 0.609, 0.868, 0.44, 0.119, 0.532, 0.705, 0.829, 0.312, 0, 0.434, 0.727, 0.811, 0.294, 0, 0.415, 0.735, 0.829, 0.312, 0, 0.434, 0.749, 0.869, 0.395, 0.034, 0.49, 0.723, 0.777, 0.653, 0.421, 0.677, 0.665, 0.441, 0.775, 0.843, 0.741, 0.388, 0.631], "1": [0.051, 0.355, 0.613, 0.913, 0.897, 0.5, 0.796, 0.885, 0.926, 0.897, 0.489, 0.646, 0.493, 0.864, 0.897, 0.04, 0.184, 0.125, 0.84, 0.897, 0, 0, 0.125, 0.852, 0.898, 0, 0, 0.125, 0.852, 0.898, 0, 0, 0.125, 0.852, 0.898, 0, 0, 0.125, 0.852, 0.898, 0, 0, 0.125, 0.852, 0.898, 0.464], "2": [0.53, 0.681, 0.716, 0.594, 0.262, 0.669, 0.597, 0.564, 0.755, 0.507, 0.251, 0.2, 0.19, 0.653, 0.595, 0, 0, 0.174, 0.688, 0.536, 0, 0.107, 0.555, 0.697, 0.259, 0.018, 0.38, 0.775, 0.418, 0.034, 0.423, 0.679, 0.308, 0.039, 0, 0.796, 0.767, 0.442, 0.398, 0.35, 0.938, 0.91, 0.875, 0.867, 0.771, 0.655], "3": [0.961, 0.818, 0.747, 1, 0.791, 0.461, 0.318, 0.247, 0.75, 1, 0, 0, 0.056, 0.583, 0.99, 0.071, 0.321, 0.556, 0.757, 0.664, 0.149, 0.483, 0.725, 0.856, 0.602, 0, 0, 0.087, 0.631, 1, 0, 0, 0.005, 0.508, 1, 0.5, 0.49, 0.498, 0.758, 1, 1, 0.99, 0.993, 0.898, 0.648, 0.636], "4": [0, 0, 0.416, 0.725, 0.247, 0, 0.149, 0.691, 0.751, 0.247, 0.039, 0.35, 0.704, 0.672, 0.248, 0.12, 0.482, 0.497, 0.615, 0.248, 0.362, 0.473, 0.273, 0.636, 0.279, 0.646, 0.567, 0.489, 0.775, 0.61, 0.651, 0.69, 0.751, 0.894, 0.807, 0.255, 0.32, 0.469, 0.765, 0.492, 0, 0, 0.208, 0.617, 0.25, 0.731], "5": [0.792, 0.924, 0.796, 0.743, 0.497, 0.876, 0.719, 0.344, 0.269, 0.142, 0.927, 0.54, 0.047, 0, 0, 0.942, 0.745, 0.499, 0.471, 0.235, 0.554, 0.564, 0.587, 0.787, 0.766, 0, 0, 0.019, 0.474, 0.926, 0, 0, 0.014, 0.464, 0.917, 0.422, 0.391, 0.432, 0.708, 0.857, 0.877, 0.864, 0.888, 0.772, 0.473, 0.626], "6": [0.218, 0.596, 0.675, 0.554, 0.418, 0.596, 0.646, 0.312, 0.123, 0.063, 0.712, 0.324, 0.017, 0.009, 0, 0.703, 0.457, 0.433, 0.433, 0.309, 0.793, 0.573, 0.438, 0.637, 0.7, 0.769, 0.315, 0.003, 0.315, 0.688, 0.744, 0.299, 0.002, 0.272, 0.636, 0.722, 0.55, 0.296, 0.514, 0.717, 0.407, 0.674, 0.724, 0.727, 0.526, 0.623], "7": [0.652, 0.781, 0.787, 0.894, 0.754, 0.223, 0.3, 0.324, 0.736, 0.61, 0, 0, 0.168, 0.705, 0.43, 0, 0, 0.334, 0.722, 0.197, 0, 0.039, 0.563, 0.561, 0.055, 0, 0.188, 0.785, 0.365, 0.014, 0, 0.362, 0.788, 0.227, 0, 0.034, 0.504, 0.635, 0.053, 0, 0.125, 0.645, 0.489, 0, 0, 0.756], "9": [0.679, 0.85, 0.753, 0.854, 0.593, 0.898, 0.595, 0.286, 0.671, 0.861, 0.846, 0.365, 0, 0.425, 0.857, 0.866, 0.385, 0, 0.433, 0.874, 0.78, 0.734, 0.513, 0.625, 0.88, 0.265, 0.459, 0.364, 0.471, 0.823, 0, 0.001, 0.096, 0.558, 0.797, 0.228, 0.344, 0.517, 0.823, 0.611, 0.629, 0.815, 0.823, 0.599, 0.22, 0.631]};
  let refs = null;

  function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
  function pixels(img) {
    const W = img.naturalWidth, H = img.naturalHeight, c = canvas(W, H), g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0);
    return { W, H, d: g.getImageData(0, 0, W, H).data };
  }
  const lum = (d, i) => (d[i] + d[i + 1] + d[i + 2]) / 3;   // eslint-disable-line no-unused-vars
  const sat = (d, i) => Math.max(d[i], d[i + 1], d[i + 2]) - Math.min(d[i], d[i + 1], d[i + 2]);

  // une annonce = une piece doree devant son prix total : on repere toutes les pieces (taches dorees de ~16 px)
  const gold = (d, i) => d[i] > 150 && d[i + 1] > 110 && d[i + 2] < 130 && d[i] - d[i + 2] > 50;
  function coins(P) {
    const { W, H, d } = P, x0 = Math.floor(W * 0.3), rows = [];
    for (let y = 0; y < H; y++) { let n = 0; for (let x = x0; x < W; x++) if (gold(d, (y * W + x) * 4)) n++; rows.push(n); }
    const out = [];
    for (let y = 0; y < H;) {
      while (y < H && rows[y] < 2) y++;
      let e = y; while (e < H && rows[e] >= 2) e++;
      if (e - y >= 8 && e - y <= 40) {
        let a = W, b = -1;
        for (let yy = y; yy < e; yy++) for (let x = x0; x < W; x++) if (gold(d, (yy * W + x) * 4)) { a = Math.min(a, x); b = Math.max(b, x); }
        if (b - a <= 2.2 * (e - y)) out.push({ x0: a, x1: b, y0: y, y1: e - 1 });
      }
      y = e + 1;
    }
    return out;
  }
  // icone de l'annonce : position fixe par rapport a la piece, a l'echelle de l'interface (mesuree sur captures)
  function iconFromCoin(co, withUnit) {
    // la piece mesure 14 a 16 px selon la ligne (detection au pixel pres) : meme echelle tant qu'elle reste dans cette plage
    const h = co.y1 - co.y0 + 1, s = h >= 13 && h <= 18 ? 1 : h / 16, cy = (co.y0 + co.y1) / 2;
    // avec une ligne « par unite » sous le prix, le prix est remonte de 11 px ; sinon il est centre sur l'icone
    return { x: Math.round(co.x0 - 933 * s), y: Math.round(cy + (withUnit ? 11 : 0) * s - 30 * s), w: Math.round(60 * s),
             h: Math.round(60 * s), s };
  }

  // glyphes d'une ligne de texte (chiffres blancs/gris, separateur de milliers = petit espace)
  function glyphs(P, x0, x1, y0, y1, stopGap) {
    const { W, H, d } = P, M = [];
    y0 = Math.max(0, y0); y1 = Math.min(H, y1); x1 = Math.min(W, x1);
    for (let y = y0; y < y1; y++) {
      const row = [];
      for (let x = x0; x < x1; x++) { const i = (y * W + x) * 4; row.push(sat(d, i) < 60 ? Math.max(0, Math.min(1, (lum(d, i) - 100) / 80)) : 0); }
      M.push(row);
    }
    const col = i => M.reduce((n, r) => n + (r[i] > 0.5 ? 1 : 0), 0), out = [];
    let x = 0; while (x < x1 - x0 && !col(x)) x++;
    while (x < x1 - x0) {
      let e = x; while (e < x1 - x0 && col(e)) e++;
      out.push({ a: x, b: e, M });
      let g = e; while (g < x1 - x0 && !col(g)) g++;
      if (g - e > stopGap) break;
      out[out.length - 1].gapAfter = g - e;
      x = g;
    }
    return out;
  }
  function vecOf(M, a, b) {
    const sub = M.map(r => r.slice(a, b)), rows = [];
    sub.forEach((r, k) => { if (r.some(v => v > 0.5)) rows.push(k); });
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
  function readPrice(gl, models) {
    // lit les chiffres de gauche a droite ; s'arrete au premier glyphe qui n'est pas un chiffre (ex. « par unite »)
    let txt = '', worst = 0;
    for (const g of gl) {
      const v = vecOf(g.M, g.a, g.b);
      if (!v || !models) break;
      let best = null;
      for (const [digit, m] of Object.entries(models)) {
        let e = 0; for (let i = 0; i < m.length; i++) e += (v[i] - m[i]) ** 2; e /= m.length;
        if (!best || e < best.e) best = { digit, e };
      }
      if (best.e > 0.08) break;
      txt += best.digit; worst = Math.max(worst, best.e);
    }
    return { value: txt ? parseInt(txt, 10) : null, err: worst, digits: txt.length };
  }
  // ecart tolerant aux badges poses sur l'icone (equipement fabrique, quantite) : on ignore le quart des pixels
  // les plus differents
  function robustDist(a, b) {
    const [mx0, my0, mx1, my1] = a.mask, S = Math.round(Math.sqrt(a.length / 4)), diffs = [];
    for (let y = my0; y < my1; y++) for (let x = mx0; x < mx1; x++) {
      const i = (y * S + x) * 4;
      diffs.push((Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2])) / 3);
    }
    diffs.sort((u, v) => u - v);
    const keep = diffs.slice(0, Math.ceil(diffs.length * 0.75));
    return keep.length ? keep.reduce((u, v) => u + v, 0) / keep.length : 999;
  }
  async function iconRefs(thumbOf) {
    if (refs) return refs;
    refs = [];
    for (const r of window.MARKET_ICONS || []) {
      try { const img = await new Promise((ok, ko) => { const i = new Image(); i.onload = () => ok(i); i.onerror = ko; i.src = r.s; });
            refs.push({ n: r.n, t: thumbOf(img, 0, 0, img.naturalWidth, img.naturalHeight) }); } catch (e) {}
    }
    return refs;
  }

  // structure brute (pour l'apprentissage des modeles) : lignes, icone, piece, glyphes des deux lignes de prix
  window.__listingRows = function (img) {
    const P = pixels(img), out = [];
    for (const co of coins(P)) {
      const s = iconFromCoin(co, false).s, ch = co.y1 - co.y0;
      const total = glyphs(P, co.x1 + 2, co.x1 + Math.round(260 * s), co.y0 - 1, co.y1 + 2, Math.round(9 * s));
      const unit = glyphs(P, co.x0 - Math.round(12 * s), co.x0 + Math.round(260 * s), co.y1 + Math.round(6 * s),
                          co.y1 + Math.round(12 * s) + ch, Math.round(7 * s));
      out.push({ icon: iconFromCoin(co, unit.length > 0), coin: co, total, unit });
    }
    return { P, rows: out, vecOf };
  };

  window.scanListings = async function (img, opts) {
    opts = opts || {};
    const models = opts.models || PRICE_MODELS, thumbOf = window.__thumb, distOf = robustDist;
    const { P, rows } = window.__listingRows(img), list = await iconRefs(thumbOf), out = [];
    for (const r of rows) {
      const ic = r.icon, t = thumbOf(img, ic.x, ic.y, ic.w, ic.h);
      const scored = list.map(x => ({ n: x.n, d: distOf(t, x.t) })).sort((a, b) => a.d - b.d);
      const best = scored[0];
      const q = window.__readNumber(P, ic.x, ic.y, { px: ic.w, py: ic.h });
      const tot = readPrice(r.total, models), uni = readPrice(r.unit, models);
      // quantite : total / unitaire quand les deux prix sont lus (plus sur que le chiffre sur l'icone)
      let qty = q.qty || 1;
      if (tot.value && uni.value && tot.value % uni.value === 0) qty = tot.value / uni.value;
      let unit = uni.value, check = [];
      if (unit == null) unit = qty === 1 ? tot.value : (tot.value ? Math.round(tot.value / qty) : null);
      if (tot.value && unit && Math.abs(unit * qty - tot.value) > Math.max(2, tot.value * 0.001)) check.push('total ≠ unitaire × quantité');
      if (!best || best.d > 22 || scored[1] && scored[1].d - best.d < 2) check.push('objet incertain');
      if (unit == null) check.push('prix illisible');
      out.push({ name: best ? best.n : null, d: best && best.d, qty, unit, total: tot.value, check,
                 x: ic.x, y: ic.y, w: ic.w, h: ic.h });
    }
    return out;
  };
})();
