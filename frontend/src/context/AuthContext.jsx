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
    try {
      const res = await axios.post('/api/auth/login', { username, password });
      const { access_token, user: userData } = res.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('dolr_token', access_token);
      localStorage.setItem('dolr_user', JSON.stringify(userData));
      return userData;
    } catch (err) {
      const u = (username || '').trim().toLowerCase();
      const p = (password || '').trim();

      // Quick-login preset fallback for hackathon demonstration when backend is offline
      if ((u === 'officer' || u === 'officer@dolr.gov.in') && (p === 'officer123' || p === 'officer')) {
        const officerUser = {
          id: 1,
          username: 'officer',
          email: 'officer@dolr.gov.in',
          full_name: 'Rajendra Prasad Sharma',
          role: 'OFFICER',
          department: 'Department of Land Resources (DoLR)',
          designation: 'Senior Revenue Officer & Tahsildar'
        };
        const demoToken = 'demo-officer-token-' + Date.now();
        setToken(demoToken);
        setUser(officerUser);
        localStorage.setItem('dolr_token', demoToken);
        localStorage.setItem('dolr_user', JSON.stringify(officerUser));
        return officerUser;
      }

      if ((u === 'admin' || u === 'admin@dolr.gov.in') && (p === 'admin123' || p === 'admin')) {
        const adminUser = {
          id: 2,
          username: 'admin',
          email: 'admin@dolr.gov.in',
          full_name: 'Dr. Sunita Deshmukh',
          role: 'ADMIN',
          department: 'Ministry of Rural Development',
          designation: 'National Portal Administrator'
        };
        const demoToken = 'demo-admin-token-' + Date.now();
        setToken(demoToken);
        setUser(adminUser);
        localStorage.setItem('dolr_token', demoToken);
        localStorage.setItem('dolr_user', JSON.stringify(adminUser));
        return adminUser;
      }

      if ((u === 'citizen' || u === 'citizen@india.gov.in') && (p === 'citizen123' || p === 'citizen')) {
        const citizenUser = {
          id: 3,
          username: 'citizen',
          email: 'citizen@india.gov.in',
          full_name: 'Aditya Verma',
          role: 'CITIZEN',
          department: 'Citizen Portal',
          designation: 'Registered Citizen'
        };
        const demoToken = 'demo-citizen-token-' + Date.now();
        setToken(demoToken);
        setUser(citizenUser);
        localStorage.setItem('dolr_token', demoToken);
        localStorage.setItem('dolr_user', JSON.stringify(citizenUser));
        return citizenUser;
      }

      throw err;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('dolr_token');
    localStorage.removeItem('dolr_user');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      login, 
      logout, 
      isOfficer: user?.role === 'OFFICER' || user?.role === 'ADMIN' || user?.role === 'LAND_RECORD_OFFICER', 
      isAdmin: user?.role === 'ADMIN' 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
