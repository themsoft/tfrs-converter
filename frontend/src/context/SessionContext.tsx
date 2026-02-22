import { createContext, useContext, useState, type ReactNode } from 'react';
import type { MappedAccount, UploadStatistics } from '../types';

interface SessionContextValue {
  sessionId: string | null;
  setSessionId: (id: string | null) => void;
  mizanData: MappedAccount[];
  setMizanData: (data: MappedAccount[]) => void;
  fileName: string | null;
  setFileName: (name: string | null) => void;
  uploadStats: UploadStatistics | null;
  setUploadStats: (stats: UploadStatistics | null) => void;
}

const SessionContext = createContext<SessionContextValue | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [mizanData, setMizanData] = useState<MappedAccount[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const [uploadStats, setUploadStats] = useState<UploadStatistics | null>(null);

  return (
    <SessionContext.Provider value={{
      sessionId, setSessionId,
      mizanData, setMizanData,
      fileName, setFileName,
      uploadStats, setUploadStats,
    }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession must be used within SessionProvider');
  return ctx;
}
