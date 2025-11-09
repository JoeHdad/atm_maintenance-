import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../../context/AuthContext';
import TechnicianForm from '../TechnicianForm';
import { hostAPI } from '../../api/host';

// Mock the API module
jest.mock('../../api/host');

// Mock the navigate function
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Wrapper component to provide auth context and routing
const TestWrapper = () => (
  <AuthProvider>
    <MemoryRouter initialEntries={['/create-technician']}>
      <Routes>
        <Route path="/create-technician" element={<TechnicianForm />} />
      </Routes>
    </MemoryRouter>
  </AuthProvider>
);

describe('TechnicianForm Integration Tests', () => {
  // Mock successful API response
  const mockApiResponse = {
    id: 1,
    username: 'tech_test1',
    role: 'technician',
    city: 'Riyadh',
    created_at: '2025-10-22T14:02:36.091791Z'
  };

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Mock successful login
    localStorage.setItem('access_token', 'fake-jwt-token');
    
    // Mock successful API call by default
    hostAPI.createTechnician.mockResolvedValue(mockApiResponse);
  });

  afterEach(() => {
    localStorage.clear();
  });

  test('renders form with all fields', () => {
    render(<TestWrapper />);
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/city/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create technician/i })).toBeInTheDocument();
  });

  test('validates form fields before submission', async () => {
    render(<TestWrapper />);
    
    // Try to submit empty form
    fireEvent.click(screen.getByRole('button', { name: /create technician/i }));
    
    // Check for validation errors
    expect(await screen.findByText(/username is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    expect(screen.getByText(/please confirm your password/i)).toBeInTheDocument();
    expect(screen.getByText(/city is required/i)).toBeInTheDocument();
    
    // Verify API was not called
    expect(hostAPI.createTechnician).not.toHaveBeenCalled();
  });

  test('shows password strength indicator', async () => {
    render(<TestWrapper />);
    
    const passwordInput = screen.getByLabelText(/password/i);
    
    // Test weak password
    fireEvent.change(passwordInput, { target: { value: 'weak' } });
    expect(await screen.findByText(/weak/i)).toBeInTheDocument();
    
    // Test fair password
    fireEvent.change(passwordInput, { target: { value: 'Better123' } });
    expect(await screen.findByText(/good/i)).toBeInTheDocument();
    
    // Test strong password
    fireEvent.change(passwordInput, { target: { value: 'Very$tr0ngP@ss' } });
    expect(await screen.findByText(/strong/i)).toBeInTheDocument();
  });

  test('submits form with valid data', async () => {
    render(<TestWrapper />);
    
    // Fill in form
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'tech_test1' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'SecurePass123!' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'SecurePass123!' } });
    fireEvent.change(screen.getByLabelText(/city/i), { target: { value: 'Riyadh' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /create technician/i }));
    
    // Verify loading state
    expect(await screen.findByText(/creating.../i)).toBeInTheDocument();
    
    // Wait for API call to complete
    await waitFor(() => {
      expect(hostAPI.createTechnician).toHaveBeenCalledWith({
        username: 'tech_test1',
        password: 'SecurePass123!',
        city: 'Riyadh'
      });
    });
    
    // Verify success message and form reset
    expect(await screen.findByText(/technician "tech_test1" created successfully!/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i).value).toBe('');
    expect(screen.getByLabelText(/password/i).value).toBe('');
    expect(screen.getByLabelText(/confirm password/i).value).toBe('');
    expect(screen.getByLabelText(/city/i).value).toBe('');
  });

  test('handles API errors', async () => {
    // Mock API error
    hostAPI.createTechnician.mockRejectedValueOnce({
      response: {
        data: {
          username: ['A user with that username already exists.']
        },
        status: 400
      }
    });
    
    render(<TestWrapper />);
    
    // Fill in form with duplicate username
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'existing_user' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'SecurePass123!' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'SecurePass123!' } });
    fireEvent.change(screen.getByLabelText(/city/i), { target: { value: 'Riyadh' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /create technician/i }));
    
    // Verify error message is displayed
    expect(await screen.findByText(/a user with that username already exists/i)).toBeInTheDocument();
  });

  test('validates username format', async () => {
    render(<TestWrapper />);
    
    const usernameInput = screen.getByLabelText(/username/i);
    
    // Test invalid characters
    fireEvent.change(usernameInput, { target: { value: 'test@user' } });
    fireEvent.blur(usernameInput);
    
    expect(await screen.findByText(/username must contain only letters, numbers, and underscores/i)).toBeInTheDocument();
    
    // Test minimum length
    fireEvent.change(usernameInput, { target: { value: 'ab' } });
    fireEvent.blur(usernameInput);
    
    expect(await screen.findByText(/username must be at least 3 characters/i)).toBeInTheDocument();
    
    // Test valid username
    fireEvent.change(usernameInput, { target: { value: 'valid_user123' } });
    fireEvent.blur(usernameInput);
    
    expect(screen.queryByText(/username must contain only letters, numbers, and underscores/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/username must be at least 3 characters/i)).not.toBeInTheDocument();
  });

  test('validates password match', async () => {
    render(<TestWrapper />);
    
    const passwordInput = screen.getByLabelText(/password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    
    // Enter mismatched passwords
    fireEvent.change(passwordInput, { target: { value: 'Password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Different456' } });
    fireEvent.blur(confirmPasswordInput);
    
    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
    
    // Make them match
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123' } });
    fireEvent.blur(confirmPasswordInput);
    
    expect(screen.queryByText(/passwords do not match/i)).not.toBeInTheDocument();
  });
});
