const API_URL = process.env.REACT_APP_API_URL || "";

export async function askCodeMind(query) {
  const response = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify({
      query: query,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to communicate with CodeMind AI");
  }

  return await response.json();
}