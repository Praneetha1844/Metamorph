import { useState } from "react";
import { Editor } from "@monaco-editor/react";
import { runJavaScript } from "./lib/runJs";
import { runRemote } from "./lib/judge0";
import { suggestRefactor } from "./lib/ollama";

const LANGUAGES = [
  { value: "javascript", label: "JavaScript" },
  { value: "python", label: "Python" },
  { value: "cpp", label: "C++" },
  { value: "java", label: "Java" },
];

export default function App() {
  const [code, setCode] = useState("// Write your code here...");
  const [language, setLanguage] = useState("javascript");
  const [output, setOutput] = useState("");
  const [suggestion, setSuggestion] = useState("");
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true);
    setOutput(language === "javascript" ? await runJavaScript(code) : await runRemote(language, code));
    setBusy(false);
  };

  const refactor = async () => {
    setBusy(true);
    setSuggestion(await suggestRefactor(language, code));
    setBusy(false);
  };

  return (
    <div className="min-h-screen bg-[#080715] px-4 py-10 text-white">
      <header className="mb-10 text-center">
        <h1 className="bg-gradient-to-r from-[#fc0060] to-[#7500e7] bg-clip-text text-5xl font-bold text-transparent">
          Metamorph
        </h1>
        <p className="mt-2 text-gray-400">Edit code, run it, and request an AI refactor suggestion.</p>
      </header>

      <main className="mx-auto w-full max-w-6xl rounded-lg bg-gray-800 p-4 shadow-lg">
        <div className="mb-4 flex items-center justify-between">
          <label htmlFor="language" className="text-lg">Language</label>
          <select
            id="language"
            className="rounded border bg-gray-700 p-2"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
        </div>

        <Editor
          height="400px"
          theme="vs-dark"
          language={language}
          value={code}
          onChange={(value) => setCode(value || "")}
        />

        <div className="mt-4 flex gap-4">
          <button
            className="w-1/2 rounded bg-blue-500 px-6 py-2 font-semibold hover:bg-blue-700 disabled:opacity-50"
            onClick={run}
            disabled={busy}
          >
            Run
          </button>
          <button
            className="w-1/2 rounded bg-green-500 px-6 py-2 font-semibold hover:bg-green-700 disabled:opacity-50"
            onClick={refactor}
            disabled={busy}
          >
            Suggest refactor
          </button>
        </div>

        <section className="mt-4 rounded-lg bg-black p-4" aria-live="polite">
          <h2 className="text-lg font-semibold">Output</h2>
          <pre className="whitespace-pre-wrap">{output}</pre>
        </section>

        {suggestion && (
          <section className="mt-4 rounded-lg bg-gray-900 p-4" aria-live="polite">
            <h2 className="text-lg font-semibold">Suggested refactor (unverified)</h2>
            <pre className="whitespace-pre-wrap">{suggestion}</pre>
          </section>
        )}
      </main>
    </div>
  );
}
