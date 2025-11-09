import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { hostAPI } from '../api/host';

const TechnicianForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    city: '',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);

  const cities = [
    'Abha',
    'Al Baha',
    'Al Namas',
    'Bishah',
    'Dammam',
    'Hail',
    'Jazan',
    'Jeddah',
    'Khamis Mushait',
    'Mecca',
    'Medina',
    'Najran',
    'Riyadh',
    'Sabya',
    'Sharurah',
    'Tabuk',
  ];

  // Calculate password strength
  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength += 25;
    if (password.length >= 12) strength += 25;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
    if (/\d/.test(password)) strength += 12.5;
    if (/[!@#$%^&*]/.test(password)) strength += 12.5;
    return Math.min(strength, 100);
  };

  // Get password strength label and color
  const getPasswordStrengthInfo = (strength) => {
    if (strength === 0) return { label: '', color: '' };
    if (strength < 40) return { label: 'Weak', color: 'bg-red-500' };
    if (strength < 70) return { label: 'Fair', color: 'bg-yellow-500' };
    if (strength < 90) return { label: 'Good', color: 'bg-blue-500' };
    return { label: 'Strong', color: 'bg-green-500' };
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      newErrors.username =
        'Username must contain only letters, numbers, and underscores';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // City validation
    if (!formData.city) {
      newErrors.city = 'City is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Update password strength
    if (name === 'password') {
      setPasswordStrength(calculatePasswordStrength(value));
    }

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage('');
    setErrorMessage('');

    // Validate form
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Prepare data for API (exclude confirmPassword)
      const apiData = {
        username: formData.username.trim(),
        password: formData.password,
        city: formData.city,
      };

      // Call API
      const response = await hostAPI.createTechnician(apiData);

      // Success
      setSuccessMessage(
        `Technician "${response.username}" created successfully!`
      );

      // Clear form
      setFormData({
        username: '',
        password: '',
        confirmPassword: '',
        city: '',
      });
      setPasswordStrength(0);
      setErrors({});
    } catch (error) {
      // Handle errors
      if (typeof error === 'object') {
        const errorMessages = Object.entries(error)
          .map(([key, value]) => {
            if (Array.isArray(value)) {
              return `${key}: ${value.join(', ')}`;
            }
            return `${key}: ${value}`;
          })
          .join('\n');
        setErrorMessage(errorMessages);
      } else {
        setErrorMessage(error || 'Failed to create technician');
      }
    } finally {
      setLoading(false);
    }
  };

  const strengthInfo = getPasswordStrengthInfo(passwordStrength);

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Create Technician Account
        </h2>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm font-medium text-green-800">{successMessage}</p>
          </div>
        )}

        {/* Error Message */}
        {errorMessage && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm font-medium text-red-800 whitespace-pre-wrap">
              {errorMessage}
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Username Field */}
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter username"
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                errors.username ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.username && (
              <p className="mt-1 text-sm text-red-600">{errors.username}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Letters, numbers, and underscores only
            </p>
          </div>

          {/* Password Field */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter password"
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                errors.password ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password}</p>
            )}

            {/* Password Strength Indicator */}
            {formData.password && (
              <div className="mt-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Password strength:</span>
                  {strengthInfo.label && (
                    <span className={`text-xs font-medium text-white px-2 py-1 rounded ${strengthInfo.color}`}>
                      {strengthInfo.label}
                    </span>
                  )}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${strengthInfo.color}`}
                    style={{ width: `${passwordStrength}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password Field */}
          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm password"
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.confirmPassword && (
              <p className="mt-1 text-sm text-red-600">
                {errors.confirmPassword}
              </p>
            )}
          </div>

          {/* City Dropdown */}
          <div>
            <label
              htmlFor="city"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              City
            </label>
            <select
              id="city"
              name="city"
              value={formData.city}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                errors.city ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select a city</option>
              {cities.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
            {errors.city && (
              <p className="mt-1 text-sm text-red-600">{errors.city}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Creating...' : 'Create Technician'}
          </button>
        </form>

        {/* Info Text */}
        <p className="mt-6 text-center text-sm text-gray-600">
          This form creates a new technician account that can be assigned devices.
        </p>
      </div>
    </div>
  );
};

export default TechnicianForm;
