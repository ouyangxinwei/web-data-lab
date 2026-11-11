import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  getSources,
  getSource,
  createSource,
  updateSource,
  deleteSource,
} from '../services/sources.js';

const PAGE_SIZE = 10;

const emptyForm = {
  name: '',
  source_type: 'api',
  base_url: '',
  description: '',
  config_json: '{}',
  is_active: true,
};

function formatDate(value) {
  if (!value) return '—';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString();
}

function getErrorMessage(error, fallback) {
  if (error?.status === 409) {
    return error.message;
  }

  return error?.message || fallback;
}

export default function Sources({ t }) {
  const [sources, setSources] = useState([]);
  const [total, setTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const [page, setPage] = useState(1);

  const [modal, setModal] = useState('');
  const [selectedSource, setSelectedSource] = useState(null);

  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

    const loadSources = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const result = await getSources({
        limit: PAGE_SIZE,
        offset: (page - 1) * PAGE_SIZE,
        source_type: typeFilter || undefined,
        is_active: statusFilter,
      });

      const items = result.items || [];

      // If the last item on the current page was deleted,
      // move back one page and load it again.
      if (items.length === 0 && page > 1 && result.total > 0) {
        setPage((current) => Math.max(1, current - 1));
        return;
      }

      setSources(items);
      setTotal(result.total ?? items.length);
    } catch (err) {
      setError(getErrorMessage(err, t.loadSourcesFailed));
    } finally {
      setLoading(false);
    }
  }, [page, typeFilter, statusFilter, t.loadSourcesFailed]);

  useEffect(() => {
    loadSources();
  }, [loadSources]);

  // Search is currently performed within the page loaded from the backend.
  // Type and status filters are handled by the backend API.
  const filteredSources = useMemo(() => {
    const keyword = search.trim().toLowerCase();

    if (!keyword) return sources;

    return sources.filter((source) =>
      source.name?.toLowerCase().includes(keyword) ||
      source.base_url?.toLowerCase().includes(keyword)
    );
  }, [sources, search]);

  const totalPages = Math.max(
    1,
    Math.ceil(total / PAGE_SIZE)
  );

  const currentPage = Math.min(page, totalPages);

  const visibleSources = filteredSources;

  function openCreate() {
    setForm({ ...emptyForm });
    setSelectedSource(null);
    setError('');
    setNotice('');
    setModal('form');
  }

  function openEdit(source) {
    setForm({
      name: source.name || '',
      source_type: source.source_type || 'api',
      base_url: source.base_url || '',
      description: source.description || '',
      config_json: JSON.stringify(source.config_json || {}, null, 2),
      is_active: source.is_active ?? true,
    });

    setSelectedSource(source);
    setError('');
    setNotice('');
    setModal('form');
  }

  async function openDetail(sourceId) {
    setError('');
    setNotice('');
    setModal('detail');
    setSelectedSource(null);

    try {
      const result = await getSource(sourceId);
      setSelectedSource(result);
    } catch (err) {
      setError(getErrorMessage(err, t.error));
      setModal('');
    }
  }

  function closeModal() {
    if (saving) return;

    setModal('');
    setSelectedSource(null);
  }

  function updateForm(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError('');
    setNotice('');

    if (!form.name.trim() || !form.base_url.trim()) {
      setError(t.requiredField);
      return;
    }

    let parsedConfig;

    try {
      parsedConfig = JSON.parse(form.config_json || '{}');

      if (
        parsedConfig === null ||
        Array.isArray(parsedConfig) ||
        typeof parsedConfig !== 'object'
      ) {
        throw new Error('Configuration must be a JSON object.');
      }
    } catch {
      setError('Config JSON 格式无效，请检查后重试。');
      return;
    }

    try {
      const url = new URL(form.base_url.trim());

      if (!['http:', 'https:'].includes(url.protocol)) {
        setError(t.invalidUrl);
        return;
      }
    } catch {
      setError(t.invalidUrl);
      return;
    }

    const payload = {
      name: form.name.trim(),
      source_type: form.source_type,
      base_url: form.base_url.trim(),
      description: form.description.trim() || null,
      config_json: parsedConfig,
      is_active: form.is_active,
    };

    setSaving(true);

    try {
      if (selectedSource?.id) {
        await updateSource(selectedSource.id, payload);
      } else {
        await createSource(payload);
      }

      setModal('');
      setSelectedSource(null);
      setNotice(t.sourceSaved);

      await loadSources();
    } catch (err) {
      setError(getErrorMessage(err, t.saveSourceFailed));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(source) {
    const confirmed = window.confirm(
      `${t.confirmDelete}\n\n${source.name}`
    );

    if (!confirmed) return;

    setError('');
    setNotice('');

    try {
      await deleteSource(source.id);

      setNotice(t.sourceDeleted);

      if (selectedSource?.id === source.id) {
        setModal('');
        setSelectedSource(null);
      }

      await loadSources();
    } catch (err) {
      const message =
        err?.status === 409
          ? t.deleteConflict
          : getErrorMessage(err, t.deleteSourceFailed);

      setError(message);
    }
  }

  function changeFilter(setter, value) {
    setter(value);
    setPage(1);
  }

  return (
    <section className="page-section">
      <div className="page-heading">
        <div>
          <div className="eyebrow">DATA MANAGEMENT</div>
          <h1>{t.sourcesTitle}</h1>
          <p>{t.sourcesIntro}</p>
        </div>

        <button className="primary-button" onClick={openCreate}>
          + {t.addSource}
        </button>
      </div>

      {notice && (
        <div className="source-notice">
          {notice}
        </div>
      )}

      {error && (
        <div className="source-error" role="alert">
          <span>{error}</span>
          <button
            className="text-button"
            onClick={() => setError('')}
          >
            {t.close}
          </button>
        </div>
      )}

      <div className="source-toolbar">
        <input
          className="source-search"
          type="search"
          placeholder={t.searchSource}
          value={search}
          onChange={(event) =>
            changeFilter(setSearch, event.target.value)
          }
        />

        <select
          value={typeFilter}
          onChange={(event) =>
            changeFilter(setTypeFilter, event.target.value)
          }
        >
          <option value="">{t.allTypes}</option>
          <option value="api">{t.apiType}</option>
          <option value="html">{t.htmlType}</option>
        </select>

        <select
          value={statusFilter}
          onChange={(event) =>
            changeFilter(setStatusFilter, event.target.value)
          }
        >
          <option value="">{t.allStatuses}</option>
          <option value="true">{t.active}</option>
          <option value="false">{t.inactive}</option>
        </select>

        <button
          className="secondary-button"
          onClick={loadSources}
          disabled={loading}
        >
          {t.refresh}
        </button>
      </div>

      <div className="source-summary">
        <span>{t.sourceCount}: <strong>{total}</strong></span>
        <span>
          {t.filter}: <strong>{filteredSources.length}</strong>
        </span>
      </div>

      <div className="source-table-wrap">
        {loading ? (
          <div className="source-state">{t.loading}</div>
        ) : visibleSources.length === 0 ? (
          <div className="source-state">
            <span className="source-empty-icon">◇</span>
            <p>
              {sources.length === 0
                ? t.noSources
                : t.noData}
            </p>
          </div>
        ) : (
          <table className="source-table">
            <thead>
              <tr>
                <th>{t.sourceName}</th>
                <th>{t.sourceType}</th>
                <th>{t.baseUrl}</th>
                <th>{t.status}</th>
                <th>{t.actions}</th>
              </tr>
            </thead>

            <tbody>
              {visibleSources.map((source) => (
                <tr key={source.id}>
                  <td>
                    <div className="source-name-cell">
                      <strong>{source.name}</strong>
                      <small>ID: {source.id}</small>
                    </div>
                  </td>

                  <td>
                    <span className="source-type-tag">
                      {source.source_type === 'api'
                        ? t.apiType
                        : t.htmlType}
                    </span>
                  </td>

                  <td className="source-url-cell">
                    {source.base_url}
                  </td>

                  <td>
                    <span
                      className={`source-status ${
                        source.is_active ? 'active' : 'inactive'
                      }`}
                    >
                      {source.is_active ? t.active : t.inactive}
                    </span>
                  </td>

                  <td>
                    <div className="source-actions">
                      <button
                        className="text-button"
                        onClick={() => openDetail(source.id)}
                      >
                        {t.detail}
                      </button>

                      <button
                        className="text-button"
                        onClick={() => openEdit(source)}
                      >
                        {t.edit}
                      </button>

                      <button
                        className="text-button danger-button"
                        onClick={() => handleDelete(source)}
                      >
                        {t.delete}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {!loading && total > 0 && (
        <div className="source-pagination">
          <span>
            {t.page} {currentPage} {t.of} {totalPages}
          </span>

          <div>
            <button
              className="secondary-button"
              disabled={currentPage <= 1}
              onClick={() => setPage((value) => value - 1)}
            >
              {t.previous}
            </button>

            <button
              className="secondary-button"
              disabled={currentPage >= totalPages}
              onClick={() => setPage((value) => value + 1)}
            >
              {t.nextPage}
            </button>
          </div>
        </div>
      )}

      {modal === 'form' && (
        <div className="source-modal-backdrop">
          <div className="source-modal">
            <div className="source-modal-header">
              <div>
                <h2>
                  {selectedSource ? t.editSource : t.addSource}
                </h2>
                <p>{t.sourceFormHint}</p>
              </div>

              <button
                className="icon-button"
                onClick={closeModal}
                disabled={saving}
                aria-label={t.close}
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <label className="source-field">
                <span>{t.sourceName} *</span>
                <input
                  value={form.name}
                  onChange={(event) =>
                    updateForm('name', event.target.value)
                  }
                  maxLength={150}
                  required
                />
              </label>

              <label className="source-field">
                <span>{t.sourceType} *</span>
                <select
                  value={form.source_type}
                  onChange={(event) =>
                    updateForm('source_type', event.target.value)
                  }
                >
                  <option value="api">{t.apiType}</option>
                  <option value="html">{t.htmlType}</option>
                </select>
              </label>

              <label className="source-field">
                <span>{t.baseUrl} *</span>
                <input
                  type="url"
                  value={form.base_url}
                  onChange={(event) =>
                    updateForm('base_url', event.target.value)
                  }
                  placeholder="https://example.com"
                  required
                />
              </label>

              <label className="source-field">
                <span>{t.description}</span>
                <textarea
                  value={form.description}
                  onChange={(event) =>
                    updateForm('description', event.target.value)
                  }
                  rows={3}
                />
              </label>

              <label className="source-field">
                <span>
                  {t.configJson} ({t.optional})
                </span>
                <textarea
                  className="source-json-input"
                  value={form.config_json}
                  onChange={(event) =>
                    updateForm('config_json', event.target.value)
                  }
                  rows={5}
                  spellCheck="false"
                />
              </label>

              <label className="source-checkbox">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(event) =>
                    updateForm('is_active', event.target.checked)
                  }
                />
                <span>{t.active}</span>
              </label>

              {error && (
                <div className="source-error" role="alert">
                  {error}
                </div>
              )}

              <div className="source-modal-footer">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={closeModal}
                  disabled={saving}
                >
                  {t.cancel}
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={saving}
                >
                  {saving ? t.loading : t.save}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {modal === 'detail' && (
        <div className="source-modal-backdrop">
          <div className="source-modal">
            <div className="source-modal-header">
              <div>
                <h2>{t.sourceDetail}</h2>
              </div>

              <button
                className="icon-button"
                onClick={closeModal}
                aria-label={t.close}
              >
                ×
              </button>
            </div>

            {!selectedSource ? (
              <div className="source-state">{t.loading}</div>
            ) : (
              <div className="source-detail">
                <div>
                  <span>{t.sourceId}</span>
                  <strong>{selectedSource.id}</strong>
                </div>

                <div>
                  <span>{t.sourceName}</span>
                  <strong>{selectedSource.name}</strong>
                </div>

                <div>
                  <span>{t.sourceType}</span>
                  <strong>
                    {selectedSource.source_type === 'api'
                      ? t.apiType
                      : t.htmlType}
                  </strong>
                </div>

                <div>
                  <span>{t.baseUrl}</span>
                  <strong className="detail-url">
                    {selectedSource.base_url}
                  </strong>
                </div>

                <div>
                  <span>{t.description}</span>
                  <strong>
                    {selectedSource.description || '—'}
                  </strong>
                </div>

                <div>
                  <span>{t.status}</span>
                  <strong>
                    {selectedSource.is_active ? t.active : t.inactive}
                  </strong>
                </div>

                <div>
                  <span>{t.createdAt}</span>
                  <strong>{formatDate(selectedSource.created_at)}</strong>
                </div>

                <div>
                  <span>{t.updatedAt}</span>
                  <strong>{formatDate(selectedSource.updated_at)}</strong>
                </div>

                <div className="source-detail-json">
                  <span>{t.configJson}</span>
                  <pre>
                    {JSON.stringify(
                      selectedSource.config_json || {},
                      null,
                      2
                    )}
                  </pre>
                </div>
              </div>
            )}

            <div className="source-modal-footer">
              <button
                className="secondary-button"
                onClick={closeModal}
              >
                {t.close}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}