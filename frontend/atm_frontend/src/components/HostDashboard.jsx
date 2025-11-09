import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Sidebar from './Sidebar';

const HostDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  console.log('[HostDashboard] Rendering - user:', user);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed lg:static inset-y-0 left-0 z-30 transform ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0 transition-transform duration-300 ease-in-out`}>
        <Sidebar onClose={() => setSidebarOpen(false)} />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden w-full">
        {/* Top Navigation Bar */}
        <header className="bg-white shadow-sm">
          <div className="flex items-center justify-between px-3 sm:px-4 md:px-6 py-3 sm:py-4">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 touch-manipulation"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="hidden lg:block">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-800">
                {user?.role === 'supervisor' ? 'Admin Portal' : 'Data Host Portal'}
              </h2>
              <p className="text-xs sm:text-sm text-gray-600 hidden sm:block">
                {user?.role === 'supervisor' 
                  ? 'Monitor technicians and system activity' 
                  : 'Manage technicians and devices'}
              </p>
            </div>
            <div className="flex items-center gap-2 sm:gap-3 md:gap-4 ml-auto">
              {/* User Info */}
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="text-right hidden sm:block">
                  <p className="text-xs sm:text-sm font-medium text-gray-900 truncate max-w-[120px]">{user?.username}</p>
                  <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                </div>
                <div className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                  <span className="text-white font-semibold text-xs sm:text-sm">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 md:px-4 py-1.5 sm:py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors touch-manipulation"
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="text-xs sm:text-sm">Logout</span>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-3 sm:p-4 md:p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default HostDashboard;
