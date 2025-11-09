import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import logoPrimary from '../logo.png';
import logoSecondary from '../logo.jpg';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();

  // Monitor error state changes (development only)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[Login] Error state changed:', error);
    }
  }, [error]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing in either field
    if (error) {
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    try {
      // CRITICAL: Prevent default form submission FIRST
      e.preventDefault();

      // Basic validation
      if (!formData.username.trim() || !formData.password.trim()) {
        setError('Please enter both username and password');
        return;
      }

      setLoading(true);
      setError('');

      try {
        const result = await login(formData.username.trim(), formData.password.trim());

        if (!result.success) {
          setError(result.error);
          setLoading(false);
        }
        // If successful, AuthContext will handle navigation
      } catch (err) {
        console.error('Login exception:', err);
        setError('An unexpected error occurred. Please try again.');
        setLoading(false);
      }
    } catch (err) {
      // Catch ANY exception to prevent page reload
      console.error('Critical error in handleSubmit:', err);
      setError('An unexpected error occurred. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-6 px-4 sm:py-12 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6 sm:space-y-8">
        <div className="flex flex-col items-center gap-4">
          <div className="flex items-center justify-center gap-4">
            <img
              src={logoPrimary}
              alt="ATM SNB primary logo"
              className="h-14 w-auto object-contain"
            />
            <img
              src={logoSecondary}
              alt="ATM SNB secondary logo"
              className="h-14 w-auto object-contain rounded-md shadow-sm"
            />
          </div>
          <h2 className="mt-4 sm:mt-6 text-center text-2xl sm:text-3xl font-extrabold text-gray-900">
            ATM SNB
          </h2>
          <p className="mt-2 text-center text-sm sm:text-base text-gray-600">
            Sign in to your account
          </p>
        </div>

        <form className="mt-6 sm:mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                className="appearance-none rounded-none relative block w-full px-4 py-3 sm:px-3 sm:py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 text-base sm:text-sm"
                placeholder="Username"
                value={formData.username}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-4 py-3 sm:px-3 sm:py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 text-base sm:text-sm"
                placeholder="Password"
                value={formData.password}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 border-l-4 border-red-500 p-4 animate-in fade-in duration-300">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-red-800">
                    {error}
                  </p>
                  <p className="mt-1 text-xs text-red-700">
                    Please check your username and password and try again.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3 px-4 sm:py-2 border border-transparent text-base sm:text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation"
            >
              {loading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </div>
              ) : (
                'Sign in'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;