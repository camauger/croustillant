/** Neon / PostgreSQL pool for Netlify Functions (Node). */
import { Pool } from "@neondatabase/serverless";

let pool;

export function getPool() {
  if (!pool) {
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error("DATABASE_URL is required");
    }
    pool = new Pool({ connectionString });
  }
  return pool;
}

function normalizeRow(row) {
  if (!row) return row;
  const out = {};
  for (const [k, v] of Object.entries(row)) {
    if (typeof v === "bigint") out[k] = Number(v);
    else out[k] = v;
  }
  return out;
}

export async function queryAll(text, params = []) {
  const res = await getPool().query(text, params);
  return res.rows.map(normalizeRow);
}

export async function queryOne(text, params = []) {
  const rows = await queryAll(text, params);
  return rows[0] ?? null;
}

export async function execReturning(text, params = []) {
  const res = await getPool().query(text, params);
  if (res.rows.length === 1) return normalizeRow(res.rows[0]);
  return res.rows.map(normalizeRow);
}

export async function execCommand(text, params = []) {
  const res = await getPool().query(text, params);
  return res.rowCount ?? 0;
}
