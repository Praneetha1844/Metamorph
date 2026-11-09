import axios from "axios";

const BASE_URL = import.meta.env.VITE_ENGINE_URL || "http://127.0.0.1:8000";

// Sends source + tests to the Metamorph engine. Resolves to { report } or { error }; never throws.
export async function verifyRefactor({ source, tests, moduleName }) {
  try {
    const { data } = await axios.post(
      `${BASE_URL}/refactor`,
      { source, tests, module_name: moduleName },
      { timeout: 10 * 60 * 1000 }, // model calls and test runs can be slow
    );
    return { report: data };
  } catch (err) {
    if (err.response) {
      const detail = err.response.data?.detail;
      const text = Array.isArray(detail)
        ? detail.map((d) => d.msg).join("; ")
        : detail || `HTTP ${err.response.status}`;
      return { error: `Engine rejected the request: ${text}` };
    }
    return { error: `Could not reach the engine at ${BASE_URL}. Is it running?` };
  }
}
