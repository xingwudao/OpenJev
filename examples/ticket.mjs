import { readFile } from "node:fs/promises";
import { OpenJevClient } from "../sdk/js/index.js";

const request = JSON.parse(await readFile(new URL("./ticket.json", import.meta.url), "utf8"));
const client = new OpenJevClient({ baseUrl: process.argv[2] ?? "http://127.0.0.1:8000" });
console.log(JSON.stringify(await client.systemOne(request), null, 2));
