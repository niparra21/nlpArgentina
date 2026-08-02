import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/nicop/Documents/GitHub/nlpArgentina";
const TMP = `${ROOT}/tmp/poster-a0`;
const OUTPUT = `${ROOT}/outputs/poster-20260728`;
const PPTX = `${OUTPUT}/poster-rag-observable-a0-vertical.pptx`;
const PREVIEW = `${TMP}/poster-preview.png`;
const LAYOUT = `${TMP}/poster-layout.json`;

await fs.mkdir(OUTPUT, { recursive: true });

const W = 3179;
const H = 4494;

const C = {
  canvas: "#FFFFFF",
  ink: "#102A43",
  muted: "#52606D",
  rule: "#CBD2D9",
  panel: "#F3F5F7",
  panelBlue: "#EAF4FB",
  panelTeal: "#E6F4F1",
  teal: "#0F766E",
  tealDark: "#0B5F58",
  blue: "#2D6CDF",
  blueDark: "#1F4FA3",
  coral: "#C95F45",
  coralPale: "#FBEDE8",
  success: "#2F855A",
  white: "#FFFFFF",
};

const FONT = "Arial";

const presentation = Presentation.create({
  slideSize: { width: W, height: H },
});
const slide = presentation.slides.add();
slide.background.fill = C.canvas;

function addShape(name, geometry, x, y, w, h, fill, lineFill = "none", lineWidth = 0) {
  return slide.shapes.add({
    name,
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
  });
}

function addText(
  name,
  text,
  x,
  y,
  w,
  h,
  {
    size = 28,
    color = C.ink,
    bold = false,
    align = "left",
    vertical = "top",
    fill = "none",
    lineFill = "none",
    lineWidth = 0,
    insets = { top: 0, right: 0, bottom: 0, left: 0 },
    autoFit = "shrinkText",
    lineSpacing = 1.0,
  } = {},
) {
  const box = slide.shapes.add({
    name,
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
  });
  box.text = text;
  box.text.style = {
    typeface: FONT,
    fontSize: size,
    color,
    bold,
    alignment: align,
    verticalAlignment: vertical,
    autoFit,
    wrap: "square",
    insets,
    lineSpacing,
  };
  return box;
}

function addSectionTitle(name, text, x, y, w, color = C.teal) {
  addShape(`${name}-bar`, "rect", x, y + 7, 10, 42, color);
  return addText(name, text, x + 28, y, w - 28, 58, {
    size: 40,
    color: C.ink,
    bold: true,
    vertical: "middle",
  });
}

function addRule(name, x, y, w, color = C.rule, height = 2) {
  return addShape(name, "rect", x, y, w, height, color);
}

function addMetric(name, value, label, x, y, w, accent) {
  addText(`${name}-value`, value, x, y, w, 92, {
    size: 70,
    color: accent,
    bold: true,
    vertical: "bottom",
  });
  addText(`${name}-label`, label, x, y + 98, w, 82, {
    size: 25,
    color: C.ink,
    bold: true,
    autoFit: "shrinkText",
  });
}

function addFinding(name, number, title, body, x, y, w, accent = C.coral) {
  addText(`${name}-number`, number, x, y, 72, 72, {
    size: 40,
    color: C.white,
    bold: true,
    align: "center",
    vertical: "middle",
    fill: accent,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  addText(`${name}-title`, title, x + 98, y - 2, w - 98, 56, {
    size: 29,
    color: C.ink,
    bold: true,
  });
  addText(`${name}-body`, body, x + 98, y + 56, w - 98, 132, {
    size: 24,
    color: C.muted,
    lineSpacing: 1.05,
  });
}

// Header
addText(
  "event-eyebrow",
  "SEGUNDA ESCUELA SUDAMERICANA DE NLP · BUENOS AIRES · 2026",
  120,
  72,
  1900,
  48,
  { size: 23, color: C.teal, bold: true, vertical: "middle" },
);

addText(
  "poster-title",
  "Diseño arquitectónico mínimo para sistemas RAG\nobservables en español latinoamericano",
  120,
  138,
  2939,
  260,
  {
    size: 104,
    color: C.ink,
    bold: true,
    lineSpacing: 0.9,
    autoFit: "shrinkText",
  },
);

addText(
  "author",
  "Nicole Tatiana Parra Valverde · Trabajo independiente",
  120,
  425,
  1800,
  56,
  { size: 33, color: C.ink, bold: true, vertical: "middle" },
);
addText(
  "case-study",
  "Caso de estudio: normativa estudiantil del Tecnológico de Costa Rica",
  120,
  488,
  1800,
  48,
  { size: 27, color: C.muted, vertical: "middle" },
);

addShape("lead-accent", "rect", 2050, 420, 12, 158, C.blue);
addText(
  "lead",
  "Registrar evidencia, citas y tiempos permite explicar no solo cuánto falla un RAG, sino en qué componente ocurre el fallo.",
  2088,
  412,
  971,
  174,
  {
    size: 30,
    color: C.blueDark,
    bold: true,
    vertical: "middle",
    lineSpacing: 1.03,
  },
);
addRule("header-rule", 120, 625, 2939, C.ink, 4);

// Architecture band
addShape("architecture-panel", "rect", 120, 680, 2939, 1050, C.panel);
addSectionTitle(
  "architecture-title",
  "Arquitectura mínima = pipeline reproducible + contrato de salida + traza por consulta",
  165,
  720,
  2849,
  C.teal,
);
addText(
  "architecture-purpose",
  "Cada componente produce un artefacto verificable y conserva suficiente contexto para atribuir los fallos.",
  193,
  782,
  2765,
  50,
  { size: 25, color: C.muted, vertical: "middle" },
);

const nodeY = 875;
const nodeW = 340;
const nodeH = 250;
const nodeGap = 65;
const nodeX = 185;
const nodeData = [
  ["Fuentes", "25 documentos\ncaptura + hash"],
  ["Secciones", "1 184 registros\nartículos + transitorios"],
  ["Índice", "1 259 fragmentos\nE5 · 384 dimensiones"],
  ["Recuperación", "top-5\nsimilitud coseno"],
  ["Generación", "Qwen3.5:9B\nOllama local"],
  ["Validación", "citas visibles\n+ estructuradas"],
  ["Salida", "respuesta\n+ traza JSON"],
];
const nodeColors = [
  C.panelBlue,
  C.panelBlue,
  C.panelTeal,
  C.panelTeal,
  C.panelBlue,
  C.coralPale,
  C.panelTeal,
];
const nodeAccents = [
  C.blue,
  C.blue,
  C.teal,
  C.teal,
  C.blue,
  C.coral,
  C.success,
];

const nodes = [];
for (let i = 0; i < nodeData.length; i += 1) {
  const x = nodeX + i * (nodeW + nodeGap);
  const node = addShape(
    `architecture-node-${i + 1}`,
    "roundRect",
    x,
    nodeY,
    nodeW,
    nodeH,
    nodeColors[i],
    nodeAccents[i],
    3,
  );
  nodes.push(node);
  addText(
    `architecture-node-${i + 1}-step`,
    String(i + 1).padStart(2, "0"),
    x + 22,
    nodeY + 18,
    70,
    42,
    { size: 22, color: nodeAccents[i], bold: true, vertical: "middle" },
  );
  addText(
    `architecture-node-${i + 1}-title`,
    nodeData[i][0],
    x + 22,
    nodeY + 70,
    nodeW - 44,
    55,
    { size: 30, color: C.ink, bold: true, vertical: "middle" },
  );
  addText(
    `architecture-node-${i + 1}-body`,
    nodeData[i][1],
    x + 22,
    nodeY + 135,
    nodeW - 44,
    88,
    { size: 23, color: C.muted, lineSpacing: 1.02 },
  );
}

for (let i = 0; i < nodes.length - 1; i += 1) {
  slide.shapes.connect(nodes[i], nodes[i + 1], {
    kind: "straight",
    fromSide: "right",
    toSide: "left",
    line: { style: "solid", fill: C.rule, width: 4 },
    tail: { type: "arrow", width: "med", length: "med" },
  });
}

addShape("trace-panel", "roundRect", 185, 1195, 2810, 330, C.panelTeal, C.teal, 2);
addText("trace-title", "Traza observable por consulta", 220, 1230, 600, 52, {
  size: 31,
  color: C.tealDark,
  bold: true,
  vertical: "middle",
});
addText(
  "trace-fields",
  "pregunta  →  IDs y puntuaciones de fragmentos  →  contexto  →  respuesta y estado  →  citas  →  tiempos",
  220,
  1305,
  2735,
  84,
  {
    size: 31,
    color: C.ink,
    bold: true,
    align: "center",
    vertical: "middle",
  },
);
addText(
  "trace-explanation",
  "El corpus, el índice, las preguntas, la configuración y los resultados quedan versionados. Esto permite reproducir la corrida y separar fallos de recuperación, generación y validación.",
  250,
  1410,
  2675,
  78,
  { size: 24, color: C.muted, align: "center", vertical: "middle" },
);

addText(
  "architecture-configuration",
  "Configuración: multilingual-e5-small · top-5 · Qwen3.5:9B Q4_K_M · temperatura 0,1 · ejecución local",
  185,
  1575,
  2810,
  72,
  {
    size: 25,
    color: C.ink,
    bold: true,
    align: "center",
    vertical: "middle",
    fill: C.white,
    lineFill: C.rule,
    lineWidth: 2,
    insets: { top: 8, right: 20, bottom: 8, left: 20 },
  },
);

// Lower three-column evidence area
const colTop = 1825;
const colBottom = 4200;
const colH = colBottom - colTop;
const colGap = 72;
const colW = 931;
const col1 = 120;
const col2 = col1 + colW + colGap;
const col3 = col2 + colW + colGap;

addRule("column-rule-1", col2 - colGap / 2, colTop + 10, 2, C.rule, colH - 20);
addRule("column-rule-2", col3 - colGap / 2, colTop + 10, 2, C.rule, colH - 20);

// Column 1
addSectionTitle("problem-title", "Problema y objetivo", col1, colTop, colW, C.blue);
addText(
  "problem-body",
  "Los prototipos RAG suelen mostrar una respuesta final, pero no siempre conservan la cadena de evidencia necesaria para explicar por qué fue generada. Sin una traza es difícil distinguir fallos de recuperación, generación o validación.",
  col1,
  colTop + 78,
  colW,
  260,
  { size: 27, color: C.muted, lineSpacing: 1.06 },
);

addShape("objective-panel", "roundRect", col1, colTop + 360, colW, 260, C.panelBlue, C.blue, 2);
addText("objective-label", "OBJETIVO", col1 + 28, colTop + 382, colW - 56, 42, {
  size: 21,
  color: C.blue,
  bold: true,
});
addText(
  "objective-body",
  "Diseñar e implementar una arquitectura RAG mínima, local y reproducible para documentos en español latinoamericano, con señales básicas de observabilidad por consulta.",
  col1 + 28,
  colTop + 438,
  colW - 56,
  150,
  { size: 27, color: C.ink, bold: true, lineSpacing: 1.04 },
);

addSectionTitle("case-title", "Caso de estudio", col1, colTop + 670, colW, C.teal);
addMetric("docs", "25", "documentos oficiales", col1, colTop + 748, 250, C.teal);
addMetric("sections", "1 184", "secciones procesadas", col1 + 300, colTop + 748, 300, C.teal);
addMetric("chunks", "1 259", "fragmentos indexados", col1 + 650, colTop + 748, 281, C.teal);

addText(
  "case-detail",
  "Normativa estudiantil del TEC, Costa Rica. Cada captura conserva URL, fecha y suma de verificación.",
  col1,
  colTop + 950,
  colW,
  110,
  { size: 25, color: C.muted, lineSpacing: 1.05 },
);

addSectionTitle("evaluation-title", "Diseño experimental", col1, colTop + 1110, colW, C.blue);
addText(
  "evaluation-body",
  "40 preguntas de referencia\n\n25 directas · 8 de varias secciones · 7 no respondibles\n\nCada ejecución guardó fragmentos, respuesta, citas y tiempos. Las 40 respuestas se revisaron manualmente con seis criterios.",
  col1,
  colTop + 1190,
  colW,
  360,
  { size: 27, color: C.ink, lineSpacing: 1.04 },
);

addSectionTitle("human-rubric-title", "Revisión humana", col1, colTop + 1590, colW, C.teal);
addText(
  "human-rubric-body",
  "- Corrección factual\n- Cobertura\n- Fidelidad a fuentes\n- Claridad\n- Evidencia gold\n- Conclusión manual",
  col1,
  colTop + 1672,
  430,
  330,
  { size: 27, color: C.ink, lineSpacing: 1.08 },
);
addText(
  "automatic-metrics-body",
  "Las métricas automáticas describen recuperación, citas y latencia; no se presentan como exactitud factual.",
  col1 + 465,
  colTop + 1672,
  colW - 465,
  250,
  {
    size: 26,
    color: C.blueDark,
    bold: true,
    fill: C.panelBlue,
    lineFill: C.rule,
    lineWidth: 1,
    insets: { top: 22, right: 22, bottom: 22, left: 22 },
    vertical: "middle",
    lineSpacing: 1.05,
  },
);

// Column 2
addSectionTitle("results-title", "Resultados", col2, colTop, colW, C.blue);
addText(
  "results-intro",
  "La evaluación humana permite distinguir contenido correcto, cobertura y calidad de la salida.",
  col2,
  colTop + 74,
  colW,
  90,
  { size: 25, color: C.muted, lineSpacing: 1.03 },
);

addMetric("strict", "78,8 %", "corrección factual estricta", col2, colTop + 180, 420, C.blue);
addMetric("faith", "93,5 %", "fidelidad total a fuentes", col2 + 500, colTop + 180, 431, C.teal);
addRule("metric-rule-1", col2, colTop + 385, colW, C.rule, 2);
addMetric("coverage", "72,7 %", "cobertura completa", col2, colTop + 420, 420, C.blue);
addMetric("abstention", "7 / 7", "abstenciones correctas", col2 + 500, colTop + 420, 431, C.success);

addSectionTitle("by-type-title", "Aprobación por tipo de pregunta", col2, colTop + 650, colW, C.teal);
slide.charts.add("bar", {
  position: { left: col2, top: colTop + 735, width: colW, height: 610 },
  categories: [
    "Directas · 19/25",
    "Varias secciones · 2/8",
    "No respondibles · 7/7",
  ],
  series: [
    {
      name: "Aprobación",
      values: [76, 25, 100],
      fill: C.blue,
      valuesFormatCode: '0"%"',
    },
  ],
  hasLegend: false,
  dataLabels: {
    showValue: true,
    position: "outEnd",
    textStyle: { fill: C.ink, fontSize: 24, bold: true },
  },
  chartFill: C.white,
  chartLine: { style: "solid", fill: C.white, width: 0 },
  plotAreaFill: { type: "none" },
  plotAreaLine: { style: "solid", fill: C.white, width: 0 },
  xAxis: {
    visible: true,
    min: 0,
    max: 100,
    majorUnit: 25,
    numberFormatCode: '0"%"',
    textStyle: { fill: C.muted, fontSize: 20 },
    line: { style: "solid", fill: C.rule, width: 1 },
    majorGridlines: { style: "solid", fill: C.panel, width: 1 },
  },
  yAxis: {
    visible: true,
    textStyle: { fill: C.ink, fontSize: 23, bold: true },
    line: { style: "solid", fill: C.white, width: 0 },
    majorGridlines: null,
  },
  barOptions: { direction: "bar", grouping: "clustered", gapWidth: 55 },
});

addText(
  "chart-takeaway",
  "Hallazgo central: el sistema se abstiene bien, pero pierde cobertura cuando debe combinar evidencia distribuida.",
  col2,
  colTop + 1365,
  colW,
  155,
  {
    size: 28,
    color: C.tealDark,
    bold: true,
    fill: C.panelTeal,
    insets: { top: 24, right: 26, bottom: 24, left: 26 },
    vertical: "middle",
    lineSpacing: 1.03,
  },
);

addSectionTitle("automatic-title", "Rendimiento automático", col2, colTop + 1570, colW, C.blue);
addText(
  "automatic-values",
  "93,9 %\nrecuperación con evidencia gold en top-5",
  col2,
  colTop + 1650,
  420,
  160,
  { size: 29, color: C.blueDark, bold: true, lineSpacing: 1.0 },
);
addText(
  "latency-values",
  "27 ms\nbúsqueda semántica promedio",
  col2 + 500,
  colTop + 1650,
  431,
  160,
  { size: 29, color: C.blueDark, bold: true, lineSpacing: 1.0 },
);
addText(
  "latency-total",
  "5,53 s por pregunta: la generación consume 5,36 s en promedio y domina la latencia del pipeline.",
  col2,
  colTop + 1840,
  colW,
  145,
  {
    size: 27,
    color: C.ink,
    fill: C.panelBlue,
    insets: { top: 22, right: 24, bottom: 22, left: 24 },
    vertical: "middle",
    lineSpacing: 1.03,
  },
);

// Column 3
addSectionTitle("findings-title", "Lo que reveló la observabilidad", col3, colTop, colW, C.coral);
addFinding(
  "finding-1",
  "1",
  "Evidencia distribuida",
  "Solo 2 de 8 preguntas de varias secciones fueron aprobadas. Con frecuencia se recuperó una parte, pero no todos los artículos necesarios.",
  col3,
  colTop + 92,
  colW,
);
addFinding(
  "finding-2",
  "2",
  "Documento correcto, fragmento incorrecto",
  "En q029 apareció el artículo relacionado, pero no el fragmento que contenía el dato. El análisis por Record ID habría ocultado el fallo.",
  col3,
  colTop + 320,
  colW,
);
addFinding(
  "finding-3",
  "3",
  "Contenido correcto, salida inválida",
  "q025 y q032 se rechazaron porque las citas visibles y estructuradas no coincidían. La validez del contrato también es calidad.",
  col3,
  colTop + 548,
  colW,
);
addFinding(
  "finding-4",
  "4",
  "Abstención confiable",
  "Las 7 preguntas sobre precios, horarios, contraseñas o cupos actuales recibieron not_found, sin inventar información ausente.",
  col3,
  colTop + 776,
  colW,
  C.success,
);

addShape("conclusion-panel", "roundRect", col3, colTop + 1025, colW, 405, C.ink);
addText("conclusion-label", "CONCLUSIÓN", col3 + 32, colTop + 1055, colW - 64, 46, {
  size: 22,
  color: "#8DE0D0",
  bold: true,
});
addText(
  "conclusion-body",
  "Una arquitectura pequeña puede ofrecer trazabilidad útil sin una plataforma compleja. Registrar evidencia, citas, estados y tiempos permitió localizar fallos en recuperación, generación y validación.",
  col3 + 32,
  colTop + 1115,
  colW - 64,
  255,
  { size: 29, color: C.white, bold: true, lineSpacing: 1.04 },
);

addSectionTitle("limitations-title", "Limitaciones y trabajo futuro", col3, colTop + 1480, colW, C.blue);
addText(
  "limitations-body",
  "Limitaciones\n- Un dominio, un embedding y un modelo generativo\n- 40 preguntas y una persona revisora\n- Sin comparación léxica, híbrida ni reranking\n\nSiguientes pasos\n- Reranking para evidencia multisección\n- Comparar recuperación densa, léxica e híbrida\n- Ampliar países, dominios y revisión humana",
  col3,
  colTop + 1560,
  colW,
  475,
  { size: 25, color: C.ink, lineSpacing: 1.03 },
);

addShape("repo-panel", "roundRect", col3, colTop + 2050, colW, 190, C.panelTeal, C.teal, 2);
addText("repo-label", "CÓDIGO, DATOS Y DOCUMENTACIÓN", col3 + 30, colTop + 2070, colW - 60, 42, {
  size: 20,
  color: C.teal,
  bold: true,
});
const repoText = addText(
  "repo-url",
  "github.com/niparra21/nlpArgentina",
  col3 + 30,
  colTop + 2123,
  colW - 60,
  70,
  { size: 31, color: C.tealDark, bold: true, vertical: "middle" },
);
repoText.text.get("github.com/niparra21/nlpArgentina").link = {
  uri: "https://github.com/niparra21/nlpArgentina",
  isExternal: true,
};

// Footer
addRule("footer-rule", 120, 4250, 2939, C.ink, 3);
addText(
  "references",
  "Referencias: Lewis et al. (2020), Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks · Wang et al. (2024), Multilingual E5 Text Embeddings · Fuentes del caso: reglamentos oficiales del TEC.",
  120,
  4280,
  2430,
  96,
  { size: 20, color: C.muted, lineSpacing: 1.02 },
);
addText(
  "poster-logistics",
  "Sesión 2 · Orden 12",
  2600,
  4280,
  459,
  48,
  { size: 23, color: C.ink, bold: true, align: "right" },
);
addText(
  "disclaimer",
  "Los resultados corresponden a una corrida reproducible del prototipo y no sustituyen la consulta de la normativa oficial.",
  120,
  4380,
  2939,
  48,
  { size: 19, color: C.muted, align: "center", vertical: "middle" },
);

slide.speakerNotes.textFrame.setText(
  `[Sources]
- Local corpus metadata: ${ROOT}/data/processed/tec/2026-07-23/processing_manifest.json
- Local index metadata: ${ROOT}/data/indexes/tec/2026-07-23/multilingual-e5-small/index_manifest.json
- Retrieval evaluation: ${ROOT}/results/retrieval/2026-07-23/multilingual-e5-small/summary.json
- Automatic RAG evaluation: ${ROOT}/results/rag-evaluation/2026-07-28/qwen3.5-9b-normalized-citations/summary.json
- Human review: ${ROOT}/outputs/rag-manual-review-20260728/revision_manual_rag_completada.xlsx
- Decision log: ${ROOT}/docs/05-bitacora-revision-manual.md
- Repository: https://github.com/niparra21/nlpArgentina
- Lewis et al. 2020: https://arxiv.org/abs/2005.11401
- Wang et al. 2024: https://arxiv.org/abs/2402.05672
- TEC sources: https://www.tec.ac.cr/`,
);

const preview = await presentation.export({
  slide,
  format: "png",
  scale: 0.5,
});
await fs.writeFile(PREVIEW, new Uint8Array(await preview.arrayBuffer()));

const layout = await slide.export({ format: "layout" });
await fs.writeFile(LAYOUT, await layout.text());

const inspection = await presentation.inspect({
  kind: "slide,textbox,shape,chart,notes",
  maxChars: 12000,
});
console.log("POSTER_INSPECTION");
console.log(inspection.ndjson);

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(PPTX);

console.log(JSON.stringify({
  pptx: PPTX,
  preview: PREVIEW,
  layout: LAYOUT,
  slideSize: { width: W, height: H },
}));
