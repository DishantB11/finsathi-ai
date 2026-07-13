import React, { useState, useRef, useEffect, useCallback } from "react";

const API_BASE = process.env.REACT_APP_API_URL ?? "http://localhost:8000";

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

  if (!res.ok) {
    throw new Error(`Poll error ${res.status}`);
  }

  return res.json();
}

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

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("english");
  const [showSuggested, setShowSuggested] = useState(true);
  const bottomRef = useRef(null);
  const pollRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const sendMessage = useCallback(
    async (question) => {
      const q = (question || input).trim();
      if (!q || loading) return;

      if (pollRef.current) clearInterval(pollRef.current);

      setMessages((prev) => [...prev, { role: "user", text: q }]);
      setInput("");
      setLoading(true);
      setShowSuggested(false);

      try {
        const jobId = await startChatJob(q, language);

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
                {
                  role: "ai",
                  text: "Sorry, an error occurred: " + result.error,
                  sources: [],
                },
              ]);
              setLoading(false);
            }
          } catch (pollErr) {
            // Keep polling through brief network interruptions.
          }
        }, 2000);
      } catch (err) {
        const errMsg =
          err.message ||
          "Sorry, could not reach the server. Make sure the backend is running.";
        setMessages((prev) => [
          ...prev,
          { role: "ai", text: "Sorry: " + errMsg, sources: [] },
        ]);
        setLoading(false);
      }
    },
    [input, language, loading]
  );

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">FS</div>
          <div>
            <div className="brand-title">FinSathi AI</div>
            <div className="brand-subtitle">
              Digital financial literacy assistant for India
            </div>
          </div>
        </div>
        <div className="status-pill">IBM Granite powered</div>
      </header>

      <main className="workspace">
        <aside className="sidebar">
          <section>
            <div className="eyebrow">Financial guidance</div>
            <h1>Simple answers for everyday money decisions.</h1>
            <p>
              Ask about UPI, savings, fraud safety, loans, budgeting, and
              government schemes in clear English or Hindi.
            </p>
          </section>

          <section className="insight-grid" aria-label="Highlights">
            <div className="insight-card">
              <strong>24/7</strong>
              <span>Ready whenever the app is awake</span>
            </div>
            <div className="insight-card">
              <strong>INR</strong>
              <span>India-first financial context</span>
            </div>
          </section>

          {showSuggested && (
            <section>
              <div className="section-title">Try a question</div>
              <div className="suggested-list">
                {SUGGESTED.map((q) => (
                  <button
                    className="suggested-button"
                    key={q}
                    onClick={() => sendMessage(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </section>
          )}
        </aside>

        <section className="chat-panel" aria-label="FinSathi chat">
          <div className="chat-header">
            <div>
              <div className="chat-title">Conversation</div>
              <div className="chat-subtitle">
                Educational guidance, not personal investment advice
              </div>
            </div>
            <div className="language-toggle" aria-label="Language">
              <button
                className={language === "english" ? "active" : ""}
                onClick={() => setLanguage("english")}
              >
                English
              </button>
              <button
                className={language === "hindi" ? "active" : ""}
                onClick={() => setLanguage("hindi")}
              >
                Hindi
              </button>
            </div>
          </div>

          <div className="chat-window">
            {messages.length === 0 && !loading ? (
              <div className="empty-state">
                <div className="empty-mark">INR</div>
                <h2>Namaste, I am ready when you are.</h2>
                <p>
                  Start with a money question, or pick one from the sidebar. I
                  will keep the answer practical, structured, and easy to act on.
                </p>
              </div>
            ) : (
              <>
                {messages.map((msg, i) => (
                  <div className={`message-row ${msg.role}`} key={`${msg.role}-${i}`}>
                    {msg.role !== "user" && <div className="avatar">AI</div>}
                    <div className={`message-bubble ${msg.role}`}>
                      <div className="message-text">{msg.text}</div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="sources">
                          <span>Sources</span>
                          {msg.sources.map((s) => (
                            <span className="source-tag" key={s}>
                              {s}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="message-row ai">
                    <div className="avatar">AI</div>
                    <div className="message-bubble ai typing">
                      <span />
                      <span />
                      <span />
                      <em>Thinking through your question...</em>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="composer">
            <div className="input-card">
              <textarea
                rows={1}
                placeholder={
                  language === "hindi"
                    ? "Apna financial question yahan likhen..."
                    : "Ask about UPI, fraud safety, savings, loans, schemes..."
                }
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <button
                className="send-button"
                onClick={() => sendMessage()}
                disabled={!input.trim() || loading}
                title="Send"
              >
                Send
              </button>
            </div>
            <div className="helper-text">
              Press Enter to send. Use Shift + Enter for a new line.
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        FinSathi AI - built for financial literacy and education.
      </footer>
    </div>
  );
}
