import { createFounderSession, getAdminKey, jsonResponse } from "../_lib.js";

export async function onRequestGet({ request, env }) {
  try {
    const expected = getAdminKey(env);
    const supplied = String(request.headers.get("X-Factory-Admin-Key") || "").trim();
    if (!supplied || supplied !== expected) return jsonResponse({ status: "unauthorized", error: "founder/admin authentication required" }, 401);
    const token = await createFounderSession(env);
    return jsonResponse({ status: "authenticated", role: "founder", sessionTtl: 3600 }, 200, {
      "Set-Cookie": `factory_session=${token}; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Strict`,
    });
  } catch (error) {
    return jsonResponse({ status: "auth_unavailable", error: String(error.message || error) }, 503);
  }
}
