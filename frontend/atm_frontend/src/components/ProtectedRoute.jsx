import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({
  children,
  requiredRole = null,
  redirectTo = '/login'
}) => {
  const { isAuthenticated, getUserRole, loading } = useAuth();
  const location = useLocation();

  console.log('[ProtectedRoute] Rendering - loading:', loading, 'isAuthenticated:', isAuthenticated(), 'location:', location.pathname);

  // Show loading spinner while checking authentication
  if (loading) {
    console.log('[ProtectedRoute] Showing loading spinner');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Check if user is authenticated
  if (!isAuthenticated()) {
    console.log('[ProtectedRoute] User not authenticated, redirecting to:', redirectTo);
    // Redirect to login with return url
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  console.log('[ProtectedRoute] User authenticated, rendering children');

  // Check role-based access if required
  if (requiredRole) {
    const userRole = getUserRole();
    const allowedRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];

    console.log('[ProtectedRoute] Checking role - userRole:', userRole, 'requiredRole:', requiredRole);

    if (!allowedRoles.includes(userRole)) {
      console.log('[ProtectedRoute] Role check failed, showing access denied');

      // User doesn't have required role, redirect to unauthorized page or dashboard
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="mt-4 text-lg font-medium text-gray-900">Access Denied</h3>
              <p className="mt-2 text-sm text-gray-600">
                You don't have permission to access this page. Your current role is: <strong>{userRole}</strong>
              </p>
              <div className="mt-6">
                <button
                  onClick={() => window.history.back()}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Go Back
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }
  }

  // User is authenticated and has required role, render children
  return children;
};

export default ProtectedRoute;