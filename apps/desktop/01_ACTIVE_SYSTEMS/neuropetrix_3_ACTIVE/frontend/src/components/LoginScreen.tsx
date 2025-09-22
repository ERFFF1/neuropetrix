import React, { useState } from 'react';
import { User } from '../types';

interface LoginScreenProps {
  onLogin: (username: string, password: string) => void;
  error: string | null;
}

const mockUsers: User[] = [
  { id: '1', name: 'Dr. Ahmet Yılmaz', email: 'ahmet@hospital.com', role: 'doctor' },
  { id: '2', name: 'Dr. Ayşe Kaya', email: 'ayse@hospital.com', role: 'radiologist' },
  { id: '3', name: 'Admin User', email: 'admin@hospital.com', role: 'admin' },
];

const LoginScreen: React.FC<LoginScreenProps> = ({ onLogin, error }) => {
  const [selectedUser, setSelectedUser] = useState<User | mockUsers[0]>(mockUsers[0]);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      // Mock login - in real app, this would be actual credentials
      const username = selectedUser.email.split('@')[0];
      const password = 'password123'; // Mock password
      await onLogin(username, password);
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
            <span className="text-2xl">🏥</span>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            NeuroPETRIX
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Klinik Karar Destek Sistemi
          </p>
        </div>
        
        <div className="mt-8 space-y-6">
          <div>
            <label htmlFor="user-select" className="block text-sm font-medium text-gray-700">
              Kullanıcı Seçin
            </label>
            <select
              id="user-select"
              value={selectedUser.id}
              onChange={(e) => {
                const user = mockUsers.find(u => u.id === e.target.value);
                if (user) setSelectedUser(user);
              }}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              {mockUsers.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.role})
                </option>
              ))}
            </select>
          </div>

          <div>
            <button
              onClick={handleLogin}
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Giriş yapılıyor...
                </div>
              ) : (
                'Giriş Yap'
              )}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-red-400">⚠️</span>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="text-center">
            <p className="text-xs text-gray-500">
              Demo için kullanıcı seçin ve giriş yapın
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;
