import axios from "axios";

const BASE_URL = import.meta.env.VITE_OLLAMA_URL || "http://localhost:11434";
const MODEL = import.meta.env.VITE_OLLAMA_MODEL || "codellama";

// Asks a locally running Ollama model for a refactor. The result is a suggestion only: it is not verified.
export async function suggestRefactor(language, code) {
  try {
    const { data } = await axios.post(`${BASE_URL}/api/generate`, {
      model: MODEL,
      prompt: `Optimize the following ${language} code for readability, efficiency, and best practices:\n\n${code}`,
      stream: false,
    });
    return data.response.trim();
  } catch {
    return `Error: could not reach Ollama at ${BASE_URL} (model: ${MODEL}). Is it running?`;
  }
}
