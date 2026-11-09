const VERDICT_STYLE = {
  accepted: "bg-green-700",
  rejected: "bg-red-700",
  baseline_failed: "bg-yellow-700",
  provider_error: "bg-yellow-700",
};

const METRIC_LABELS = {
  sloc: "Source lines",
  cc_mean: "Mean complexity",
  cc_max: "Max complexity",
  maintainability_index: "Maintainability index",
};

function attemptOutcome(attempt) {
  if (attempt.suite) {
    if (attempt.suite.passed) return "tests passed";
    return attempt.suite.timed_out ? "tests timed out" : "tests failed";
  }
  return attempt.note || "no result";
}

export default function VerifiedResult({ report }) {
  const { verdict, message, attempts, before, after, deltas, diff, limitation, provider } = report;

  return (
    <section className="mt-4 rounded-lg bg-gray-900 p-4" aria-live="polite">
      <h2 className="text-lg font-semibold">Verified refactor</h2>
      <p className="mt-2">
        <span className={`rounded px-2 py-1 text-sm font-semibold ${VERDICT_STYLE[verdict] ?? "bg-gray-700"}`}>
          {verdict.replace("_", " ")}
        </span>
        <span className="ml-3 text-gray-300">{message}</span>
      </p>
      <p className="mt-1 text-sm text-gray-400">Model: {provider}</p>

      {attempts.length > 0 && (
        <table className="mt-3 w-full text-left text-sm">
          <caption className="sr-only">Attempts</caption>
          <thead>
            <tr className="text-gray-400">
              <th scope="col" className="pr-4">Attempt</th>
              <th scope="col">Outcome</th>
            </tr>
          </thead>
          <tbody>
            {attempts.map((a) => (
              <tr key={a.number}>
                <td className="pr-4">{a.number}</td>
                <td>{attemptOutcome(a)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {before && after && deltas && (
        <table className="mt-3 w-full text-left text-sm">
          <caption className="sr-only">Static metrics before and after</caption>
          <thead>
            <tr className="text-gray-400">
              <th scope="col">Metric</th>
              <th scope="col">Before</th>
              <th scope="col">After</th>
              <th scope="col">Change</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(METRIC_LABELS).map(([key, label]) => (
              <tr key={key}>
                <td>{label}</td>
                <td>{before[key]}</td>
                <td>{after[key]}</td>
                <td>{deltas[key] > 0 ? `+${deltas[key]}` : deltas[key]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {diff && (
        <>
          <h3 className="mt-3 font-semibold">Diff</h3>
          <pre className="mt-1 overflow-x-auto whitespace-pre rounded bg-black p-3 text-sm">{diff}</pre>
        </>
      )}

      <p className="mt-3 text-xs text-gray-400">{limitation}</p>
    </section>
  );
}
