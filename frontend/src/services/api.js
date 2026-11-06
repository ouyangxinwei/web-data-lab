const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
export async function getBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`, { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(5000) });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
export { API_BASE_URL };