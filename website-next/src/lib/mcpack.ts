import * as fs from "fs";
import * as zlib from "zlib";
import * as path from "path";
import { packSourceDir, Pack } from "./catalog";

// ---- deterministic PRNG (mulberry32) ----
function hashStr(s: string): number {
  let h = 1779033703 ^ s.length;
  for (let i = 0; i < s.length; i++) {
    h = Math.imul(h ^ s.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return h >>> 0;
}
function mulberry32(a: number) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---- palette per pack type ----
const PALETTES: Record<string, [number, number, number][]> = {
  skins: [
    [0x2e, 0x5c, 0xff], [0x3d, 0xb4, 0x68], [0xcb, 0x31, 0x31],
    [0xf0, 0xc4, 0x4c], [0x8e, 0x44, 0xad], [0x16, 0xa0, 0x85],
  ],
  textures: [
    [0x6d, 0x4c, 0x41], [0x95, 0x75, 0x5b], [0x4d, 0xa1, 0x67],
    [0xdd, 0xdd, 0xdd], [0x3d, 0x5a, 0x80], [0xa1, 0x88, 0x6a],
  ],
  worlds: [
    [0x2e, 0x7d, 0x32], [0x55, 0x6b, 0x2f], [0x81, 0xc7, 0x84],
    [0x4f, 0xc3, 0xf7], [0x79, 0x86, 0xcb], [0xbf, 0x9b, 0x6f],
  ],
  mashup: [
    [0x2e, 0x5c, 0xff], [0xcb, 0x31, 0x31], [0x8e, 0x44, 0xad],
    [0xf0, 0xc4, 0x4c], [0x16, 0xa0, 0x85], [0xef, 0x6c, 0x9f],
  ],
};

function typeKey(t: string): string {
  if (t.includes("skin")) return "skins";
  if (t.includes("texture")) return "textures";
  if (t.includes("world")) return "worlds";
  return "mashup";
}

// ---- PNG encoder (truecolor RGBA, no deps) ----
function crc32(buf: Buffer): number {
  let c = ~0;
  for (let i = 0; i < buf.length; i++) {
    c ^= buf[i];
    for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1));
  }
  return ~c >>> 0;
}
function chunk(type: string, data: Buffer): Buffer {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const t = Buffer.from(type, "ascii");
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([t, data])) >>> 0, 0);
  return Buffer.concat([len, t, data, crc]);
}
export function encodePNG(width: number, height: number, rgba: Buffer): Buffer {
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type RGBA
  ihdr[10] = 0;
  ihdr[11] = 0;
  ihdr[12] = 0;
  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y++) {
    raw[y * (width * 4 + 1)] = 0; // filter none
    rgba.copy(raw, y * (width * 4 + 1) + 1, y * width * 4, (y + 1) * width * 4);
  }
  const idat = zlib.deflateSync(raw);
  return Buffer.concat([sig, chunk("IHDR", ihdr), chunk("IDAT", idat), chunk("IEND", Buffer.alloc(0))]);
}

// ---- generate a deterministic 64x64 skin-ish texture ----
export function generateSkinPNG(seed: string, kind: string, size = 64): Buffer {
  const rnd = mulberry32(hashStr(seed));
  const pal = PALETTES[typeKey(kind)] || PALETTES.skins;
  const rgba = Buffer.alloc(size * size * 4);
  // base gradient + blocks
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const i = (y * size + x) * 4;
      const g1 = pal[(x >> 3) % pal.length];
      const g2 = pal[(y >> 3) % pal.length];
      const t = rnd();
      const c = t > 0.5 ? g1 : g2;
      // subtle noise
      const n = (Math.floor(rnd() * 30) - 15);
      rgba[i] = clamp(c[0] + n);
      rgba[i + 1] = clamp(c[1] + n);
      rgba[i + 2] = clamp(c[2] + n);
      rgba[i + 3] = 255;
    }
  }
  // signature border
  for (let x = 0; x < size; x++) {
    for (const y of [0, size - 1]) {
      const i = (y * size + x) * 4;
      rgba[i] = 0x2e; rgba[i + 1] = 0x5c; rgba[i + 2] = 0xff; rgba[i + 3] = 255;
    }
  }
  return encodePNG(size, size, rgba);
}

function clamp(v: number): number {
  return Math.max(0, Math.min(255, v | 0));
}

// ---- build a real .mcpack zip from a source dir, generating missing textures ----
import { ZipWriter } from "./zip";

export function buildMcpack(pack: Pack): Buffer {
  const src = packSourceDir(pack);
  const zw = new ZipWriter();
  // manifest + skins already present? copy raw files
  const files = fs.existsSync(src) ? fs.readdirSync(src) : [];
  for (const f of files) {
    if (f === "manifest.json" || f.endsWith(".json")) {
      zw.add(f, fs.readFileSync(path.join(src, f)));
    }
  }
  // generate textures for skins.json references
  const skinsPath = path.join(src, "skins.json");
  if (fs.existsSync(skinsPath)) {
    const sj = JSON.parse(fs.readFileSync(skinsPath, "utf8"));
    for (const s of sj.skins || []) {
      const tex = s.texture as string;
      if (tex && !files.includes(tex)) {
        zw.add(tex, generateSkinPNG(pack.dir + ":" + tex, pack.type));
      }
    }
  } else if (!files.length) {
    // fully synthetic fallback: manifest + one generated texture
    const man = {
      format_version: 2,
      header: { name: pack.name, uuid: cryptoUUID(pack.dir), version: [1, 0, 0] },
      modules: [{ type: "skin_pack", uuid: cryptoUUID(pack.dir + "m"), version: [1, 0, 0] }],
    };
    zw.add("manifest.json", Buffer.from(JSON.stringify(man, null, 2)));
    zw.add("preview.png", generateSkinPNG(pack.dir, pack.type, 128));
  }
  // preview icon
  zw.add("pack_icon.png", generateSkinPNG(pack.dir + "icon", pack.type, 128));
  return zw.finish();
}

function cryptoUUID(seed: string): string {
  // RFC4122-ish v4 from hash
  const h = hashStr(seed);
  const hex = (h.toString(16) + (h * 2654435761).toString(16)).padEnd(32, "0").slice(0, 32);
  return [
    hex.slice(0, 8), hex.slice(8, 12), "4" + hex.slice(13, 16),
    "8" + hex.slice(17, 20), hex.slice(20, 32),
  ].join("-");
}
