import * as zlib from "zlib";

// Minimal ZIP writer (STORE method). .mcpack accepts stored entries.
export class ZipWriter {
  private entries: { name: string; data: Buffer }[] = [];

  add(name: string, data: Buffer) {
    this.entries.push({ name, data });
  }

  finish(): Buffer {
    const chunks: Buffer[] = [];
    const central: Buffer[] = [];
    let offset = 0;

    for (const e of this.entries) {
      const nameBuf = Buffer.from(e.name, "utf8");
      const crc = crc32(e.data);
      const local = Buffer.alloc(30);
      local.writeUInt32LE(0x04034b50, 0);
      local.writeUInt16LE(20, 4); // version needed
      local.writeUInt16LE(0, 6); // flags
      local.writeUInt16LE(0, 8); // method = store
      local.writeUInt16LE(0, 10); // time
      local.writeUInt16LE(0, 12); // date
      local.writeUInt32LE(crc, 14);
      local.writeUInt32LE(e.data.length, 18); // compressed
      local.writeUInt32LE(e.data.length, 22); // uncompressed
      local.writeUInt16LE(nameBuf.length, 26);
      local.writeUInt16LE(0, 28);
      chunks.push(local, nameBuf, e.data);

      const cen = Buffer.alloc(46);
      cen.writeUInt32LE(0x02014b50, 0);
      cen.writeUInt16LE(20, 4); // version made by
      cen.writeUInt16LE(20, 6); // version needed
      cen.writeUInt16LE(0, 8);
      cen.writeUInt16LE(0, 10); // method
      cen.writeUInt16LE(0, 12);
      cen.writeUInt16LE(0, 14);
      cen.writeUInt32LE(crc, 16);
      cen.writeUInt32LE(e.data.length, 20);
      cen.writeUInt32LE(e.data.length, 24);
      cen.writeUInt16LE(nameBuf.length, 28);
      cen.writeUInt16LE(0, 30);
      cen.writeUInt16LE(0, 32);
      cen.writeUInt16LE(0, 34);
      cen.writeUInt16LE(0, 36);
      cen.writeUInt32LE(0, 38);
      cen.writeUInt32LE(offset, 42);
      central.push(cen, nameBuf);

      offset += local.length + nameBuf.length + e.data.length;
    }

    const centralBuf = Buffer.concat(central);
    const end = Buffer.alloc(22);
    end.writeUInt32LE(0x06054b50, 0);
    end.writeUInt16LE(0, 4);
    end.writeUInt16LE(0, 6);
    end.writeUInt16LE(this.entries.length, 8);
    end.writeUInt16LE(this.entries.length, 10);
    end.writeUInt32LE(centralBuf.length, 12);
    end.writeUInt32LE(offset, 16);
    end.writeUInt16LE(0, 20);

    return Buffer.concat([...chunks, centralBuf, end]);
  }
}

function crc32(buf: Buffer): number {
  let c = ~0;
  for (let i = 0; i < buf.length; i++) {
    c ^= buf[i];
    for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1));
  }
  return ~c >>> 0;
}
