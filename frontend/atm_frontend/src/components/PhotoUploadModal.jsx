import React, { useState } from 'react';
import { technicianAPI } from '../api/technician';

const PhotoUploadModal = ({ device, isOpen, onClose, onSuccess }) => {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Form state
  const [formData, setFormData] = useState({
    job_description: '',
    job_status: 'Ok',
    remarks: ''
  });
  
  // Photo state
  const [photos, setPhotos] = useState({
    section1_1: null,
    section1_2: null,
    section1_3: null,
    section2_1: null,
    section2_2: null,
    section2_3: null,
    section3_1: null,
    section3_2: null,
  });
  
  const [photoPreviews, setPhotoPreviews] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePhotoChange = (photoKey, file) => {
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      if (!validTypes.includes(file.type)) {
        setError(`Invalid file type for ${photoKey}. Only JPG and PNG allowed.`);
        return;
      }
      
      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError(`File ${photoKey} is too large. Maximum size is 10MB.`);
        return;
      }
      
      setPhotos(prev => ({
        ...prev,
        [photoKey]: file
      }));
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreviews(prev => ({
          ...prev,
          [photoKey]: reader.result
        }));
      };
      reader.readAsDataURL(file);
      
      // Clear error if it was about this photo
      setError('');
    }
  };

  const validateForm = () => {
    // Check all photos are uploaded
    const missingPhotos = Object.keys(photos).filter(key => !photos[key]);
    if (missingPhotos.length > 0) {
      setError(`Please upload all 8 photos. Missing: ${missingPhotos.join(', ')}`);
      return false;
    }
    
    if (!formData.job_description.trim()) {
      setError('Please enter job description');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setSubmitting(true);
      
      // Create FormData
      const submitData = new FormData();
      submitData.append('device_id', device.id);
      submitData.append('visit_date', new Date().toISOString().split('T')[0]);
      submitData.append('job_description', formData.job_description);
      submitData.append('status', formData.status);
      submitData.append('remarks', formData.remarks);
      
      // Append all photos
      Object.keys(photos).forEach(key => {
        if (photos[key]) {
          submitData.append(key, photos[key]);
        }
      });
      
      await technicianAPI.submitMaintenance(submitData);
      
      setSuccess('Maintenance submission successful!');
      
      // Reset form and close modal after 1.5 seconds
      setTimeout(() => {
        resetForm();
        onSuccess();
        onClose();
      }, 1500);
      
    } catch (err) {
      setError(err.error || 'Failed to submit maintenance');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      job_description: '',
      job_status: 'Ok',
      remarks: ''
    });
    setPhotos({
      section1_1: null,
      section1_2: null,
      section1_3: null,
      section2_1: null,
      section2_2: null,
      section2_3: null,
      section3_1: null,
      section3_2: null,
    });
    setPhotoPreviews({});
    setError('');
    setSuccess('');
  };

  const handleClose = () => {
    if (!submitting) {
      resetForm();
      onClose();
    }
  };

  const PhotoUploadBox = ({ photoKey, label }) => (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-blue-500 transition-colors">
      <label className="block cursor-pointer">
        <div className="text-center">
          {photoPreviews[photoKey] ? (
            <div className="relative">
              <img
                src={photoPreviews[photoKey]}
                alt={label}
                className="w-full h-32 object-cover rounded"
              />
              <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          ) : (
            <div className="py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <p className="mt-2 text-sm text-gray-600">{label}</p>
              <p className="text-xs text-gray-500">JPG, PNG (max 10MB)</p>
            </div>
          )}
        </div>
        <input
          type="file"
          accept="image/jpeg,image/jpg,image/png"
          onChange={(e) => handlePhotoChange(photoKey, e.target.files[0])}
          className="hidden"
        />
      </label>
    </div>
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-2 sm:p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between z-10">
          <div>
            <h2 className="text-lg sm:text-2xl font-bold text-gray-900">Submit Maintenance</h2>
            <p className="text-xs sm:text-sm text-gray-600 mt-1">
              Device: {device?.interaction_id} - {device?.gfm_cost_center}
            </p>
          </div>
          <button
            onClick={handleClose}
            disabled={submitting}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Modal Body */}
        <div className="px-4 sm:px-6 py-4 sm:py-6">
          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                {success}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Photo Upload Sections */}
            <div className="bg-gray-50 rounded-lg p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-xl font-semibold mb-3 sm:mb-4">Section 1 Photos (3 required)</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
                <PhotoUploadBox photoKey="section1_1" label="Photo 1" />
                <PhotoUploadBox photoKey="section1_2" label="Photo 2" />
                <PhotoUploadBox photoKey="section1_3" label="Photo 3" />
              </div>

              <h3 className="text-base sm:text-xl font-semibold mb-3 sm:mb-4">Section 2 Photos (3 required)</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
                <PhotoUploadBox photoKey="section2_1" label="Photo 1" />
                <PhotoUploadBox photoKey="section2_2" label="Photo 2" />
                <PhotoUploadBox photoKey="section2_3" label="Photo 3" />
              </div>

              <h3 className="text-base sm:text-xl font-semibold mb-3 sm:mb-4">Section 3 Photos (2 required)</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <PhotoUploadBox photoKey="section3_1" label="Photo 1" />
                <PhotoUploadBox photoKey="section3_2" label="Photo 2" />
              </div>
            </div>

            {/* Maintenance Details */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-xl font-semibold mb-3 sm:mb-4">Maintenance Details</h3>
              
              {/* Job Description */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description *
                </label>
                <textarea
                  name="job_description"
                  value={formData.job_description}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe the maintenance work performed..."
                  required
                />
              </div>

              {/* Status */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status *
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="Ok">Ok</option>
                  <option value="Not Ok">Not Ok</option>
                </select>
              </div>

              {/* Remarks */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Remarks (Optional)
                </label>
                <textarea
                  name="remarks"
                  value={formData.remarks}
                  onChange={handleInputChange}
                  rows={2}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Additional notes or observations..."
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row justify-end gap-3 sm:gap-4">
              <button
                type="button"
                onClick={handleClose}
                disabled={submitting}
                className="w-full sm:w-auto px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation order-2 sm:order-1"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="w-full sm:w-auto px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center touch-manipulation order-1 sm:order-2"
              >
                {submitting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Submitting...
                  </>
                ) : (
                  'Submit Maintenance'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PhotoUploadModal;
