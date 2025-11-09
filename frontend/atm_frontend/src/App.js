import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import HostDashboard from './components/HostDashboard';
import HostHome from './components/HostHome';
import TechnicianForm from './components/TechnicianForm';
import ExcelUpload from './components/ExcelUpload';
import TechnicianDashboard from './components/TechnicianDashboard';
import DeviceList from './components/DeviceList';
import DeviceDetail from './components/DeviceDetail';
import SupervisorLayout from './components/SupervisorLayout';
import SupervisorDashboard from './components/SupervisorDashboard';
import SubmissionList from './components/SubmissionList';
import SubmissionDetail from './components/SubmissionDetail';
import ErrorBoundary from './components/ErrorBoundary';
import OfflineIndicator from './components/OfflineIndicator';
import './App.css';


// App Routes Component
const AppRoutes = React.memo(() => {
  const { isAuthenticated, loading, user } = useAuth();
  
  // Call isAuthenticated ONCE and store the boolean result
  // This prevents function reference instability issues
  const isAuth = isAuthenticated();
  const userRole = user?.role;
  
  console.log('[AppRoutes] Rendering - loading:', loading, 'isAuth:', isAuth, 'userRole:', userRole);
  
  // Calculate default dashboard using useMemo
  // Depends on BOOLEAN values, not function references
  const defaultDashboard = React.useMemo(() => {
    if (loading) return null;
    
    if (!isAuth) {
      return '/login';
    }
    
    console.log('[AppRoutes] Calculating dashboard for role:', userRole);
    
    if (userRole === 'host') {
      return '/host-dashboard';
    } else if (userRole === 'supervisor') {
      return '/supervisor/dashboard';
    } else if (userRole === 'technician') {
      return '/technician-dashboard';
    }
    
    return '/login';
  }, [loading, isAuth, userRole]);
  
  // Show loading screen while auth is initializing
  if (loading || !defaultDashboard) {
    console.log('[AppRoutes] Showing loading screen');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuth ? <Navigate to={defaultDashboard} replace /> : <Login />
        }
      />
      
      {/* Host Dashboard with nested routes */}
      <Route
        path="/host-dashboard"
        element={
          <ProtectedRoute>
            <HostDashboard />
          </ProtectedRoute>
        }
      >
        <Route index element={<HostHome />} />
        <Route path="create-technician" element={<TechnicianForm />} />
        <Route path="upload-devices" element={<ExcelUpload />} />
      </Route>

      {/* Technician Dashboard */}
      <Route
        path="/technician-dashboard"
        element={
          <ProtectedRoute>
            <TechnicianDashboard />
          </ProtectedRoute>
        }
      />

      {/* Technician Device List */}
      <Route
        path="/technician/devices"
        element={
          <ProtectedRoute>
            <DeviceList />
          </ProtectedRoute>
        }
      />

      {/* Technician Device Detail */}
      <Route
        path="/technician/devices/:deviceId"
        element={
          <ProtectedRoute>
            <DeviceDetail />
          </ProtectedRoute>
        }
      />
      
      {/* Technician Device Detail (alternative route) */}
      <Route
        path="/technician/device/:deviceId"
        element={
          <ProtectedRoute>
            <DeviceDetail />
          </ProtectedRoute>
        }
      />
      
      {/* Technician route (shorthand for dashboard) */}
      <Route
        path="/technician"
        element={
          <ProtectedRoute>
            <TechnicianDashboard />
          </ProtectedRoute>
        }
      />

      {/* Supervisor Routes with Layout */}
      <Route
        path="/supervisor/dashboard"
        element={
          <ProtectedRoute requiredRole="supervisor">
            <SupervisorLayout>
              <SupervisorDashboard />
            </SupervisorLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/supervisor/submissions"
        element={
          <ProtectedRoute requiredRole="supervisor">
            <SupervisorLayout>
              <SubmissionList />
            </SupervisorLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/supervisor/submissions/:id"
        element={
          <ProtectedRoute requiredRole="supervisor">
            <SupervisorLayout>
              <SubmissionDetail />
            </SupervisorLayout>
          </ProtectedRoute>
        }
      />
      {/* Legacy supervisor route - redirect to dashboard */}
      <Route
        path="/supervisor"
        element={<Navigate to="/supervisor/dashboard" replace />}
      />

      {/* Legacy routes - redirect to new structure */}
      <Route
        path="/dashboard"
        element={<Navigate to={defaultDashboard} replace />}
      />
      <Route
        path="/create-technician"
        element={<Navigate to="/host-dashboard/create-technician" replace />}
      />
      <Route
        path="/upload-excel"
        element={<Navigate to="/host-dashboard/upload-devices" replace />}
      />

      <Route
        path="/"
        element={
          <Navigate to={defaultDashboard} replace />
        }
      />
      
      {/* Catch all route */}
      <Route
        path="*"
        element={<Navigate to={defaultDashboard} replace />}
      />
    </Routes>
  );
});

// Main App Component
function App() {
  console.log('[App] Rendering main App component');
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="App">
            <OfflineIndicator />
            <AppRoutes />
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
