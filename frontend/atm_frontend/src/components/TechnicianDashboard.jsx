import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { technicianAPI } from '../api/technician';

const TechnicianDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [excelData, setExcelData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('All Types');
  const [statusFilter, setStatusFilter] = useState('All Status');
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetchExcelData();
  }, []);
  
  // Force refresh function
  const handleRefresh = () => {
    setLoading(true);
    fetchExcelData();
  };

  const fetchExcelData = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await technicianAPI.getMyExcelData();
      setExcelData(data);
      checkForNotifications(data);
    } catch (err) {
      setError(err.error || 'Failed to load Excel data');
      console.error('Error fetching Excel data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Check for status changes and create notifications
  const checkForNotifications = (currentData) => {
    if (!currentData || !currentData.uploads) return;

    const previousStatuses = JSON.parse(localStorage.getItem('technician_device_statuses') || '{}');
    const currentStatuses = {};
    const newNotifications = [];

    // Process current device statuses
    currentData.uploads.forEach(upload => {
      if (upload.parsed_data && upload.parsed_data.length > 0) {
        upload.parsed_data.forEach((row) => {
          if (row.device_id) {
            const deviceId = row.device_id;
            const currentStatus = row.submission_status || 'Active';
            const costCenter = String(row.col_2 || 'N/A');
            
            currentStatuses[deviceId] = currentStatus;
            
            // Check if status changed from previous state
            const previousStatus = previousStatuses[deviceId];
            if (previousStatus && previousStatus !== currentStatus) {
              // Status changed - create notification if it's approved or rejected
              if (currentStatus === 'Approved' || currentStatus === 'Rejected') {
                const action = currentStatus === 'Approved' ? 'approved' : 'rejected';
                newNotifications.push({
                  id: `${deviceId}_${Date.now()}`,
                  deviceId: deviceId,
                  costCenter: costCenter,
                  action: action,
                  timestamp: new Date().toISOString(),
                  read: false
                });
              }
            }
          }
        });
      }
    });

    // Save current statuses for next comparison
    localStorage.setItem('technician_device_statuses', JSON.stringify(currentStatuses));

    // Add new notifications
    if (newNotifications.length > 0) {
      setNotifications(prev => [...newNotifications, ...prev]);
    }
  };

  // Dismiss a notification
  const dismissNotification = (notificationId) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleViewDetails = (device) => {
    // Use interaction_id or gfm_cost_center as the device identifier
    const deviceId = device.interaction_id || device.gfm_cost_center || device.col_1 || device.col_2;
    if (deviceId && deviceId !== 'N/A') {
      navigate(`/technician/device/${deviceId}`);
    } else {
      setError('Cannot view details: Device ID not found');
    }
  };

  // Get all devices from all uploads
  const getAllDevices = () => {
    if (!excelData || !excelData.uploads) return [];
    
    const allDevices = [];
    excelData.uploads.forEach(upload => {
      if (upload.parsed_data && upload.parsed_data.length > 0) {
        // Skip header row (first row) and process data rows
        upload.parsed_data.forEach((row, index) => {
          // Skip rows without a valid device_id (includes header rows)
          if (!row.device_id) {
            return; // Skip rows without device_id
          }
          
          // Map Excel columns to device fields based on actual Excel structure:
          // col_1: Interaction ID
          // col_2: Gfm Cost Center
          // col_3: Gfm Problem (Problem Type)
          // col_4: Gfm Problem Date (Next Due Date)
          // col_5: Status (City name)
          const device = {
            id: row.device_id, // Database device ID from backend
            interaction_id: String(row.col_1 || 'N/A'),
            gfm_cost_center: String(row.col_2 || 'N/A'),
            gfm_problem: String(row.col_3 || 'Routine Maintenance'), // Gfm Problem (Problem Type)
            gfm_problem_date: String(row.col_4 || 'N/A'), // Gfm Problem Date
            city: String(row.col_5 || 'N/A'), // Status column = City
            device_type: upload.device_type || 'N/A',
            // Status from backend: Active, Pending, Approved, Rejected
            submission_status: row.submission_status || 'Active',
            // Rejection remarks if any
            submission_remarks: row.submission_remarks || null,
            // Store original row data for reference
            _raw: row
          };
          
          allDevices.push(device);
        });
      }
    });
    return allDevices;
  };

  // Filter devices based on search and filters
  const getFilteredDevices = () => {
    let devices = getAllDevices();
    
    // Apply search filter
    if (searchQuery) {
      devices = devices.filter(device => {
        const searchLower = searchQuery.toLowerCase();
        
        // Convert values to strings before searching
        const interactionId = device.interaction_id ? String(device.interaction_id).toLowerCase() : '';
        const costCenter = device.gfm_cost_center ? String(device.gfm_cost_center).toLowerCase() : '';
        
        return (
          interactionId.includes(searchLower) ||
          costCenter.includes(searchLower)
        );
      });
    }
    
    // Apply type filter (case-insensitive to handle data inconsistencies)
    if (typeFilter !== 'All Types') {
      const selectedType = typeFilter.toLowerCase();
      
      if (selectedType === 'electrical') {
        // Special handling for Electrical: check gfm_problem_type for "Electro Mechanical" or device_type
        devices = devices.filter(device => {
          const problemType = (device.gfm_problem || '').toLowerCase();
          const deviceType = (device.device_type || '').toLowerCase();
          
          // Device is electrical if:
          // 1. gfm_problem_type contains "electro" AND "mechanical"
          // 2. gfm_problem_type contains "electrical" 
          // 3. device_type is "electrical"
          const isElectricalByProblemType = (
            problemType.includes('electro') && problemType.includes('mechanical')
          ) || problemType.includes('electrical');
          
          const isElectricalByDeviceType = deviceType === 'electrical';
          
          return isElectricalByProblemType || isElectricalByDeviceType;
        });
      } else {
        // For other types, use exact match on device_type
        devices = devices.filter(device =>
          (device.device_type || '').toLowerCase() === selectedType
        );
      }
    }
    
    // Apply status filter
    if (statusFilter !== 'All Status') {
      devices = devices.filter(device => device.submission_status === statusFilter);
    }
    
    // Sort devices: Approved and Rejected at the top
    devices.sort((a, b) => {
      const statusOrder = { 'Approved': 1, 'Rejected': 2, 'Pending': 3, 'Active': 4 };
      const aOrder = statusOrder[a.submission_status] || 5;
      const bOrder = statusOrder[b.submission_status] || 5;
      return aOrder - bOrder;
    });
    
    return devices;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top Navigation Bar */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-4 gap-3 sm:gap-0">
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Technician Dashboard</h1>
            </div>
            <div className="flex items-center gap-2 sm:gap-4 w-full sm:w-auto">
              {/* Refresh Button */}
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="inline-flex items-center justify-center px-3 sm:px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-300 rounded-md hover:bg-blue-100 disabled:opacity-50 touch-manipulation flex-1 sm:flex-initial">
                <svg className="w-4 h-4 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className="hidden sm:inline">Refresh</span>
              </button>
              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="inline-flex items-center justify-center px-3 sm:px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 touch-manipulation flex-1 sm:flex-initial">
                <svg className="w-4 h-4 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            <p className="font-medium">Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Notification Alerts */}
        {notifications.length > 0 && (
          <div className="mb-6 space-y-3">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`flex items-start justify-between p-4 rounded-lg border-2 shadow-lg ${
                  notification.action === 'approved'
                    ? 'bg-blue-50 border-blue-400'
                    : 'bg-red-50 border-red-400'
                }`}
              >
                <div className="flex items-start">
                  {/* Icon */}
                  <div className={`flex-shrink-0 ${
                    notification.action === 'approved' ? 'text-blue-600' : 'text-red-600'
                  }`}>
                    {notification.action === 'approved' ? (
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                  </div>
                  
                  {/* Message */}
                  <div className="ml-3">
                    <p className={`text-sm font-semibold ${
                      notification.action === 'approved' ? 'text-blue-800' : 'text-red-800'
                    }`}>
                      Your report for device {notification.costCenter} has been {notification.action}.
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      {new Date(notification.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                
                {/* Dismiss Button */}
                <button
                  onClick={() => dismissNotification(notification.id)}
                  className={`flex-shrink-0 ml-4 ${
                    notification.action === 'approved' ? 'text-blue-600 hover:text-blue-800' : 'text-red-600 hover:text-red-800'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}

        {/* My Assigned Devices Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-4 sm:px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900">My Assigned Devices</h2>
            <p className="text-xs sm:text-sm text-gray-600 mt-1">View and manage your ATM maintenance assignments</p>
          </div>

          <div className="p-4 sm:p-6">
            {/* Search and Filters */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              {/* Search Bar */}
              <div className="flex-1">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by Interaction ID or Cost Center..."
                    className="block w-full pl-10 pr-3 py-3 sm:py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-base sm:text-sm"
                  />
                </div>
              </div>

              {/* Type Filter */}
              <div className="w-full md:w-48">
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option>All Types</option>
                  <option>Cleaning1</option>
                  <option>Cleaning2</option>
                  <option>Electrical</option>
                  <option>Security</option>
                  <option>Stand Alone</option>
                </select>
              </div>

              {/* Status Filter */}
              <div className="w-full md:w-48">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option>All Status</option>
                  <option>Active</option>
                  <option>Pending</option>
                  <option>Approved</option>
                  <option>Rejected</option>
                </select>
              </div>
            </div>

            {/* Device Cards */}
            {!excelData || getAllDevices().length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No devices assigned</h3>
                <p className="mt-1 text-sm text-gray-500">No Excel files have been uploaded for your account yet.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {getFilteredDevices().map((device, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 sm:p-6 hover:shadow-md transition-shadow">
                    <div className="flex flex-col sm:flex-row items-start justify-between gap-4 sm:gap-0">
                      <div className="flex-1">
                        {/* Device ID and Badges */}
                        <div className="flex flex-wrap items-center gap-2 mb-2">
                          <h3 className="text-base sm:text-lg font-semibold text-gray-900">
                            {device.gfm_cost_center || device.interaction_id || 'N/A'}
                          </h3>
                          {device.gfm_problem && device.gfm_problem !== 'N/A' && (
                            <span className="px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                              {device.gfm_problem}
                            </span>
                          )}
                          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                            device.submission_status === 'Approved' 
                              ? 'bg-blue-100 text-blue-800' 
                              : device.submission_status === 'Rejected'
                              ? 'bg-red-100 text-red-800'
                              : device.submission_status === 'Pending'
                              ? 'bg-orange-100 text-orange-800'
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {device.submission_status || 'Active'}
                          </span>
                        </div>

                        {/* Location */}
                        <div className="flex items-center text-xs sm:text-sm text-gray-600 mb-2">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          <span>{device.gfm_cost_center || 'N/A'} - {device.city || 'N/A'}</span>
                        </div>

                        {/* Interaction ID */}
                        <div className="text-xs sm:text-sm text-gray-600">
                          <span className="font-medium">Interaction ID:</span> {device.interaction_id || 'N/A'}
                        </div>
                      </div>

                      {/* Right Side - Next Due and Button */}
                      <div className="flex flex-col sm:items-end gap-2 w-full sm:w-auto sm:ml-4">
                        {/* Next Due Date */}
                        {device.gfm_problem_date && device.gfm_problem_date !== 'N/A' && (
                          <div className="flex items-center text-xs sm:text-sm text-gray-600">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span>Next Due: {device.gfm_problem_date}</span>
                          </div>
                        )}

                        {/* View Details Button */}
                        <button
                          onClick={() => handleViewDetails(device)}
                          className="w-full sm:w-auto px-4 py-3 sm:py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 touch-manipulation"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default TechnicianDashboard;
