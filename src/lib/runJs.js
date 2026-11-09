// Runs JavaScript in a throwaway Web Worker so user code never touches the page's DOM or globals.
// shortcut: a worker is isolated from the DOM but can still use fetch; move to a sandboxed iframe or a server if untrusted code must be run.
const WORKER_SOURCE = `
  onmessage = ({ data }) => {
    const out = [];
    const fmt = (args) => args.map((v) => (typeof v === "string" ? v : JSON.stringify(v) ?? String(v))).join(" ");
    console.log = (...a) => out.push(fmt(a));
    console.error = (...a) => out.push("Error: " + fmt(a));
    try {
      const result = (0, eval)(data);
      if (result !== undefined) out.push(fmt([result]));
      postMessage(out.join("\\n"));
    } catch (e) {
      postMessage(out.concat("Error: " + e.message).join("\\n"));
    }
  };
`;

export function runJavaScript(code, timeoutMs = 3000) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(new Blob([WORKER_SOURCE], { type: "text/javascript" }));
    const worker = new Worker(url);
    const finish = (text) => {
      clearTimeout(timer);
      worker.terminate();
      URL.revokeObjectURL(url);
      resolve(text);
    };
    const timer = setTimeout(() => finish(`Error: execution exceeded ${timeoutMs} ms`), timeoutMs);
    worker.onmessage = (e) => finish(e.data || "(no output)");
    worker.onerror = (e) => finish(`Error: ${e.message}`);
    worker.postMessage(code);
  });
}
