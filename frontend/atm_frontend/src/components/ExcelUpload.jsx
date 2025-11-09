import React, { useState, useEffect } from 'react';
import { hostAPI } from '../api/host';

const ExcelUpload = () => {
  const [technicians, setTechnicians] = useState([]);
  const [selectedTechnician, setSelectedTechnician] = useState('');
  const [currentDeviceType, setCurrentDeviceType] = useState('');
  const [uploadedTypes, setUploadedTypes] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [viewingFileDetails, setViewingFileDetails] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // Fetch technicians on component mount
  useEffect(() => {
    fetchTechnicians();
    
    // Suppress browser extension errors
    const handleUnhandledRejection = (event) => {
      if (event.reason?.name === 'FetchError' && event.reason?.message?.includes('content.js')) {
        console.log('[SUPPRESSED] Browser extension FetchError caught and suppressed');
        event.preventDefault();
      }
    };
    
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    
    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  const fetchTechnicians = async () => {
    setLoading(true);
    setError('');
    try {
      console.log('[FETCH_TECH] Calling getTechnicians...');
      const data = await hostAPI.getTechnicians();
      console.log('[FETCH_TECH] Successfully fetched technicians:', data);
      setTechnicians(data);
    } catch (err) {
      console.error('[FETCH_TECH] Error fetching technicians:', err);
      console.error('[FETCH_TECH] Error name:', err.name);
      console.error('[FETCH_TECH] Error message:', err.message);
      console.error('[FETCH_TECH] Error details:', JSON.stringify(err, null, 2));
      setError('Failed to load technicians. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchUploadedTypes = async (technicianId) => {
    if (!technicianId) return;
    try {
      console.log(`[FETCH_TYPES] Fetching uploaded types for technician: ${technicianId}`);
      const data = await hostAPI.getUploadedTypes(technicianId);
      console.log(`[FETCH_TYPES] Received uploaded types:`, data.uploaded_types);
      setUploadedTypes(data.uploaded_types || []);
      
      // Also fetch detailed file information
      await fetchUploadedFiles(technicianId);
    } catch (err) {
      console.error('[FETCH_TYPES] Error fetching uploaded types:', err);
      console.error('[FETCH_TYPES] Error name:', err.name);
      console.error('[FETCH_TYPES] Error message:', err.message);
      setUploadedTypes([]);
    }
  };

  const fetchUploadedFiles = async (technicianId) => {
    if (!technicianId) return;
    try {
      console.log(`[FETCH_FILES] Fetching uploaded files for technician: ${technicianId}`);
      const data = await hostAPI.getUploadedFiles(technicianId);
      console.log(`[FETCH_FILES] Received files:`, data.files);
      setUploadedFiles(data.files || []);
    } catch (err) {
      console.error('[FETCH_FILES] Error fetching uploaded files:', err);
      setUploadedFiles([]);
    }
  };

  const handleTechnicianChange = (technicianId) => {
    setSelectedTechnician(technicianId);
    setCurrentDeviceType('');
    setFile(null);
    setUploadedTypes([]);
    setUploadedFiles([]);
    setSelectedFile(null);
    setViewingFileDetails(false);
    setEditMode(false);
    setSuccess(false);
    setError('');
    setUploadResult(null);
    if (technicianId) {
      fetchUploadedTypes(technicianId);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    const fileName = selectedFile.name.toLowerCase();
    if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid Excel file (.xlsx or .xls)');
      setFile(null);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setUploadResult(null);

    // Validation
    if (!selectedTechnician) {
      setError('Please select a technician');
      return;
    }
    if (!currentDeviceType) {
      setError('Please select a device type');
      return;
    }
    if (!file) {
      setError('Please select an Excel file');
      return;
    }

    setUploading(true);

    let result; // Move result variable declaration outside nested try block

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('technician_id', selectedTechnician);
      formData.append('device_type', currentDeviceType);

      console.log(`[UPLOAD] Uploading file for device type: ${currentDeviceType}`);
      console.log(`[UPLOAD] Technician ID: ${selectedTechnician}`);
      console.log(`[UPLOAD] File name: ${file.name}`);

      // Upload
      try {
        result = await hostAPI.uploadExcel(formData);
        console.log(`[UPLOAD] Upload successful:`, result);
      } catch (uploadErr) {
        console.error('[UPLOAD] Upload error:', uploadErr);
        console.error('[UPLOAD] Error name:', uploadErr.name);
        console.error('[UPLOAD] Error message:', uploadErr.message);
        throw uploadErr;
      }

      // Success
      setSuccess(true);
      setUploadResult(result);
      
      // Refresh uploaded types and files from backend to ensure consistency
      console.log(`[UPLOAD] Refreshing uploaded types from backend...`);
      try {
        await fetchUploadedTypes(selectedTechnician);
        console.log(`[UPLOAD] Uploaded types refreshed successfully`);
      } catch (refreshErr) {
        console.error('[UPLOAD] Error refreshing uploaded types:', refreshErr);
      }
      
      // Exit edit mode if we were editing
      setEditMode(false);
      setSelectedFile(null);
      setViewingFileDetails(false);
      
      // Reset only file and device type (keep technician selected)
      setFile(null);
      setCurrentDeviceType('');
      
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) {
        fileInput.value = '';
      }
    } catch (err) {
      console.error('Upload error:', err);
      if (typeof err === 'object' && err.error) {
        setError(err.error);
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError('Failed to upload Excel file. Please try again.');
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Upload Device Excel File
          </h2>
          <p className="text-sm text-gray-600">
            Upload an Excel file to assign devices to a technician
          </p>
        </div>

        {/* Warning Message */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700 font-medium">
                Warning: This will replace all existing devices for this technician
              </p>
            </div>
          </div>
        </div>

        {/* Upload Form */}
        <div className="bg-white rounded-lg shadow-md p-8">
          {/* Success Message */}
          {success && uploadResult && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <div className="flex items-start">
                <svg
                  className="h-5 w-5 text-green-400 mt-0.5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">
                    Upload Successful!
                  </h3>
                  <p className="mt-1 text-sm text-green-700">
                    {uploadResult.total_rows} rows imported from {uploadResult.file_name}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm font-medium text-red-800 whitespace-pre-wrap">
                {error}
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Technician Dropdown */}
            <div>
              <label
                htmlFor="technician"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Select Technician *
              </label>
              {loading ? (
                <div className="text-sm text-gray-500">Loading technicians...</div>
              ) : (
                <select
                  id="technician"
                  value={selectedTechnician}
                  onChange={(e) => handleTechnicianChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  disabled={uploading}
                >
                  <option value="">-- Select a technician --</option>
                  {technicians.map((tech) => (
                    <option key={tech.id} value={tech.id}>
                      {tech.username} - {tech.city}
                    </option>
                  ))}
                </select>
              )}
              {technicians.length === 0 && !loading && (
                <p className="mt-2 text-sm text-gray-500">
                  No technicians found. Please create a technician first.
                </p>
              )}
            </div>

            {/* Show uploaded files with details */}
            {selectedTechnician && uploadedFiles.length > 0 && (
              <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
                <p className="text-sm font-medium text-gray-800 mb-3">Uploaded Files:</p>
                <div className="space-y-2">
                  {uploadedFiles.map((fileInfo) => (
                    <div key={fileInfo.id} className="bg-white border border-gray-200 rounded-md">
                      <div 
                        className="p-3 cursor-pointer hover:bg-gray-50 transition-colors"
                        onClick={() => {
                          if (selectedFile?.id === fileInfo.id) {
                            setSelectedFile(null);
                            setViewingFileDetails(false);
                          } else {
                            setSelectedFile(fileInfo);
                            setViewingFileDetails(true);
                          }
                        }}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                            </svg>
                            <div>
                              <p className="text-sm font-medium text-gray-900">{fileInfo.device_type}</p>
                              <p className="text-xs text-gray-500">{fileInfo.file_name}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500">{fileInfo.row_count} rows</span>
                            <svg 
                              className={`w-5 h-5 text-gray-400 transition-transform ${selectedFile?.id === fileInfo.id ? 'transform rotate-180' : ''}`}
                              fill="currentColor" 
                              viewBox="0 0 20 20"
                            >
                              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                      </div>
                      
                      {/* File Details - Show when selected */}
                      {selectedFile?.id === fileInfo.id && viewingFileDetails && (
                        <div className="px-3 pb-3 border-t border-gray-200 bg-gray-50">
                          <div className="mt-3 space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Device Type:</span>
                              <span className="font-medium text-gray-900">{fileInfo.device_type}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">File Name:</span>
                              <span className="font-medium text-gray-900">{fileInfo.file_name}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Upload Date:</span>
                              <span className="font-medium text-gray-900">
                                {new Date(fileInfo.upload_date).toLocaleDateString()} {new Date(fileInfo.upload_date).toLocaleTimeString()}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Total Rows:</span>
                              <span className="font-medium text-gray-900">{fileInfo.row_count}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Uploaded By:</span>
                              <span className="font-medium text-gray-900">{fileInfo.uploaded_by}</span>
                            </div>
                          </div>
                          
                          {/* Edit/Replace Button */}
                          <div className="mt-4">
                            <button
                              type="button"
                              onClick={() => {
                                setEditMode(true);
                                setCurrentDeviceType(fileInfo.device_type);
                                setViewingFileDetails(false);
                              }}
                              className="w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            >
                              Replace This File
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Device Type Dropdown - Only show when technician is selected and not viewing details */}
            {selectedTechnician && !viewingFileDetails && (
              <div>
                <label
                  htmlFor="deviceType"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  {editMode ? `Replacing File for ${currentDeviceType}` : 'Select Device Type to Upload *'}
                </label>
                {editMode ? (
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={currentDeviceType}
                      disabled
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        setEditMode(false);
                        setCurrentDeviceType('');
                        setFile(null);
                      }}
                      className="px-3 py-2 text-sm text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <select
                    id="deviceType"
                    value={currentDeviceType}
                    onChange={(e) => setCurrentDeviceType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    disabled={uploading}
                  >
                    <option value="">-- Select device type --</option>
                    <option value="Cleaning1">
                      Cleaning1 {uploadedTypes.includes('Cleaning1') && '(✓ Uploaded)'}
                    </option>
                    <option value="Cleaning2">
                      Cleaning2 {uploadedTypes.includes('Cleaning2') && '(✓ Uploaded)'}
                    </option>
                    <option value="Electrical">
                      Electrical {uploadedTypes.includes('Electrical') && '(✓ Uploaded)'}
                    </option>
                    <option value="Security">
                      Security {uploadedTypes.includes('Security') && '(✓ Uploaded)'}
                    </option>
                    <option value="Stand Alone">
                      Stand Alone {uploadedTypes.includes('Stand Alone') && '(✓ Uploaded)'}
                    </option>
                  </select>
                )}
                {currentDeviceType && uploadedTypes.includes(currentDeviceType) && !editMode && (
                  <p className="mt-2 text-sm text-yellow-600">
                    ⚠️ This device type has already been uploaded. Uploading again will replace the existing data.
                  </p>
                )}
                {editMode && (
                  <p className="mt-2 text-sm text-blue-600">
                    📝 You are replacing the existing file for {currentDeviceType}. Upload a new file below.
                  </p>
                )}
              </div>
            )}

            {/* File Upload - Only show when device type is selected */}
            {currentDeviceType && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Excel File for {currentDeviceType} *
                </label>

              {/* Drag and Drop Area */}
              <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 bg-gray-50'
                } ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !uploading && document.getElementById('file-input').click()}
              >
                <input
                  id="file-input"
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileChange}
                  className="hidden"
                  disabled={uploading}
                />

                {file ? (
                  <div className="space-y-2">
                    <svg
                      className="mx-auto h-12 w-12 text-green-500"
                      xmlns="http://www.w3.org/2000/svg"
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
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                        document.getElementById('file-input').value = '';
                      }}
                      className="text-sm text-red-600 hover:text-red-800"
                      disabled={uploading}
                    >
                      Remove file
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium text-blue-600">Click to upload</span> or
                      drag and drop
                    </p>
                    <p className="text-xs text-gray-500">Excel files only (.xlsx, .xls)</p>
                  </div>
                )}
              </div>
              </div>
            )}

            {/* Upload Button - Only show when ready to upload */}
            {selectedTechnician && currentDeviceType && (
              <button
                type="submit"
                disabled={uploading || !file}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
              {uploading ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Uploading...
                </span>
                ) : (
                  `Upload Excel for ${currentDeviceType}`
                )}
              </button>
            )}
          </form>
        </div>

        {/* Import Summary */}
        {success && uploadResult && uploadResult.data && (
          <div className="mt-6 bg-white rounded-lg shadow-md p-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Import Summary
            </h3>

            <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-600 font-medium">Total Rows</p>
                <p className="text-2xl font-bold text-blue-900">
                  {uploadResult.total_rows}
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-green-600 font-medium">File Name</p>
                <p className="text-lg font-bold text-green-900 truncate">
                  {uploadResult.file_name}
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <p className="text-sm text-purple-600 font-medium">Status</p>
                <p className="text-lg font-bold text-purple-900">
                  {uploadResult.status === 'success' ? '✓ Success' : 'Pending'}
                </p>
              </div>
            </div>

            {/* Data Preview Table */}
            <div className="mt-6">
              <h4 className="text-md font-medium text-gray-900 mb-3">
                Data Preview (showing first 10 rows)
              </h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {uploadResult.data.length > 0 &&
                        Object.keys(uploadResult.data[0]).map((key) => (
                          <th
                            key={key}
                            className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {key}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {uploadResult.data.slice(0, 10).map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {Object.values(row).map((value, colIdx) => (
                          <td
                            key={colIdx}
                            className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate"
                          >
                            {value !== null && value !== undefined ? String(value) : '-'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {uploadResult.data.length > 10 && (
                <p className="mt-3 text-sm text-gray-500 text-center">
                  ... and {uploadResult.data.length - 10} more rows
                </p>
              )}
            </div>
          </div>
        )}
    </div>
  );
};

export default ExcelUpload;
