import React, { useState, useEffect } from 'react';
import { User, Case } from './types';
import { apiService } from './services/api';
import LoginScreen from './components/LoginScreen';
import CaseList from './components/CaseList';
import CaseDetail from './components/CaseDetail';
import Header from './components/Header';
import { useWebSocket } from './hooks/useWebSocket';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection
  const { isConnected, lastMessage } = useWebSocket();

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (token) {
          const currentUser = await apiService.getCurrentUser();
          setUser(currentUser);
          await loadCases();
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        apiService.logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  useEffect(() => {
    // Handle WebSocket messages
    if (lastMessage) {
      switch (lastMessage.type) {
        case 'case_update':
          handleCaseUpdate(lastMessage.data);
          break;
        case 'analysis_progress':
          handleAnalysisProgress(lastMessage.data);
          break;
        case 'notification':
          handleNotification(lastMessage.data);
          break;
        default:
          break;
      }
    }
  }, [lastMessage]);

  const loadCases = async () => {
    try {
      const response = await apiService.getCases();
      setCases(response.cases);
    } catch (error) {
      console.error('Failed to load cases:', error);
      setError('Vakalar yüklenirken hata oluştu');
    }
  };

  const handleLogin = async (username: string, password: string) => {
    try {
      setLoading(true);
      const { user: loggedInUser } = await apiService.login(username, password);
      setUser(loggedInUser);
      await loadCases();
    } catch (error) {
      console.error('Login failed:', error);
      setError('Giriş yapılırken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    apiService.logout();
    setUser(null);
    setCases([]);
    setSelectedCase(null);
  };

  const handleCreateCase = async (patientData: any) => {
    try {
      const newCase = await apiService.createCase(patientData);
      setCases(prev => [newCase, ...prev]);
      setSelectedCase(newCase);
    } catch (error) {
      console.error('Failed to create case:', error);
      setError('Vaka oluşturulurken hata oluştu');
    }
  };

  const handleUpdateCase = async (caseId: string, updates: Partial<Case>) => {
    try {
      const updatedCase = await apiService.updateCase(caseId, updates);
      setCases(prev => prev.map(c => c.id === caseId ? updatedCase : c));
      if (selectedCase?.id === caseId) {
        setSelectedCase(updatedCase);
      }
    } catch (error) {
      console.error('Failed to update case:', error);
      setError('Vaka güncellenirken hata oluştu');
    }
  };

  const handleCaseUpdate = (data: any) => {
    setCases(prev => prev.map(c => c.id === data.caseId ? { ...c, ...data.updates } : c));
    if (selectedCase?.id === data.caseId) {
      setSelectedCase(prev => prev ? { ...prev, ...data.updates } : null);
    }
  };

  const handleAnalysisProgress = (data: any) => {
    setCases(prev => prev.map(c => 
      c.id === data.caseId 
        ? { ...c, systemStatus: data.status, analysis: data.analysis }
        : c
    ));
  };

  const handleNotification = (data: any) => {
    // Show notification to user
    console.log('Notification:', data);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginScreen onLogin={handleLogin} error={error} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        user={user} 
        onLogout={handleLogout}
        isConnected={isConnected}
      />
      
      <div className="flex h-screen pt-16">
        <div className="w-1/3 border-r bg-white">
          <CaseList
            cases={cases}
            selectedCase={selectedCase}
            onSelectCase={setSelectedCase}
            onCreateCase={handleCreateCase}
            onUpdateCase={handleUpdateCase}
          />
        </div>
        
        <div className="flex-1">
          {selectedCase ? (
            <CaseDetail
              case={selectedCase}
              onUpdateCase={handleUpdateCase}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <div className="text-6xl mb-4">🏥</div>
                <h2 className="text-xl font-semibold mb-2">Vaka Seçin</h2>
                <p>Detayları görüntülemek için soldan bir vaka seçin</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg">
          {error}
          <button 
            onClick={() => setError(null)}
            className="ml-2 text-white hover:text-gray-200"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
