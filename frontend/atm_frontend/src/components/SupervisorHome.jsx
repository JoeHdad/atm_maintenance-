import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supervisorAPI } from '../api/supervisor';

const SupervisorHome = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await supervisorAPI.getSubmissions({});
      
      if (data.submissions) {
        const submissions = data.submissions;
        setStats({
          total: submissions.length,
          pending: submissions.filter(s => s.status === 'Pending').length,
          approved: submissions.filter(s => s.status === 'Approved').length,
          rejected: submissions.filter(s => s.status === 'Rejected').length
        });
      }
    } catch (err) {
      setError(err.error || 'Failed to load statistics');
      console.error('Error fetching statistics:', err);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, count, color }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="text-sm text-gray-600 mb-1">{title}</div>
      <div className={`text-3xl font-bold ${color}`}>{count}</div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Submissions" count={stats.total} color="text-gray-900" />
        <StatCard title="Pending Review" count={stats.pending} color="text-orange-500" />
        <StatCard title="Approved" count={stats.approved} color="text-green-500" />
        <StatCard title="Rejected" count={stats.rejected} color="text-red-500" />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Quick Action */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Quick Actions</h2>
        <p className="text-gray-600 mb-4">Manage technician submissions</p>
        <button
          onClick={() => navigate('/supervisor/submissions')}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          View All Submissions
        </button>
      </div>
    </div>
  );
};

export default SupervisorHome;
