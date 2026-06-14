import { Lock, Lightbulb, TrendingUp, Clock, FileText, GraduationCap, Users } from 'lucide-react';

export default function EmployerDashboard() {
  return (
    <div className="dashboard">
      <div className="dash-header">
        <h2>Bloom — HR insights</h2>
        <div className="dash-badge">
          <Lock size={12} />
          Aggregated &amp; k-anonymized
        </div>
      </div>

      <div className="dash-metrics">
        <div className="dash-metric">
          <div className="dash-metric-value neutral">47%</div>
          <div className="dash-metric-label">Adoption rate (6 months)</div>
        </div>
        <div className="dash-metric">
          <div className="dash-metric-value positive">+12%</div>
          <div className="dash-metric-label">Female retention improvement</div>
        </div>
        <div className="dash-metric">
          <div className="dash-metric-value positive">-23%</div>
          <div className="dash-metric-label">Health-related absences</div>
        </div>
        <div className="dash-metric">
          <div className="dash-metric-value neutral">4.6/5</div>
          <div className="dash-metric-label">Employee satisfaction</div>
        </div>
      </div>

      <div className="dash-section">
        <h3>Anonymous insights</h3>
        <div className="dash-insight">
          <div className="dash-insight-icon" style={{ background: 'var(--rose-50)', color: 'var(--rose-400)' }}>
            <Lightbulb size={16} />
          </div>
          <div className="dash-insight-text">
            <strong>Top unmet need:</strong> 34% of users cite schedule rigidity as their primary obstacle when managing health symptoms at work. Consider piloting a flexible hours policy.
          </div>
        </div>
        <div className="dash-insight">
          <div className="dash-insight-icon" style={{ background: 'var(--sage-50)', color: 'var(--sage-400)' }}>
            <TrendingUp size={16} />
          </div>
          <div className="dash-insight-text">
            <strong>Positive trend:</strong> Since Bloom's launch, the number of employees accessing the occupational health service has increased by 18% — suggesting that the agent successfully bridges the gap between awareness and action.
          </div>
        </div>
        <div className="dash-insight">
          <div className="dash-insight-icon" style={{ background: 'var(--lav-50)', color: 'var(--lav-600)' }}>
            <Clock size={16} />
          </div>
          <div className="dash-insight-text">
            <strong>Usage pattern:</strong> Peak usage occurs between 7-9 AM and 9-11 PM — outside of work hours. This confirms that employees value privacy and prefer consulting the agent when they're alone.
          </div>
        </div>
      </div>

      <div className="dash-section">
        <h3>Policy tools</h3>
        <div className="dash-policy-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="dash-insight-icon" style={{ background: 'var(--rose-50)', color: 'var(--rose-400)' }}>
              <FileText size={16} />
            </div>
            <div className="dash-policy-info">
              <h4>Menstrual health charter</h4>
              <p>Generate a policy adapted to your company agreement and local law</p>
            </div>
          </div>
          <button className="dash-policy-btn">Generate</button>
        </div>
        <div className="dash-policy-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="dash-insight-icon" style={{ background: 'var(--sage-50)', color: 'var(--sage-400)' }}>
              <FileText size={16} />
            </div>
            <div className="dash-policy-info">
              <h4>Menopause action plan</h4>
              <p>Based on the Rist Report recommendations and your company context</p>
            </div>
          </div>
          <button className="dash-policy-btn">Generate</button>
        </div>
        <div className="dash-policy-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="dash-insight-icon" style={{ background: 'var(--lav-50)', color: 'var(--lav-600)' }}>
              <GraduationCap size={16} />
            </div>
            <div className="dash-policy-info">
              <h4>Manager training module</h4>
              <p>Interactive conversation simulations — what to say, what not to say</p>
            </div>
          </div>
          <button className="dash-policy-btn">Launch</button>
        </div>
        <div className="dash-policy-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="dash-insight-icon" style={{ background: 'var(--amber-50)', color: 'var(--amber-600)' }}>
              <Users size={16} />
            </div>
            <div className="dash-policy-info">
              <h4>Sector benchmark</h4>
              <p>Compare your policies with industry leaders (anonymized)</p>
            </div>
          </div>
          <button className="dash-policy-btn">View</button>
        </div>
      </div>
    </div>
  );
}
