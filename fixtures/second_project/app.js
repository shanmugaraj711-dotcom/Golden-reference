const STORAGE_KEY = "factory-second-project.tasks";
const form = document.getElementById("task-form");
const input = document.getElementById("task-input");
const list = document.getElementById("task-list");
const empty = document.getElementById("empty-state");
const clear = document.getElementById("clear-completed");

function loadTasks() {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(value) ? value.filter(t => t && typeof t.text === "string" && typeof t.done === "boolean") : [];
  } catch (_) { return []; }
}

let tasks = loadTasks();
function save() { localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks)); }
function render() {
  list.replaceChildren();
  empty.hidden = tasks.length !== 0;
  for (const task of tasks) {
    const li = document.createElement("li");
    const toggle = document.createElement("button");
    toggle.type = "button"; toggle.textContent = task.done ? "Undo" : "Done";
    toggle.onclick = () => { task.done = !task.done; save(); render(); };
    const text = document.createElement("span"); text.textContent = task.text;
    if (task.done) text.className = "done";
    const remove = document.createElement("button");
    remove.type = "button"; remove.textContent = "Delete";
    remove.onclick = () => { tasks = tasks.filter(t => t.id !== task.id); save(); render(); };
    li.append(toggle, text, remove); list.append(li);
  }
}
form.addEventListener("submit", event => {
  event.preventDefault(); const text = input.value.trim(); if (!text) return;
  tasks.push({ id: crypto.randomUUID(), text, done: false }); input.value = ""; save(); render();
});
clear.addEventListener("click", () => { tasks = tasks.filter(t => !t.done); save(); render(); });
render();
