const BACKEND = "https://mr-rithish-rag-backend.hf.space";
let sessionId = null;  // store session ID here

// ---- Get session on page load ----
async function initSession() {
    const res = await fetch(`${BACKEND}/session`);
    const data = await res.json();
    sessionId = data.session_id;
    console.log("Session created:", sessionId);
}

// call immediately when page loads
initSession();

// Upload logic
const uploadBox = document.getElementById("uploadBox");
const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

uploadBox.addEventListener("click", () => fileInput.click());
uploadBox.addEventListener("dragover", e => { e.preventDefault(); uploadBox.style.borderColor = "#111"; });
uploadBox.addEventListener("dragleave", () => uploadBox.style.borderColor = "#ddd");
uploadBox.addEventListener("drop", e => {
    e.preventDefault();
    fileInput.files = e.dataTransfer.files;
    handleFiles();
});

fileInput.addEventListener("change", handleFiles);

function handleFiles() {
    fileList.innerHTML = "";
    const files = Array.from(fileInput.files);
    files.forEach(f => {
        const tag = document.createElement("div");
        tag.className = "file-tag";
        tag.textContent = f.name;
        fileList.appendChild(tag);
    });
    uploadBtn.disabled = files.length === 0;
}

uploadBtn.addEventListener("click", async () => {
    const formData = new FormData();
    Array.from(fileInput.files).forEach(f => formData.append("files", f));
    // formData.append("session_id", sessionId);  // attach session ID

    uploadBtn.disabled = true;
    uploadStatus.textContent = "Processing...";

    try {
        const res = await fetch(`${BACKEND}/upload?session_id=${sessionId}`, { method: "POST", body: formData });
        if (!res.ok) {
            const err = await res.json();
            uploadStatus.textContent = "❌ " + (err.detail || "Upload failed");
            uploadBtn.disabled = false;
            return;
        }
        const data = await res.json();
        uploadStatus.textContent = "✅ " + data.message;
        document.getElementById("chatSection").style.display = "block";
    } catch (err) {
        uploadStatus.textContent = "❌ Upload failed: " + err.message;
    }
    uploadBtn.disabled = false;
});

// Chat logic
const chatBox = document.getElementById("chatBox");
const questionInput = document.getElementById("questionInput");
const askBtn = document.getElementById("askBtn");

askBtn.addEventListener("click", sendQuestion);
questionInput.addEventListener("keydown", e => { if (e.key === "Enter") sendQuestion(); });

async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    addMessage("user", question);
    questionInput.value = "";
    askBtn.disabled = true;

    try {
        const res = await fetch(`${BACKEND}/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, session_id: sessionId })  // attach session ID
        });
        const data = await res.json();
        addMessage("bot", data.answer, data.sources);
    } catch (err) {
        addMessage("bot", "❌ Error: " + err.message);
    }
    askBtn.disabled = false;
}

function addMessage(role, text, sources = []) {
    const msg = document.createElement("div");
    msg.className = `message ${role}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    msg.appendChild(bubble);

    if (sources.length > 0) {
        const src = document.createElement("div");
        src.className = "sources";
        src.textContent = "Sources: " + sources.join(" · ");
        msg.appendChild(src);
    }

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// cleanup session when user leaves
window.addEventListener("beforeunload", () => {
    if (sessionId) {
        navigator.sendBeacon(`${BACKEND}/session/${sessionId}`, "");
    }
});