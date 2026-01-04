import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import jsPDF from "jspdf";
import ReactMarkdown from "react-markdown";

// ChatGPT-style Copy Button
const CopyIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
    <path d="M5 15H4a2 2 0 0 1-2-2V4
             a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
  </svg>
);

const CheckIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

function CopyButton({ text }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1000);
  };

  return (
    <button className="floating-copy-btn" onClick={handleCopy}>
      {copied ? CheckIcon : CopyIcon}
    </button>
  );
}



const API_BASE = "http://127.0.0.1:8000";

export default function ChatPanel() {
  const [tab, setTab] = useState("chat");
  const [messages, setMessages] = useState(
    JSON.parse(localStorage.getItem("lawease_current") || "[]")
  );

  const [input, setInput] = useState("");
  const [translateInput, setTranslateInput] = useState("");
  const [fromLang, setFromLang] = useState("English");
  const [toLang, setToLang] = useState("Tamil");

  const msgRef = useRef();

  // Auto-store messages
  useEffect(() => {
    localStorage.setItem("lawease_current", JSON.stringify(messages));
  }, [messages]);

  // Scroll bottom
  useEffect(() => {
    if (msgRef.current) {
      msgRef.current.scrollTop = msgRef.current.scrollHeight;
    }
  }, [messages]);

  // System events
  useEffect(() => {
    function onNew() {
      setMessages([]);
      setInput("");
      localStorage.removeItem("lawease_current");
    }

    function onClear() {
      setMessages([]);
      setInput("");
      localStorage.removeItem("lawease_current");
    }

    function onLoad(e) {
      setMessages(e.detail.messages || []);
    }

    function onDoc(e) {
      const text = e.detail.text;
      if (text) {
        pushMessage("bot", "Extracted document text:\n" + text);
      }
    }

    window.addEventListener("lawease:newchat", onNew);
    window.addEventListener("lawease:clearmessages", onClear);
    window.addEventListener("lawease:loadconv", onLoad);
    window.addEventListener("lawease:document", onDoc);

    return () => {
      window.removeEventListener("lawease:newchat", onNew);
      window.removeEventListener("lawease:clearmessages", onClear);
      window.removeEventListener("lawease:loadconv", onLoad);
      window.removeEventListener("lawease:document", onDoc);
    };
  }, []);

  // Push message
  function pushMessage(from, text) {
    const m = { id: Date.now(), from, text };
    setMessages((prev) => [...prev, m]);
  }

  // Send chat message
  async function send() {
    if (!input.trim()) return;

    pushMessage("user", input);
    const loadingId = Date.now();
    pushMessage("bot", "Thinking...");

    const userInput = input;
    setInput("");

    try {
      const resp = await axios.post(`${API_BASE}/chat`, {
        prompt: userInput,
      });

      updateLastBotMessage(resp.data.response);
    } catch (e) {
      updateLastBotMessage("[Error] Could not reach server.");
    }
  }

  // Update last bot message (replace "Thinking...")
  function updateLastBotMessage(text) {
    setMessages((prev) => {
      const arr = [...prev];
      arr[arr.length - 1] = { id: Date.now(), from: "bot", text };
      return arr;
    });
  }

  // Translate text
  async function translate() {
    if (!translateInput.trim()) return;

    pushMessage("user", `(Translate) ${translateInput}`);
    pushMessage("bot", "Translating...");

    try {
      const resp = await axios.post(`${API_BASE}/translate`, {
        text: translateInput,
        from_lang: fromLang,
        to_lang: toLang,
      });

      updateLastBotMessage(resp.data.translation);
    } catch (e) {
      updateLastBotMessage("[Error] Translation failed.");
    }
  }

  // Save conversation
  function saveConversation() {
  const history = JSON.parse(localStorage.getItem("lawease_history") || "[]");

  // Get FIRST user message as title base
  const firstUserMessage = messages.find(m => m.from === "user")?.text?.trim() || "";

  // Generate a clean title from first message
  function generateChatTitle(text) {
    if (!text) return "New Chat";

    // Remove long sentences but allow topic visibility
    let t = text.replace(/\s+/g, " ").trim();

    // Limit to 45 chars
    if (t.length > 45) {
      t = t.substring(0, 45) + "...";
    }

    return t;
  }

  const entry = {
    title: generateChatTitle(firstUserMessage),
    messages,
    created: Date.now(),
  };

  // Save latest first (up to 50 chats)
  localStorage.setItem(
    "lawease_history",
    JSON.stringify([entry, ...history].slice(0, 50))
  );

  window.dispatchEvent(new Event("storage"));
}


  // Export PDF
  function exportPdf() {
    const doc = new jsPDF();
    let y = 12;

    doc.setFontSize(14);
    doc.text("LawEase Conversation", 12, y);
    y += 10;

    messages.forEach((m) => {
      doc.setFontSize(11);
      const prefix = m.from === "user" ? "User: " : "LawEase: ";
      const lines = doc.splitTextToSize(prefix + m.text, 180);
      doc.text(lines, 12, y);
      y += lines.length * 6 + 6;

      if (y > 270) {
        doc.addPage();
        y = 12;
      }
    });

    doc.save("conversation.pdf");
  }

  

  // Summaries
  // Summaries (Document Aware)
async function summarize(type) {
  pushMessage("user", `Please provide a ${type} summary of my uploaded document.`);
  pushMessage("bot", "Summarizing...");

  try {
    const resp = await axios.post(`${API_BASE}/summarize`, {
      type: type
    });

    updateLastBotMessage(resp.data.summary);
  } catch (e) {
    updateLastBotMessage("[Error] Summarization failed.");
  }
}


  return (
    <div className="card flex-1 flex flex-col">
      {/* TAB SWITCHER */}
      <div className="flex items-center justify-between px-2 mt-2">
        <div></div>

        <div className="flex gap-2">
          <button
            onClick={() => setTab("chat")}
            className={
              "px-3 py-1 rounded " +
              (tab === "chat"
                ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white"
                : "bg-[#1a2340]")
            }
          >
            Chat
          </button>

          <button
            onClick={() => setTab("translate")}
            className={
              "px-3 py-1 rounded " +
              (tab === "translate"
                ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white"
                : "bg-[#1a2340]")
            }
          >
            Translate
          </button>
        </div>
      </div>

      {/* MESSAGES */}
      <div ref={msgRef} className="messages mt-3">
        {messages.length === 0 && (
          <div className="message bot">
            Hello! I'm LawEase — how can I assist you today?
          </div>
        )}


      {messages.map(msg => (
  <div key={msg.id} className="msg-wrapper">

    <div className={msg.from === "bot" ? "bot-msg" : "user-msg"}>
      <ReactMarkdown>{msg.text}</ReactMarkdown>

      {/* FLOATING COPY BUTTON */}
      <CopyButton text={msg.text} />
    </div>

  </div>
))}





      </div>

      {/* TRANSLATE PANEL */}
      {tab === "translate" && (
        <div className="p-4 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-xl mt-4 border border-slate-700/50">
          <div className="flex items-center gap-3 mb-3">
            <select
              value={fromLang}
              onChange={(e) => setFromLang(e.target.value)}
              className="p-2.5 bg-slate-700/60 border border-slate-600 rounded-xl text-sm"
            >
              <option>Kannada</option>
              <option>English</option>
              <option>Hindi</option>
              <option>Tamil</option>
              <option>Spanish</option>
            </select>

            <div className="text-lg font-bold text-purple-400">⇄</div>

            <select
              value={toLang}
              onChange={(e) => setToLang(e.target.value)}
              className="p-2.5 bg-slate-700/60 border border-slate-600 rounded-xl text-sm"
            >
              <option>Kannada</option>
              <option>English</option>
              <option>Hindi</option>
              <option>Tamil</option>
              <option>Spanish</option>
            </select>
          </div>

          <textarea
            value={translateInput}
            onChange={(e) => setTranslateInput(e.target.value)}
            rows={4}
            className="w-full p-3 bg-slate-700/60 border border-slate-600 rounded-xl text-sm"
            placeholder="Enter text to translate..."
          />

          <div className="flex gap-3 mt-3">
            <button
              onClick={translate}
              className="flex-1 py-2 rounded-2xl bg-gradient-to-r from-purple-500 to-blue-600 text-white"
            >
              Translate
            </button>

            <button
              onClick={() => setTranslateInput("")}
              className="flex-1 py-2 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-500 text-white"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* CHAT INPUT BAR */}
      {tab === "chat" && (
        <div className="input mt-5 mr-2 fixed bottom-10 left-[25%] right-10 gap-5">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
            placeholder="Ask a legal question..."
          />

          <button onClick={send} className="btn mr-1">
            Send
          </button>
          <button onClick={() => summarize("short")} className="btn mr-1">
            Summarize
          </button>
          <button onClick={saveConversation} className="btn mr-1">
            Save
          </button>
          <button onClick={exportPdf} className="btn mr-1">
            Export PDF
          </button>
        </div>
      )}
    </div>
  );
}
