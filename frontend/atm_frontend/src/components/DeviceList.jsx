import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { technicianAPI } from '../api/technician';
import PhotoUploadModal from './PhotoUploadModal';

const DeviceList = () => {
  const navigate = useNavigate();
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    type: 'All',
    status: ''
  });
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [excelData, setExcelData] = useState(null);
  const [excelLoading, setExcelLoading] = useState(false);
  const [showExcelData, setShowExcelData] = useState(false);

  const fetchDevices = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await technicianAPI.getDevices(filters);
      setDevices(data.devices || []);
    } catch (err) {
      setError(err.error || 'Failed to load devices');
      console.error('Error fetching devices:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  const fetchExcelData = useCallback(async (deviceType) => {
    try {
      setExcelLoading(true);
      console.log(`[FRONTEND] Fetching Excel data for device type: ${deviceType}`);
      const data = await technicianAPI.getExcelDataByType(deviceType);
      console.log(`[FRONTEND] Received data:`, data);
      console.log(`[FRONTEND] Device type in response: ${data.device_type}`);
      console.log(`[FRONTEND] File name: ${data.file_name}`);
      console.log(`[FRONTEND] Data rows: ${data.data?.length || 0}`);
      setExcelData(data);
      if (data.data && data.data.length > 0) {
        setShowExcelData(true);
      }
    } catch (err) {
      console.error('[FRONTEND] Error fetching Excel data:', err);
      console.error('[FRONTEND] Error details:', JSON.stringify(err, null, 2));
      setExcelData(null);
      setShowExcelData(false);
    } finally {
      setExcelLoading(false);
    }
  }, []);

  useEffect(() => {
    // Fetch Excel data when device type filter changes
    if (filters.type && filters.type !== 'All') {
      fetchExcelData(filters.type);
    } else {
      setExcelData(null);
      setShowExcelData(false);
    }
  }, [filters.type, fetchExcelData]);

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const handleViewDetails = (deviceId) => {
    navigate(`/technician/devices/${deviceId}`);
  };

  const handleOpenModal = (device) => {
    setSelectedDevice(device);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedDevice(null);
  };

  const handleSubmissionSuccess = () => {
    // Refresh devices list after successful submission
    fetchDevices();
  };

  const toggleExcelData = () => {
    setShowExcelData(!showExcelData);
  };

  const getTypeBadgeColor = (type) => {
    return type === 'Cleaning' 
      ? 'bg-blue-100 text-blue-800' 
      : 'bg-purple-100 text-purple-800';
  };

  const getStatusBadgeColor = (status) => {
    return status === 'submitted'
      ? 'bg-green-100 text-green-800'
      : 'bg-yellow-100 text-yellow-800';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">My Devices</h1>
        <p className="text-gray-600 mt-2">View and manage your assigned ATM devices</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Device Type
            </label>
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="All">All Types</option>
              <option value="Cleaning1">Cleaning1</option>
              <option value="Cleaning2">Cleaning2</option>
              <option value="Electrical">Electrical</option>
              <option value="Security">Security</option>
              <option value="Stand Alone">Stand Alone</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Region/Status
            </label>
            <input
              type="text"
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              placeholder="Filter by region..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Excel Data Section */}
      {excelData && filters.type !== 'All' && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Excel Data for {filters.type}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                File: {excelData.file_name} | Uploaded: {new Date(excelData.upload_date).toLocaleDateString()}
              </p>
            </div>
            <button
              onClick={toggleExcelData}
              className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
            >
              {showExcelData ? 'Hide Data' : 'Show Data'}
            </button>
          </div>
          
          {excelLoading && (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          )}
          
          {showExcelData && excelData.data && excelData.data.length > 0 && (
            <div>
              <div className="mb-4 flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  Showing {Math.min(10, excelData.data.length)} of {excelData.data.length} rows
                </p>
              </div>
              
              <div className="overflow-x-auto border border-gray-200 rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(excelData.data[0]).map((key) => (
                        <th
                          key={key}
                          className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                        >
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {excelData.data.slice(0, 10).map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {Object.values(row).map((value, colIdx) => (
                          <td
                            key={colIdx}
                            className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap"
                          >
                            {value !== null && value !== undefined ? String(value) : '-'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {excelData.data.length > 10 && (
                <p className="mt-3 text-sm text-gray-500 text-center">
                  ... and {excelData.data.length - 10} more rows
                </p>
              )}
            </div>
          )}
          
          {showExcelData && (!excelData.data || excelData.data.length === 0) && (
            <div className="text-center py-8 text-gray-500">
              <p>No Excel data available for this device type.</p>
            </div>
          )}
        </div>
      )}

      {/* Device Count */}
      <div className="mb-4">
        <p className="text-gray-600">
          Showing <span className="font-semibold">{devices.length}</span> device{devices.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Devices Grid */}
      {devices.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-lg font-medium text-gray-900">No devices found</h3>
          <p className="mt-1 text-gray-500">
            {filters.type !== 'All' || filters.status
              ? 'Try adjusting your filters'
              : 'No devices have been assigned to you yet'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {devices.map((device) => (
            <div
              key={device.id}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden"
            >
              {/* Card Header */}
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
                <h3 className="text-white font-semibold text-lg">
                  {device.interaction_id}
                </h3>
                <p className="text-blue-100 text-sm">{device.gfm_cost_center}</p>
              </div>

              {/* Card Body */}
              <div className="p-6">
                {/* Type and Submission Status Badges */}
                <div className="flex gap-2 mb-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getTypeBadgeColor(device.type)}`}>
                    {device.type}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeColor(device.submission_status)}`}>
                    {device.submission_status === 'submitted' ? 'Submitted' : 'Pending'}
                  </span>
                </div>

                {/* Device Info */}
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Region:</span>
                    <span className="font-medium text-gray-900">{device.region}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">City:</span>
                    <span className="font-medium text-gray-900">{device.city}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Problem Type:</span>
                    <span className="font-medium text-gray-900">{device.gfm_problem_type}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Problem Date:</span>
                    <span className="font-medium text-gray-900">
                      {new Date(device.gfm_problem_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Next Due Date */}
                {device.next_due_date && (
                  <div className="bg-gray-50 rounded-lg p-3 mb-4">
                    <p className="text-xs text-gray-600 mb-1">Next Due:</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {device.next_due_date.description}
                    </p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleOpenModal(device)}
                    disabled={device.submission_status === 'submitted'}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
                    title={device.submission_status === 'submitted' ? 'Already submitted for current period' : 'Upload maintenance photos'}
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Add
                  </button>
                  <button
                    onClick={() => handleViewDetails(device.id)}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
                  >
                    View
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Photo Upload Modal */}
      <PhotoUploadModal
        device={selectedDevice}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSuccess={handleSubmissionSuccess}
      />
    </div>
  );
};

export default DeviceList;
