import { firestoreGet, firestorePatch, jsonResponse, normalizeProject, requireAdmin } from "../_lib.js";

const STEPS = Array.from({ length: 10 }, (_, i) => i + 1);
const ACTIONS = new Set(["start", "revise", "pause", "resume", "approve", "claim", "checkpoint", "configure-destination"]);

function controlState(pid, project) {
  const s = { ...(project.factoryControl || {}) };
  s.status ||= "IDLE"; s.currentStage ||= 1; s.startStep ||= 1; s.endStep ||= 10; s.outputTarget ||= "web";
  s.version ||= String(project.currentVersion || "0.1.0"); s.queue ||= []; s.history ||= [];
  return { projectId: pid, ...s };
}

function validateRange(start, end) {
  if (!STEPS.includes(start) || !STEPS.includes(end) || start > end) throw new Error("startStep/endStep must be a valid range from 1 to 10");
}

function nextVersion(current) {
  const [major, minor] = String(current || "0.1.0").split(".").map(Number);
  return Number.isFinite(major) && Number.isFinite(minor) ? `${major}.${minor + 1}.0` : "0.2.0";
}

async function command(env, pid, data) {
  const project = await firestoreGet(env, pid);
  if (!project) return jsonResponse({ status: "not_found", error: "project not found" }, 404);
  const action = String(data.action || "").toLowerCase().trim();
  if (!ACTIONS.has(action)) return jsonResponse({ status: "invalid_request", error: `unsupported action: ${action || "missing"}` }, 400);
  const state = controlState(pid, project);
  const now = new Date().toISOString();
  const queue = [...(state.queue || [])];
  const history = [...(state.history || [])];

  if (action === "configure-destination") {
    const repo = String(data.destinationRepo || "").trim();
    const branch = String(data.destinationBranch || "main").trim() || "main";
    const productionUrl = String(data.productionUrl || "").trim();
    const previewUrl = String(data.previewUrl || "").trim();
    if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repo)) throw new Error("destinationRepo must be owner/repository");
    if (productionUrl && !/^https?:\/\//i.test(productionUrl)) throw new Error("productionUrl must be an http(s) URL");
    if (previewUrl && !/^https?:\/\//i.test(previewUrl)) throw new Error("previewUrl must be an http(s) URL");
    state.destinationRepo = repo; state.destinationBranch = branch; state.productionUrl = productionUrl; state.previewUrl = previewUrl; state.updatedAt = now;
    history.push({ action, at: now, stage: state.currentStage, status: state.status }); state.history = history.slice(-50);
    await firestorePatch(env, pid, { destinationRepo: repo, destinationBranch: branch, productionUrl, previewUrl, factoryControl: state, updatedAt: now });
    return jsonResponse({ status: "updated", factory: state });
  }

  if (action === "start" || action === "revise") {
    const start = Number(data.startStep || 1), end = Number(data.endStep || 10);
    validateRange(start, end);
    const instruction = String(data.instruction || "").trim();
    if (!instruction) throw new Error("instruction is required");
    const target = String(data.outputTarget || "web").trim().toLowerCase();
    const version = action === "revise" ? nextVersion(project.currentVersion) : String(project.currentVersion || "0.1.0");
    const item = { id: `cmd_${crypto.randomUUID().replaceAll("-", "")}`, action, instruction, startStep: start, endStep: end, outputTarget: target, version, status: "QUEUED", createdAt: now };
    queue.push(item);
    state.status = "QUEUED"; state.currentStage = start; state.startStep = start; state.endStep = end; state.outputTarget = target; state.version = version; state.queue = queue.slice(-20); state.lastCommand = item; state.updatedAt = now;
  } else if (action === "pause") {
    state.status = "PAUSED"; state.pauseReason = String(data.reason || "admin pause"); state.updatedAt = now;
  } else if (action === "resume") {
    if (state.status !== "PAUSED") throw new Error("factory is not paused");
    state.status = "RUNNING"; state.updatedAt = now;
  } else if (action === "approve") {
    state.status = "APPROVED"; state.approvedAt = now; state.updatedAt = now;
  } else if (action === "claim") {
    const pending = [...queue].reverse().find(x => x.status === "QUEUED");
    if (!pending) throw new Error("no queued factory command");
    pending.status = "RUNNING"; pending.claimedAt = now; state.status = "RUNNING"; state.lastCommand = pending; state.queue = queue; state.updatedAt = now;
  } else if (action === "checkpoint") {
    const stage = Number(data.stage || 1); validateRange(stage, stage);
    const start = Number(state.startStep || 1), end = Number(state.endStep || 10);
    if (stage < start || stage > end) throw new Error(`checkpoint stage must be between ${start} and ${end}`);
    state.status = "RUNNING"; state.currentStage = stage; state.evidence = data.evidence && typeof data.evidence === "object" ? data.evidence : {}; state.updatedAt = now;
  }
  history.push({ action, at: now, stage: state.currentStage, status: state.status }); state.history = history.slice(-50);
  await firestorePatch(env, pid, { factoryControl: state, updatedAt: now });
  return jsonResponse({ status: "updated", factory: state });
}

export async function onRequestGet({ request, env }) {
  try {
    await requireAdmin(request, env);
    const pid = new URL(request.url).searchParams.get("projectId")?.trim();
    if (!pid) return jsonResponse({ status: "invalid_request", error: "projectId is required" }, 400);
    const project = await firestoreGet(env, pid);
    if (!project) return jsonResponse({ status: "not_found", error: "project not found" }, 404);
    return jsonResponse({ status: "ok", factory: controlState(pid, normalizeProject(project)) });
  } catch (error) {
    if (error instanceof Response) return error;
    const message = String(error.message || error);
    return jsonResponse({ status: message.includes("configured") ? "persistence_error" : "error", error: message }, 503);
  }
}

export async function onRequestPost({ request, env }) {
  try {
    await requireAdmin(request, env);
    const data = await request.json();
    const pid = String(data.projectId || "").trim();
    if (!pid) return jsonResponse({ status: "invalid_request", error: "projectId is required" }, 400);
    return await command(env, pid, data);
  } catch (error) {
    if (error instanceof Response) return error;
    const message = String(error.message || error);
    const status = message.includes("project not found") ? 404 : message.includes("required") || message.includes("valid range") || message.includes("unsupported") || message.includes("paused") || message.includes("queued") || message.includes("checkpoint") || message.includes("destinationRepo") || message.includes("productionUrl") || message.includes("previewUrl") ? 400 : 503;
    return jsonResponse({ status: status === 404 ? "not_found" : status === 400 ? "invalid_request" : "persistence_error", error: message }, status);
  }
}
