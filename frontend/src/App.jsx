
import { useEffect, useState } from 'react';
import { getBackendHealth } from './services/api.js';
import { messages } from './i18n/messages.js';

import Overview from './pages/Overview.jsx';
import Sources from './pages/Sources.jsx';
import Tasks from './pages/Tasks.jsx';
import Lab from './pages/Lab.jsx';
import History from './pages/History.jsx';
import Records from './pages/Records.jsx';
import Settings from './pages/Settings.jsx';

const navItems = [
  { key: 'overview', symbol: '⌂', Component: Overview },
  { key: 'sources', symbol: '▤', Component: Sources },
  { key: 'tasks', symbol: '▦', Component: Tasks },
  { key: 'lab', symbol: '⌘', Component: Lab },
  { key: 'history', symbol: '◷', Component: History },
  { key: 'records', symbol: '▧', Component: Records },
  { key: 'settings', symbol: '⚙', Component: Settings },
];

export default function App() {
  const [language, setLanguage] = useState(
    () => localStorage.getItem('wdl-language') || 'zh'
  );

  const [theme, setTheme] = useState(
    () => localStorage.getItem('wdl-theme') || 'dark'
  );

  const [active, setActive] = useState('overview');
  const [health, setHealth] = useState('checking');
  const [healthDetail, setHealthDetail] = useState('');

  const t = messages[language] || messages.zh;

  const activePage = navItems.find((item) => item.key === active);
  const ActivePage = activePage?.Component || Overview;

  // Persist language and update the document language.
  useEffect(() => {
    localStorage.setItem('wdl-language', language);
    document.documentElement.lang =
      language === 'zh' ? 'zh-CN' : language;
  }, [language]);

  // Persist the selected theme.
  useEffect(() => {
    localStorage.setItem('wdl-theme', theme);
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  // Check backend availability.
  async function refreshHealth() {
    setHealth('checking');

    try {
      const data = await getBackendHealth();

      setHealth(data.status === 'ok' ? 'online' : 'offline');
      setHealthDetail(data.version ? `v${data.version}` : '');
    } catch {
      setHealth('offline');
      setHealthDetail('Start the FastAPI service to connect');
    }
  }

  useEffect(() => {
    refreshHealth();
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">WD</div>

        <div className="brand-copy">
          <strong>Web Data Lab</strong>
          <span>DATA COLLECTION WORKSPACE</span>
        </div>

        <nav className="main-nav" aria-label="Main navigation">
          {navItems.map(({ key, symbol }) => (
            <button
              key={key}
              className={active === key ? 'nav-item active' : 'nav-item'}
              onClick={() => setActive(key)}
            >
              <span className="nav-symbol">{symbol}</span>
              <span>{t[key]}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <span className="tiny-dot" />
          <span>Personal Lab · v0.1.0</span>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            WORKSPACE <span>/</span> {t[active].toUpperCase()}
          </div>

          <div className="toolbar">
            <label className="sr-only" htmlFor="language">
              {t.language}
            </label>

            <select
              id="language"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
            >
              <option value="zh">简体中文</option>
              <option value="ja">日本語</option>
              <option value="en">English</option>
            </select>

            <button
              className="icon-button"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              title={t.theme}
              aria-label={t.theme}
            >
              {theme === 'dark' ? '☼' : '☾'}
            </button>
          </div>
        </header>

        <section className="content">
          {active === 'overview' && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">YOUR DATA WORKBENCH</div>
                  <h1>{t.welcome}</h1>
                  <p>{t.intro}</p>
                </div>
              </div>

              <div className="status-banner">
                <div className="status-left">
                  <span
                    className={
                      health === 'online'
                        ? 'status-indicator online'
                        : 'status-indicator'
                    }
                  />

                  <div>
                    <strong>{t.backend}</strong>
                    <span>
                      {health === 'checking'
                        ? t.checking
                        : health === 'online'
                          ? t.online
                          : t.offline}
                      {healthDetail ? ` · ${healthDetail}` : ''}
                    </span>
                  </div>
                </div>

                <button className="text-button" onClick={refreshHealth}>
                  ↻ {t.refresh}
                </button>
              </div>
            </>
          )}

          <ActivePage t={t} />
        </section>
      </main>
    </div>
  );
}
