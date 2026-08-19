export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token");
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/";
      return;
    }
    throw new Error(data.detail || "Erreur lors de l'appel API");
  }

  return data;
}
