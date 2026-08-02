const path = require("node:path");
const fs = require("node:fs/promises");
const sharp = require("sharp");

const projectRoot = path.resolve(__dirname, "..");
const outputDir = path.join(
  projectRoot,
  "poster",
  "assets",
  "canva-icons",
);

const common = `
  <style>
    .ink { fill: none; stroke: #111; stroke-width: 5; stroke-linecap: round; stroke-linejoin: round; }
    .thin { fill: none; stroke: #111; stroke-width: 3.5; stroke-linecap: round; stroke-linejoin: round; }
    .soft { fill: none; stroke: #777; stroke-width: 5; stroke-linecap: round; stroke-linejoin: round; }
  </style>
`;

const icons = [
  {
    name: "orquestador-rag.png",
    width: 150,
    height: 165,
    body: `
      <rect x="7" y="5" width="135" height="42" rx="18" class="ink"/>
      <rect x="7" y="60" width="135" height="42" rx="18" class="ink"/>
      <rect x="7" y="115" width="135" height="42" rx="18" class="ink"/>
      <circle cx="31" cy="26" r="5" fill="#111"/>
      <circle cx="31" cy="81" r="5" fill="#111"/>
      <circle cx="31" cy="136" r="5" fill="#111"/>
      <line x1="50" y1="26" x2="114" y2="26" class="thin"/>
      <line x1="50" y1="81" x2="114" y2="81" class="thin"/>
      <line x1="50" y1="136" x2="114" y2="136" class="thin"/>
    `,
  },
  {
    name: "modelo-embeddings.png",
    width: 150,
    height: 135,
    body: `
      <g transform="translate(7 4)">
        <path d="M60 7 C30 7 12 28 14 52 C-1 66 6 91 26 95 C29 118 57 128 73 111 C91 125 120 114 122 91 C142 80 139 53 122 45 C122 20 91 5 73 21 C69 12 65 7 60 7 Z" class="soft"/>
        <circle cx="37" cy="48" r="5" fill="#777"/>
        <circle cx="66" cy="35" r="5" fill="#777"/>
        <circle cx="91" cy="54" r="5" fill="#777"/>
        <circle cx="52" cy="79" r="5" fill="#777"/>
        <circle cx="91" cy="89" r="5" fill="#777"/>
        <line x1="37" y1="48" x2="66" y2="35" class="soft"/>
        <line x1="66" y1="35" x2="91" y2="54" class="soft"/>
        <line x1="37" y1="48" x2="52" y2="79" class="soft"/>
        <line x1="52" y1="79" x2="91" y2="89" class="soft"/>
        <line x1="91" y1="54" x2="91" y2="89" class="soft"/>
      </g>
    `,
  },
  {
    name: "llm-local.png",
    width: 150,
    height: 120,
    body: `
      <g transform="translate(3 4)">
        <path d="M30 35 Q72 7 114 35 V100 H30 Z" class="ink"/>
        <line x1="42" y1="35" x2="27" y2="16" class="ink"/>
        <line x1="102" y1="35" x2="117" y2="16" class="ink"/>
        <circle cx="58" cy="66" r="7" fill="#777"/>
        <circle cx="86" cy="66" r="7" fill="#777"/>
        <line x1="58" y1="88" x2="86" y2="88" class="soft"/>
      </g>
    `,
  },
  {
    name: "validador.png",
    width: 135,
    height: 140,
    body: `
      <g transform="translate(5 4)">
        <rect x="15" y="8" width="96" height="120" rx="6" class="thin"/>
        <rect x="41" y="0" width="44" height="18" rx="5" fill="#fff" stroke="#111" stroke-width="3.5"/>
        <path d="M36 48 l12 12 l22 -28" class="ink"/>
        <line x1="76" y1="43" x2="99" y2="43" class="thin"/>
        <path d="M36 88 l12 12 l22 -28" class="ink"/>
        <line x1="76" y1="83" x2="99" y2="83" class="thin"/>
      </g>
    `,
  },
  {
    name: "respuesta.png",
    width: 140,
    height: 125,
    body: `
      <g transform="translate(5 4)">
        <rect x="0" y="0" width="126" height="84" rx="10" class="ink"/>
        <path d="M87 84 L105 111 L63 84" class="ink"/>
        <line x1="22" y1="27" x2="102" y2="27" class="thin"/>
        <line x1="22" y1="47" x2="91" y2="47" class="thin"/>
        <line x1="22" y1="67" x2="72" y2="67" class="thin"/>
      </g>
    `,
  },
];

async function main() {
  await fs.mkdir(outputDir, { recursive: true });

  for (const icon of icons) {
    const svg = `
      <svg xmlns="http://www.w3.org/2000/svg"
           width="${icon.width}" height="${icon.height}"
           viewBox="0 0 ${icon.width} ${icon.height}">
        ${common}
        ${icon.body}
      </svg>
    `;

    await sharp(Buffer.from(svg)).png().toFile(path.join(outputDir, icon.name));
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
