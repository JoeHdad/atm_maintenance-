import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supervisorAPI } from '../api/supervisor';
import RejectModal from './RejectModal';
import MediaImage from './MediaImage';
import { ensureAbsoluteUrl } from '../utils/mediaUrlHelper';

const SubmissionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [previewingPDF, setPreviewingPDF] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [showImageModal, setShowImageModal] = useState(false);

  const fetchSubmissionDetail = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await supervisorAPI.getSubmissionDetail(id);
      setSubmission(data.submission);
    } catch (err) {
      setError(err.error || 'Failed to load submission details');
      console.error('Error fetching submission:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchSubmissionDetail();
  }, [fetchSubmissionDetail]);

  // Handle ESC key to close image modal
  useEffect(() => {
    const handleEscKey = (event) => {
      if (event.key === 'Escape' && showImageModal) {
        closeImageModal();
      }
    };

    if (showImageModal) {
      document.addEventListener('keydown', handleEscKey);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey);
      document.body.style.overflow = 'unset';
    };
  }, [showImageModal]);

  const handleApprove = async () => {
    if (!window.confirm('Are you sure you want to approve this submission?')) {
      return;
    }

    try {
      setProcessing(true);
      setError('');
      await supervisorAPI.approveSubmission(id);
      setSuccessMessage('Submission approved successfully!');
      
      // Refresh submission data
      setTimeout(() => {
        fetchSubmissionDetail();
        setSuccessMessage('');
      }, 2000);
    } catch (err) {
      setError(err.error || 'Failed to approve submission');
      console.error('Error approving submission:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async (remarks) => {
    try {
      setProcessing(true);
      setError('');
      await supervisorAPI.rejectSubmission(id, remarks);
      setSuccessMessage('Submission rejected successfully!');
      setShowRejectModal(false);
      
      // Refresh submission data
      setTimeout(() => {
        fetchSubmissionDetail();
        setSuccessMessage('');
      }, 2000);
    } catch (err) {
      setError(err.error || 'Failed to reject submission');
      console.error('Error rejecting submission:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handlePreviewPDF = async () => {
    try {
      setPreviewingPDF(true);
      setError('');
      
      console.log('[PDF Preview] Starting PDF generation for submission:', id);
      const startTime = Date.now();
      
      // Reduced timeout to 10 seconds for faster feedback
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('PDF generation timed out after 10 seconds. Please try again.')), 10000)
      );
      
      const pdfPromise = supervisorAPI.previewPDF(id);
      
      const response = await Promise.race([pdfPromise, timeoutPromise]);
      
      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      console.log('[PDF Preview] Response received in', duration, 'seconds:', response);
      
      if (response.pdf_url) {
        // Backend now returns absolute URL directly
        const pdfUrl = ensureAbsoluteUrl(response.pdf_url);
        
        console.log('[PDF Preview] Opening PDF:', pdfUrl);
        
        // Open PDF in new tab
        const newWindow = window.open(pdfUrl, '_blank');
        
        // Check if popup was blocked
        if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
          setError('Popup blocked. Please allow popups for this site and try again.');
        }
      } else {
        setError('PDF URL not found in response. Please try again.');
        console.error('[PDF Preview] No PDF URL in response:', response);
      }
    } catch (err) {
      console.error('[PDF Preview] Error:', err);
      
      // Handle different error types
      if (err.message && err.message.includes('timed out')) {
        setError('PDF generation is taking longer than expected. Please try again in a moment.');
      } else if (err.error) {
        setError(err.error);
      } else if (err.message) {
        setError(err.message);
      } else {
        setError('Failed to generate PDF preview. Please check your connection and try again.');
      }
    } finally {
      setPreviewingPDF(false);
    }
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

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  // Determine if this is an electrical device
  const gfmProblemType = (submission?.device_info?.gfm_problem_type || '').toLowerCase();
  const isElectrical = (
    gfmProblemType.includes('electro') && gfmProblemType.includes('mechanical')
  ) || gfmProblemType.includes('electrical') || submission?.type === 'Electrical';

  // Group photos by section
  const getPhotosBySection = (sectionNumber) => {
    if (!submission || !submission.photos) return [];
    return submission.photos
      .filter(photo => photo.section === sectionNumber)
      .sort((a, b) => a.order_index - b.order_index);
  };

  const PhotoPlaceholder = ({ message = "No photo" }) => (
    <div className="bg-gray-200 rounded-lg flex flex-col items-center justify-center h-48">
      <svg className="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  );

  const handleImageClick = (photo, section) => {
    setSelectedImage({
      url: ensureAbsoluteUrl(photo.file_url),
      alt: `Section ${section} - Photo ${photo.order_index}`,
      section: section,
      orderIndex: photo.order_index
    });
    setShowImageModal(true);
  };

  const closeImageModal = () => {
    setShowImageModal(false);
    setSelectedImage(null);
  };

  const PhotoDisplay = ({ photo, section }) => {
    return (
      <div
        className="cursor-pointer hover:opacity-90 transition-opacity"
        onClick={() => handleImageClick(photo, section)}
      >
        <MediaImage
          src={photo.file_url}
          alt={`Section ${section}, item ${photo.order_index}`}
          className="w-full h-48 rounded-lg border border-gray-200"
          imgClassName="w-full h-48 object-cover rounded-lg border border-gray-200"
          fallbackSrc={null}
          onError={(e) => console.warn(`Failed to load photo ${photo.id}`)}
        />
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error && !submission) {
    return (
      <div className="min-h-screen bg-gray-100 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
          <button
            onClick={() => navigate('/supervisor/submissions')}
            className="mt-4 text-blue-600 hover:text-blue-800 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 py-4 sm:py-6">
        {/* Back Button */}
        <button
          onClick={() => navigate('/supervisor/submissions')}
          className="mb-4 text-gray-600 hover:text-gray-900 flex items-center gap-2 touch-manipulation"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="text-sm sm:text-base">Back to Dashboard</span>
        </button>

        {/* Status Badge */}
        <div className="flex justify-end mb-4">
          <span className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-medium ${getStatusBadgeClass(submission.status)}`}>
            {submission.status}
          </span>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-sm sm:text-base">
            {successMessage}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-sm sm:text-base">
            {error}
          </div>
        )}

        {/* Submission Info Card */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
          <div className="mb-4">
            <h2 className="text-lg sm:text-xl md:text-2xl font-bold text-gray-900 break-words">{submission.device_info.interaction_id}</h2>
            <p className="text-xs sm:text-sm text-gray-600 mt-1">Submitted by {submission.technician_name}</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 bg-gray-50 p-3 sm:p-4 rounded-lg">
            <div>
              <p className="text-xs text-gray-600 mb-1">Cost Center</p>
              <p className="font-medium text-gray-900 text-sm sm:text-base break-words">{submission.device_info.gfm_cost_center}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">City - Region</p>
              <p className="font-medium text-gray-900 text-sm sm:text-base break-words">{submission.device_info.city} - {submission.device_info.region}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Visit Date</p>
              <p className="font-medium text-gray-900 text-sm sm:text-base">{formatDate(submission.visit_date)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Type</p>
              <p className="font-medium text-gray-900 text-sm sm:text-base">{submission.type}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Half Month</p>
              <p className="font-medium text-gray-900 text-sm sm:text-base">Period {submission.half_month} (1-14)</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Submitted On</p>
              <p className="font-medium text-gray-900 text-sm sm:text-base break-words">{formatDateTime(submission.created_at)}</p>
            </div>
          </div>
        </div>

        {/* Photo Sections - Conditional based on device type */}
        {isElectrical ? (
          // Electrical device: 5 sections
          <>
            {/* Section 1 */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-2">Section 1</h3>
              <p className="text-sm text-gray-600 mb-3">Photos must be Nightly and clear, also showing machine and pylon from four sides from 3 to 5 meters away.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                {getPhotosBySection(1).length > 0 ? (
                  getPhotosBySection(1).map((photo) => (
                    <div key={photo.id}>
                      <PhotoDisplay photo={photo} section={1} />
                    </div>
                  ))
                ) : (
                  <>
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                  </>
                )}
              </div>
            </div>

            {/* Section 2 */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-2">Section 2</h3>
              <p className="text-sm text-gray-600 mb-3">Photos must be Nightly and clear. Zoom in and out for front and back from 3 to 5 meters away.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                {getPhotosBySection(2).length > 0 ? (
                  getPhotosBySection(2).map((photo) => (
                    <div key={photo.id}>
                      <PhotoDisplay photo={photo} section={2} />
                    </div>
                  ))
                ) : (
                  <>
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                  </>
                )}
              </div>
            </div>

            {/* Section 3 */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-2">Section 3</h3>
              <p className="text-sm text-gray-600 mb-3">Photos must be clear, also showing HVAC Temperature, Power voltmeter, Internally Light & Externally Light.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                {getPhotosBySection(3).length > 0 ? (
                  getPhotosBySection(3).map((photo) => (
                    <div key={photo.id}>
                      <PhotoDisplay photo={photo} section={3} />
                    </div>
                  ))
                ) : (
                  <>
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                  </>
                )}
              </div>
            </div>

            {/* Section 4 */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-2">Section 4</h3>
              <p className="text-sm text-gray-600 mb-3">Photos for machine Screen, Keyboard, ATM Code, Kiosk and Pylon.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                {getPhotosBySection(4).length > 0 ? (
                  getPhotosBySection(4).map((photo) => (
                    <div key={photo.id}>
                      <PhotoDisplay photo={photo} section={4} />
                    </div>
                  ))
                ) : (
                  <>
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                  </>
                )}
              </div>
            </div>

            {/* Section 5 */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-2">Section 5</h3>
              <p className="text-sm text-gray-600 mb-3">Photos for machine Screen, Keyboard, ATM Code, Kiosk and Pylon.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                {getPhotosBySection(5).length > 0 ? (
                  getPhotosBySection(5).map((photo) => (
                    <div key={photo.id}>
                      <PhotoDisplay photo={photo} section={5} />
                    </div>
                  ))
                ) : (
                  <>
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                  </>
                )}
              </div>
            </div>
          </>
        ) : (
          // Default device: 3 sections
          <>
            {/* Section 1: Machine & Pylon */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-3 sm:mb-4">Section 1: Machine & Pylon (3-5m away)</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                {getPhotosBySection(1).length > 0 ? (
                  getPhotosBySection(1).map((photo) => (
                    <div key={photo.id}>
                      <PhotoDisplay photo={photo} section={1} />
                    </div>
                  ))
                ) : (
                  <>
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                  </>
                )}
              </div>
            </div>

            {/* Section 2: Zoomed Front & Back */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-3 sm:mb-4">Section 2: Zoomed Front & Back (3-5m)</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                {getPhotosBySection(2).length > 0 ? (
                  getPhotosBySection(2).map((photo) => (
                    <div key={photo.id}>
                      <PhotoDisplay photo={photo} section={2} />
                    </div>
                  ))
                ) : (
                  <>
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                  </>
                )}
              </div>
            </div>

            {/* Section 3: Asphalt & Pavement */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-3 sm:mb-4">Section 3: Asphalt & Pavement</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {getPhotosBySection(3).length > 0 ? (
                  getPhotosBySection(3).map((photo) => (
                    <div key={photo.id}>
                      <PhotoDisplay photo={photo} section={3} />
                    </div>
                  ))
                ) : (
                  <>
                    <PhotoPlaceholder message="No photo uploaded" />
                    <PhotoPlaceholder message="No photo uploaded" />
                  </>
                )}
              </div>
            </div>
          </>
        )}

        {/* Action Buttons - Only for Pending submissions */}
        {submission.status === 'Pending' && (
          <>
            {/* Preview PDF Button */}
            <div className="mb-3 sm:mb-4">
              <button
                onClick={handlePreviewPDF}
                disabled={previewingPDF}
                className="w-full py-2.5 sm:py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium text-sm sm:text-base touch-manipulation"
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span className="truncate">{previewingPDF ? 'Generating Preview...' : 'View PDF Preview'}</span>
              </button>
            </div>

            {/* Approve and Reject Buttons */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
              <button
                onClick={handleApprove}
                disabled={processing}
                className="w-full py-2.5 sm:py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium text-sm sm:text-base touch-manipulation order-1"
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="truncate">{processing ? 'Processing...' : 'Approve & Generate PDF'}</span>
              </button>
              <button
                onClick={() => setShowRejectModal(true)}
                disabled={processing}
                className="w-full py-2.5 sm:py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium text-sm sm:text-base touch-manipulation order-2"
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span className="truncate">{processing ? 'Processing...' : 'Reject Submission'}</span>
              </button>
            </div>
          </>
        )}

        {/* Info message for already processed submissions */}
        {submission.status !== 'Pending' && (
          <div className={`mb-4 sm:mb-6 p-3 sm:p-4 rounded-lg border-2 ${
            submission.status === 'Approved' 
              ? 'bg-green-50 border-green-300' 
              : 'bg-red-50 border-red-300'
          }`}>
            <div className="flex items-start gap-2 sm:gap-3">
              {submission.status === 'Approved' ? (
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
              <div className="flex-1 min-w-0">
                <p className={`font-bold text-sm sm:text-base ${submission.status === 'Approved' ? 'text-green-900' : 'text-red-900'}`}>
                  This submission has already been {submission.status.toLowerCase()}
                </p>
                <p className={`text-xs sm:text-sm mt-1 ${submission.status === 'Approved' ? 'text-green-700' : 'text-red-700'}`}>
                  No further action is required.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Show remarks if rejected */}
        {submission.status === 'Rejected' && submission.remarks && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 sm:p-4 mb-4">
            <h4 className="font-bold text-red-900 mb-2 text-sm sm:text-base">Rejection Reason:</h4>
            <p className="text-red-700 text-sm sm:text-base break-words">{submission.remarks}</p>
          </div>
        )}

        {/* Show remarks if approved */}
        {submission.status === 'Approved' && submission.remarks && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 sm:p-4 mb-4">
            <h4 className="font-bold text-green-900 mb-2 text-sm sm:text-base">Approval Remarks:</h4>
            <p className="text-green-700 text-sm sm:text-base break-words">{submission.remarks}</p>
          </div>
        )}

      {/* Reject Modal */}
      <RejectModal
        isOpen={showRejectModal}
        onClose={() => setShowRejectModal(false)}
        onConfirm={handleReject}
        submissionId={id}
      />

      {/* Image Full View Modal */}
      {showImageModal && selectedImage && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-2 sm:p-4"
          onClick={closeImageModal}
        >
          <div className="relative w-full max-w-7xl max-h-full">
            {/* Close Button */}
            <button
              onClick={closeImageModal}
              className="absolute top-2 right-2 sm:top-4 sm:right-4 bg-white rounded-full p-2 hover:bg-gray-200 transition-colors z-10 shadow-lg touch-manipulation"
              aria-label="Close image"
            >
              <svg className="w-5 h-5 sm:w-6 sm:h-6 text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Image Info */}
            <div className="absolute top-2 left-2 sm:top-4 sm:left-4 bg-white bg-opacity-90 rounded-lg px-2 py-1 sm:px-4 sm:py-2 shadow-lg">
              <p className="text-xs sm:text-sm font-semibold text-gray-800">
                Section {selectedImage.section} - Photo {selectedImage.orderIndex}
              </p>
            </div>

            {/* Image */}
            <img
              src={selectedImage.url}
              alt={selectedImage.alt}
              className="w-full max-h-[85vh] sm:max-h-[90vh] object-contain rounded-lg shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            />

            {/* Instructions */}
            <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 bg-white bg-opacity-90 rounded-lg px-3 py-1.5 sm:px-4 sm:py-2 shadow-lg">
              <p className="text-xs sm:text-sm text-gray-800 whitespace-nowrap">
                Click outside or press ESC to close
              </p>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default SubmissionDetail;
