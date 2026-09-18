export const choice = (instructions, criteria) => ({ type: "choice", instructions, criteria });
export const score = (instructions, criteria) => ({ type: "score", instructions, criteria });
export const noul = (instructions, criteria) => ({
  type: "noul", instructions, ...(criteria === undefined ? {} : { criteria }),
});

export class OpenJevError extends Error {
  constructor(status, code, message) {
    super(message);
    this.name = "OpenJevError";
    this.status = status;
    this.code = code;
  }
}

export class OpenJevClient {
  constructor({ baseUrl = "http://127.0.0.1:8000", timeout = 10000 } = {}) {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
    this.timeout = timeout;
  }

  async systemOne(request) {
    const response = await fetch(`${this.baseUrl}/v1/system_one`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: AbortSignal.timeout(this.timeout),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new OpenJevError(response.status, body?.error?.code ?? "http_error",
        body?.error?.message ?? `HTTP ${response.status}`);
    }
    return response.json();
  }
}
