import { MoonStar, Heart, Leaf, Ribbon } from 'lucide-react';
import { MODULES } from '../data/modules';

const ICONS = { MoonStar, Heart, Leaf, Ribbon };

export default function ModuleNav({ activeModule, onModuleChange }) {
  return (
    <nav className="module-nav" aria-label="Health modules">
      {MODULES.map((mod) => {
        const Icon = ICONS[mod.icon];
        const isActive = activeModule === mod.id;
        return (
          <button
            key={mod.id}
            className={`module-tab ${isActive ? 'active' : ''}`}
            onClick={() => onModuleChange(mod.id)}
            aria-current={isActive ? 'true' : undefined}
            style={isActive ? { background: mod.bg, borderColor: mod.color } : {}}
          >
            <div
              className="module-tab-icon"
              style={{ background: isActive ? mod.color : mod.bg, color: isActive ? '#fff' : mod.color }}
            >
              <Icon size={16} />
            </div>
            <span style={isActive ? { color: mod.activeColor } : {}}>{mod.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
