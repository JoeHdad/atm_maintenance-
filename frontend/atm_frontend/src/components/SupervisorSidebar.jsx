import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logoPng from '../logo.png';

const SupervisorSidebar = ({ onClose }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLinkClick = () => {
    // Close sidebar on mobile when a link is clicked
    if (onClose) {
      onClose();
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    {
      name: 'Dashboard',
      path: '/supervisor/dashboard',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      )
    },
    {
      name: 'Submissions',
      path: '/supervisor/submissions',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )
    }
  ];

  const isActive = (path) => {
    if (path === '/supervisor/dashboard') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      {/* Logo/Header */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <img
            src={logoPng}
            alt="ATM SNB logo"
            className="w-10 h-auto object-contain rounded-lg bg-white/5 p-1"
            loading="lazy"
          />
          <div>
            <h1 className="text-lg font-bold">ATM SNB</h1>
            <p className="text-xs text-gray-400">Supervisor Panel</p>
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            onClick={handleLinkClick}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
              isActive(item.path)
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
            }`}
          >
            {item.icon}
            <span className="font-medium">{item.name}</span>
            {isActive(item.path) && (
              <div className="ml-auto w-2 h-2 bg-white rounded-full"></div>
            )}
          </Link>
        ))}
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-gray-700">
        <div className="mb-3 px-4 py-2 bg-gray-700 rounded-lg">
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="text-gray-300">Supervisor</span>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-red-600 hover:text-white transition-all duration-200"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default SupervisorSidebar;
