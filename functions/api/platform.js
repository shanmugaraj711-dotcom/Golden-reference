import { jsonResponse, enforceSoftRateLimit, verifyCustomerToken, firestoreGet, firestorePatch, customerConfig } from "../_lib.js";

export async function onRequestGet({ request, env }) {
  try {
    enforceSoftRateLimit(request, env, "platform-read");
    const url = new URL(request.url);

    if (url.searchParams.get("check") === "1") {
      const production = String(env.PRODUCTION_HEALTH_URL || "").trim();
      let health = { configured: Boolean(production), status: "NOT_CONFIGURED" };
      if (production) {
        const started = Date.now();
        try {
          const response = await fetch(production, { method: "GET", redirect: "follow" });
          health = {
            configured: true,
            status: response.ok ? "PASSED" : "FAILED",
            httpStatus: response.status,
            latencyMs: Date.now() - started,
          };
        } catch (error) {
          health = {
            configured: true,
            status: "FAILED",
            error: String(error.message || error),
            latencyMs: Date.now() - started,
          };
        }
      }
      return jsonResponse({
        status: "ok",
        capabilities: {
          customerAuth: Boolean(env.FIREBASE_WEB_API_KEY && env.FIREBASE_PROJECT_ID),
          rateLimit: true,
          healthCheck: health,
          localModel: Boolean(env.LOCAL_MODEL_URL),
          billing: Boolean(env.STRIPE_SECRET_KEY && env.STRIPE_PRICE_ID),
          support: true,
          managedChanges: true,
        },
      });
    }

    return jsonResponse({ status: "ok", firebase: customerConfig(env) });
  } catch (error) {
    return jsonResponse({ status: "error", error: String(error.message || error) }, 503);
  }
}

export async function onRequestPost({ request, env }) {
  try {
    enforceSoftRateLimit(request, env, "platform-write");
    const data = await request.json();
    const action = String(data.action || "").toLowerCase();

    if (action === "local_model") {
      const endpoint = String(env.LOCAL_MODEL_URL || "").trim();
      if (!endpoint) {
        return jsonResponse({ status: "not_configured", error: "LOCAL_MODEL_URL is not configured" }, 503);
      }
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: data.model || env.LOCAL_MODEL_NAME || "local",
          messages: Array.isArray(data.messages) ? data.messages : [],
          temperature: data.temperature ?? 0.2,
        }),
      });
      const text = await response.text();
      return new Response(text, {
        status: response.status,
        headers: {
          "Content-Type": response.headers.get("Content-Type") || "application/json",
          "Cache-Control": "no-store",
        },
      });
    }

    if (action === "billing_status") {
      const configured = Boolean(env.STRIPE_SECRET_KEY && env.STRIPE_PRICE_ID);
      return jsonResponse({
        status: "ok",
        configured,
        message: configured ? "Billing provider configured" : "Billing provider credentials are not configured",
      });
    }

    if (action === "checkout") {
      if (!env.STRIPE_SECRET_KEY || !env.STRIPE_PRICE_ID) {
        return jsonResponse({ status: "not_configured", error: "Billing is not configured" }, 503);
      }

      const user = await verifyCustomerToken(request, env);
      const origin = new URL(request.url).origin;
      const form = new URLSearchParams({
        mode: "payment",
        "line_items[0][price]": String(env.STRIPE_PRICE_ID),
        "line_items[0][quantity]": "1",
        success_url: `${origin}/portal.html?billing=success`,
        cancel_url: `${origin}/portal.html?billing=cancelled`,
        client_reference_id: user.uid,
      });

      const response = await fetch("https://api.stripe.com/v1/checkout/sessions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: form,
      });
      const result = await response.json();
      if (!response.ok) {
        return jsonResponse({ status: "billing_error", error: result.error?.message || "Stripe checkout failed" }, 502);
      }
      return jsonResponse({ status: "ok", url: result.url });
    }

    if (action === "support") {
      const user = await verifyCustomerToken(request, env);
      const projectId = String(data.projectId || "").trim();
      const text = String(data.message || "").trim();
      if (!projectId || !text) {
        return jsonResponse({ status: "invalid_request", error: "projectId and message are required" }, 400);
      }

      const project = await firestoreGet(env, projectId);
      if (!project || String(project.customerId) !== String(user.uid)) {
        return jsonResponse({ status: "unauthorized", error: "project access denied" }, 401);
      }

      const requests = [...(project.changeRequests || [])];
      requests.push({
        id: `support_${crypto.randomUUID().replaceAll("-", "")}`,
        request: `SUPPORT: ${text}`,
        status: "OPEN",
        priority: String(data.priority || "NORMAL").toUpperCase(),
        version: String(project.currentVersion || "0.1.0"),
        customerId: user.uid,
        userId: user.uid,
        createdAt: new Date().toISOString(),
      });

      await firestorePatch(env, projectId, {
        changeRequests: requests.slice(-50),
        nextCustomerAction: "Support request received",
        updatedAt: new Date().toISOString(),
      });
      return jsonResponse({ status: "created", message: "Support request received" }, 201);
    }

    return jsonResponse({ status: "invalid_request", error: "unknown platform action" }, 400);
  } catch (error) {
    if (error instanceof Response) return error;
    return jsonResponse({ status: "error", error: String(error.message || error) }, 503);
  }
}
