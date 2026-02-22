import { useState, useRef, useCallback } from 'react';
import { Upload, FileSpreadsheet, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../../utils/api';
import { useSession } from '../../context/SessionContext';

const ACCEPTED_TYPES = [
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'text/csv',
];
const ACCEPTED_EXTS = ['.xlsx', '.xls', '.csv'];

export function FileUpload() {
  const { setSessionId, setMizanData, setFileName, setUploadStats } = useSession();
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [uploadInfo, setUploadInfo] = useState<{ totalRows: number; mappingRate: number } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (file: File) => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ACCEPTED_EXTS.includes(ext) && !ACCEPTED_TYPES.includes(file.type)) {
      setError('Lütfen .xlsx, .xls veya .csv dosyası yükleyin.');
      return;
    }

    setError(null);
    setUploading(true);
    setUploadInfo(null);

    try {
      const result = await api.upload(file);
      setSessionId(result.session_id);
      setMizanData([]);
      setFileName(file.name);
      setUploadedFile(file.name);
      setUploadStats(result.statistics);
      setUploadInfo({
        totalRows: result.total_rows,
        mappingRate: result.statistics.mapping_rate,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Dosya yüklenirken bir hata oluştu.');
    } finally {
      setUploading(false);
    }
  }, [setSessionId, setMizanData, setFileName, setUploadStats]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const onInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const reset = () => {
    setUploadedFile(null);
    setUploadInfo(null);
    setError(null);
    setSessionId(null);
    setMizanData([]);
    setFileName(null);
    setUploadStats(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      {!uploadedFile && !uploading && (
        <div
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onClick={() => inputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-300 glass ${
            dragOver
              ? 'border-[var(--accent)] animate-pulse-glow scale-[1.01]'
              : 'border-[var(--border-color)] hover:border-[var(--border-hover)] hover:bg-[var(--bg-hover)]'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={onInputChange}
            className="hidden"
          />
          <div className="flex flex-col items-center gap-3">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors ${
              dragOver ? 'bg-[var(--accent)]' : 'bg-[var(--bg-tertiary)]'
            }`}>
              <Upload className={`w-7 h-7 ${dragOver ? 'text-white' : 'text-[var(--text-muted)]'}`} />
            </div>
            <div>
              <p className="text-base font-medium text-[var(--text-primary)]">
                Mizan dosyanızı sürükleyip bırakın
              </p>
              <p className="text-sm text-[var(--text-muted)] mt-1">
                veya dosya seçmek için tıklayın
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span>Excel (.xlsx, .xls) veya CSV (.csv)</span>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {uploading && (
        <div className="p-6 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] animate-fade-in">
          <div className="flex items-center justify-center gap-3">
            <Loader2 className="w-6 h-6 text-[var(--accent)] animate-spin" />
            <span className="text-sm font-medium text-[var(--text-primary)]">Dosya yükleniyor ve analiz ediliyor...</span>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 p-4 rounded-xl bg-[var(--error-light)] border border-[var(--error)] animate-scale-in">
          <AlertCircle className="w-5 h-5 text-[var(--error)] shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-[var(--error)]">Hata</p>
            <p className="text-sm text-[var(--error)] opacity-80">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-[var(--error)] hover:opacity-70 cursor-pointer bg-transparent border-none">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Success */}
      {uploadedFile && !uploading && (
        <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden animate-scale-in">
          <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-color)] bg-[var(--success-light)]">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-6 h-6 text-[var(--success)]" />
              <div>
                <span className="text-sm font-medium text-[var(--success)]">
                  Dosya başarıyla yüklendi
                </span>
                <span className="text-xs text-[var(--text-muted)] ml-2">
                  ({uploadedFile})
                </span>
              </div>
            </div>
            <button
              onClick={reset}
              className="text-xs text-[var(--text-muted)] hover:text-[var(--error)] cursor-pointer bg-transparent border-none flex items-center gap-1"
            >
              <X className="w-3.5 h-3.5" />
              Kaldır
            </button>
          </div>

          {/* Upload Stats */}
          {uploadInfo && (
            <div className="px-5 py-4 flex flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[var(--info)]" />
                <span className="text-sm text-[var(--text-secondary)]">
                  <strong className="text-[var(--text-primary)]">{uploadInfo.totalRows}</strong> hesap yüklendi
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[var(--success)]" />
                <span className="text-sm text-[var(--text-secondary)]">
                  <strong className="text-[var(--text-primary)]">%{uploadInfo.mappingRate.toFixed(1)}</strong> eşleşme oranı
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
