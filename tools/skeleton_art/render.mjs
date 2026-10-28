// One SVG file to a PNG at a zoom, with resvg from the Loom repository's node_modules (LOOMINARY_REPO, default ../Loom beside this repository).
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const repo = process.env.LOOMINARY_REPO || path.join(here, "..", "..", "..", "Loom");
const {Resvg} = await import(path.join(repo, "node_modules", "@resvg", "resvg-js", "index.js"));
const [inp, out, zoom] = process.argv.slice(2);
fs.writeFileSync(out, new Resvg(fs.readFileSync(inp, "utf8"), {fitTo: {mode: "zoom", value: Number(zoom || 1)}}).render().asPng());
