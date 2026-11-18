const message = document.getElementById("message");
const counter = document.getElementById("counter");
const analyzeBtn = document.getElementById("analyzeBtn");
const emptyState = document.getElementById("emptyState");
const report = document.getElementById("report");
const loading = document.getElementById("loading");

message.addEventListener("input", () => counter.textContent = `${message.value.length.toLocaleString()} / 5,000`);
document.getElementById("clearBtn").addEventListener("click", () => {
  message.value = ""; counter.textContent = "0 / 5,000"; message.focus();
});
document.querySelectorAll("[data-example]").forEach(btn => btn.addEventListener("click", () => {
  const examples = {
    safe: "Hi, the project meeting is scheduled for tomorrow at 10 AM in the college seminar hall. Please bring your notes.",
    scam: "Congratulations! You are selected as our lucky winner and have won a cash prize. Claim your reward now by paying a small processing fee. Offer expires today!",
    otp: "URGENT: Your bank account will be blocked today. Verify your account immediately by sharing your OTP and password with our support team."
  };
  message.value = examples[btn.dataset.example]; counter.textContent = `${message.value.length} / 5,000`;
}));

analyzeBtn.addEventListener("click", async () => {
  if (!message.value.trim()) { message.focus(); return; }
  analyzeBtn.disabled = true; emptyState.hidden = true; report.hidden = true; loading.hidden = false;
  try {
    const response = await fetch("/api/analyze", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({message: message.value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed.");
    showReport(data);
  } catch (error) {
    emptyState.hidden = false;
    emptyState.querySelector("h3").textContent = "Could not analyze";
    emptyState.querySelector("p").textContent = error.message;
  } finally {
    loading.hidden = true; analyzeBtn.disabled = false;
  }
});

function showReport(data) {
  report.hidden = false;
  document.getElementById("verdict").textContent = data.verdict;
  document.getElementById("score").textContent = data.risk_score;
  const fill = document.getElementById("meterFill");
  fill.style.width = `${data.risk_score}%`;
  fill.style.background = data.level === "high" ? "#ff727e" : data.level === "medium" ? "#ffc56c" : "#55dfd0";
  document.querySelector(".score strong").style.color = fill.style.background;
  document.getElementById("signals").replaceChildren(...data.signals.map(x => makeLi(x)));
  document.getElementById("recommendations").replaceChildren(...data.recommendations.map(x => makeLi(x)));
  const urlSection = document.getElementById("urlSection");
  const urlResults = document.getElementById("urlResults");
  urlResults.replaceChildren();
  urlSection.hidden = !data.urls.length;
  data.urls.forEach(u => {
    const card = document.createElement("div"); card.className = "url-card";
    const title = document.createElement("b"); title.textContent = u.host;
    const details = document.createElement("div"); details.textContent = u.flags.length ? u.flags.join(" · ") : "No simple URL red flags detected";
    card.append(title, details); urlResults.append(card);
  });
  document.getElementById("modelNote").textContent = `Text model signal: ${data.model_score}/100 · Combined score also considers transparent rules and URL indicators.`;
  document.getElementById("disclaimer").textContent = data.disclaimer;
}
function makeLi(text) { const li = document.createElement("li"); li.textContent = text; return li; }
