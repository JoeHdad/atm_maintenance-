import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logoPng from '../logo.png';

const Sidebar = ({ onClose }) => {
  const location = useLocation();
  const { user } = useAuth();

  const handleLinkClick = () => {
    // Close sidebar on mobile when a link is clicked
    if (onClose) {
      onClose();
    }
  };

  // All menu items with role restrictions
  const allMenuItems = [
    {
      path: '/host-dashboard',
      label: 'Dashboard Home',
      roles: ['host', 'supervisor'], // Both can view dashboard
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
    },
    {
      path: '/host-dashboard/create-technician',
      label: 'Create Technician',
      roles: ['host'], // Only host can create technicians
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
      ),
    },
    {
      path: '/host-dashboard/upload-devices',
      label: 'Upload Devices',
      roles: ['host'], // Only host can upload devices
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      ),
    },
  ];

  // Filter menu items based on user role
  const menuItems = allMenuItems.filter(item => 
    item.roles.includes(user?.role)
  );

  const isActive = (path) => {
    if (path === '/host-dashboard') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="w-64 bg-gray-800 text-white min-h-screen flex flex-col">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <img
            src={logoPng}
            alt="ATM SNB logo"
            className="h-10 w-auto object-contain rounded-lg bg-white/5 p-1"
            loading="lazy"
          />
          <h1 className="text-2xl font-bold text-blue-400">ATM SNB</h1>
        </div>
        <p className="text-sm text-gray-400 mt-1">
          {user?.role === 'supervisor' ? 'Admin Portal' : 'Data Host Portal'}
        </p>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                onClick={handleLinkClick}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200 ${
                  isActive(item.path)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                {item.icon}
                <span className="font-medium">{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700">
        <p className="text-xs text-gray-500 text-center">
          © 2025 ATM SNB
        </p>
      </div>
    </div>
  );
};

export default Sidebar;
