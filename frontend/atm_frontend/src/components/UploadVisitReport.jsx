import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { technicianAPI } from '../api/technician';

const electricalPhotoSections = [
  {
    id: 'section1',
    title: 'Section 1',
    photoCount: 4,
    description: 'Photos must be Nightly and clear, also showing machine and pylon from four sides from 3 to 5 meters away.'
  },
  {
    id: 'section2',
    title: 'Section 2',
    photoCount: 4,
    description: 'Photos must be Nightly and clear. Zoom in and out for front and back from 3 to 5 meters away.'
  },
  {
    id: 'section3',
    title: 'Section 3',
    photoCount: 4,
    description: 'Photos must be clear, also showing HVAC Temperature, Power voltmeter, Internally Light & Externally Light.'
  },
  {
    id: 'section4',
    title: 'Section 4',
    photoCount: 4,
    description: 'Photos for machine Screen, Keyboard, ATM Code, Kiosk and Pylon.'
  },
  {
    id: 'section5',
    title: 'Section 5',
    photoCount: 3,
    description: 'Photos for machine Screen, Keyboard, ATM Code, Kiosk and Pylon.'
  }
];

const defaultPhotoSections = [
  {
    id: 'section1',
    title: 'Section 1: Machine & Pylon (3-5m away)',
    photoCount: 3,
    slotLabels: [
      'Side view of the device',
      'Front view of the device',
      'Back view of the device'
    ]
  },
  {
    id: 'section2',
    title: 'Section 2: Zoomed Front & Back (3-5m)',
    photoCount: 3,
    slotLabels: [
      'Device pole photo',
      'Device with cleaning worker',
      'Device serial/number photo'
    ]
  },
  {
    id: 'section3',
    title: 'Section 3: Asphalt & Pavement',
    photoCount: 2,
    slotLabels: [
      'Pavement photo',
      'Close-up of the device'
    ]
  }
];

const createInitialPhotosState = (sections) => {
  const initialState = {};
  sections.forEach((section) => {
    for (let i = 1; i <= section.photoCount; i += 1) {
      initialState[`${section.id}_${i}`] = null;
    }
  });
  return initialState;
};

const UploadVisitReport = ({ device, onBack }) => {
  const navigate = useNavigate();
  const deviceTypeRaw = (device?.device_type || device?.type || '').toString();
  const gfmProblemType = (device?.gfm_problem || device?.gfm_problem_type || '').toString();

  const normalizedProblem = gfmProblemType.toLowerCase().replace(/[^a-z]/g, ' ');
  const normalizedDeviceType = deviceTypeRaw.toLowerCase();
  const isElectrical = (
    normalizedProblem.includes('electro') && normalizedProblem.includes('mechanical')
  ) || normalizedProblem.includes('electrical') || normalizedDeviceType.includes('electrical');
  const photoSections = isElectrical ? electricalPhotoSections : defaultPhotoSections;
  const totalPhotosRequired = photoSections.reduce((total, section) => total + section.photoCount, 0);
  
  // Get today's date in YYYY-MM-DD format
  const getTodayDate = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  
  const [visitDate, setVisitDate] = useState(getTodayDate());
  const [halfMonthPeriod, setHalfMonthPeriod] = useState('1-14');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [photos, setPhotos] = useState(() => createInitialPhotosState(photoSections));

  useEffect(() => {
    setPhotos(createInitialPhotosState(photoSections));
  }, [photoSections]);

  const handlePhotoChange = (photoKey, event) => {
    const file = event.target.files[0];
    if (file) {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      if (!validTypes.includes(file.type)) {
        setError('Only JPG and PNG files are allowed');
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      setPhotos(prev => ({ ...prev, [photoKey]: file }));
      setError('');
    }
  };

  const getUploadedCount = () => {
    return Object.values(photos).filter(p => p !== null).length;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (getUploadedCount() < totalPhotosRequired) {
      setError(`Please upload all ${totalPhotosRequired} required photos`);
      return;
    }
    
    if (!visitDate) {
      setError('Please select a visit date');
      return;
    }
    
    if (!device || !device.id) {
      console.error('Device ID is missing!', device);
      setError('Device ID not found. Please refresh the dashboard and try again.');
      return;
    }
    
    try {
      setSubmitting(true);
      setError('');
      
      const formData = new FormData();
      formData.append('device_id', device.id); // Use database device ID
      formData.append('visit_date', visitDate);
      formData.append('job_description', 'Routine maintenance visit'); // Required field
      formData.append('job_status', 'Ok'); // Required field (Ok/Not Ok)
      formData.append('remarks', ''); // Optional field
      
      Object.keys(photos).forEach(key => {
        if (photos[key]) {
          formData.append(key, photos[key]);
        }
      });
      
      await technicianAPI.submitMaintenance(formData);
      
      setSuccess('Visit report submitted successfully!');
      setTimeout(() => {
        navigate('/technician');
      }, 1500);
      
    } catch (err) {
      setError(err.error || 'Failed to submit visit report');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Back Link */}
        <button
          onClick={onBack}
          className="mb-6 text-gray-600 hover:text-gray-900 flex items-center"
        >
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Devices
        </button>

        {/* Device Info Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{device.interaction_id || device.gfm_cost_center}</h1>
              <p className="text-sm text-gray-600">Device Information</p>
            </div>
            {device.gfm_problem && device.gfm_problem !== 'N/A' && (
              <span className="px-3 py-1 text-sm font-semibold rounded-full bg-blue-600 text-white">
                {device.gfm_problem}
              </span>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4 mt-4">
            <div>
              <p className="text-sm text-gray-600">Cost Center</p>
              <p className="font-medium">{device.gfm_cost_center || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className={`font-medium ${
                device.submission_status === 'Done' 
                  ? 'text-red-600' 
                  : device.submission_status === 'Pending'
                  ? 'text-yellow-600'
                  : 'text-green-600'
              }`}>
                {device.submission_status || 'Active'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Problem Type</p>
              <p className="font-medium">{device.gfm_problem || 'Routine Maintenance'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Problem Date</p>
              <p className="font-medium">{device.gfm_problem_date || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">City</p>
              <p className="font-medium">{device.city || 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* Upload Visit Report Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Upload Visit Report</h2>
          <p className="text-sm text-gray-600 mb-6">Upload all 8 required photos to submit your visit report</p>

          {/* Success Message */}
          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Visit Date and optional Half Month Period */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Visit Date
                </label>
                <input
                  type="date"
                  value={visitDate}
                  onChange={(e) => setVisitDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                />
              </div>
              {!isElectrical && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Half Month Period
                  </label>
                  <select
                    value={halfMonthPeriod}
                    onChange={(e) => setHalfMonthPeriod(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="1-14">1-14</option>
                    <option value="15-30">15-30</option>
                  </select>
                </div>
              )}
            </div>

            {/* Photo Sections */}
            {photoSections.map((section) => {
              const uploadedInSection = Array.from({ length: section.photoCount }).reduce((count, _, index) => {
                const key = `${section.id}_${index + 1}`;
                return photos[key] ? count + 1 : count;
              }, 0);

              let gridColsClass = 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4';
              if (section.photoCount === 3) {
                gridColsClass = 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4';
              } else if (section.photoCount === 2) {
                gridColsClass = 'grid grid-cols-1 sm:grid-cols-2 gap-4';
              }

              return (
                <div className="mb-6" key={section.id}>
                  <h3 className="text-base font-medium text-gray-900 mb-3">
                    {section.title} <span className="text-gray-500">({uploadedInSection}/{section.photoCount} photos)</span>
                  </h3>
                  {section.description && (
                    <p className="text-sm text-gray-600 mb-3">{section.description}</p>
                  )}
                  <div className={gridColsClass}>
                    {Array.from({ length: section.photoCount }).map((_, index) => {
                      const photoKey = `${section.id}_${index + 1}`;
                      const slotLabel = section.slotLabels?.[index];
                      return (
                        <div key={photoKey}>
                          <label className="block cursor-pointer">
                            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-500 transition-colors">
                              {photos[photoKey] ? (
                                <div className="text-green-600">
                                  <svg className="w-8 h-8 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                  <p className="text-sm mt-2">Photo {index + 1} uploaded</p>
                                </div>
                              ) : (
                                <div>
                                  <svg className="w-8 h-8 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                  </svg>
                                  <p className="text-sm text-gray-600 mt-2">Choose Photo</p>
                                  <p className="text-xs text-blue-600 font-medium mt-2">
                                    {slotLabel || `Slot ${index + 1}`}
                                  </p>
                                </div>
                              )}
                            </div>
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => handlePhotoChange(photoKey, e)}
                              className="hidden"
                            />
                          </label>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}

            {/* Photo Count */}
            <p className="text-sm text-gray-600 mb-6">
              Total: {getUploadedCount()}/{totalPhotosRequired} photos uploaded
            </p>

            {/* Action Buttons */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={onBack}
                className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                disabled={submitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || getUploadedCount() < totalPhotosRequired}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {submitting ? 'Submitting...' : 'Submit Report'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UploadVisitReport;
