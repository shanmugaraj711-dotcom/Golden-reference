import { firestoreGet, jsonResponse, latestProject, normalizeProject, firestorePatch } from "../_lib.js";

export async function onRequestGet({ request, env }) {
  try {
    const url = new URL(request.url);
    const pid = url.searchParams.get("id")?.trim();
    const cid = url.searchParams.get("customerId")?.trim();
    const project = pid ? await firestoreGet(env, pid) : await latestProject(env);
    if (!project) return jsonResponse({ status: "not_found", error: "project not found" }, 404);
    if (cid && String(project.customerId || "") !== cid) return jsonResponse({ status: "unauthorized", error: "project access denied" }, 401);
    return jsonResponse({ status: "ok", project: normalizeProject(project), lifecycleStates: ["INTAKE", "BUILDING", "VERIFYING", "READY", "DELIVERED"] });
  } catch (error) {
    return jsonResponse({ status: "persistence_error", error: String(error.message || error) }, 503);
  }
}

export async function onRequestPost({ request, env }) {
  try {
    const data = await request.json();
    const pid = String(data.projectId || "").trim();
    if (!pid) return jsonResponse({ status: "invalid_request", error: "projectId is required" }, 400);
    const project = await firestoreGet(env, pid);
    if (!project) return jsonResponse({ status: "not_found", error: "project not found" }, 404);
    const patch = {};
    for (const field of ["repository", "hostingTarget", "previewUrl", "productionUrl", "currentVersion", "lifecycleState", "nextCustomerAction"]) if (field in data) patch[field] = String(data[field]);
    if (data.verification && typeof data.verification === "object") patch.verification = { ...(project.verification || {}), ...data.verification };
    if (data.ownership && typeof data.ownership === "object") patch.ownership = { ...(project.ownership || {}), ...data.ownership };
    if (data.maintenance && typeof data.maintenance === "object") patch.maintenance = { ...(project.maintenance || {}), ...data.maintenance };
    patch.updatedAt = new Date().toISOString();
    await firestorePatch(env, pid, patch);
    return jsonResponse({ status: "updated", project: normalizeProject({ ...project, ...patch }) });
  } catch (error) {
    return jsonResponse({ status: "persistence_error", error: String(error.message || error) }, 503);
  }
}
