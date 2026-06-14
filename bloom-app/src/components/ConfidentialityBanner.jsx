import { ShieldCheck } from 'lucide-react';

export default function ConfidentialityBanner() {
  return (
    <div className="shield-banner" role="status">
      <ShieldCheck size={14} />
      <span>End-to-end encrypted — your employer never sees this conversation</span>
    </div>
  );
}
