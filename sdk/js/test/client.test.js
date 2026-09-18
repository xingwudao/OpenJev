import assert from "node:assert/strict";
import { createServer } from "node:http";
import { test } from "node:test";
import { choice, score, noul, OpenJevClient, OpenJevError } from "../index.js";

test("question constructors preserve the protocol", () => {
  assert.deepEqual(choice("Pick", { a: "A", b: "B" }), {
    type: "choice", instructions: "Pick", criteria: { a: "A", b: "B" },
  });
  assert.deepEqual(score("Rate", ["Low", "High"]).criteria, ["Low", "High"]);
  assert.deepEqual(noul("True?"), { type: "noul", instructions: "True?" });
  assert.deepEqual(noul("True?", "Evidence").criteria, "Evidence");
});

test("HTTP errors, non-JSON errors and timeout", async (t) => {
  const server = createServer((req, res) => {
    if (req.url.startsWith("/slow/")) return;
    res.statusCode = req.url.startsWith("/text/") ? 502 : 422;
    res.end(res.statusCode === 502 ? "Bad gateway" : JSON.stringify({
      error: { code: "invalid_request", message: "Invalid request" },
    }));
  });
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  t.after(() => { server.closeAllConnections(); server.close(); });
  const url = `http://127.0.0.1:${server.address().port}`;
  await assert.rejects(new OpenJevClient({ baseUrl: url }).systemOne({}), error => {
    assert.ok(error instanceof OpenJevError);
    assert.equal(error.status, 422);
    assert.equal(error.code, "invalid_request");
    return true;
  });
  await assert.rejects(new OpenJevClient({ baseUrl: url + "/text" }).systemOne({}),
    { status: 502, code: "http_error" });
  await assert.rejects(new OpenJevClient({ baseUrl: url + "/slow", timeout: 20 }).systemOne({}),
    { name: "TimeoutError" });
});
