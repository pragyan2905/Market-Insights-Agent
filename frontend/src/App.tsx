import { useState } from 'react';
import './index.css';

interface QuantitativeMetric {
  metric_name: string;
  value: string;
  context: string;
  source: string;
}

interface QualitativeTrend {
  trend_name: string;
  description: string;
  adoption_level: string;
  asi_relevance: string;
}

interface MarketReport {
  title: string;
  executive_summary: string;
  key_trends: QualitativeTrend[];
  quantitative_data: QuantitativeMetric[];
  strategic_recommendations: string[];
}

function App() {
  const [query, setQuery] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<MarketReport | null>(null);
  const [error, setError] = useState('');

  const generateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    setError('');
    setReport(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/research/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, api_key: apiKey }),
      });

      if (!response.ok) {
        throw new Error(await response.text() || 'Failed to generate report');
      }

      const data = await response.json();
      setReport(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="hero-header">
        <h1>Market Insight Agent</h1>
        <p>Synthesize live web data into deterministic market intelligence</p>
      </header>

      <main className="main-content">
        <form className="search-form" onSubmit={generateReport}>
          <div className="input-group">
            <label>API Key (Optional if set in backend environment)</label>
            <input 
              type="password" 
              placeholder="Google Gemini API Key" 
              value={apiKey} 
              onChange={e => setApiKey(e.target.value)} 
            />
          </div>
          <div className="input-group search-box">
            <input 
              type="text" 
              placeholder="e.g. Analysis of the current Quantum Computing market trends and players" 
              value={query} 
              onChange={e => setQuery(e.target.value)} 
              required
            />
            <button type="submit" disabled={loading} className={loading ? 'loading' : ''}>
              {loading ? <span className="spinner"></span> : 'Generate Insight'}
            </button>
          </div>
        </form>

        {error && <div className="error-banner">{error}</div>}

        {report && (
          <div className="report-container fade-in">
            <div className="report-header">
              <h2>{report.title}</h2>
              <p className="summary">{report.executive_summary}</p>
            </div>

            <div className="dashboard-grid">
              <section className="dashboard-card metrics-card" style={{ gridColumn: '1 / -1' }}>
                <h3>Quantitative Data</h3>
                <div className="metrics-grid">
                  {report.quantitative_data.map((item, idx) => (
                    <div key={idx} className="metric-item">
                      <div className="metric-value">{item.value}</div>
                      <div className="metric-name">{item.metric_name}</div>
                      <div className="metric-context">{item.context}</div>
                      <a href={item.source} target="_blank" rel="noreferrer" className="source-link">Source</a>
                    </div>
                  ))}
                </div>
              </section>

              <section className="dashboard-card trends-card">
                <h3>Key Trends</h3>
                <div className="trends-list">
                  {report.key_trends.map((trend, idx) => (
                    <div key={idx} className="trend-item">
                      <div className="trend-header">
                        <h4>{trend.trend_name}</h4>
                        <span className="badge">{trend.adoption_level}</span>
                      </div>
                      <p>{trend.description}</p>
                      <div className="relevance">
                        <strong>ASI Relevance:</strong> {trend.asi_relevance}
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              <section className="dashboard-card recs-card">
                <h3>Strategic Recommendations</h3>
                <ul className="recs-list">
                  {report.strategic_recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </section>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
