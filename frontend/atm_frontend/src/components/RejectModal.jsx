import React, { useState } from 'react';

const RejectModal = ({ isOpen, onClose, onConfirm, submissionId }) => {
  const [remarks, setRemarks] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleConfirm = () => {
    // Validate remarks
    if (!remarks.trim()) {
      setError('Remarks are required');
      return;
    }
    
    if (remarks.trim().length < 10) {
      setError('Remarks must be at least 10 characters long');
      return;
    }

    onConfirm(remarks);
    setRemarks('');
    setError('');
  };

  const handleClose = () => {
    setRemarks('');
    setError('');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-bold text-gray-900">Reject Submission</h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          <p className="text-sm text-gray-600 mb-4">
            Please provide a reason for rejecting this submission. The technician will be notified.
          </p>

          <textarea
            value={remarks}
            onChange={(e) => {
              setRemarks(e.target.value);
              setError('');
            }}
            placeholder="Enter your remarks here..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />

          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}

          <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Minimum 10 characters required</span>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-4 border-t">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700"
          >
            Confirm Rejection
          </button>
        </div>
      </div>
    </div>
  );
};

export default RejectModal;
