import React, { useState, useRef, useEffect, useCallback } from "react";

// ── Config ────────────────────────────────────────────────────────────────────
// In production: set to ngrok or deployment URL
// In development: falls back to http://localhost:8000 via setupProxy.js
const API_BASE = process.env.REACT_APP_API_URL ?? "http://localhost:8000";

// ── Async polling chat ────────────────────────────────────────────────────────
// Step 1: POST /chat/async  → get job_id immediately (no waiting)
// Step 2: GET  /chat/result/{job_id} every 2s until status = "done" or "error"
// This pattern is immune to tab switching because each poll is a fresh short request.
async function startChatJob(question, language) {
  const res = await fetch(`${API_BASE}/chat/async`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "true",
    },
    body: JSON.stringify({ question, language }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${res.status}`);
  }
  const { job_id } = await res.json();
  return job_id;
}

async function pollResult(jobId) {
  const res = await fetch(`${API_BASE}/chat/result/${jobId}`, {
    headers: { "ngrok-skip-browser-warning": "true" },
  });
  if (!res.ok) throw new Error(`Poll error ${res.status}`);
  return res.json();   // { status, answer, sources, error }
}

// ── Suggested questions ───────────────────────────────────────────────────────
const SUGGESTED = [
  "What is UPI and how does it work?",
  "How can I protect myself from online payment fraud?",
  "Explain the 50-30-20 budgeting rule",
  "What is PM Jan Dhan Yojana?",
  "How is EMI calculated for a loan?",
  "What is a CIBIL score and how to improve it?",
  "What government insurance schemes are available for free?",
  "What should I do if I get defrauded online?",
];

// ── Styles ────────────────────────────────────────────────────────────────────
const S = {
  app: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    background: "#f4f6fb",
  },
  header: {
    background: "#0f62fe",
    color: "#fff",
    padding: "16px 24px",
    display: "flex",
    alignItems: "center",
    gap: 14,
    boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
  },
  headerLogo: {
    width: 40,
    height: 40,
    background: "#fff",
    borderRadius: 10,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 22,
  },
  headerTitle: { fontSize: 20, fontWeight: 700 },
  headerSub: { fontSize: 12, opacity: 0.85, marginTop: 2 },
  badge: {
    marginLeft: "auto",
    background: "rgba(255,255,255,0.2)",
    border: "1px solid rgba(255,255,255,0.4)",
    borderRadius: 20,
    padding: "4px 12px",
    fontSize: 12,
    fontWeight: 600,
  },
  main: {
    flex: 1,
    maxWidth: 820,
    width: "100%",
    margin: "0 auto",
    padding: "24px 16px",
    display: "flex",
    flexDirection: "column",
    gap: 20,
  },
  suggestedGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
    gap: 10,
  },
  suggestedBtn: {
    background: "#fff",
    border: "1px solid #d0d7de",
    borderRadius: 10,
    padding: "10px 14px",
    fontSize: 13,
    color: "#0f62fe",
    cursor: "pointer",
    textAlign: "left",
    lineHeight: 1.4,
    transition: "border-color 0.15s, box-shadow 0.15s",
  },
  chatWindow: {
    flex: 1,
    background: "#fff",
    borderRadius: 14,
    border: "1px solid #e5e7eb",
    padding: "20px 20px 0",
    minHeight: 380,
    maxHeight: 480,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  emptyState: {
    margin: "auto",
    textAlign: "center",
    color: "#57606a",
    padding: "40px 20px",
  },
  emptyIcon: { fontSize: 48, marginBottom: 12 },
  emptyTitle: { fontSize: 18, fontWeight: 600, marginBottom: 6 },
  emptyText: { fontSize: 14, lineHeight: 1.6 },
  msgRow: (role) => ({
    display: "flex",
    justifyContent: role === "user" ? "flex-end" : "flex-start",
    gap: 10,
    alignItems: "flex-start",
  }),
  avatar: (role) => ({
    width: 32,
    height: 32,
    borderRadius: "50%",
    background: role === "user" ? "#0f62fe" : "#198038",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 14,
    fontWeight: 700,
    flexShrink: 0,
    marginTop: 2,
  }),
  bubble: (role) => ({
    maxWidth: "75%",
    background: role === "user" ? "#0f62fe" : "#f0f4ff",
    color: role === "user" ? "#fff" : "#1f2328",
    borderRadius: role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
    padding: "12px 16px",
    fontSize: 14,
    lineHeight: 1.65,
    border: role === "user" ? "none" : "1px solid #d0d7de",
  }),
  sources: {
    marginTop: 8,
    paddingTop: 8,
    borderTop: "1px solid #d0d7de",
    fontSize: 11,
    color: "#57606a",
    display: "flex",
    flexWrap: "wrap",
    gap: 6,
  },
  sourceTag: {
    background: "#e8f0fe",
    color: "#0f62fe",
    borderRadius: 12,
    padding: "2px 8px",
    fontWeight: 500,
  },
  typingDot: {
    display: "inline-block",
    width: 8,
    height: 8,
    background: "#57606a",
    borderRadius: "50%",
    margin: "0 2px",
    animation: "bounce 1.2s infinite",
  },
  inputRow: {
    display: "flex",
    gap: 10,
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 12,
    padding: "10px 14px",
    alignItems: "flex-end",
  },
  textarea: {
    flex: 1,
    border: "none",
    outline: "none",
    fontSize: 14,
    resize: "none",
    fontFamily: "inherit",
    lineHeight: 1.5,
    color: "#1f2328",
    background: "transparent",
    minHeight: 24,
    maxHeight: 120,
  },
  langToggle: {
    display: "flex",
    gap: 6,
    alignItems: "center",
    fontSize: 12,
    color: "#57606a",
  },
  langBtn: (active) => ({
    padding: "4px 10px",
    borderRadius: 20,
    border: "1px solid",
    borderColor: active ? "#0f62fe" : "#d0d7de",
    background: active ? "#e8f0fe" : "transparent",
    color: active ? "#0f62fe" : "#57606a",
    fontSize: 12,
    cursor: "pointer",
    fontWeight: active ? 600 : 400,
  }),
  sendBtn: (disabled) => ({
    width: 38,
    height: 38,
    borderRadius: 10,
    background: disabled ? "#d0d7de" : "#0f62fe",
    border: "none",
    cursor: disabled ? "not-allowed" : "pointer",
    color: "#fff",
    fontSize: 18,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    transition: "background 0.15s",
  }),
  footer: {
    textAlign: "center",
    padding: "16px 0 20px",
    fontSize: 12,
    color: "#8b949e",
    borderTop: "1px solid #e5e7eb",
    marginTop: 8,
  },
};

// ── Component ─────────────────────────────────────────────────────────────────
export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("english");
  const [showSuggested, setShowSuggested] = useState(true);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);
  // pollRef holds the setInterval id so we can clear it
  const pollRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Cleanup: clear polling interval on unmount
  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  const sendMessage = useCallback(async (question) => {
    const q = (question || input).trim();
    if (!q || loading) return;

    // Clear any previous poll
    if (pollRef.current) clearInterval(pollRef.current);

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setInput("");
    setLoading(true);
    setShowSuggested(false);

    try {
      // Step 1: submit job — returns immediately with a job_id
      const jobId = await startChatJob(q, language);

      // Step 2: poll every 2 seconds for the result
      // Each poll is a tiny GET request — totally unaffected by tab switching
      pollRef.current = setInterval(async () => {
        try {
          const result = await pollResult(jobId);
          if (result.status === "done") {
            clearInterval(pollRef.current);
            setMessages((prev) => [
              ...prev,
              { role: "ai", text: result.answer, sources: result.sources },
            ]);
            setLoading(false);
          } else if (result.status === "error") {
            clearInterval(pollRef.current);
            setMessages((prev) => [
              ...prev,
              { role: "ai", text: "Sorry, an error occurred: " + result.error, sources: [] },
            ]);
            setLoading(false);
          }
          // if "pending", just wait for next poll
        } catch (pollErr) {
          // network blip during poll — just wait and try again next interval
        }
      }, 2000);

    } catch (err) {
      const errMsg = err.message || "Sorry, could not reach the server. Make sure the backend is running.";
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "Sorry: " + errMsg, sources: [] },
      ]);
      setLoading(false);
    }
  }, [input, language, loading]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={S.app}>
      {/* ── Header ── */}
      <header style={S.header}>
        <div style={S.headerLogo}>💰</div>
        <div>
          <div style={S.headerTitle}>FinSathi AI</div>
          <div style={S.headerSub}>Your Digital Financial Literacy Assistant</div>
        </div>
        <div style={S.badge}>Powered by IBM Granite</div>
      </header>

      <main style={S.main}>
        {/* ── Suggested questions ── */}
        {showSuggested && (
          <div>
            <p style={{ fontSize: 13, color: "#57606a", marginBottom: 10 }}>
              💡 <strong>Try asking:</strong>
            </p>
            <div style={S.suggestedGrid}>
              {SUGGESTED.map((q) => (
                <button
                  key={q}
                  style={S.suggestedBtn}
                  onClick={() => sendMessage(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ── Chat window ── */}
        <div style={S.chatWindow}>
          {messages.length === 0 && !loading ? (
            <div style={S.emptyState}>
              <div style={S.emptyIcon}>🇮🇳</div>
              <div style={S.emptyTitle}>Namaste! I'm FinSathi AI</div>
              <div style={S.emptyText}>
                Ask me anything about UPI, digital payments, budgeting,
                loans, government schemes, or online fraud prevention.
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <div key={i} style={S.msgRow(msg.role)}>
                  <div style={S.avatar(msg.role)}>
                    {msg.role === "user" ? "U" : "AI"}
                  </div>
                  <div style={S.bubble(msg.role)}>
                    {msg.text}
                    {msg.sources && msg.sources.length > 0 && (
                      <div style={S.sources}>
                        <span>Sources:</span>
                        {msg.sources.map((s) => (
                          <span key={s} style={S.sourceTag}>{s}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div style={S.msgRow("ai")}>
                  <div style={S.avatar("ai")}>AI</div>
                  <div style={S.bubble("ai")}>
                    <span style={S.typingDot} />
                    <span style={{ ...S.typingDot, animationDelay: "0.2s" }} />
                    <span style={{ ...S.typingDot, animationDelay: "0.4s" }} />
                    <span style={{ fontSize: 11, color: "#57606a", marginLeft: 10 }}>
                      Thinking... (you can switch tabs safely)
                    </span>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={bottomRef} />
        </div>

        {/* ── Language toggle + Input ── */}
        <div>
          <div style={{ ...S.langToggle, marginBottom: 8 }}>
            <span>Language:</span>
            <button style={S.langBtn(language === "english")} onClick={() => setLanguage("english")}>English</button>
            <button style={S.langBtn(language === "hindi")} onClick={() => setLanguage("hindi")}>हिंदी</button>
          </div>
          <div style={S.inputRow}>
            <textarea
              ref={textareaRef}
              style={S.textarea}
              rows={1}
              placeholder={
                language === "hindi"
                  ? "अपना वित्तीय प्रश्न यहाँ लिखें..."
                  : "Ask about UPI, loans, savings, government schemes..."
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button
              style={S.sendBtn(!input.trim() || loading)}
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              title="Send"
            >
              ➤
            </button>
          </div>
          <p style={{ fontSize: 11, color: "#8b949e", marginTop: 6, textAlign: "center" }}>
            Press Enter to send · Shift+Enter for new line
          </p>
        </div>
      </main>

      {/* ── Footer ── */}
      <footer style={S.footer}>
        FinSathi AI · Built with IBM Granite &amp; watsonx.ai · For educational purposes only
      </footer>

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
}
