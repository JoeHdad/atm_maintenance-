import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDashboardStats } from '../api/supervisor';

const SupervisorDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_submissions: 0,
    pending_submissions: 0,
    approved_submissions: 0,
    rejected_submissions: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await getDashboardStats();
      setStats(data);
      setError('');
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Submissions',
      value: stats.total_submissions,
      textColor: 'text-blue-600'
    },
    {
      title: 'Pending Review',
      value: stats.pending_submissions,
      textColor: 'text-orange-600'
    },
    {
      title: 'Approved',
      value: stats.approved_submissions,
      textColor: 'text-green-600'
    },
    {
      title: 'Rejected',
      value: stats.rejected_submissions,
      textColor: 'text-red-600'
    }
  ];


  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome to the Supervisor Panel</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, index) => (
          <div
            key={index}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className={`text-3xl font-bold ${card.textColor} mb-1`}>
              {card.value}
            </div>
            <div className="text-sm text-gray-600">{card.title}</div>
          </div>
        ))}
      </div>

      {/* Recent Activity Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">System Overview</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-gray-900">Total Submissions</p>
                <p className="text-sm text-gray-600">All time submissions</p>
              </div>
            </div>
            <span className="text-2xl font-bold text-blue-600">{stats.total_submissions}</span>
          </div>

          {stats.pending_submissions > 0 && (
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Pending Review</p>
                  <p className="text-sm text-gray-600">Requires your attention</p>
                </div>
              </div>
              <span className="text-2xl font-bold text-orange-600">{stats.pending_submissions}</span>
            </div>
          )}

          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-gray-900">Approval Rate</p>
                <p className="text-sm text-gray-600">Approved submissions</p>
              </div>
            </div>
            <span className="text-2xl font-bold text-green-600">
              {stats.total_submissions > 0 
                ? Math.round((stats.approved_submissions / stats.total_submissions) * 100)
                : 0}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupervisorDashboard;
