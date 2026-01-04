import React, { useEffect, useState } from 'react';
import axios from 'axios';
import logo from "../assets/logo3.png";

export default function LeftPanel({ onThemeToggle, theme }) {

  const [history, setHistory] = useState(JSON.parse(localStorage.getItem('lawease_history') || '[]'));
  const [selectedFile, setSelectedFile] = useState(null);  // ✅ Added state

  useEffect(() => {
    const ev = () => setHistory(JSON.parse(localStorage.getItem('lawease_history') || '[]'));
    window.addEventListener('storage', ev);
    return () => window.removeEventListener('storage', ev);
  }, []);

  function newChat() {
    localStorage.removeItem('lawease_current');
    window.dispatchEvent(new CustomEvent('lawease:newchat'));
  }

  function clearChat() {
    localStorage.removeItem('lawease_current');
    window.dispatchEvent(new CustomEvent('lawease:clearmessages'));
  }

  function clearHistory() {
    localStorage.removeItem('lawease_history');
    setHistory([]);
  }

  async function handleFile(e) {
  const f = e.target.files[0];
  if (!f) return;

  setSelectedFile(f);

  const fd = new FormData();
  fd.append('file', f);

  try {
    const r = await axios.post(
      'http://127.0.0.1:8000/upload-document',
      fd,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

    // Dispatch to update other components
    window.dispatchEvent(new CustomEvent('lawease:document', { detail: r.data }));

    // No alert — silent success
    console.log("Document uploaded successfully:", r.data);

  } catch (err) {
    // No alert on error — just log
    console.error("Upload failed:", err);
  }
}

  function loadConversation(idx) {
    const h = JSON.parse(localStorage.getItem('lawease_history') || '[]');
    const conv = h[idx];
    if (conv) window.dispatchEvent(new CustomEvent('lawease:loadconv', { detail: conv }));
  }

  return (
    <div className='card p-4 shadow-lg border border-white/10'>
      
      {/* Logo + Title */}
      <div className="flex items-center gap-3 mb-6">
        <img 
          src={logo} 
          alt="LawEase Logo" 
          className="w-24 h-24 rounded-3xl shadow-lg"
        />

        <div>
          <h1 className="text-4xl font-bold text-indigo-400 drop-shadow-[0_0_8px_rgba(99,102,241,0.6)]">
            LawEase
          </h1>
          <p className="mt-1 ml-3 text-xs text-indigo-400 drop-shadow-[0_0_8px_rgba(99,102,241,0.6)]">
            Legal Assistant
          </p>
        </div>
      </div>

      {/* Upload Section */}
<div className="space-y-3 mb-4">
  
  {/* Upload Box */}
  <label className="w-full cursor-pointer group">
    <div className="bg-[#1f2650] border-2 border-dashed border-indigo-400/40 group-hover:border-indigo-300
                    text-indigo-200 rounded-xl p-4 shadow-md flex flex-col items-center justify-center 
                    transition-all">

      <span className="font-semibold text-indigo-300 text-sm tracking-wide">
        Click to Upload Document
      </span>

      <p className="text-xs text-slate-400 mt-1">
        PDF, DOCX • Max 200MB
      </p>
    </div>

    <input
      type="file"
      onChange={handleFile}
      className="hidden"
      id="uploadInput"
    />
  </label>

  {/* Uploaded File Name */}
  {selectedFile && (
    <div className="text-sm text-white-300 bg-[#1a2340] p-3 rounded-lg border border-indigo-400/20 shadow flex items-center justify-between">
      <div>
        <span className="font-medium">Uploaded:</span> {selectedFile.name}
      </div>

      <button
        onClick={() => {
          document.getElementById("uploadInput").value = "";
          setSelectedFile(null);
        }}
        className="text-white-400 hover:text-red-300 text-lg font-bold px-1"
        title="Remove File"
      >
        ✖
      </button>
    </div>
  )}

</div>
<div className="mt-10 space-y-5">

  <button className='btn w-full' onClick={newChat}>+ New Chat</button>

  <button className='btn w-full' onClick={clearChat}>Clear Chat</button>

  <button className='btn w-full' onClick={clearHistory}>Clear Conversation History</button>

  

</div>


      {/* Conversation History */}
      <div className='mt-10'>
        <strong>Conversation History</strong>
        <div className='mt-2 space-y-2' style={{ maxHeight: 260, overflow: 'auto' }}>
          
          {history.length === 0 && (
            <div className='text-sm text-gray-400'>No conversations yet</div>
          )}

          {history.map((h, idx) => (
            <div 
              key={idx}
              className='p-2 bg-[#1a2340] hover:bg-[#263056] rounded cursor-pointer transition'
              onClick={() => loadConversation(idx)}
            >
              <div className='font-medium'>
                {h.title || ('Chat ' + (idx + 1))}
              </div>
              <div className='text-xs text-gray-400'>
                {new Date(h.created).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
