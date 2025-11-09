import React, { useState } from 'react';
import SupervisorSidebar from './SupervisorSidebar';
import logoPng from '../logo.png';

const SupervisorLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 z-50">
        <SupervisorSidebar onClose={() => setSidebarOpen(false)} />
      </aside>

      {/* Sidebar - Mobile */}
      <aside
        className={`fixed inset-y-0 left-0 w-64 z-50 transform transition-transform duration-300 ease-in-out lg:hidden ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <SupervisorSidebar onClose={() => setSidebarOpen(false)} />
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:ml-64">
        {/* Top Bar - Mobile */}
        <header className="lg:hidden bg-white shadow-sm z-30 sticky top-0">
          <div className="flex items-center justify-between px-4 py-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg text-gray-600 hover:bg-gray-100"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="flex items-center gap-2">
              <img src={logoPng} alt="ATM SNB" className="w-8 h-8 rounded-lg bg-blue-600/10 p-1" />
              <span className="font-bold text-gray-900">ATM SNB</span>
            </div>
            <div className="w-10"></div> {/* Spacer for centering */}
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default SupervisorLayout;
