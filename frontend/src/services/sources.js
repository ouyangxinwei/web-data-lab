
import { apiRequest } from './api.js';

/**
 * Data Sources API service.
 *
 * All methods use the shared apiRequest handler.
 * This module only manages source definitions;
 * it does not execute external data collection.
 */

// Get paginated data sources with optional filters.
export function getSources({
  limit = 50,
  offset = 0,
  source_type,
  is_active,
} = {}) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  if (source_type) {
    params.set('source_type', source_type);
  }

  if (is_active !== undefined && is_active !== '') {
    params.set('is_active', String(is_active));
  }

  return apiRequest(`/api/sources?${params.toString()}`);
}

// Get one data source.
export function getSource(sourceId) {
  return apiRequest(`/api/sources/${sourceId}`);
}

// Create a data source.
export function createSource(payload) {
  return apiRequest('/api/sources', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

// Replace all editable fields of a data source.
export function updateSource(sourceId, payload) {
  return apiRequest(`/api/sources/${sourceId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

// Delete an unused data source.
export function deleteSource(sourceId) {
  return apiRequest(`/api/sources/${sourceId}`, {
    method: 'DELETE',
  });
}
