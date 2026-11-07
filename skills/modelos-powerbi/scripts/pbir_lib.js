// Librería para escribir informes PBIR (PBIP) con la identidad visual de Miguel Egea.
// La definición de cada informe vive en el proyecto (p. ej. powerbi/_generador/informe.js) y usa esto:
//
//   const { Informe, M, Col, C, barras, multiserie, tabla } = require('<skill>/scripts/pbir_lib.js');
//   const inf = new Informe({ nombre, raiz, cabecera, segmentadores });
//   inf.pagina('clave', 'Nombre', 'SECCIÓN', '¿Pregunta de negocio?', add => { inf.kpis(add, [...]); add('id', [x, y, w, h], barras(...)); });
//   inf.escribir();
//
// Rejilla 1280x720: margen 24, separación 16. Cabecera hasta y=92, KPIs en y=104 (alto 80), contenido de y=184 a 704
// (se reescala a 200..704). Ids deterministas (sha1 de página/clave): regenerar da los mismos ficheros.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const S = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition';
const VC = `${S}/visualContainer/2.9.0/schema.json`;

// Paleta de la identidad visual de Miguel Egea
const C = {
  fondo: '#F7F9FC', superficie: '#FFFFFF', texto: '#172033', azul: '#1769AA', cian: '#00A6C7',
  oro: '#F2B544', verde: '#35A77C', rojo: '#D95C5C', gris: '#8792A2', borde: '#E3E8EF', grisClaro: '#C9D1DC',
};

// Ids deterministas: el mismo informe se regenera igual (diffs limpios).
const hid = (s, n = 20) => crypto.createHash('sha1').update(s).digest('hex').slice(0, n);
const escribir = (ruta, obj) => {
  fs.mkdirSync(path.dirname(ruta), { recursive: true });
  fs.writeFileSync(ruta, (typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2)) + '\n', 'utf8');
};

// ---------------------------------------------------------------- expresiones
const L = v => ({ expr: { Literal: { Value: v } } });
const txt = s => L(`'${s.replace(/'/g, "''")}'`);
const color = hex => ({ solid: { color: L(`'${hex}'`) } });
const B = b => L(b ? 'true' : 'false');
const M = (t, m) => ({ field: { Measure: { Expression: { SourceRef: { Entity: t } }, Property: m } }, queryRef: `${t}.${m}`, nativeQueryRef: m });
const Col = (t, c) => ({ field: { Column: { Expression: { SourceRef: { Entity: t } }, Property: c } }, queryRef: `${t}.${c}`, nativeQueryRef: c });
const sortPor = (p, dir = 'Descending') => ({ sort: [{ field: p.field, direction: dir }], isDefaultSort: false });

const padding = (t, b, l, r) => [{ properties: { top: L(`${t}D`), bottom: L(`${b}D`), left: L(`${l}D`), right: L(`${r}D`) } }];
const titulo = (texto, sub) => ({
  title: [{ properties: { show: B(true), text: txt(texto) } }],
  subTitle: [{ properties: sub ? { show: B(true), text: txt(sub) } : { show: B(false) } }],
});
const sinCaja = () => ({
  background: [{ properties: { show: B(false) } }],
  border: [{ properties: { show: B(false) } }],
  padding: padding(0, 0, 0, 0),
});

let z = 1000;
function contenedor(nombrePagina, clave, pos, visual) {
  z += 1000;
  return {
    $schema: VC,
    name: hid(`${nombrePagina}/${clave}`),
    position: { x: pos[0], y: pos[1], z, height: pos[3], width: pos[2], tabOrder: z },
    visual,
  };
}

// ---------------------------------------------------------------- tipos de visual
// unidades: '1D' = número completo (sin «mil» ni «mill.»), útil para recuentos como pedidos.
function tarjeta(medida, etiqueta, acento = C.azul, tabla = 'Ventas', { unidades } = {}) {
  return {
    visualType: 'cardVisual',
    query: { queryState: { Data: { projections: [M(tabla, medida)] } } },
    objects: {
      value: [{ properties: { fontSize: L('24D'), fontColor: color(C.texto), ...(unidades ? { labelDisplayUnits: L(unidades) } : {}) }, selector: { id: 'default' } }],
      label: [{ properties: { show: B(true), text: txt(etiqueta), fontSize: L('10D'), fontColor: color(C.gris) }, selector: { id: 'default' } }],
      outline: [{ properties: { show: B(false) }, selector: { id: 'default' } }],
      accentBar: [{ properties: { show: B(true), position: txt('Left'), width: L('4D'), color: color(acento) }, selector: { id: 'default' } }],
    },
    visualContainerObjects: { title: [{ properties: { show: B(false) } }], padding: padding(0, 0, 0, 0) },
  };
}

function texto(runs, align = 'left') {
  return {
    visualType: 'textbox',
    objects: { general: [{ properties: { paragraphs: [{ textRuns: runs, horizontalTextAlignment: align }] } }] },
    visualContainerObjects: sinCaja(),
  };
}
const run = (value, size, col = C.texto, fam = 'Segoe UI Semibold') => ({ value, textStyle: { fontFamily: fam, fontSize: `${size}px`, color: col } });

function rectangulo(hex) {
  return {
    visualType: 'shape',
    objects: {
      shape: [{ properties: { tileShape: txt('rectangle') } }],
      fill: [{ properties: { fillColor: color(hex), transparency: L('0D') }, selector: { id: 'default' } }],
      outline: [{ properties: { show: B(false) }, selector: { id: 'default' } }],
    },
    visualContainerObjects: sinCaja(),
  };
}

function segmentador(t, c, cabecera, seleccion) {
  const general = seleccion === undefined ? [] : [{ properties: { filter: { filter: {
    Version: 2,
    From: [{ Name: 's', Entity: t, Type: 0 }],
    Where: [{ Condition: { In: {
      Expressions: [{ Column: { Expression: { SourceRef: { Source: 's' } }, Property: c } }],
      Values: [[{ Literal: { Value: seleccion } }]],
    } } }],
  } } } }];
  return {
    visualType: 'slicer',
    query: { queryState: { Values: { projections: [Col(t, c)] } } },
    objects: {
      data: [{ properties: { mode: txt('Dropdown') } }],
      header: [{ properties: { show: B(true), text: txt(cabecera) } }],
      ...(general.length ? { general } : {}),
    },
    visualContainerObjects: { padding: padding(8, 8, 8, 8) },
  };
}

// Barras/columnas de una sola serie: un color dominante.
function barras(tipo, cat, medida, tit, sub, { col = C.azul, orden = 'medida', etiquetas = true, tabla = 'Ventas' } = {}) {
  const y = M(tabla, medida);
  const v = {
    visualType: tipo,
    query: { queryState: { Category: { projections: [cat] }, Y: { projections: [y] } } },
    objects: {
      dataPoint: [{ properties: { defaultColor: color(col) } }],
      labels: [{ properties: { show: B(etiquetas) } }],
    },
    visualContainerObjects: titulo(tit, sub),
  };
  if (orden === 'medida') v.query.sortDefinition = sortPor(y);
  if (orden === 'categoria') v.query.sortDefinition = sortPor(cat, 'Ascending');
  return v;
}

// Varias medidas con color fijo por medida (selector metadata = queryRef).
function multiserie(tipo, cat, series, tit, sub, { y2 = [], orden = 'categoria' } = {}) {
  const proy = series.map(([t, m]) => M(t, m));
  const proy2 = y2.map(([t, m]) => M(t, m));
  const qs = { Category: { projections: [cat] }, Y: { projections: proy } };
  if (proy2.length) qs.Y2 = { projections: proy2 };
  const fills = [...series, ...y2].map(([t, m, hex]) => ({
    properties: { fill: color(hex) }, selector: { metadata: `${t}.${m}` },
  }));
  const v = {
    visualType: tipo,
    query: { queryState: qs },
    objects: { dataPoint: fills, legend: [{ properties: { show: B(true), position: txt('Top') } }] },
    visualContainerObjects: titulo(tit, sub),
  };
  if (orden === 'categoria') v.query.sortDefinition = sortPor(cat, 'Ascending');
  if (orden === 'medida') v.query.sortDefinition = sortPor(proy[0]);
  return v;
}

function tabla(cols, tit, sub, ordenarPor) {
  const v = {
    visualType: 'tableEx',
    query: { queryState: { Values: { projections: cols } } },
    objects: {
      columnHeaders: [{ properties: { columnAdjustment: txt('growToFit'), autoSizeColumnWidth: B(true) } }],
    },
    visualContainerObjects: titulo(tit, sub),
  };
  if (ordenarPor) v.query.sortDefinition = sortPor(ordenarPor);
  return v;
}

function matriz(filas, valores, tit, sub, expandir = []) {
  const exp = expandir.length ? { expansionStates: [{
    roles: ['Rows'],
    levels: [{ queryRefs: [filas[0].queryRef], isCollapsed: false, identityKeys: [filas[0].field], isPinned: true }],
    root: { children: expandir.map(v => ({ identityValues: [{ Literal: { Value: `'${v}'` } }], isToggled: true })) },
  }] } : {};
  return {
    visualType: 'pivotTable',
    query: { queryState: { Rows: { projections: filas }, Values: { projections: valores } } },
    objects: {
      columnHeaders: [{ properties: { columnAdjustment: txt('growToFit'), autoSizeColumnWidth: B(true) } }],
    },
    visualContainerObjects: titulo(tit, sub),
    ...exp,
  };
}


// ---------------------------------------------------------------- tema
const temaEgea = nombre => ({
  name: nombre,
  dataColors: [C.azul, C.cian, C.oro, C.gris, C.verde, C.rojo, '#5B8DBE', '#7FD3E3', '#F7D08A', '#B9C2CF'],
  good: C.verde, neutral: C.oro, bad: C.rojo,
  maximum: C.azul, center: C.oro, minimum: '#DCEAF6', null: C.gris,
  foreground: C.texto, foregroundNeutralSecondary: C.gris, foregroundNeutralTertiary: '#A9B2BF',
  background: C.superficie, backgroundLight: C.borde, backgroundNeutral: C.borde, tableAccent: C.azul,
  textClasses: {
    callout: { fontSize: 24, fontFace: 'Segoe UI Semibold', color: C.texto },
    title: { fontSize: 11, fontFace: 'Segoe UI Semibold', color: C.texto },
    header: { fontSize: 11, fontFace: 'Segoe UI Semibold', color: C.texto },
    label: { fontSize: 10, fontFace: 'Segoe UI', color: C.texto },
  },
  visualStyles: {
    '*': {
      '*': {
        title: [{ show: true, fontFamily: "'Segoe UI Semibold'", fontSize: 12, fontColor: { solid: { color: C.texto } } }],
        subTitle: [{ fontFamily: "'Segoe UI'", fontSize: 9, fontColor: { solid: { color: C.gris } } }],
        background: [{ show: true, color: { solid: { color: C.superficie } }, transparency: 0 }],
        border: [{ show: true, color: { solid: { color: C.borde } }, radius: 8, width: 1 }],
        dropShadow: [{ show: false }],
        padding: [{ top: 8, bottom: 8, left: 12, right: 12 }],
        valueAxis: [{ gridlineColor: { solid: { color: '#EEF1F5' } } }],
      },
    },
    page: { '*': { background: [{ color: { solid: { color: C.fondo } }, transparency: 0 }], outspace: [{ color: { solid: { color: C.fondo } } }] } },
    tableEx: { '*': { columnHeaders: [{ columnAdjustment: 'growToFit', autoSizeColumnWidth: true, fontColor: { solid: { color: C.gris } } }] } },
    pivotTable: { '*': { columnHeaders: [{ columnAdjustment: 'growToFit', autoSizeColumnWidth: true, fontColor: { solid: { color: C.gris } } }] } },
  },
});

// ---------------------------------------------------------------- informe
class Informe {
  /**
   * @param {object} o
   * @param {string} o.nombre        nombre del PBIP (= nombre del modelo semántico que tiene al lado)
   * @param {string} o.raiz          carpeta del PBIP
   * @param {string} o.cabecera      texto gris de la cabecera (p. ej. 'GreatAdventures · Canal revendedores')
   * @param {Array}  o.segmentadores [[tabla, columna, etiqueta, selecciónPorDefecto?], ...] (máx. 3, arriba a la derecha)
   * @param {string} o.tema          fichero de tema; cambia el sufijo al editarlo (Desktop cachea los temas por nombre)
   */
  constructor({ nombre, raiz, cabecera, segmentadores = [], tema = 'EgeaDataLight-7c41a2e9.json',
                idInforme = crypto.randomUUID(), idModelo = crypto.randomUUID() }) {
    Object.assign(this, { nombre, raiz, cabecera, segmentadores, tema, idInforme, idModelo, paginas: [] });
  }

  /** Página con la cabecera común. construir(add) recibe add(clave, [x, y, ancho, alto], visual).
   *  segmentadores: los de la página, si no son los del informe (p. ej. solo Año en una página cuyos datos no filtran Región ni Categoría). */
  pagina(clave, nombre, seccion, pregunta, construir, { segmentadores } = {}) {
    const id = hid(`pagina/${clave}`);
    const visuales = [];
    const add = (k, pos, v) => visuales.push(contenedor(id, k, pos, v));
    add('marca', [24, 20, 8, 36], rectangulo(C.oro));
    add('titulo', [40, 14, 560, 30], texto([run(this.cabecera, 13, C.gris, 'Segoe UI'), run(`   ${seccion}`, 13, C.azul)]));
    add('pregunta', [40, 40, 700, 32], texto([run(pregunta, 18, C.texto)]));
    add('divisor', [24, 90, 1232, 1], rectangulo(C.borde));
    const claves = ['seg_anio', 'seg_grupo', 'seg_categoria'];
    const segs = (segmentadores || this.segmentadores).slice(0, 3);
    segs.forEach(([t, c, et, sel], i) => {
      const x = 1116 - (segs.length - 1 - i) * 148;
      add(claves[i], [x, 8, 140, 76], segmentador(t, c, et, sel));
    });
    // El contenido se diseña para y=184..704 y se reescala a y=200..704 bajo la cabecera.
    const f = 504 / 520;
    construir((k, pos, v) => add(k, pos[1] >= 184 ? [pos[0], Math.round(200 + (pos[1] - 184) * f), pos[2], Math.round(pos[3] * f)] : pos, v));
    this.paginas.push({ id, nombre, visuales });
  }

  /** Fila de KPIs: [[medida, etiqueta, colorAcento, tabla, opciones], ...]. Oro solo para el KPI clave de la página.
   *  opciones: { unidades: '1D' } para enseñar el número completo. */
  kpis(add, lista) {
    const n = lista.length, ancho = (1232 - 16 * (n - 1)) / n;
    lista.forEach(([m, et, ac, t, op], i) => add(`kpi_${i}`, [Math.round(24 + i * (ancho + 16)), 104, Math.round(ancho), 80], tarjeta(m, et, ac, t, op)));
  }

  escribir() {
    const { nombre: NOMBRE, raiz: RAIZ, tema: TEMA, paginas } = this;
    const REP = path.join(RAIZ, `${NOMBRE}.Report`);
    const DEF = path.join(REP, 'definition');
    const plataforma = (tipo, id) => ({
      $schema: 'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json',
      metadata: { type: tipo, displayName: NOMBRE }, config: { version: '2.0', logicalId: id },
    });
    escribir(path.join(REP, 'definition.pbir'), {
      $schema: 'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json',
      version: '4.0', datasetReference: { byPath: { path: `../${NOMBRE}.SemanticModel` } },
    });
    escribir(path.join(REP, '.platform'), plataforma('Report', this.idInforme));
    const platModelo = path.join(RAIZ, `${NOMBRE}.SemanticModel`, '.platform');
    if (!fs.existsSync(platModelo)) escribir(platModelo, plataforma('SemanticModel', this.idModelo));
    escribir(path.join(RAIZ, `${NOMBRE}.pbip`), {
      $schema: 'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json',
      version: '1.0', artifacts: [{ report: { path: `${NOMBRE}.Report` } }], settings: { enableAutoRecovery: true },
    });
    escribir(path.join(DEF, 'version.json'), { $schema: `${S}/versionMetadata/1.0.0/schema.json`, version: '2.0.0' });
    escribir(path.join(DEF, 'report.json'), {
      $schema: `${S}/report/3.3.0/schema.json`,
      themeCollection: {
        customTheme: { name: TEMA, reportVersionAtImport: { visual: '2.9.0', report: '3.3.0', page: '2.1.0' }, type: 'RegisteredResources' },
      },
      resourcePackages: [{ name: 'RegisteredResources', type: 'RegisteredResources', items: [{ name: TEMA, path: TEMA, type: 'CustomTheme' }] }],
      settings: { useStylableVisualContainerHeader: true, exportDataMode: 'AllowSummarized', defaultDrillFilterOtherVisuals: true,
        allowChangeFilterTypes: true, useEnhancedTooltips: true, useDefaultAggregateDisplayName: true },
    });
    escribir(path.join(REP, 'StaticResources', 'RegisteredResources', TEMA), temaEgea(TEMA));
    escribir(path.join(DEF, 'pages', 'pages.json'), {
      $schema: `${S}/pagesMetadata/1.0.0/schema.json`, pageOrder: paginas.map(p => p.id), activePageName: paginas[0].id,
    });
    for (const p of paginas) {
      escribir(path.join(DEF, 'pages', p.id, 'page.json'), {
        $schema: `${S}/page/2.1.0/schema.json`, name: p.id, displayName: p.nombre, displayOption: 'FitToPage', height: 720, width: 1280,
      });
      for (const v of p.visuales) escribir(path.join(DEF, 'pages', p.id, 'visuals', v.name, 'visual.json'), v);
    }
    const gi = path.join(RAIZ, '.gitignore');
    if (!fs.existsSync(gi)) escribir(gi, '**/.pbi/localSettings.json\n**/.pbi/cache.abf\n');
    // Avisar (no borrar) de páginas o visuales que ya no están en la definición.
    const dirPag = path.join(DEF, 'pages');
    for (const d of fs.readdirSync(dirPag, { withFileTypes: true }).filter(d => d.isDirectory())) {
      const p = paginas.find(x => x.id === d.name);
      if (!p) { console.log(`AVISO: la página ${d.name} ya no está en la definición (bórrala a mano si sobra)`); continue; }
      const dv = path.join(dirPag, d.name, 'visuals');
      if (!fs.existsSync(dv)) continue;
      const sobran = fs.readdirSync(dv).filter(v => !p.visuales.some(x => x.name === v));
      if (sobran.length) console.log(`AVISO: visuales sobrantes en "${p.nombre}": ${sobran.join(', ')}`);
    }
    console.log(`Informe ${NOMBRE}: ${paginas.length} páginas, ${paginas.reduce((a, p) => a + p.visuales.length, 0)} visuales`);
  }
}

module.exports = { Informe, C, L, txt, color, B, M, Col, sortPor, padding, titulo, sinCaja, tarjeta, texto, run, rectangulo,
  segmentador, barras, multiserie, tabla, matriz, temaEgea };
