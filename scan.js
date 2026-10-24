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
  function readPrice(gl, models, maxErr) {
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
      if (best.e > (maxErr || 0.08)) break;
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
  // icones de reference : chargees en parallele (par lots), une seule fois tant que la page reste ouverte
  async function iconRefs(thumbOf, progress) {
    if (refs) return refs;
    const all = window.MARKET_ICONS || [], out = [], batch = 24;
    for (let k = 0; k < all.length; k += batch) {
      progress(`Chargement des icônes de référence : ${k} / ${all.length} (seulement au premier collage)…`);
      const got = await Promise.all(all.slice(k, k + batch).map(r => new Promise(ok => {
        const i = new Image();
        i.onload = () => ok({ n: r.n, g: (/\.(Common|Rare|Legend|Unique|Epic|Special)\./.exec(r.s) || [])[1],
                              t: thumbOf(i, 0, 0, i.naturalWidth, i.naturalHeight) });
        i.onerror = () => ok(null);
        i.src = r.s;
      })));
      got.forEach(g => g && out.push(g));
    }
    refs = out;
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
    const progress = opts.progress || (() => {});
    const { P, rows } = window.__listingRows(img), list = await iconRefs(thumbOf, progress), out = [];
    progress(`Lecture des ${rows.length} annonce(s)…`);
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

  // ====================================================================== historique des ventes
  // Capture de l'historique des ventes : une ligne par vente (icone avec quantite, nom, prix total + « par unite »,
  // montant recu apres taxe + « par unite », date « jj.mm.aaaa hh:mm » derriere un badge bleu). Deux pieces par ligne :
  // la premiere precede le prix de vente, la seconde le montant recu. La piece y est plus pale que dans « Mes ventes ».
  const paleGold = (d, i) => d[i] > 120 && d[i + 1] > 95 && d[i] - d[i + 2] > 28 && d[i] >= d[i + 1] && d[i + 1] >= d[i + 2] - 5;
  function coinsOf(P, test) {
    const { W, H, d } = P, x0 = Math.floor(W * 0.3), cols = [];
    // taches de pixels dores, regroupees par composantes connexes (assez grosses, a peu pres rondes)
    const seen = new Uint8Array(W * H), out = [];
    for (let y = 0; y < H; y++) for (let x = x0; x < W; x++) {
      const k = y * W + x;
      if (seen[k] || !test(d, k * 4)) continue;
      let a = x, b = x, t = y, u = y, n = 0;
      const st = [k]; seen[k] = 1;
      while (st.length) {
        const q = st.pop(), qx = q % W, qy = (q - qx) / W; n++;
        a = Math.min(a, qx); b = Math.max(b, qx); t = Math.min(t, qy); u = Math.max(u, qy);
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
          const nx = qx + dx, ny = qy + dy, nk = ny * W + nx;
          if (nx < x0 || nx >= W || ny < 0 || ny >= H || seen[nk] || !test(d, nk * 4)) continue;
          seen[nk] = 1; st.push(nk);
        }
      }
      const w = b - a + 1, h = u - t + 1;
      if (h >= 10 && h <= 30 && w >= 0.6 * h && w <= 1.5 * h && n > 0.3 * w * h) out.push({ x0: a, x1: b, y0: t, y1: u });
    }
    return out;
  }
  // hauteur d'encre d'un glyphe ; nettoyage : on retire les eclats (bord de piece, points, deux-points) et on coupe
  // en deux les chiffres colles (« 24 » lu comme un seul glyphe de 13 px)
  function inkH(g) {
    let t = -1, b = -1;
    g.M.forEach((r, k) => { for (let x = g.a; x < g.b; x++) if (r[x] > 0.5) { if (t < 0) t = k; b = k; break; } });
    return t < 0 ? 0 : b - t + 1;
  }
  function clean(gl) {
    const hs = gl.map(inkH), H = Math.max(0, ...hs), out = [];
    gl.forEach((g, k) => {
      const h = hs[k], w = g.b - g.a;
      if (h < 0.6 * H || w <= 0.35 * h) return;
      const n = Math.max(1, Math.round(w / (0.7 * h)));
      for (let j = 0; j < n; j++) out.push({ a: g.a + Math.round(j * w / n), b: g.a + Math.round((j + 1) * w / n), M: g.M });
    });
    return out;
  }
  // chiffres de l'historique, appris sur des captures reelles : prix (gros), « par unite » (petits), date
  const HIST_MODELS = {"big":{"0":[0.278,0.626,0.692,0.407,0.049,0.764,0.886,0.811,0.854,0.331,1.0,0.58,0.322,0.812,0.567,1.0,0.355,0.0,0.645,0.703,1.0,0.355,0.0,0.645,0.8,1.0,0.355,0.0,0.645,0.778,1.0,0.441,0.048,0.672,0.59,0.86,0.763,0.548,0.839,0.545,0.496,0.918,1.0,0.822,0.289,0.659],"1":[0.25,0.623,0.873,1.0,0.882,0.75,1.0,1.0,1.0,0.889,0.722,0.721,0.75,1.0,0.885,0.222,0.221,0.5,1.0,0.887,0.0,0.0,0.5,1.0,0.894,0.0,0.0,0.5,1.0,0.887,0.0,0.0,0.5,1.0,0.884,0.0,0.0,0.5,1.0,0.889,0.0,0.0,0.5,1.0,0.891,0.545],"2":[0.421,0.661,0.727,0.405,0.069,0.921,0.919,0.888,0.845,0.294,0.5,0.419,0.405,0.816,0.449,0.0,0.0,0.276,0.816,0.448,0.0,0.156,0.743,0.799,0.224,0.0,0.436,0.968,0.466,0.005,0.569,0.775,0.241,0.0,0.025,0.906,0.833,0.5,0.497,0.445,1.0,1.0,1.0,0.995,0.872,0.675],"3":[0.509,0.617,0.73,0.555,0.296,1.0,0.875,0.833,0.984,0.742,0.5,0.375,0.343,0.775,0.893,0.14,0.395,0.617,0.868,0.637,0.366,0.872,1.0,0.927,0.396,0.226,0.476,0.647,0.918,0.652,0.0,0.0,0.028,0.564,0.934,0.5,0.5,0.528,0.796,0.905,1.0,1.0,1.0,0.935,0.616,0.601],"4":[0.0,0.049,0.585,0.827,0.241,0.0,0.258,0.879,0.829,0.243,0.012,0.434,0.919,0.825,0.237,0.08,0.555,0.729,0.829,0.243,0.506,0.606,0.46,0.867,0.3,0.872,0.788,0.689,0.975,0.712,0.865,0.95,0.967,1.0,0.919,0.365,0.45,0.657,0.918,0.547,0.0,0.0,0.379,0.835,0.253,0.793],"5":[0.939,0.975,0.921,0.902,0.703,1.0,0.852,0.548,0.477,0.309,1.0,0.705,0.169,0.049,0.035,1.0,0.856,0.571,0.5,0.251,0.693,0.699,0.703,0.856,0.826,0.05,0.05,0.059,0.538,1.0,0.003,0.0,0.055,0.583,1.0,0.503,0.5,0.555,0.833,0.99,1.0,1.0,1.0,0.887,0.627,0.631],"6":[0.103,0.523,0.73,0.609,0.191,0.445,0.825,0.68,0.391,0.113,0.842,0.666,0.229,0.087,0.03,1.0,0.667,0.535,0.431,0.141,1.0,0.858,0.796,0.818,0.35,1.0,0.509,0.335,0.755,0.568,1.0,0.401,0.111,0.711,0.687,0.88,0.734,0.556,0.789,0.425,0.485,0.903,1.0,0.722,0.167,0.715],"7":[0.666,0.896,0.895,0.97,0.767,0.23,0.396,0.402,0.81,0.568,0.0,0.0,0.183,0.786,0.419,0.0,0.0,0.352,0.78,0.169,0.0,0.025,0.586,0.555,0.0,0.0,0.177,0.829,0.333,0.0,0.0,0.344,0.816,0.181,0.0,0.014,0.475,0.663,0.014,0.0,0.041,0.632,0.563,0.0,0.0,0.808],"8":[0.435,0.744,0.761,0.673,0.436,0.852,0.865,0.617,0.856,0.748,1.0,0.673,0.297,0.761,0.833,0.75,0.944,0.805,0.943,0.583,0.556,0.995,0.96,0.889,0.389,0.833,0.854,0.634,0.861,0.667,1.0,0.444,0.0,0.556,0.919,1.0,0.722,0.496,0.778,0.878,0.75,1.0,0.996,0.945,0.584,0.629],"9":[0.618,0.826,0.799,0.779,0.339,0.885,0.671,0.451,0.81,0.589,0.934,0.469,0.082,0.655,0.665,0.953,0.429,0.0,0.619,0.798,0.803,0.794,0.542,0.781,0.786,0.286,0.583,0.45,0.705,0.688,0.0,0.0,0.213,0.807,0.64,0.375,0.495,0.713,0.878,0.39,0.835,0.995,0.988,0.56,0.071,0.7]},"small":{"0":[0.432,0.625,0.613,0.6,0.39,0.706,0.481,0.21,0.487,0.678,0.69,0.273,0.0,0.293,0.7,0.57,0.159,0.0,0.177,0.59,0.517,0.1,0.0,0.117,0.533,0.567,0.155,0.0,0.174,0.587,0.683,0.274,0.0,0.29,0.704,0.684,0.474,0.205,0.489,0.702,0.405,0.607,0.611,0.624,0.425,0.6],"1":[0.0,0.137,0.361,0.699,0.705,0.289,0.498,0.567,0.742,0.699,0.289,0.361,0.241,0.603,0.692,0.0,0.0,0.0,0.568,0.704,0.0,0.0,0.0,0.565,0.688,0.0,0.0,0.0,0.56,0.69,0.0,0.0,0.0,0.563,0.701,0.0,0.0,0.0,0.565,0.692,0.0,0.0,0.0,0.566,0.695,0.435],"2":[0.557,0.646,0.64,0.685,0.524,0.401,0.283,0.224,0.523,0.779,0.0,0.0,0.0,0.386,0.799,0.0,0.0,0.034,0.449,0.671,0.0,0.005,0.245,0.56,0.371,0.0,0.213,0.546,0.439,0.107,0.211,0.53,0.447,0.126,0.0,0.626,0.654,0.344,0.211,0.21,0.834,0.748,0.641,0.625,0.625,0.6],"3":[0.538,0.572,0.609,0.684,0.511,0.31,0.173,0.178,0.546,0.796,0.0,0.0,0.0,0.407,0.723,0.158,0.359,0.406,0.461,0.364,0.203,0.516,0.71,0.657,0.31,0.045,0.157,0.303,0.556,0.625,0.0,0.0,0.0,0.308,0.732,0.165,0.042,0.138,0.486,0.754,0.534,0.471,0.553,0.625,0.478,0.6],"4":[0.0,0.008,0.311,0.717,0.469,0.0,0.188,0.56,0.786,0.47,0.097,0.431,0.513,0.597,0.476,0.311,0.456,0.193,0.439,0.455,0.444,0.259,0.022,0.436,0.474,0.546,0.237,0.24,0.577,0.598,0.668,0.541,0.601,0.75,0.755,0.353,0.357,0.378,0.61,0.634,0.0,0.0,0.028,0.438,0.473,0.6],"5":[0.673,0.761,0.66,0.646,0.399,0.745,0.541,0.243,0.23,0.122,0.784,0.401,0.0,0.0,0.0,0.811,0.608,0.419,0.401,0.194,0.415,0.411,0.496,0.681,0.599,0.002,0.001,0.077,0.417,0.747,0.0,0.0,0.0,0.306,0.719,0.236,0.117,0.212,0.535,0.709,0.595,0.537,0.618,0.635,0.4,0.6],"6":[0.205,0.512,0.594,0.522,0.378,0.557,0.613,0.276,0.102,0.044,0.585,0.238,0.0,0.0,0.0,0.547,0.318,0.414,0.416,0.299,0.708,0.484,0.414,0.584,0.672,0.667,0.258,0.0,0.191,0.604,0.616,0.216,0.0,0.112,0.531,0.664,0.464,0.185,0.369,0.695,0.407,0.6,0.594,0.644,0.55,0.6],"7":[0.615,0.603,0.623,0.691,0.802,0.204,0.188,0.192,0.451,0.774,0.0,0.0,0.0,0.39,0.593,0.0,0.0,0.182,0.602,0.424,0.0,0.0,0.385,0.665,0.279,0.0,0.144,0.558,0.481,0.068,0.0,0.339,0.69,0.351,0.0,0.101,0.511,0.552,0.141,0.0,0.312,0.718,0.406,0.0,0.0,0.6],"8":[0.539,0.578,0.434,0.535,0.482,0.727,0.349,0.023,0.405,0.767,0.701,0.349,0.0,0.366,0.68,0.511,0.564,0.416,0.484,0.367,0.362,0.716,0.728,0.666,0.291,0.54,0.473,0.312,0.507,0.552,0.541,0.11,0.0,0.148,0.578,0.583,0.177,0.0,0.177,0.583,0.528,0.562,0.423,0.525,0.512,0.6],"9":[0.531,0.652,0.602,0.558,0.337,0.677,0.389,0.207,0.471,0.647,0.493,0.08,0.0,0.212,0.63,0.565,0.155,0.0,0.244,0.673,0.688,0.559,0.411,0.5,0.709,0.334,0.404,0.411,0.342,0.541,0.0,0.0,0.0,0.216,0.558,0.0,0.039,0.232,0.597,0.539,0.354,0.472,0.557,0.519,0.215,0.6]},"date":{"0":[0.433,0.695,0.705,0.579,0.228,0.842,0.812,0.649,0.849,0.527,1.0,0.537,0.215,0.723,0.679,1.0,0.397,0.009,0.605,0.739,1.0,0.397,0.009,0.608,0.809,1.0,0.397,0.009,0.607,0.773,1.0,0.474,0.046,0.615,0.684,0.833,0.776,0.542,0.796,0.645,0.44,0.886,0.999,0.834,0.379,0.658],"1":[0.25,0.621,0.872,1.0,0.874,0.75,1.0,1.0,1.0,0.875,0.715,0.715,0.75,1.0,0.871,0.215,0.215,0.5,1.0,0.871,0.0,0.0,0.5,1.0,0.871,0.0,0.0,0.5,1.0,0.873,0.0,0.0,0.5,1.0,0.87,0.0,0.0,0.5,1.0,0.871,0.0,0.0,0.5,1.0,0.875,0.545],"2":[0.478,0.672,0.722,0.471,0.084,0.848,0.829,0.789,0.862,0.329,0.429,0.344,0.31,0.81,0.5,0.0,0.0,0.25,0.833,0.499,0.0,0.166,0.735,0.809,0.238,0.02,0.458,0.94,0.452,0.0,0.531,0.761,0.25,0.0,0.0,0.889,0.833,0.5,0.5,0.444,1.0,1.0,1.0,1.0,0.893,0.675],"3":[0.583,0.607,0.692,0.628,0.396,0.917,0.779,0.712,0.958,0.844,0.417,0.302,0.26,0.729,1.0,0.11,0.36,0.58,0.856,0.735,0.301,0.773,0.958,0.978,0.513,0.174,0.382,0.537,0.889,0.792,0.0,0.0,0.003,0.505,1.0,0.5,0.5,0.503,0.755,1.0,1.0,1.0,1.0,0.944,0.694,0.592],"4":[0.0,0.019,0.528,0.799,0.199,0.0,0.203,0.851,0.799,0.198,0.001,0.364,0.908,0.795,0.192,0.028,0.513,0.733,0.794,0.19,0.41,0.642,0.451,0.837,0.256,0.809,0.815,0.676,0.959,0.689,0.81,0.918,0.94,1.0,0.9,0.31,0.418,0.616,0.902,0.503,0.0,0.0,0.352,0.801,0.202,0.808],"5":[0.957,1.0,0.924,0.893,0.663,0.999,0.829,0.476,0.393,0.216,1.0,0.659,0.106,0.0,0.0,1.0,0.83,0.553,0.5,0.25,0.652,0.665,0.666,0.833,0.833,0.0,0.0,0.0,0.5,1.0,0.0,0.0,0.037,0.556,1.0,0.5,0.5,0.537,0.806,0.988,1.0,1.0,1.0,0.869,0.607,0.636],"6":[0.191,0.715,0.78,0.586,0.257,0.632,0.774,0.465,0.188,0.064,0.941,0.503,0.087,0.021,0.001,1.0,0.664,0.504,0.456,0.179,1.0,0.75,0.621,0.875,0.504,1.0,0.388,0.079,0.704,0.732,1.0,0.385,0.0,0.667,0.676,0.854,0.718,0.5,0.833,0.523,0.428,0.883,1.0,0.833,0.25,0.713],"7":[0.62,0.868,0.885,0.973,0.749,0.198,0.368,0.386,0.807,0.557,0.0,0.0,0.176,0.767,0.399,0.0,0.0,0.35,0.766,0.149,0.0,0.022,0.583,0.554,0.0,0.0,0.17,0.822,0.333,0.0,0.0,0.336,0.802,0.172,0.0,0.015,0.456,0.655,0.005,0.0,0.04,0.613,0.552,0.0,0.0,0.809],"8":[0.472,0.747,0.723,0.736,0.553,0.861,0.886,0.577,0.841,0.907,1.0,0.747,0.314,0.724,1.0,0.75,1.0,0.832,0.997,0.75,0.574,0.998,0.949,1.0,0.574,0.861,0.885,0.609,0.889,0.861,1.0,0.5,0.0,0.5,1.0,1.0,0.75,0.491,0.75,1.0,0.75,1.0,0.991,1.0,0.75,0.607],"9":[0.751,0.903,0.819,0.875,0.375,1.0,0.591,0.319,0.812,0.625,1.0,0.375,0.0,0.625,0.66,1.0,0.375,0.0,0.625,0.763,0.833,0.792,0.555,0.785,0.743,0.25,0.5,0.333,0.678,0.635,0.0,0.0,0.229,0.812,0.625,0.41,0.5,0.729,0.875,0.375,0.899,1.0,0.981,0.544,0.062,0.705]}};
  const blue = (d, i) => d[i + 2] > 140 && d[i + 2] - d[i] > 60;
  window.__historyRows = function (img) {
    const P = pixels(img), all = coinsOf(P, paleGold).sort((a, b) => a.y0 - b.y0 || a.x0 - b.x0), lines = [];
    // une ligne = deux pieces a la meme hauteur (vente, montant recu)
    for (const co of all) {
      const l = lines.find(l => Math.abs(l[0].y0 - co.y0) <= 4);
      if (l) l.push(co); else lines.push([co]);
    }
    const out = [];
    for (const l of lines) {
      if (l.length < 2) continue;
      l.sort((a, b) => a.x0 - b.x0);
      const [c1, c2] = l, h = c1.y1 - c1.y0 + 1, s = h >= 14 && h <= 19 ? 1 : h / 17;
      const line = co => clean(glyphs(P, co.x1 + 2, co.x1 + Math.round(200 * s), co.y0 - 1, co.y1 + 2, Math.round(9 * s)));
      const unitLine = co => clean(glyphs(P, co.x0 - Math.round(12 * s), co.x0 + Math.round(200 * s), co.y1 + Math.round(6 * s),
                                          co.y1 + Math.round(12 * s) + h, Math.round(7 * s)));
      const total = line(c1), unit = unitLine(c1), net = line(c2), netUnit = unitLine(c2);
      // icone : 1082 px a gauche de la premiere piece ; centree sur le prix, ou 12 px plus bas s'il y a une ligne « par unite »
      const cy = (c1.y0 + c1.y1) / 2 + (unit.length ? 12 * s : 0);
      const icon = { x: Math.round(c1.x0 - 1082 * s), y: Math.round(cy - 30 * s), w: Math.round(60 * s), h: Math.round(60 * s), s };
      // date : apres le badge bleu, a droite de la ligne, centree sur l'icone
      const y0 = Math.round(cy - 11 * s), y1 = Math.round(cy + 11 * s);
      let bx = -1;
      for (let x = c2.x0 + Math.round(250 * s); x < P.W; x++)
        for (let y = y0; y < y1; y++) if (blue(P.d, (y * P.W + x) * 4)) { bx = x; break; }
      const date = bx < 0 ? [] : clean(glyphs(P, bx + 2, P.W, y0, y1, Math.round(30 * s)));
      out.push({ icon, coins: [c1, c2], total, unit, net, netUnit, date });
    }
    return { P, rows: out, vecOf };
  };

  // capture -> ventes : objet (icone), quantite, prix, montant recu, date ; verifications croisees :
  // recu = prix - taxe 10 % (arrondi a l'inferieur), prix = unitaire x quantite, date plausible
  window.scanHistory = async function (img, opts) {
    opts = opts || {};
    const progress = opts.progress || (() => {}), thumbOf = window.__thumb;
    const { P, rows } = window.__historyRows(img), list = await iconRefs(thumbOf, progress), out = [];
    progress(`Lecture des ${rows.length} vente(s)…`);
    const read = (g, m) => readPrice(g, HIST_MODELS[m], m === 'date' ? 0.12 : 0.08);
    // rarete d'apres la couleur du nom (blanc commun, vert rare, bleu legendaire, or unique, orange epique) : departage
    // les objets qui ont la meme icone (Mijote de pujery / de maitre)
    const grade = ic => {
      const { W, d } = P, cy = ic.y + ic.h / 2;
      let n = 0, r = 0, g = 0, b = 0;
      for (let y = Math.max(0, Math.round(cy - 22 * ic.s)); y < cy + 4 * ic.s; y++)
        for (let x = ic.x + ic.w + 8; x < Math.min(W, ic.x + ic.w + 380 * ic.s); x++) {
          const i = (y * W + x) * 4;
          if (Math.max(d[i], d[i + 1], d[i + 2]) > 150) { n++; r += d[i]; g += d[i + 1]; b += d[i + 2]; }
        }
      if (n < 50) return null;
      r /= n; g /= n; b /= n;
      if (g > r + 60 && g > b + 50) return 'Rare';
      if (b > r + 70 && b > g + 30) return 'Legend';
      if (r > 190 && b < 120 && g > 150) return 'Unique';
      if (r > 190 && b < 120 && g <= 150) return 'Epic';
      if (Math.abs(r - g) < 25 && Math.abs(g - b) < 25) return 'Common';
      return null;
    };
    // date jj mm aaaa hh mm : chaque position n'admet que certains chiffres (dizaine des heures 0-2, etc.), ce qui
    // corrige les chiffres colles mal coupes (« 04 » dont le 0 ressemble a un 6)
    const ALLOWED = ['0123', '', '01', '', '2', '0', '', '', '012', '', '012345', ''];
    const readDate = gl => {
      let z = '';
      for (let k = 0; k < 12; k++) {
        const v = vecOf(gl[k].M, gl[k].a, gl[k].b);
        if (!v) return null;
        let best = null;
        for (const [digit, m] of Object.entries(HIST_MODELS.date)) {
          if (ALLOWED[k] && !ALLOWED[k].includes(digit)) continue;
          let e = 0; for (let i = 0; i < m.length; i++) e += (v[i] - m[i]) ** 2; e /= m.length;
          if (!best || e < best.e) best = { digit, e };
        }
        if (best.e > 0.12) return null;
        z += best.digit;
      }
      return z;
    };
    // prix unitaire : les chiffres sont suivis de « par unite » ; on garde le plus long debut qui divise le prix total
    const unitOf = (gl, total) => {
      const u = read(gl, 'small');
      if (!u.value || !total) return null;
      for (let s = String(u.value); s.length; s = s.slice(0, -1)) if (total % +s === 0 && total / +s <= 9999) return +s;
      return null;
    };
    for (const r of rows) {
      const ic = r.icon, t = thumbOf(img, ic.x, ic.y, ic.w, ic.h);
      const gr = grade(ic);
      let scored = list.map(x => ({ n: x.n, g: x.g, d: robustDist(t, x.t) })).sort((a, b) => a.d - b.d);
      // parmi les icones presque identiques a la meilleure, on garde celles de la rarete lue sur le nom
      if (gr && scored.length) {
        const near = scored.filter(x => x.d <= scored[0].d + 6), same = near.filter(x => x.g === gr);
        if (same.length) scored = same.concat(scored.filter(x => !same.includes(x) && x.g === gr));
      }
      const best = scored[0];
      const tot = read(r.total, 'big'), net = read(r.net, 'big'), uni = r.unit.length ? unitOf(r.unit, tot.value) : null;
      const check = [];
      let qty = 1;
      if (uni) qty = tot.value / uni;
      else if (r.unit.length) { const q = window.__readNumber(P, ic.x, ic.y, { px: ic.w, py: ic.h }); qty = q.qty || 1; check.push('quantité incertaine'); }
      if (!tot.value) check.push('prix illisible');
      else if (net.value !== Math.floor(tot.value * 0.9)) check.push('montant reçu ≠ prix − 10 %');
      const z = r.date.length === 12 ? readDate(r.date) : null;
      let date = null;
      if (z) {
        const [dd, mo, yy, hh, mi] = [z.slice(0, 2), z.slice(2, 4), z.slice(4, 8), z.slice(8, 10), z.slice(10)];
        if (+dd >= 1 && +dd <= 31 && +mo >= 1 && +mo <= 12 && +hh <= 23 && +mi <= 59) date = `${yy}-${mo}-${dd} ${hh}:${mi}`;
      }
      if (!date) check.push('date illisible');
      if (!best || best.d > 22 || scored[1] && scored[1].d - best.d < 2) check.push('objet incertain');
      out.push({ name: best ? best.n : null, d: best && best.d, qty, unit: uni || tot.value, total: tot.value, net: net.value, date, check,
                 x: ic.x, y: ic.y, w: ic.w, h: ic.h });
    }
    // l'historique va du plus recent au plus ancien : une date qui casse l'ordre est suspecte
    out.forEach((v, k) => {
      const a = out[k - 1], b = out[k + 1];
      if (v.date && ((a && a.date && v.date > a.date) || (b && b.date && v.date < b.date))) v.check.push('date à vérifier');
    });
    return out;
  };

  // ====================================================================== ravitaillement
  // Capture de la fenetre de ravitaillement : des cartes, chacune avec une rangee de cases (objets a livrer, icones
  // assombries) sur fond uni plus clair, puis « N livre(s) parmi les objets ci-dessus », « 0 / N » et les recompenses.
  // Cases : taches carrees sombres ; objet : forme de l'icone (contours) comparee aux icones de reference, ce qui
  // resiste a l'assombrissement ; N : dernier chiffre de la ligne « 0 / N ».
  const SN = 32;
  function edges(img, x, y, w, h) {
    const c = canvas(SN, SN), g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, x, y, w, h, 0, 0, SN, SN);
    const d = g.getImageData(0, 0, SN, SN).data, v = [], e = [];
    for (let i = 0; i < d.length; i += 4) v.push((d[i] + d[i + 1] + d[i + 2]) / 3);
    for (let yy = 1; yy < SN - 1; yy++) for (let xx = 1; xx < SN - 1; xx++) {
      const k = yy * SN + xx;
      e.push(Math.hypot(v[k + 1] - v[k - 1], v[k + SN] - v[k - SN]));
    }
    const m = e.reduce((a, b) => a + b, 0) / e.length, sd = Math.sqrt(e.reduce((a, b) => a + (b - m) ** 2, 0) / e.length) || 1;
    return e.map(z => (z - m) / sd);
  }
  const corr = (a, b) => { let t = 0; for (let i = 0; i < a.length; i++) t += a[i] * b[i]; return t / a.length; };
  // teinte du fond de la case (coins, hors objet) : couleur de la qualite, seule difference entre un objet et sa version
  // eclatante (meme icone). Ecart de chaque canal a la moyenne : gris = commun ; vert, bleu, orange... meme assombri.
  function tint(img, x, y, w, h) {
    const c = canvas(SN, SN), g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, x, y, w, h, 0, 0, SN, SN);
    const d = g.getImageData(0, 0, SN, SN).data, t = [0, 0, 0];
    let n = 0;
    for (const [cx, cy] of [[2, 2], [SN - 5, 2], [2, SN - 5], [SN - 5, SN - 5]])
      for (let yy = cy; yy < cy + 3; yy++) for (let xx = cx; xx < cx + 3; xx++) {
        const i = (yy * SN + xx) * 4; t[0] += d[i]; t[1] += d[i + 1]; t[2] += d[i + 2]; n++;
      }
    const m = (t[0] + t[1] + t[2]) / 3 / n;
    return t.map(v => v / n - m);
  }
  const norm = v => Math.hypot(v[0], v[1], v[2]);
  let supplyRefs = null;
  async function supplyIcons(progress) {
    if (supplyRefs) return supplyRefs;
    const all = window.SUPPLY || [], out = [], seen = {};
    for (let k = 0; k < all.length; k += 24) {
      progress(`Chargement des icônes de référence : ${k} / ${all.length}…`);
      const got = await Promise.all(all.slice(k, k + 24).map(r => new Promise(ok => {
        if (seen[r.s]) return ok(null);
        seen[r.s] = 1;
        const i = new Image();
        i.onload = () => ok({ s: r.s, v: edges(i, 0, 0, i.naturalWidth, i.naturalHeight), t: tint(i, 0, 0, i.naturalWidth, i.naturalHeight) });
        i.onerror = () => ok(null);
        i.src = r.s;
      })));
      got.forEach(g => g && out.push(g));
    }
    return (supplyRefs = out);
  }
  // cases : composantes de pixels sombres (plus sombres que le fond de carte), carrees, de 30 a 90 px
  function supplyBoxes(P) {
    const { W, H, d } = P, dark = new Uint8Array(W * H), seen = new Uint8Array(W * H), out = [];
    const hist = new Array(256).fill(0);
    for (let k = 0; k < W * H; k++) hist[Math.round(lum(d, k * 4))]++;
    const bg = hist.indexOf(Math.max(...hist));                       // fond de carte le plus frequent
    for (let k = 0; k < W * H; k++) dark[k] = lum(d, k * 4) < bg - 5 ? 1 : 0;
    for (let k = 0; k < W * H; k++) {
      if (!dark[k] || seen[k]) continue;
      let a = W, b = 0, t = H, u = 0, n = 0;
      const st = [k]; seen[k] = 1;
      while (st.length) {
        const q = st.pop(), x = q % W, y = (q - x) / W; n++;
        if (x < a) a = x; if (x > b) b = x; if (y < t) t = y; if (y > u) u = y;
        for (const nq of [q + 1, q - 1, q + W, q - W]) {
          if (nq < 0 || nq >= W * H || seen[nq] || !dark[nq] || Math.abs((nq % W) - x) > 1) continue;
          seen[nq] = 1; st.push(nq);
        }
      }
      const w = b - a + 1, h = u - t + 1;
      if (w >= 30 && w <= 90 && h >= 30 && h <= 90 && Math.abs(w - h) <= 0.15 * w && n > 0.35 * w * h)
        out.push({ x: a, y: t, w, h });
    }
    return out;
  }
  // « 0 / N » : chiffres blancs sous les cases ; on lit le dernier glyphe avec les chiffres de la date de l'historique
  function supplyCount(P, card) {
    const { W, d } = P, x0 = Math.max(0, card.x0 - 20), x1 = Math.min(W, card.x1 + 20), top = card.y1 + 4;
    const lines = [];
    for (let y = top, inLine = false, start = 0; y < Math.min(P.H, top + 160); y++) {
      let n = 0; for (let x = x0; x < x1; x++) if (lum(d, (y * W + x) * 4) > 170 && sat(d, (y * W + x) * 4) < 60) n++;
      if (n >= 2 && !inLine) { inLine = true; start = y; }
      else if (n < 2 && inLine) { inLine = false; if (y - start >= 7) lines.push([start, y]); }
    }
    if (lines.length < 2) return null;
    const [ya, yb] = lines[1];
    const gl = clean(glyphs(P, x0, x1, ya - 1, yb + 1, 40));
    const last = gl[gl.length - 1];
    if (!last) return null;
    const v = vecOf(last.M, last.a, last.b);
    let best = null;
    for (const [digit, m] of Object.entries(HIST_MODELS.date)) {
      if (digit === '0') continue;
      let e = 0; for (let i = 0; i < m.length; i++) e += (v[i] - m[i]) ** 2; e /= m.length;
      if (!best || e < best.e) best = { digit, e };
    }
    return best && best.e < 0.15 ? +best.digit : null;
  }
  window.scanSupply = async function (img, opts) {
    opts = opts || {};
    const progress = opts.progress || (() => {});
    const refs = await supplyIcons(progress), P = pixels(img);
    progress('Recherche des cases…');
    const boxes = supplyBoxes(P).sort((p, q) => p.x - q.x);
    // une case est un objet si son icone ressemble nettement a un equipement connu (les recompenses sont ignorees)
    const items = [];
    for (const b of boxes) {
      let best = { c: -1 };
      const v = edges(img, b.x, b.y, b.w, b.h);
      const sc = refs.map(r => ({ r, c: corr(v, r.v) }));
      for (const x of sc) if (x.c > best.c) best = { c: x.c, s: x.r.s };
      // meme forme (objet normal / version eclatante) : la teinte du fond de la case departage
      const same = sc.filter(x => x.c >= best.c - 0.02);
      if (same.length > 1) {
        const t = tint(img, b.x, b.y, b.w, b.h), nt = norm(t);
        const score = x => nt < 1.5 ? norm(x.r.t)
          : -(norm(x.r.t) < 1.5 ? 0 : (t[0] * x.r.t[0] + t[1] * x.r.t[1] + t[2] * x.r.t[2]) / (nt * norm(x.r.t)));
        best.s = same.sort((p, q) => score(p) - score(q))[0].r.s;
      }
      if (best.c >= 0.55) items.push({ ...b, s: best.s, score: best.c });
    }
    // cartes : cases sur la meme rangee, separees de moins d'une largeur de case
    const cards = [];
    for (const it of items) {
      const c = cards.find(c => Math.abs(c.y - it.y) < it.h / 2 && it.x - c.x1 < it.w);
      if (c) { c.items.push(it); c.x1 = it.x + it.w; c.y1 = Math.max(c.y1, it.y + it.h); }
      else cards.push({ y: it.y, x0: it.x, x1: it.x + it.w, y1: it.y + it.h, items: [it] });
    }
    cards.forEach(c => { c.need = supplyCount(P, c); });
    return cards;
  };
})();
