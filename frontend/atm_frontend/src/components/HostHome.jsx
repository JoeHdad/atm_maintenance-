import React, { useState, useEffect } from 'react';
import { hostAPI } from '../api/host';
import { useAuth } from '../context/AuthContext';

const HostHome = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState({ show: false, technician: null });
  const [deleting, setDeleting] = useState(false);
  const { user } = useAuth();

  console.log('[HostHome] Rendering - loading:', loading, 'stats:', stats, 'error:', error);

  useEffect(() => {
    console.log('[HostHome] useEffect - fetching dashboard stats');
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await hostAPI.getDashboardStats();
      setStats(data);
    } catch (err) {
      setError(err.error || 'Failed to load dashboard statistics');
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (technician) => {
    setDeleteConfirm({ show: true, technician });
  };

  const handleDeleteCancel = () => {
    setDeleteConfirm({ show: false, technician: null });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm.technician) return;

    try {
      setDeleting(true);
      setError('');
      
      await hostAPI.deleteTechnician(deleteConfirm.technician.id);
      
      // Update stats by removing the deleted technician from the list
      setStats(prevStats => ({
        ...prevStats,
        total_technicians: prevStats.total_technicians - 1,
        technicians_with_devices: prevStats.technicians_with_devices.filter(
          tech => tech.id !== deleteConfirm.technician.id
        )
      }));
      
      setDeleteConfirm({ show: false, technician: null });
    } catch (err) {
      setError(err.error || 'Failed to delete technician');
      console.error('Error deleting technician:', err);
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <p className="font-medium">Error loading dashboard</p>
        <p className="text-sm mt-1">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm sm:text-base text-gray-600 mt-1 sm:mt-2">Welcome to the Data Host Portal</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
        {/* Total Technicians Card */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-4 sm:p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-xs sm:text-sm font-medium">Total Technicians</p>
              <p className="text-3xl sm:text-4xl font-bold mt-1 sm:mt-2">{stats?.total_technicians || 0}</p>
            </div>
            <div className="bg-blue-400 bg-opacity-30 rounded-full p-3 sm:p-4">
              <svg className="w-6 h-6 sm:w-8 sm:h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Total Devices Card */}
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-4 sm:p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-xs sm:text-sm font-medium">Total Devices</p>
              <p className="text-3xl sm:text-4xl font-bold mt-1 sm:mt-2">{stats?.total_devices || 0}</p>
            </div>
            <div className="bg-green-400 bg-opacity-30 rounded-full p-3 sm:p-4">
              <svg className="w-6 h-6 sm:w-8 sm:h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Technicians Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200">
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900">Recent Technicians</h2>
          <p className="text-xs sm:text-sm text-gray-600 mt-1">Latest technician accounts with device assignments</p>
        </div>
        <div className="overflow-x-auto">
          {stats?.technicians_with_devices && stats.technicians_with_devices.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Username
                  </th>
                  <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">
                    City
                  </th>
                  <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Devices
                  </th>
                  <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">
                    Created At
                  </th>
                  <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {stats.technicians_with_devices.map((tech) => (
                  <tr key={tech.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 sm:h-10 sm:w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-semibold text-xs sm:text-sm">
                            {tech.username.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="ml-2 sm:ml-4 min-w-0">
                          <div className="text-xs sm:text-sm font-medium text-gray-900 truncate">{tech.username}</div>
                          <div className="text-xs text-gray-500 sm:hidden truncate">{tech.city}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap hidden sm:table-cell">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                        {tech.city}
                      </span>
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className={`text-xs sm:text-sm font-semibold ${tech.device_count > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                          {tech.device_count}
                        </span>
                        <span className="text-xs text-gray-500 ml-1 hidden sm:inline">devices</span>
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500 hidden md:table-cell">
                      {formatDate(tech.created_at)}
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap text-right">
                      <button
                        onClick={() => handleDeleteClick(tech)}
                        className="text-red-600 hover:text-red-900 font-medium text-xs sm:text-sm transition-colors"
                        title="Delete technician"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="px-4 sm:px-6 py-8 sm:py-12 text-center">
              <svg className="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <p className="mt-2 text-xs sm:text-sm text-gray-500">No technicians found</p>
              <p className="text-xs text-gray-400 mt-1">Create your first technician account to get started</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions - Only show for hosts, not supervisors */}
      {user?.role === 'host' && (
        <div className="bg-white rounded-lg shadow p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <a
              href="/host-dashboard/create-technician"
              className="flex items-center p-3 sm:p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-colors touch-manipulation"
            >
              <div className="bg-blue-100 rounded-full p-2 sm:p-3 flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </div>
              <div className="ml-3 sm:ml-4 min-w-0">
                <p className="font-semibold text-gray-900 text-sm sm:text-base">Create Technician</p>
                <p className="text-xs sm:text-sm text-gray-600 truncate">Add a new technician account</p>
              </div>
            </a>
            <a
              href="/host-dashboard/upload-devices"
              className="flex items-center p-3 sm:p-4 border-2 border-green-200 rounded-lg hover:border-green-400 hover:bg-green-50 transition-colors touch-manipulation"
            >
              <div className="bg-green-100 rounded-full p-2 sm:p-3 flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div className="ml-3 sm:ml-4 min-w-0">
                <p className="font-semibold text-gray-900 text-sm sm:text-base">Upload Devices</p>
                <p className="text-xs sm:text-sm text-gray-600 truncate">Import devices from Excel</p>
              </div>
            </a>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deleteConfirm.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">
              Delete Technician?
            </h3>
            <p className="text-sm text-gray-600 text-center mb-6">
              Are you sure you want to delete <span className="font-semibold">{deleteConfirm.technician?.username}</span>?
              <br />
              <span className="text-red-600 font-medium">This will permanently delete all related data including:</span>
              <br />
              • Device assignments
              <br />
              • Maintenance submissions
              <br />
              • Uploaded photos and PDFs
              <br />
              • Excel files
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleDeleteCancel}
                disabled={deleting}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={deleting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {deleting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Deleting...
                  </>
                ) : (
                  'Delete'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HostHome;
