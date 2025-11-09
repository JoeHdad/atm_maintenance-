import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { technicianAPI } from '../api/technician';
import { useAuth } from '../context/AuthContext';
import UploadVisitReport from './UploadVisitReport';

const DeviceDetail = () => {
  const { deviceId } = useParams();
  const navigate = useNavigate();
  const { logout } = useAuth();
  
  const [device, setDevice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showUploadForm, setShowUploadForm] = useState(false);

  useEffect(() => {
    fetchDeviceDetails();
  }, [deviceId]);

  const fetchDeviceDetails = async () => {
    try {
      setLoading(true);
      setError('');
      
      const data = await technicianAPI.getMyExcelData();
      
      if (!data || !data.uploads) {
        setError('No device data found');
        return;
      }
      
      let foundDevice = null;
      for (const upload of data.uploads) {
        if (upload.parsed_data && upload.parsed_data.length > 0) {
          // Process each row and map columns
          for (let index = 0; index < upload.parsed_data.length; index++) {
            const row = upload.parsed_data[index];
            
            // Skip rows without a valid device_id (includes header rows)
            if (!row.device_id) {
              continue;
            }
            
            // Map columns to device fields based on actual Excel structure
            // col_1: Interaction ID
            // col_2: Gfm Cost Center
            // col_3: Gfm Problem (Problem Type)
            // col_4: Gfm Problem Date
            // col_5: Status (City)
            const mappedDevice = {
              id: row.device_id, // Database device ID from backend
              interaction_id: String(row.col_1 || 'N/A'),
              gfm_cost_center: String(row.col_2 || 'N/A'),
              gfm_problem: String(row.col_3 || 'Routine Maintenance'), // Gfm Problem (Problem Type)
              gfm_problem_date: String(row.col_4 || 'N/A'), // Gfm Problem Date
              city: String(row.col_5 || 'N/A'), // Status column = City
              device_type: upload.device_type || 'N/A',
              submission_status: row.submission_status || 'Active',
              submission_remarks: row.submission_remarks || null,
              _raw: row
            };
            
            // Check if this is the device we're looking for
            if (mappedDevice.interaction_id === deviceId || 
                mappedDevice.gfm_cost_center === deviceId ||
                row.col_1 === deviceId ||
                row.col_2 === deviceId) {
              foundDevice = mappedDevice;
              break;
            }
          }
          
          if (foundDevice) break;
        }
      }
      
      if (foundDevice) {
        console.log('DeviceDetail: Found device with ID:', foundDevice.id, 'interaction_id:', foundDevice.interaction_id);
        setDevice(foundDevice);
      } else {
        setError(`Device ${deviceId} not found`);
      }
    } catch (err) {
      setError(err.error || 'Failed to load device details');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleAddVisitReport = () => {
    setShowUploadForm(true);
  };

  const handleBackToDeviceInfo = () => {
    setShowUploadForm(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!device && !loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error || 'Device not found'}
          </div>
          <button
            onClick={() => navigate('/technician')}
            className="mt-4 text-gray-600 hover:text-gray-900 flex items-center"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Devices
          </button>
        </div>
      </div>
    );
  }

  // Show upload form if button clicked
  if (showUploadForm) {
    return <UploadVisitReport device={device} onBack={handleBackToDeviceInfo} />;
  }

  // Show device details page (Screenshot 2)
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between py-3 sm:py-4 gap-3 sm:gap-0">
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Device Details</h1>
            </div>
            <div className="w-full sm:w-auto">
              <button
                onClick={handleLogout}
                className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 touch-manipulation"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        {/* Back to Devices Link */}
        <button
          onClick={() => navigate('/technician')}
          className="mb-6 text-gray-600 hover:text-gray-900 flex items-center"
        >
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Devices
        </button>

        {/* Device Information Card */}
        <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-4 sm:mb-6">
          <div className="flex flex-col sm:flex-row items-start justify-between mb-4 sm:mb-6 gap-3 sm:gap-0">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900">{device.interaction_id || device.gfm_cost_center}</h2>
              <p className="text-xs sm:text-sm text-gray-600">Device Information</p>
            </div>
            {device.gfm_problem && device.gfm_problem !== 'N/A' && (
              <span className="px-3 py-1 text-sm font-semibold rounded-full bg-blue-600 text-white">
                {device.gfm_problem}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <p className="text-sm text-gray-600">Cost Center</p>
              <p className="font-medium text-gray-900">{device.gfm_cost_center || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className={`font-medium ${
                device.submission_status === 'Approved' 
                  ? 'text-blue-600' 
                  : device.submission_status === 'Rejected'
                  ? 'text-red-600'
                  : device.submission_status === 'Pending'
                  ? 'text-orange-600'
                  : 'text-green-600'
              }`}>
                {device.submission_status || 'Active'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Problem Type</p>
              <p className="font-medium text-gray-900">{device.gfm_problem || 'Routine Maintenance'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Problem Date</p>
              <p className="font-medium text-gray-900">{device.gfm_problem_date || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">City</p>
              <p className="font-medium text-gray-900">{device.city || 'N/A'}</p>
            </div>
          </div>

          {/* Rejection Reason Box - Only show if rejected */}
          {device.submission_status === 'Rejected' && device.submission_remarks && (
            <div className="mt-6 bg-red-50 border-2 border-red-300 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div className="flex-1">
                  <h4 className="font-bold text-red-900 text-lg mb-2">Submission Rejected</h4>
                  <p className="text-sm text-red-800 font-medium mb-1">Reason from Supervisor:</p>
                  <p className="text-red-700 bg-white rounded p-3 border border-red-200">
                    {device.submission_remarks}
                  </p>
                  <p className="text-sm text-red-600 mt-2 italic">
                    Please review the feedback and resubmit your report.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Add Visit Report Button - Disabled if Approved */}
          {device.submission_status === 'Approved' ? (
            <div className="mt-6">
              <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4 mb-4">
                <div className="flex items-start gap-3">
                  <svg className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="flex-1">
                    <h4 className="font-bold text-blue-900 text-lg mb-1">Task Completed</h4>
                    <p className="text-sm text-blue-700">
                      This ATM maintenance report has been approved by the supervisor. No further action is required.
                    </p>
                  </div>
                </div>
              </div>
              <button
                disabled
                className="w-full flex items-center justify-center px-6 py-3 bg-gray-300 text-gray-500 font-medium rounded-md cursor-not-allowed"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                Report Already Approved
              </button>
            </div>
          ) : (
            <div className="mt-6">
              <button
                onClick={handleAddVisitReport}
                disabled={device.submission_status === 'Pending'}
                className={`w-full flex items-center justify-center px-6 py-3 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 touch-manipulation ${
                  device.submission_status === 'Pending'
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
                }`}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                {device.submission_status === 'Pending' ? 'Report Pending Review' : 'Add Visit Report'}
              </button>
              {device.submission_status === 'Pending' && (
                <p className="text-sm text-gray-600 text-center mt-2">
                  Your report is currently under review by the supervisor.
                </p>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DeviceDetail;
