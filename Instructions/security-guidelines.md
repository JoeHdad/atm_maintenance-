# Security Guidelines - ATM Maintenance Management System

## Authentication & Authorization

### JWT Token Management
**Token Storage Strategy:**
- **Frontend**: Store access and refresh tokens in React state (not localStorage or sessionStorage)
- **Backend**: Use `djangorestframework-simplejwt` for token generation and validation
- **Token Expiry**: Access token (1 hour), Refresh token (7 days)
- **Automatic Refresh**: Implement token refresh logic before expiry

**Implementation Example:**
```javascript
// React Context for Auth
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [tokens, setTokens] = useState(null);

  const refreshToken = async () => {
    try {
      const response = await api.post('/api/auth/refresh/', {
        refresh: tokens.refresh
      });
      setTokens(response.data);
    } catch (error) {
      logout();
    }
  };

  return (
    <AuthContext.Provider value={{ tokens, setTokens, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
};
```

---

### Role-Based Access Control (RBAC)
**User Roles:**
- **Data Host**: Can upload Excel files and create technicians
- **Technician**: Can view assigned devices and submit maintenance reports
- **Supervisor**: Can review submissions and generate PDF reports

**Permission Implementation:**
```python
# Django permissions
from rest_framework.permissions import BasePermission

class IsDataHost(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'host'

class IsTechnician(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'technician'

class IsSupervisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'supervisor'
```

---

## Input Validation & Sanitization

### Backend Validation
**Django REST Framework Validators:**
- Use `serializers` for all input validation
- Implement custom validators for business logic
- Validate file uploads (type, size, content)

**Example Serializers:**
```python
class TechnicianCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'password', 'city']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
```

### Frontend Validation
**Form Validation:**
- Client-side validation for immediate feedback
- Server-side validation as the source of truth
- Use libraries like `react-hook-form` for complex forms

---

## File Upload Security

### Photo Upload Validation
**Security Checks:**
- **File Type**: Allow only `jpg`, `jpeg`, `png`
- **File Size**: Maximum 10MB per photo
- **Content Validation**: Verify file headers match extension
- **Storage**: Use secure file paths, avoid user-controlled filenames

**Implementation:**
```python
def validate_photo_file(file):
    # Check file size
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise ValidationError("File too large")

    # Check file type
    allowed_types = ['image/jpeg', 'image/png']
    if file.content_type not in allowed_types:
        raise ValidationError("Invalid file type")

    # Additional security checks
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension not in ['.jpg', '.jpeg', '.png']:
        raise ValidationError("Invalid file extension")

    return file
```

---

## Data Protection

### Password Security
**Password Policies:**
- Minimum 8 characters
- Require uppercase, lowercase, numbers, special characters
- Use Django's built-in password validators
- Hash passwords with PBKDF2 (Django default)

**Password Reset:**
- Implement secure password reset flow
- Use time-limited reset tokens
- Send reset emails securely

### Sensitive Data Handling
**Environment Variables:**
- Store all secrets in environment variables
- Use `python-decouple` for configuration
- Never commit secrets to version control

**Database Security:**
- Use parameterized queries (ORM protection)
- Implement proper database permissions
- Regular security updates for PostgreSQL

---

## API Security

### Request Security
**Rate Limiting:**
- Implement rate limiting on authentication endpoints
- Use Django's throttling classes

**CORS Configuration:**
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
```

### Error Handling
**Secure Error Responses:**
- Never expose stack traces in production
- Use generic error messages
- Log detailed errors for debugging

**Example:**
```python
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Add custom error formatting
        response.data = {
            'error': 'An error occurred',
            'code': response.status_code
        }

    return response
```

---

## HTTPS & SSL/TLS

### Development Setup
- Use HTTPS in development with self-signed certificates
- Configure Django for secure cookies
- Test all functionality over HTTPS

### Production Deployment
- Enforce HTTPS redirects
- Use valid SSL certificates
- Configure secure headers (HSTS, CSP, etc.)

---

## Audit Logging

### Security Event Logging
**Log Important Events:**
- User authentication attempts
- File uploads
- Permission changes
- Data modifications

**Implementation:**
```python
import logging

logger = logging.getLogger(__name__)

def log_security_event(user, action, details):
    logger.info(f"Security Event - User: {user.username}, Action: {action}, Details: {details}")
```

---

## Third-Party Dependencies

### Dependency Management
**Security Practices:**
- Regularly update dependencies
- Use tools like `safety` to check for vulnerabilities
- Audit new packages before adding
- Pin dependency versions in requirements.txt

**Vulnerability Scanning:**
```bash
# Check for vulnerabilities
pip install safety
safety check
```

---

## Session Management

### Secure Sessions
**Session Configuration:**
- Use secure, httpOnly cookies
- Implement session timeout
- Invalidate sessions on logout
- Use CSRF protection

**Django Settings:**
```python
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_SECURE = True
```

---

## Data Encryption

### At Rest
- Encrypt sensitive data in database
- Use PostgreSQL's encryption features
- Implement field-level encryption for PII

### In Transit
- Use TLS 1.3 for all communications
- Encrypt file transfers
- Secure API communications

---

## Security Testing

### Testing Checklist
- **Authentication Testing**: Test login, logout, token refresh
- **Authorization Testing**: Verify role-based access
- **Input Validation Testing**: Test boundary conditions and malicious inputs
- **File Upload Testing**: Test various file types and sizes
- **Session Management Testing**: Test session timeout and invalidation

### Automated Security Testing
- Use `bandit` for Python security linting
- Implement OWASP ZAP for API security testing
- Regular security audits and penetration testing

---

These security guidelines ensure the ATM Maintenance Management System maintains high security standards throughout its development and deployment lifecycle.