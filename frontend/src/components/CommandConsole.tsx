"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";

interface CommandConsoleProps {
  output: string[];
  onCommand: (cmd: string) => void;
  connected: boolean;
  sessionId: string | null;
}

const HISTORY_LIMIT = 50;

export default function CommandConsole({
  output,
  onCommand,
  connected,
  sessionId,
}: CommandConsoleProps) {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [histIdx, setHistIdx] = useState(-1);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [output.length]);

  const submit = () => {
    const cmd = input.trim();
    if (!cmd) return;
    setHistory((prev) => [cmd, ...prev].slice(0, HISTORY_LIMIT));
    setHistIdx(-1);
    onCommand(cmd);
    setInput("");
  };

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      submit();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      const next = Math.min(histIdx + 1, history.length - 1);
      setHistIdx(next);
      setInput(history[next] ?? "");
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      const next = Math.max(histIdx - 1, -1);
      setHistIdx(next);
      setInput(next === -1 ? "" : history[next]);
    }
  };

  return (
    <div className="panel flex flex-col h-full" onClick={() => inputRef.current?.focus()}>
      <div className="panel-header">
        <span className="text-[#06b6d4]">&#62;_</span>
        Command Console
        {!connected && (
          <span className="ml-auto text-[9px] text-[#ef4444]">OFFLINE</span>
        )}
      </div>

      {/* Output area */}
      <div className="flex-1 overflow-y-auto p-3 font-mono text-[11px] leading-relaxed text-[#8892a4] space-y-0.5">
        {output.map((line, i) => (
          <div
            key={i}
            className={`wrap-break-word ${
              line.startsWith(">")
                ? "text-[#06b6d4]"
                : line.includes("ERROR")
                ? "text-[#ef4444]"
                : line.includes("CONNECTED")
                ? "text-[#22c55e]"
                : line.includes("DISCONNECTED")
                ? "text-[#ef4444]"
                : line.includes("STAGE") || line.includes("DONE")
                ? "text-[#f97316]"
                : "text-[#8892a4]"
            }`}
          >
            {line}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input row */}
      <div className="flex items-center gap-2 px-3 py-2.5 border-t border-[#1e3a5f] flex-shrink-0">
        <span className="text-[#06b6d4] text-[12px] shrink-0">
          {sessionId ? sessionId.slice(0, 8) : "no-session"}
          <span className="text-[#22c55e]"> &gt;</span>
        </span>
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={!connected}
          placeholder={connected ? "help | create | run <stage> | status | restore" : "offline…"}
          className="flex-1 bg-transparent outline-none text-[#e0e6ed] placeholder:text-[#4a5568] text-[12px] disabled:opacity-40"
          autoComplete="off"
          spellCheck={false}
        />
        <span className="cursor-blink text-[#22c55e] text-[12px]">█</span>
      </div>
    </div>
  );
}
