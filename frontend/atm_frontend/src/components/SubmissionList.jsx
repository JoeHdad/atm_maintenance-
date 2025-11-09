import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supervisorAPI } from '../api/supervisor';

const SubmissionList = () => {
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filter states
  const [filters, setFilters] = useState({
    status: 'All',
    device_type: 'All',
    technician_id: '',
    search: ''
  });
  
  // Dropdown options
  const [deviceTypes, setDeviceTypes] = useState([]);
  const [technicians, setTechnicians] = useState([]);
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);
  const [showDeviceTypeDropdown, setShowDeviceTypeDropdown] = useState(false);

  // All available device types from the model
  const allDeviceTypes = ['Cleaning1', 'Cleaning2', 'Electrical', 'Security', 'Stand Alone'];

  useEffect(() => {
    fetchSubmissions();
  }, [filters.status, filters.device_type, filters.technician_id]);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await supervisorAPI.getSubmissions(filters);
      setSubmissions(data.submissions || []);
      
      // Extract unique device types and technicians
      if (data.submissions && data.submissions.length > 0) {
        const uniqueDeviceTypes = [...new Set(data.submissions.map(s => s.type))];
        const uniqueTechs = [...new Set(data.submissions.map(s => ({
          id: s.technician,
          name: s.technician_name
        })))];
        setDeviceTypes(uniqueDeviceTypes);
        setTechnicians(uniqueTechs);
      }
    } catch (err) {
      setError(err.error || 'Failed to load submissions');
      console.error('Error fetching submissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setShowStatusDropdown(false);
    setShowDeviceTypeDropdown(false);
  };

  const handleReviewClick = (submissionId) => {
    navigate(`/supervisor/submissions/${submissionId}`);
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Pending':
        return 'bg-orange-500 text-white';
      case 'Approved':
        return 'bg-green-500 text-white';
      case 'Rejected':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  // Filter submissions by search
  const filteredSubmissions = submissions.filter(submission => {
    if (!filters.search) return true;
    const searchLower = filters.search.toLowerCase();
    return (
      submission.device_info.interaction_id.toLowerCase().includes(searchLower) ||
      submission.technician_name.toLowerCase().includes(searchLower)
    );
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Calculate statistics
  const totalSubmissions = submissions.length;
  const pendingCount = submissions.filter(s => s.status === 'Pending').length;
  const approvedCount = submissions.filter(s => s.status === 'Approved').length;
  const rejectedCount = submissions.filter(s => s.status === 'Rejected').length;

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 py-4 sm:py-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-4 sm:mb-6">
        {/* Total Submissions */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 border border-gray-200">
          <div className="text-2xl sm:text-3xl font-bold text-gray-900 mb-1">{totalSubmissions}</div>
          <div className="text-xs sm:text-sm text-gray-600">Total Submissions</div>
        </div>

        {/* Pending Review */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 border border-gray-200">
          <div className="text-2xl sm:text-3xl font-bold text-orange-500 mb-1">{pendingCount}</div>
          <div className="text-xs sm:text-sm text-gray-600">Pending Review</div>
        </div>

        {/* Approved */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 border border-gray-200">
          <div className="text-2xl sm:text-3xl font-bold text-green-500 mb-1">{approvedCount}</div>
          <div className="text-xs sm:text-sm text-gray-600">Approved</div>
        </div>

        {/* Rejected */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 border border-gray-200">
          <div className="text-2xl sm:text-3xl font-bold text-red-500 mb-1">{rejectedCount}</div>
          <div className="text-xs sm:text-sm text-gray-600">Rejected</div>
        </div>
      </div>

      {/* Submission Reports Section */}
      <div className="mb-4 sm:mb-6">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-1">Submission Reports</h2>
        <p className="text-sm sm:text-base text-gray-600">Review and approve technician visit reports</p>
      </div>

      {/* Search and Filters */}
      <div className="mb-4 sm:mb-6 flex flex-col sm:flex-row gap-3 sm:gap-4">
        {/* Search Bar */}
        <div className="flex-1 min-w-0">
          <div className="relative">
            <svg
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              placeholder="Search by ATM ID or Technician..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="w-full pl-9 sm:pl-10 pr-3 sm:pr-4 py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Status Filter */}
        <div className="relative flex-shrink-0">
          <button
            onClick={() => setShowStatusDropdown(!showStatusDropdown)}
            className="w-full sm:w-auto px-3 sm:px-4 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 flex items-center justify-between sm:justify-start gap-2 min-w-0 sm:min-w-[150px] text-sm sm:text-base touch-manipulation"
          >
            <span className="truncate">{filters.status === 'All' ? 'All Status' : filters.status}</span>
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {showStatusDropdown && (
            <div className="absolute top-full mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg z-10 min-w-[150px]">
              {['All Status', 'Pending', 'Approved', 'Rejected'].map((status) => (
                <button
                  key={status}
                  onClick={() => handleFilterChange('status', status === 'All Status' ? 'All' : status)}
                  className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base text-left hover:bg-blue-50 flex items-center gap-2 touch-manipulation"
                >
                  {filters.status === (status === 'All Status' ? 'All' : status) && (
                    <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                  <span>{status}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Device Type Filter */}
        <div className="relative flex-shrink-0">
          <button
            onClick={() => setShowDeviceTypeDropdown(!showDeviceTypeDropdown)}
            className="w-full sm:w-auto px-3 sm:px-4 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 flex items-center justify-between sm:justify-start gap-2 min-w-0 sm:min-w-[150px] text-sm sm:text-base touch-manipulation"
          >
            <span className="truncate">{filters.device_type === 'All' ? 'All Types' : filters.device_type}</span>
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {showDeviceTypeDropdown && (
            <div className="absolute top-full mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto min-w-[150px]">
              <button
                onClick={() => handleFilterChange('device_type', 'All')}
                className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base text-left hover:bg-blue-50 flex items-center gap-2 touch-manipulation"
              >
                {filters.device_type === 'All' && (
                  <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                <span>All Types</span>
              </button>
              {allDeviceTypes.map((deviceType) => (
                <button
                  key={deviceType}
                  onClick={() => handleFilterChange('device_type', deviceType)}
                  className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base text-left hover:bg-blue-50 flex items-center gap-2 touch-manipulation"
                >
                  {filters.device_type === deviceType && (
                    <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                  <span>{deviceType}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-sm sm:text-base">
          {error}
        </div>
      )}

      {/* Submissions List */}
      <div className="space-y-3 sm:space-y-4">
        {filteredSubmissions.length === 0 ? (
          <div className="text-center py-8 sm:py-12 bg-gray-50 rounded-lg">
            <svg
              className="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="mt-2 text-sm sm:text-base text-gray-600">No submissions found</p>
          </div>
        ) : (
          filteredSubmissions.map((submission) => (
            <div
              key={submission.id}
              className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col lg:flex-row lg:items-center gap-3 sm:gap-4">
                {/* Left Section */}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
                    <h3 className="text-base sm:text-lg font-bold text-gray-900 break-words">
                      {submission.device_info.interaction_id}
                    </h3>
                    <span className={`px-2 sm:px-3 py-0.5 sm:py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(submission.status)}`}>
                      {submission.status}
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs sm:text-sm text-gray-600 mb-1">
                    <svg className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span className="truncate">{submission.technician_name}</span>
                    <span className="text-gray-400">•</span>
                    <span className="font-medium truncate">{submission.device_info.gfm_cost_center}</span>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs sm:text-sm text-gray-600">
                    <span>Type: {submission.type}</span>
                    <span className="text-gray-400">•</span>
                    <span>Half {submission.half_month}</span>
                    <span className="text-gray-400 hidden sm:inline">•</span>
                    <div className="flex items-center gap-1 sm:gap-2">
                      <svg className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span className="truncate">{submission.device_info.city}</span>
                    </div>
                  </div>
                </div>

                {/* Right Section */}
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-4 lg:flex-shrink-0">
                  <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-600">
                    <svg className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span>{formatDate(submission.visit_date)}</span>
                  </div>
                  <button
                    onClick={() => navigate(`/supervisor/submissions/${submission.id}`)}
                    className="w-full sm:w-auto px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-xs sm:text-sm font-medium touch-manipulation whitespace-nowrap"
                  >
                    Review Submission
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      </div>
    </div>
  );
};

export default SubmissionList;
