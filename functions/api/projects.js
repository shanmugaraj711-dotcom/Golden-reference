import { firestoreGet, jsonResponse, latestProject, normalizeProject, firestorePatch, requireAdmin } from "../_lib.js";

const STATES = ["INTAKE", "BUILDING", "VERIFYING", "READY", "DELIVERED"];
const QUALITY_KEYS = ["qualityGate", "deployment", "healthCheck"];
const OWNERSHIP_KEYS = ["repository", "hosting", "handoff"];

function auditEntry(action, projectId, detail) {
  return { id: `audit_${crypto.randomUUID().replaceAll("-", "")}`, action, projectId, detail, actor: "founder", at: new Date().toISOString() };
}

function validateLifecycle(project, patch) {
  if (!Object.prototype.hasOwnProperty.call(patch, "lifecycleState")) return;
  const oldState = String(project.lifecycleState || "INTAKE").toUpperCase();
  const nextState = String(patch.lifecycleState || oldState).toUpperCase();
  if (!STATES.includes(nextState)) throw new Error("invalid lifecycleState");
  if (STATES.indexOf(nextState) < STATES.indexOf(oldState)) throw new Error("lifecycleState cannot move backwards");
  if (nextState === "READY") {
    const verification = patch.verification || project.verification || {};
    if (!QUALITY_KEYS.every(k => String(verification[k] || "PENDING").toUpperCase() === "PASSED")) {
      throw new Error("READY requires qualityGate, deployment and healthCheck to be PASSED");
    }
  }
  if (nextState === "DELIVERED") {
    if (oldState !== "READY") throw new Error("DELIVERED requires READY");
    const ownership = patch.ownership || project.ownership || {};
    if (!OWNERSHIP_KEYS.every(k => ["READY", "CONNECTED", "PASSED"].includes(String(ownership[k] || "PENDING").toUpperCase()))) {
      throw new Error("DELIVERED requires repository, hosting and handoff evidence");
    }
  }
}

export async function onRequestGet({ request, env }) {
  try {
    const url = new URL(request.url);
    const pid = url.searchParams.get("id")?.trim();
    const cid = url.searchParams.get("customerId")?.trim();
    const project = pid ? await firestoreGet(env, pid) : await latestProject(env);
    if (!project) return jsonResponse({ status: "not_found", error: "project not found" }, 404);
    if (cid && String(project.customerId || "") !== cid) return jsonResponse({ status: "unauthorized", error: "project access denied" }, 401);
    return jsonResponse({ status: "ok", project: normalizeProject(project), lifecycleStates: STATES });
  } catch (error) {
    return jsonResponse({ status: "persistence_error", error: String(error.message || error) }, 503);
  }
}

export async function onRequestPost({ request, env }) {
  try {
    await requireAdmin(request, env);
    const data = await request.json();
    const pid = String(data.projectId || "").trim();
    if (!pid) return jsonResponse({ status: "invalid_request", error: "projectId is required" }, 400);
    const project = await firestoreGet(env, pid);
    if (!project) return jsonResponse({ status: "not_found", error: "project not found" }, 404);

    const patch = {};
    for (const field of ["repository", "hostingTarget", "previewUrl", "productionUrl", "currentVersion", "lifecycleState", "nextCustomerAction"]) {
      if (field in data) patch[field] = String(data[field]);
    }
    if (data.verification && typeof data.verification === "object") patch.verification = { ...(project.verification || {}), ...data.verification };
    if (data.ownership && typeof data.ownership === "object") patch.ownership = { ...(project.ownership || {}), ...data.ownership };
    if (data.maintenance && typeof data.maintenance === "object") patch.maintenance = { ...(project.maintenance || {}), ...data.maintenance };
    if (data.deliveryEvidence && typeof data.deliveryEvidence === "object") patch.deliveryEvidence = { ...(project.deliveryEvidence || {}), ...data.deliveryEvidence };

    validateLifecycle(project, patch);

    const auditLog = [...(project.auditLog || [])];
    auditLog.push(auditEntry("project.update", pid, "Founder-controlled project state update"));
    patch.auditLog = auditLog.slice(-100);
    patch.updatedAt = new Date().toISOString();
    await firestorePatch(env, pid, patch);
    return jsonResponse({ status: "updated", project: normalizeProject({ ...project, ...patch }) });
  } catch (error) {
    if (error instanceof Response) return error;
    const message = String(error.message || error);
    const status = message.includes("project not found") ? 404 : message.includes("required") || message.includes("invalid") || message.includes("cannot move") || message.includes("requires") ? 400 : 503;
    return jsonResponse({ status: status === 404 ? "not_found" : status === 400 ? "invalid_request" : "persistence_error", error: message }, status);
  }
}
