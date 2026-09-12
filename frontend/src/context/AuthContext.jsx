import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('dolr_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('dolr_token') || null);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  const login = async (username, password) => {
    const res = await axios.post('/api/auth/login', { username, password });
    const { access_token, user: userData } = res.data;
    setToken(access_token);
    setUser(userData);
    localStorage.setItem('dolr_token', access_token);
    localStorage.setItem('dolr_user', JSON.stringify(userData));
    return userData;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('dolr_token');
    localStorage.removeItem('dolr_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isOfficer: user?.role === 'OFFICER' || user?.role === 'ADMIN', isAdmin: user?.role === 'ADMIN' }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
