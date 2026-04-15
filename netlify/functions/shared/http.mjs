/** Shared JSON / CORS helpers for Lambda-compatible handlers. */

const cors = {
  "Content-Type": "application/json; charset=utf-8",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
};

export function json(statusCode, body) {
  return {
    statusCode,
    headers: cors,
    body: JSON.stringify(body),
  };
}

export function err(statusCode, message, extra = {}) {
  return json(statusCode, { success: false, error: message, ...extra });
}
