// Definición del informe GreatAdventuresVentas (5 páginas) sobre el modelo semántico del mismo nombre.
// Uso, desde la raíz del proyecto:  node powerbi/_generador/informe.js
// Librería y reglas de diseño: skills/modelos-powerbi (scripts/pbir_lib.js, references/informe.md).
const path = require('path');
const RAIZ_PROYECTO = path.resolve(__dirname, '..', '..');
const { Informe, C, L, M, Col, barras, multiserie, tabla } = require(path.join(RAIZ_PROYECTO, 'skills', 'modelos-powerbi', 'scripts', 'pbir_lib.js'));

const ANIO_DEFECTO = '2013L';   // último año completo con datos (2014 solo llega a junio)

const inf = new Informe({
  nombre: 'GreatAdventuresVentas',
  raiz: path.join(RAIZ_PROYECTO, 'powerbi'),
  cabecera: 'GreatAdventures · Canal revendedores',
  segmentadores: [['Fecha', 'Año', 'Año', ANIO_DEFECTO], ['Territorio', 'Grupo', 'Región'], ['Producto', 'Categoría', 'Categoría']],
  idInforme: '5d6f0f1e-9a4b-4c2e-8f3a-2b7c1d9e4a61',
  idModelo: '8b2e6c4a-1f7d-4e9b-a3c5-6d0f2e8b1c47',
});

// 1 · Resumen ejecutivo: ¿cómo va el negocio?
inf.pagina('resumen', 'Resumen ejecutivo', 'RESUMEN', '¿Cómo va el canal y hacia dónde se mueve?', add => {
  inf.kpis(add, [
    ['Ventas netas', 'Ventas netas', C.oro], ['% Crecimiento ventas', 'Crecimiento vs año anterior', C.azul],
    ['% Margen bruto', 'Margen bruto', C.azul], ['Pedidos', 'Pedidos', C.azul],
    ['Ticket medio', 'Ticket medio', C.azul], ['Revendedores activos', 'Revendedores activos', C.azul],
  ]);
  add('tendencia', [24, 184, 800, 268], multiserie('lineChart', Col('Fecha', 'Fin de mes'),
    [['Ventas', 'Ventas netas', C.azul], ['Ventas', 'Ventas netas AA', C.grisClaro]],
    'Ventas netas por mes frente al año anterior', 'Gris: mismo mes del año anterior'));
  add('categoria', [840, 184, 416, 268], barras('clusteredBarChart', Col('Producto', 'Categoría'), 'Ventas netas',
    'Ventas netas por categoría', 'Bikes concentra la mayor parte del negocio'));
  add('territorio', [24, 468, 608, 236], barras('clusteredColumnChart', Col('Territorio', 'Territorio'), 'Ventas netas',
    'Ventas netas por territorio', null));
  add('crecimiento', [648, 468, 608, 236], multiserie('lineClusteredColumnComboChart', Col('Fecha', 'Año trimestre'),
    [['Ventas', 'Margen bruto', C.azul]], 'Margen bruto y % de margen por trimestre', 'Columnas: margen bruto · Línea: % margen',
    { y2: [['Ventas', '% Margen bruto', C.oro]] }));
});

// 2 · Producto y rentabilidad: ¿qué vendemos y cuánto nos deja?
inf.pagina('producto', 'Producto y rentabilidad', 'PRODUCTO Y RENTABILIDAD', '¿Qué vendemos y cuánto margen nos deja?', add => {
  inf.kpis(add, [
    ['Margen bruto', 'Margen bruto', C.oro], ['% Margen bruto', '% Margen bruto', C.azul],
    ['Unidades', 'Unidades', C.azul], ['Precio medio de venta', 'Precio medio de venta', C.azul],
    ['% Descuento', 'Tasa de descuento', C.azul], ['Productos vendidos', 'Referencias vendidas', C.azul],
  ]);
  add('matriz', [24, 184, 720, 520], tabla([Col('Producto', 'Categoría'), Col('Producto', 'Subcategoría'),
    M('Ventas', 'Ventas netas'), M('Ventas', 'Margen bruto'), M('Ventas', '% Margen bruto'), M('Ventas', '% Descuento'),
    M('Ventas', 'Unidades')],
    'Rentabilidad por subcategoría', 'Ordenado por ventas netas', M('Ventas', 'Ventas netas')));
  add('margen_sub', [760, 184, 496, 260], barras('clusteredBarChart', Col('Producto', 'Subcategoría'), '% Margen bruto',
    '% de margen bruto por subcategoría', 'Ordenado de mayor a menor margen', { col: C.azul }));
  add('promo', [760, 460, 496, 244], barras('clusteredBarChart', Col('Promoción', 'Tipo de promoción'), 'Ventas netas',
    'Ventas netas por tipo de promoción', "'No Discount' = venta sin promoción", { col: C.cian }));
});

// 3 · Revendedores: ¿quién nos compra y lo retenemos?
inf.pagina('revendedores', 'Revendedores', 'REVENDEDORES', '¿Quién nos compra, cuánto y si repite?', add => {
  inf.kpis(add, [
    ['Revendedores activos', 'Revendedores activos', C.azul], ['Revendedores nuevos', 'Revendedores nuevos', C.oro],
    ['% Retención de revendedores', 'Retención vs año anterior', C.azul], ['Ventas por revendedor', 'Ventas por revendedor', C.azul],
    ['Pedidos por revendedor', 'Pedidos por revendedor', C.azul], ['% Ventas top 10 revendedores', 'Peso del top 10', C.azul],
  ]);
  add('top', [24, 184, 720, 520], tabla([Col('Revendedor', 'Revendedor'), Col('Revendedor', 'País'),
    M('Ventas', 'Ventas netas'), M('Ventas', 'Pedidos'), M('Ventas', 'Ticket medio'), M('Ventas', '% Margen bruto')],
    'Revendedores por ventas netas', 'Ordenado de mayor a menor', M('Ventas', 'Ventas netas')));
  add('evolucion', [760, 184, 496, 260], multiserie('clusteredColumnChart', Col('Fecha', 'Año trimestre'),
    [['Ventas', 'Revendedores activos', C.azul], ['Ventas', 'Revendedores nuevos', C.oro]],
    'Revendedores activos y nuevos por trimestre', null));
  add('pais', [760, 460, 496, 244], barras('clusteredBarChart', Col('Revendedor', 'País'), 'Ventas por revendedor',
    'Ventas por revendedor según su país', 'Ventas netas medias por revendedor activo'));
});

// 4 · Comerciales y territorios: ¿cumplimos cuota?
inf.pagina('comerciales', 'Comerciales y territorios', 'COMERCIALES Y TERRITORIOS', '¿Cumplen cuota los comerciales y qué territorios tiran?', add => {
  inf.kpis(add, [
    ['Ventas netas', 'Ventas netas', C.azul, 'Ventas'], ['Cuota', 'Cuota', C.azul, 'Cuotas'],
    ['% Cumplimiento de cuota', 'Cumplimiento de cuota', C.oro, 'Cuotas'], ['Desviación sobre cuota', 'Desviación sobre cuota', C.azul, 'Cuotas'],
    ['Comerciales que cumplen cuota', 'Comerciales que cumplen', C.azul, 'Cuotas'], ['Comisión estimada', 'Comisión estimada', C.azul, 'Cuotas'],
  ]);
  add('ventas_cuota', [24, 184, 608, 300], multiserie('clusteredBarChart', Col('Vendedor', 'Vendedor'),
    [['Ventas', 'Ventas netas', C.azul], ['Cuotas', 'Cuota', C.grisClaro]],
    'Ventas netas frente a cuota por comercial', 'Gris: cuota del periodo', { orden: 'medida' }));
  add('tabla_com', [648, 184, 608, 300], tabla([Col('Vendedor', 'Vendedor'), M('Ventas', 'Ventas netas'), M('Cuotas', 'Cuota'),
    M('Cuotas', '% Cumplimiento de cuota'), M('Cuotas', 'Desviación sobre cuota')],
    'Cumplimiento de cuota por comercial', 'Analiza la cuota por trimestre o año', M('Cuotas', '% Cumplimiento de cuota')));
  add('cumpl_trim', [24, 500, 608, 204], multiserie('lineClusteredColumnComboChart', Col('Fecha', 'Año trimestre'),
    [['Ventas', 'Ventas netas', C.azul], ['Cuotas', 'Cuota', C.grisClaro]], 'Ventas, cuota y cumplimiento por trimestre',
    'Línea: % cumplimiento', { y2: [['Cuotas', '% Cumplimiento de cuota', C.oro]] }));
  add('grupo', [648, 500, 608, 204], multiserie('clusteredColumnChart', Col('Territorio', 'Territorio'),
    [['Ventas', 'Ventas netas', C.azul], ['Ventas', 'Ventas netas AA', C.grisClaro]],
    'Ventas netas por territorio frente al año anterior', null, { orden: 'medida' }));
});

// 5 · Cobros y deuda: ¿cuánto nos deben y desde cuándo?
// Cobros no se relaciona con Fecha ni con Territorio o Producto: la deuda es una foto al último día del periodo,
// y en esta página solo hay segmentador de Año (Región y Categoría no filtrarían nada).
inf.pagina('cobros', 'Cobros y deuda', 'COBROS Y DEUDA', '¿Cuánto nos deben, desde cuándo y cómo nos pagan?', add => {
  inf.kpis(add, [
    ['Deuda vencida pendiente', 'Deuda vencida al cierre', C.oro, 'Cobros'], ['Facturas vencidas pendientes', 'Facturas vencidas', C.azul, 'Cobros'],
    ['Deuda pendiente total', 'Deuda pendiente total', C.azul, 'Cobros'],
    ['Importe cobrado', 'Cobrado en el periodo', C.azul, 'Cobros'],
  ]);
  add('evolucion', [24, 184, 800, 268], multiserie('lineChart', Col('Fecha', 'Fin de mes'),
    [['Cobros', 'Deuda vencida pendiente', C.azul], ['Cobros', 'Deuda pendiente total', C.grisClaro]],
    'Deuda vencida pendiente a fin de mes', 'Gris: deuda pendiente total (vencida y por vencer)'));
  const metodo = barras('clusteredBarChart', Col('Método de pago', 'Método de pago'), 'Deuda vencida pendiente',
    'Deuda vencida por método de pago', 'Al último día del periodo', { tabla: 'Cobros' });
  metodo.objects.categoryAxis = [{ properties: { maxMarginFactor: L('35L') } }];   // «Recibo domiciliado» sin cortar
  add('metodo', [840, 184, 416, 268], metodo);
  add('facturas', [24, 468, 800, 236], barras('clusteredColumnChart', Col('Fecha', 'Fin de mes'), 'Facturas vencidas pendientes',
    'Facturas vencidas pendientes a fin de mes', 'Número de facturas vencidas y sin pagar al cierre de cada mes', { tabla: 'Cobros', orden: 'categoria' }));
  add('cobrado', [840, 468, 416, 236], barras('clusteredColumnChart', Col('Fecha', 'Fin de mes'), 'Importe cobrado',
    'Importe cobrado por mes', null, { tabla: 'Cobros', orden: 'categoria', etiquetas: false }));
}, { segmentadores: [['Fecha', 'Año', 'Año', ANIO_DEFECTO]] });

inf.escribir();
