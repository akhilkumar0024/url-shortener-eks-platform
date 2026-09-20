import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';
import {
  Activity,
  Link as LinkIcon,
  MousePointerClick,
  Clock,
  Globe,
  RefreshCw,
  BarChart3,
  ExternalLink,
  Zap,
  Server,
  AlertCircle
} from 'lucide-react';
import './App.css';

// Read API URL from Vite env or runtime window config, with fallback
const ANALYTICS_API_URL = 
  (typeof window !== 'undefined' && window.__ENV__?.VITE_API_URL) ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:8001';

const SHORTENER_API_URL = 
  (typeof window !== 'undefined' && window.__ENV__?.VITE_SHORTENER_API_URL) ||
  import.meta.env.VITE_SHORTENER_API_URL ||
  'http://localhost:8000';

export default function App() {
  const [stats, setStats] = useState({ by_short_code: [], by_time: [] });
  const [clicksData, setClicksData] = useState({ items: [], total: 0, limit: 15, offset: 0 });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // URL Shortener Sandbox State
  const [longUrlInput, setLongUrlInput] = useState('');
  const [shortenResult, setShortenResult] = useState(null);
  const [shortenLoading, setShortenLoading] = useState(false);
  const [shortenError, setShortenError] = useState(null);

  // Fetch telemetry from analytics-backend
  const fetchData = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    setError(null);

    try {
      const [statsRes, clicksRes] = await Promise.all([
        fetch(`${ANALYTICS_API_URL}/stats`),
        fetch(`${ANALYTICS_API_URL}/clicks?limit=${clicksData.limit}&offset=${clicksData.offset}`)
      ]);

      if (!statsRes.ok || !clicksRes.ok) {
        throw new Error(`Analytics API returned status ${statsRes.status} / ${clicksRes.status}`);
      }

      const statsJson = await statsRes.json();
      const clicksJson = await clicksRes.json();

      setStats(statsJson);
      setClicksData(clicksJson);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError(err.message || 'Failed to connect to analytics backend');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [clicksData.limit, clicksData.offset]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle Quick URL Shortening
  const handleShorten = async (e) => {
    e.preventDefault();
    if (!longUrlInput.trim()) return;

    setShortenLoading(true);
    setShortenError(null);
    setShortenResult(null);

    try {
      const res = await fetch(`${SHORTENER_API_URL}/shorten`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: longUrlInput.trim() })
      });

      if (!res.ok) {
        throw new Error(`Shortener service error: ${res.statusText}`);
      }

      const data = await res.json();
      setShortenResult(data.short_url);
      setLongUrlInput('');
    } catch (err) {
      setShortenError(err.message || 'Failed to shorten URL');
    } finally {
      setShortenLoading(false);
    }
  };

  // Format timestamp for charts
  const formatTimeBucket = (bucketStr) => {
    try {
      const date = new Date(bucketStr);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return bucketStr;
    }
  };

  // Format date for table
  const formatDate = (isoStr) => {
    try {
      const date = new Date(isoStr);
      return date.toLocaleString([], {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return isoStr;
    }
  };

  // Calculate high-level summary KPIs
  const totalClicksCount = clicksData.total || stats.by_short_code.reduce((acc, curr) => acc + curr.total_clicks, 0);
  const uniqueCodesCount = stats.by_short_code.length;
  const topLink = stats.by_short_code[0]?.short_code || '—';
  const topLinkClicks = stats.by_short_code[0]?.total_clicks || 0;

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-brand">
          <div className="brand-icon-box">
            <Activity size={26} />
          </div>
          <div className="header-title-box">
            <h1>CloudScale Telemetry</h1>
            <p>High-Throughput Distributed URL Shortener Analytics</p>
          </div>
        </div>

        <div className="header-actions">
          <div className="live-indicator">
            <span className="pulse-dot"></span>
            <span>LIVE INGESTION</span>
          </div>

          <button
            className="btn btn-secondary"
            onClick={() => fetchData(true)}
            disabled={refreshing}
            title="Refresh analytics data"
          >
            <RefreshCw size={16} className={refreshing ? 'spinner' : ''} />
            <span>{refreshing ? 'Updating...' : 'Refresh'}</span>
          </button>
        </div>
      </header>

      {/* Quick Test URL Shortener Banner */}
      <section className="shorten-sandbox">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Zap size={20} color="#818cf8" />
          <strong style={{ fontSize: '0.9rem', color: '#f1f5f9' }}>Test Link Generator:</strong>
        </div>

        <form className="sandbox-form" onSubmit={handleShorten}>
          <input
            type="url"
            className="sandbox-input"
            placeholder="Paste a long destination URL (e.g. https://github.com/kubernetes/kubernetes)..."
            value={longUrlInput}
            onChange={(e) => setLongUrlInput(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary" disabled={shortenLoading}>
            {shortenLoading ? 'Generating...' : 'Shorten & Test'}
          </button>
        </form>

        {shortenResult && (
          <div className="sandbox-result">
            <span>Created:</span>
            <a
              href={shortenResult}
              target="_blank"
              rel="noreferrer"
              style={{ color: '#34d399', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              {shortenResult}
              <ExternalLink size={14} />
            </a>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>(Click link to trigger redirect & SQS event)</span>
          </div>
        )}

        {shortenError && (
          <div style={{ color: '#ef4444', fontSize: '0.85rem' }}>
            {shortenError}
          </div>
        )}
      </section>

      {/* Error alert banner */}
      {error && (
        <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#ef4444' }}>
            <AlertCircle size={20} />
            <span><strong>Backend Connectivity Alert:</strong> {error}</span>
          </div>
        </div>
      )}

      {/* Summary KPI Cards */}
      <section className="metrics-grid">
        <div className="glass-card metric-card">
          <div className="metric-icon-wrapper metric-icon-indigo">
            <MousePointerClick size={26} />
          </div>
          <div className="metric-details">
            <span className="metric-label">Total Clicks</span>
            <span className="metric-value">{totalClicksCount.toLocaleString()}</span>
            <span className="metric-subtitle">Across all distributed routes</span>
          </div>
        </div>

        <div className="glass-card metric-card">
          <div className="metric-icon-wrapper metric-icon-cyan">
            <LinkIcon size={26} />
          </div>
          <div className="metric-details">
            <span className="metric-label">Tracked Short Codes</span>
            <span className="metric-value">{uniqueCodesCount}</span>
            <span className="metric-subtitle">Unique base62 keys tracked</span>
          </div>
        </div>

        <div className="glass-card metric-card">
          <div className="metric-icon-wrapper metric-icon-emerald">
            <BarChart3 size={26} />
          </div>
          <div className="metric-details">
            <span className="metric-label">Top Link</span>
            <span className="metric-value mono">/{topLink}</span>
            <span className="metric-subtitle">{topLinkClicks} lifetime clicks</span>
          </div>
        </div>

        <div className="glass-card metric-card">
          <div className="metric-icon-wrapper metric-icon-purple">
            <Server size={26} />
          </div>
          <div className="metric-details">
            <span className="metric-label">Storage Architecture</span>
            <span className="metric-value" style={{ fontSize: '1.25rem', marginTop: '0.2rem' }}>PostgreSQL</span>
            <span className="metric-subtitle">Redis L1 Cache + SQS Ingestion</span>
          </div>
        </div>
      </section>

      {/* Charts Section */}
      <section className="charts-grid">
        {/* Bar Chart: Clicks per short_code */}
        <div className="glass-card">
          <div className="chart-header">
            <div className="chart-title-group">
              <h3>Clicks per Short Code</h3>
              <p>Aggregated distribution by short_code</p>
            </div>
            <span className="badge badge-indigo">Categorical</span>
          </div>
          <div className="chart-body">
            {stats.by_short_code.length === 0 ? (
              <div className="state-container">
                <Clock size={32} color="#64748b" />
                <p style={{ color: '#94a3b8' }}>No clicks recorded yet. Create or click links to view stats.</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.by_short_code} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="short_code"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'JetBrains Mono' }}
                  />
                  <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#111625',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      color: '#f1f5f9'
                    }}
                    cursor={{ fill: 'rgba(99, 102, 241, 0.1)' }}
                  />
                  <Bar
                    dataKey="total_clicks"
                    name="Total Clicks"
                    fill="url(#barGradient)"
                    radius={[6, 6, 0, 0]}
                  />
                  <defs>
                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#818cf8" />
                      <stop offset="100%" stopColor="#4f46e5" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Time-Series Chart: Clicks over time */}
        <div className="glass-card">
          <div className="chart-header">
            <div className="chart-title-group">
              <h3>Click Velocity Over Time</h3>
              <p>Hourly event aggregation timeline</p>
            </div>
            <span className="badge badge-cyan">Chronological</span>
          </div>
          <div className="chart-body">
            {stats.by_time.length === 0 ? (
              <div className="state-container">
                <Clock size={32} color="#64748b" />
                <p style={{ color: '#94a3b8' }}>No timeline events recorded yet.</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats.by_time} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
                  <defs>
                    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="time_bucket"
                    tickFormatter={formatTimeBucket}
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                  />
                  <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <Tooltip
                    labelFormatter={(val) => formatDate(val)}
                    contentStyle={{
                      backgroundColor: '#111625',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      color: '#f1f5f9'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="click_count"
                    name="Clicks"
                    stroke="#22d3ee"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#areaGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </section>

      {/* Recent Click Events Data Table */}
      <section className="glass-card">
        <div className="table-header">
          <div>
            <h3>Recent Click Events</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Real-time audit log of incoming redirects processed by the platform
            </p>
          </div>
          <div className="badge badge-emerald">
            {clicksData.total} Total Recorded
          </div>
        </div>

        <div className="table-responsive">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Short Code</th>
                <th>Timestamp (UTC)</th>
                <th>Client IP</th>
                <th>HTTP Referrer</th>
                <th>User Agent</th>
              </tr>
            </thead>
            <tbody>
              {clicksData.items.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '3rem' }}>
                    {loading ? (
                      <div className="state-container" style={{ padding: '1rem' }}>
                        <div className="spinner"></div>
                        <span>Connecting to analytics feed...</span>
                      </div>
                    ) : (
                      'No click events found in the database.'
                    )}
                  </td>
                </tr>
              ) : (
                clicksData.items.map((click, idx) => (
                  <tr key={idx}>
                    <td>
                      <span className="badge badge-indigo table-code">
                        /{click.short_code}
                      </span>
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                      {formatDate(click.clicked_at)}
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem', color: '#38bdf8' }}>
                      {click.client_ip || 'direct'}
                    </td>
                    <td className="table-meta" title={click.referrer || 'Direct / None'}>
                      {click.referrer ? (
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Globe size={13} color="#94a3b8" />
                          {click.referrer}
                        </span>
                      ) : (
                        <span style={{ color: '#64748b' }}>Direct / Bookmark</span>
                      )}
                    </td>
                    <td className="table-meta" title={click.user_agent || 'Unknown'}>
                      {click.user_agent || '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="table-footer">
          <span>
            Showing {clicksData.items.length > 0 ? clicksData.offset + 1 : 0} to{' '}
            {Math.min(clicksData.offset + clicksData.items.length, clicksData.total)} of{' '}
            {clicksData.total} events
          </span>

          <div className="pagination-controls">
            <button
              className="btn btn-secondary"
              style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
              disabled={clicksData.offset === 0}
              onClick={() =>
                setClicksData((prev) => ({
                  ...prev,
                  offset: Math.max(0, prev.offset - prev.limit)
                }))
              }
            >
              Previous
            </button>
            <button
              className="btn btn-secondary"
              style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
              disabled={clicksData.offset + clicksData.limit >= clicksData.total}
              onClick={() =>
                setClicksData((prev) => ({
                  ...prev,
                  offset: prev.offset + prev.limit
                }))
              }
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
