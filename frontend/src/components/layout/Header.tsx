import { Sun, Moon, FileSpreadsheet } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useSession } from '../../context/SessionContext';
import { useNavigate, useLocation } from 'react-router-dom';

export function Header() {
  const { theme, toggleTheme } = useTheme();
  const { sessionId, fileName } = useSession();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <header
      className="sticky top-0 z-50 border-b border-[var(--border-color)] bg-[var(--bg-card)]"
      style={{ boxShadow: 'var(--shadow-sm)' }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity cursor-pointer bg-transparent border-none group"
          >
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--accent-dark)] flex items-center justify-center transition-shadow group-hover:shadow-[0_0_16px_rgba(245,158,11,0.4)]">
              <FileSpreadsheet className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-[var(--text-primary)] leading-tight">
                TFRS Dönüştürücü
              </h1>
              <p className="text-[10px] text-[var(--text-muted)] leading-tight">
                TDHP → UFRS Dönüşüm Aracı
              </p>
            </div>
          </button>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {sessionId && (
              <>
                <NavButton
                  active={location.pathname === '/'}
                  onClick={() => navigate('/')}
                >
                  Mizan
                </NavButton>
                <NavButton
                  active={location.pathname === `/reports/${sessionId}`}
                  onClick={() => navigate(`/reports/${sessionId}`)}
                >
                  Raporlar
                </NavButton>
              </>
            )}
          </nav>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {fileName && (
              <span className="hidden sm:inline-flex items-center gap-1.5 text-xs text-[var(--text-muted)] bg-[var(--bg-tertiary)] px-3 py-1.5 rounded-full">
                <FileSpreadsheet className="w-3.5 h-3.5" />
                {fileName}
              </span>
            )}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-colors text-[var(--text-secondary)] cursor-pointer border-none bg-transparent"
              title={theme === 'dark' ? 'Açık temaya geç' : 'Koyu temaya geç'}
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

function NavButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer border-none ${
        active
          ? 'bg-[var(--accent-light)] text-[var(--accent-dark)]'
          : 'text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:translate-y-[-1px] bg-transparent'
      }`}
    >
      {children}
    </button>
  );
}
