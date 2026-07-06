const queryInput = document.getElementById("query-input");
const charCount = document.getElementById("char-count");
const askBtn = document.getElementById("ask-btn");
const spine = document.getElementById("spine");
const result = document.getElementById("result");
const resultActions = document.getElementById("result-actions");
const copyBtn = document.getElementById("copy-btn");
const pdfBtn = document.getElementById("pdf-btn");
const toast = document.getElementById("toast");
const themeToggle = document.getElementById("theme-toggle");
const topics = document.getElementById("topics");

let lastAnswer = { markdown: "", query: "" };

/* ---------- Theme ---------- */

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("quanta-theme", theme);
}

(function initTheme() {
  const saved = localStorage.getItem("quanta-theme");
  const preferred = saved || (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  applyTheme(preferred);
})();

themeToggle.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");
  applyTheme(current === "dark" ? "light" : "dark");
});

/* ---------- Character count ---------- */

queryInput.addEventListener("input", () => {
  charCount.textContent = `${queryInput.value.length} / 2000`;
});

/* ---------- Topic chips ---------- */

topics.addEventListener("click", (e) => {
  const chip = e.target.closest(".chip");
  if (!chip) return;
  queryInput.value = `Explain ${chip.dataset.topic} and its current real-world applications.`;
  charCount.textContent = `${queryInput.value.length} / 2000`;
  queryInput.focus();
});

/* ---------- Toast ---------- */

let toastTimer;
function showToast(message, isError = false) {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
}

/* ---------- Ask Quanta ---------- */

async function askQuanta() {
  const query = queryInput.value.trim();
  if (!query) {
    showToast("Type a question first.", true);
    queryInput.focus();
    return;
  }

  askBtn.disabled = true;
  askBtn.classList.add("loading");
  spine.classList.remove("done");
  spine.classList.add("thinking");
  resultActions.hidden = true;

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();

    if (!res.ok) {
      result.innerHTML = `<div class="result-empty"><p class="result-empty-title">Couldn't get an answer</p><p class="result-empty-sub">${escapeHtml(data.error || "Unknown error.")}</p></div>`;
      spine.classList.remove("thinking");
      showToast(data.error || "Something went wrong.", true);
      return;
    }

    lastAnswer = { markdown: data.markdown, query: data.query };
    result.innerHTML = `<div class="result-content">${data.html}</div>`;
    resultActions.hidden = false;
    spine.classList.remove("thinking");
    spine.classList.add("done");
  } catch (err) {
    result.innerHTML = `<div class="result-empty"><p class="result-empty-title">Couldn't reach the server</p><p class="result-empty-sub">Check that the Flask app is running.</p></div>`;
    spine.classList.remove("thinking");
    showToast("Network error.", true);
  } finally {
    askBtn.disabled = false;
    askBtn.classList.remove("loading");
  }
}

askBtn.addEventListener("click", askQuanta);
queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
    e.preventDefault();
    askQuanta();
  }
});

/* ---------- Copy answer ---------- */

copyBtn.addEventListener("click", async () => {
  if (!lastAnswer.markdown) return;
  try {
    await navigator.clipboard.writeText(lastAnswer.markdown);
    showToast("Answer copied to clipboard.");
  } catch {
    showToast("Couldn't copy — try selecting the text manually.", true);
  }
});

/* ---------- Download PDF ---------- */

pdfBtn.addEventListener("click", async () => {
  if (!lastAnswer.markdown) return;
  pdfBtn.disabled = true;
  pdfBtn.textContent = "Preparing PDF…";
  try {
    const res = await fetch("/api/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastAnswer),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || "PDF generation failed.");
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(lastAnswer.query || "research-report").slice(0, 40)}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showToast("PDF downloaded.");
  } catch (err) {
    showToast(err.message, true);
  } finally {
    pdfBtn.disabled = false;
    pdfBtn.textContent = "Download PDF";
  }
});

/* ---------- Utils ---------- */

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
