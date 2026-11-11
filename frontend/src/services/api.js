
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/$/, '');

/**
 * Unified API request handler.
 *
 * Centralizes JSON handling, timeout control and error messages
 * so individual API services do not need duplicated fetch logic.
 */
export async function apiRequest(path, options = {}) {
  const {
    headers = {},
    ...requestOptions
  } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers: {
      Accept: 'application/json',
      ...headers,
    },
    signal: requestOptions.signal || AbortSignal.timeout(10000),
  });

  // HTTP 204 has no response body.
  if (response.status === 204) {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  const data = isJson
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    // FastAPI may return either a string or a validation-error array.
    let message = `HTTP ${response.status}`;

    if (typeof data?.detail === 'string') {
      message = data.detail;
    } else if (Array.isArray(data?.detail)) {
      message = data.detail
        .map((item) => item.msg || 'Invalid input')
        .join('; ');
    }

    const error = new Error(message);
    error.status = response.status;
    error.data = data;

    throw error;
  }

  return data;
}

/**
 * Check whether the FastAPI backend is available.
 */
export async function getBackendHealth() {
  return apiRequest('/api/health', {
    signal: AbortSignal.timeout(5000),
  });
}

export { API_BASE_URL };
