import axios from "axios";

const LANGUAGE_IDS = { python: 71, cpp: 54, java: 62 };

const BASE_URL = import.meta.env.VITE_JUDGE0_URL || "https://judge0-ce.p.rapidapi.com";
const KEY = import.meta.env.VITE_JUDGE0_KEY;

// Note: VITE_* variables are bundled into client code. Use a throwaway key or put a proxy in front.
export async function runRemote(language, code) {
  if (!KEY) {
    return "Remote execution is not configured. Set VITE_JUDGE0_KEY (see .env.example).";
  }
  try {
    const { data } = await axios.post(
      `${BASE_URL}/submissions`,
      { source_code: code, language_id: LANGUAGE_IDS[language], stdin: "" },
      {
        params: { base64_encoded: "false", wait: "true" },
        headers: {
          "X-RapidAPI-Host": new URL(BASE_URL).host,
          "X-RapidAPI-Key": KEY,
        },
      }
    );
    return data.stdout || data.stderr || data.compile_output || "(no output)";
  } catch {
    return "Error: unable to compile or run the code.";
  }
}
