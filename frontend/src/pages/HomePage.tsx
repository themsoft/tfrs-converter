import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileUpload } from '../components/upload/FileUpload';
import { MizanTable } from '../components/mizan/MizanTable';
import { MappingView } from '../components/mapping/MappingView';
import { useSession } from '../context/SessionContext';
import { api } from '../utils/api';
import { ArrowRight, FileSpreadsheet, GitBranch, BarChart3, Shield, Zap, Globe } from 'lucide-react';
import { mockMappedAccounts, mockUnmappedAccounts, mockUploadResponse } from '../utils/mockData';

export function HomePage() {
  const { sessionId, mizanData, setMizanData, setSessionId, setFileName, setUploadStats } = useSession();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'upload' | 'mizan' | 'mapping'>('upload');

  // When sessionId is set, show mizan tab
  useEffect(() => {
    if (sessionId && activeTab === 'upload') {
      setActiveTab('mizan');
    }
  }, [sessionId, activeTab]);

  // Load mapping data when session exists and mizan is empty
  useEffect(() => {
    if (sessionId && mizanData.length === 0) {
      api.getMapping(sessionId).then(result => {
        setMizanData([...result.mapped, ...result.unmapped]);
      }).catch(() => {
        // Fallback: if API fails, keep empty
      });
    }
  }, [sessionId, mizanData.length, setMizanData]);

  // Quick demo loader
  const loadDemo = () => {
    setSessionId('mock-session-001');
    setMizanData([...mockMappedAccounts, ...mockUnmappedAccounts]);
    setFileName('ornek_mizan_2025.xlsx');
    setUploadStats(mockUploadResponse.statistics);
    setActiveTab('mizan');
  };

  return (
    <div className="space-y-6">
      {/* Hero Section (when no session) */}
      {!sessionId && (
        <div className="text-center py-8">
          <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-3 animate-fade-in-up">
            TDHP Mizanınızı <span className="text-[var(--accent)]">UFRS</span>'ye Dönüştürün
          </h2>
          <p className="text-[var(--text-secondary)] max-w-2xl mx-auto mb-8 animate-fade-in-up stagger-1">
            Mizan dosyanızı yükleyin, otomatik eşleştirme ve UFRS düzeltme kayıtlarını görün,
            profesyonel finansal raporlarınızı oluşturun.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto mb-8">
            <FeatureCard
              icon={<Zap className="w-6 h-6 text-[var(--accent)]" />}
              title="Hızlı Dönüşüm"
              desc="Mizanınızı yükleyin, anında UFRS eşleştirmesi yapın"
              className="animate-fade-in-up stagger-2"
            />
            <FeatureCard
              icon={<Shield className="w-6 h-6 text-[var(--success)]" />}
              title="Standartlara Uygun"
              desc="IAS/IFRS standartlarına uygun düzeltme kayıtları"
              className="animate-fade-in-up stagger-3"
            />
            <FeatureCard
              icon={<Globe className="w-6 h-6 text-[var(--info)]" />}
              title="Detaylı Raporlama"
              desc="Bilanço, gelir tablosu ve karşılaştırmalı analizler"
              className="animate-fade-in-up stagger-4"
            />
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      {sessionId && (
        <div className="flex items-center gap-2 border-b border-[var(--border-color)] pb-1 animate-fade-in">
          <TabButton
            active={activeTab === 'upload'}
            onClick={() => setActiveTab('upload')}
            icon={<FileSpreadsheet className="w-4 h-4" />}
            label="Dosya Yükleme"
          />
          <TabButton
            active={activeTab === 'mizan'}
            onClick={() => setActiveTab('mizan')}
            icon={<BarChart3 className="w-4 h-4" />}
            label="Mizan"
          />
          <TabButton
            active={activeTab === 'mapping'}
            onClick={() => setActiveTab('mapping')}
            icon={<GitBranch className="w-4 h-4" />}
            label="Eşleştirme"
          />
          <div className="ml-auto">
            <button
              onClick={() => navigate(`/reports/${sessionId}`)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--accent)] text-white text-sm font-medium hover:bg-[var(--accent-dark)] transition-all duration-200 cursor-pointer border-none hover:shadow-[0_0_12px_rgba(245,158,11,0.3)]"
            >
              Raporlara Git
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="animate-fade-in" key={activeTab}>
        {activeTab === 'upload' && (
          <div className="space-y-4">
            <FileUpload />
            {!sessionId && (
              <div className="text-center">
                <button
                  onClick={loadDemo}
                  className="text-sm text-[var(--accent)] hover:text-[var(--accent-dark)] underline underline-offset-2 cursor-pointer bg-transparent border-none"
                >
                  veya örnek veri ile deneyin
                </button>
              </div>
            )}
          </div>
        )}
        {activeTab === 'mizan' && mizanData.length > 0 && <MizanTable data={mizanData} />}
        {activeTab === 'mapping' && <MappingView />}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: {
  active: boolean; onClick: () => void; icon: React.ReactNode; label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium border-b-2 transition-all duration-200 cursor-pointer bg-transparent border-t-0 border-x-0 ${
        active
          ? 'border-b-[var(--accent)] text-[var(--accent)]'
          : 'border-b-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
      }`}
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </button>
  );
}

function FeatureCard({ icon, title, desc, className = '' }: { icon: React.ReactNode; title: string; desc: string; className?: string }) {
  return (
    <div className={`p-5 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] text-center transition-all duration-300 hover:scale-[1.03] hover:shadow-[0_0_20px_rgba(245,158,11,0.15)] ${className}`} style={{ boxShadow: 'var(--shadow-sm)' }}>
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-[var(--bg-tertiary)] mb-3">
        {icon}
      </div>
      <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-1">{title}</h3>
      <p className="text-xs text-[var(--text-muted)]">{desc}</p>
    </div>
  );
}
