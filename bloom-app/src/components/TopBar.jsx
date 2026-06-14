import { User, BarChart3 } from 'lucide-react';
import BloomLogo from './BloomLogo';

export default function TopBar({ view, onViewChange }) {
  return (
    <header className="topbar">
      <div className="topbar-brand">
        <div className="topbar-logo">
          <BloomLogo size={40} alt="Bloom logo" />
        </div>
        <div>
          <div className="topbar-name">Bloom</div>
          <div className="topbar-tagline">Your health, your rhythm, your way</div>
        </div>
      </div>
      <div className="topbar-actions">
        <div className="topbar-view-toggle">
          <button
            className={`topbar-view-btn ${view === 'employee' ? 'active' : ''}`}
            onClick={() => onViewChange('employee')}
            aria-label="Employee view"
          >
            <User size={14} style={{ marginRight: 4, verticalAlign: -2 }} />
            My health
          </button>
          <button
            className={`topbar-view-btn ${view === 'employer' ? 'active' : ''}`}
            onClick={() => onViewChange('employer')}
            aria-label="HR dashboard view"
          >
            <BarChart3 size={14} style={{ marginRight: 4, verticalAlign: -2 }} />
            HR insights
          </button>
        </div>
      </div>
    </header>
  );
}
