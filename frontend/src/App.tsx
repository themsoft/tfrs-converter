import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { SessionProvider } from './context/SessionContext';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage';
import { ReportsPage } from './pages/ReportsPage';

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <SessionProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/reports/:sessionId" element={<ReportsPage />} />
            </Routes>
          </Layout>
        </SessionProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
