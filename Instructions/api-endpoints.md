# API Endpoints - ATM Maintenance Management System

## Overview

The ATM Maintenance Management System provides a RESTful API built with Django REST Framework. All endpoints require JWT authentication except for login. The API follows REST conventions with proper HTTP status codes and JSON responses.

---

## Authentication Endpoints

### POST /api/auth/login/
**Login user and return JWT tokens**

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "technician1",
    "role": "technician",
    "city": "Riyadh"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Account disabled

---

### POST /api/auth/refresh/
**Refresh access token**

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Data Host Endpoints

### POST /api/host/technicians/
**Create new technician account**

**Authorization:** Data Host only

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "city": "string"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "username": "technician2",
  "role": "technician",
  "city": "Jeddah",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### POST /api/host/upload-excel/
**Upload Excel file and import devices**

**Authorization:** Data Host only

**Request Body:** FormData
- `file`: Excel file (.xlsx)
- `technician_id`: integer (optional, for specific technician)

**Response (200 OK):**
```json
{
  "message": "Successfully imported 25 devices",
  "imported_count": 25,
  "errors": []
}
```

**Excel Format:**
| Interaction ID | Gfm cost Center | Status | Gfm Problem Type | Gfm Problem Date |
|----------------|-----------------|--------|------------------|------------------|
| ATM001 | CC001 | Active | Hardware | 2024-01-01 |

---

## Technician Endpoints

### GET /api/technician/devices/
**List devices assigned to technician**

**Authorization:** Technician only

**Query Parameters:**
- `type`: "Cleaning" or "Electrical"
- `status`: Device status filter

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "interaction_id": "ATM001",
      "gfm_cost_center": "CC001",
      "status": "Active",
      "gfm_problem_type": "Hardware",
      "gfm_problem_date": "2024-01-01",
      "city": "Riyadh",
      "region": "Central",
      "type": "Cleaning",
      "next_due_date": "2024-01-15"
    }
  ]
}
```

---

### POST /api/technician/submit/
**Submit maintenance photos and data**

**Authorization:** Technician only

**Request Body:** FormData
- `device_id`: integer
- `type`: "Cleaning" or "Electrical"
- `visit_date`: "YYYY-MM-DD"
- `half_month`: 1 or 2
- `photos`: File[] (exactly 8 photos)

**Photo Requirements:**
- Section 1: 3 photos (machine + pylon, 3-5 meters away)
- Section 2: 3 photos (zoomed front + back, 3-5 meters)
- Section 3: 2 photos (asphalt + pavement with security column)

**Response (201 Created):**
```json
{
  "id": 1,
  "technician": 2,
  "device": 1,
  "type": "Cleaning",
  "visit_date": "2024-01-15",
  "half_month": 1,
  "status": "Pending",
  "created_at": "2024-01-15T14:30:00Z",
  "photos": [
    {
      "id": 1,
      "section": 1,
      "file_url": "/media/photos/1/section1_1.jpg",
      "order_index": 1
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request`: Missing photos or invalid data
- `409 Conflict`: Duplicate submission for same device/half-month

---

## Supervisor Endpoints

### GET /api/supervisor/submissions/
**List all submissions with filtering**

**Authorization:** Supervisor only

**Query Parameters:**
- `status`: "Pending", "Approved", "Rejected"
- `city`: City filter
- `technician`: Technician ID filter
- `date_from`: "YYYY-MM-DD"
- `date_to`: "YYYY-MM-DD"
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://api.example.com/api/supervisor/submissions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "technician": {
        "id": 2,
        "username": "technician1",
        "city": "Riyadh"
      },
      "device": {
        "interaction_id": "ATM001",
        "city": "Riyadh",
        "type": "Cleaning"
      },
      "type": "Cleaning",
      "visit_date": "2024-01-15",
      "half_month": 1,
      "status": "Pending",
      "created_at": "2024-01-15T14:30:00Z",
      "photo_count": 8
    }
  ]
}
```

---

### GET /api/supervisor/submissions/{id}/
**Get detailed submission information**

**Authorization:** Supervisor only

**Response (200 OK):**
```json
{
  "id": 1,
  "technician": {
    "id": 2,
    "username": "technician1",
    "city": "Riyadh"
  },
  "device": {
    "interaction_id": "ATM001",
    "gfm_cost_center": "CC001",
    "status": "Active",
    "gfm_problem_type": "Hardware",
    "gfm_problem_date": "2024-01-01",
    "city": "Riyadh",
    "region": "Central",
    "type": "Cleaning"
  },
  "type": "Cleaning",
  "visit_date": "2024-01-15",
  "half_month": 1,
  "status": "Pending",
  "pdf_url": null,
  "remarks": null,
  "created_at": "2024-01-15T14:30:00Z",
  "photos": [
    {
      "id": 1,
      "section": 1,
      "file_url": "/media/photos/1/section1_1.jpg",
      "order_index": 1
    }
  ]
}
```

---

### PATCH /api/supervisor/submissions/{id}/
**Approve or reject submission**

**Authorization:** Supervisor only

**Request Body (Approve):**
```json
{
  "action": "approve"
}
```

**Request Body (Reject):**
```json
{
  "action": "reject",
  "remarks": "Photos unclear, please retake"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "Approved",
  "pdf_url": "/media/pdfs/submission_1.pdf",
  "remarks": null,
  "approved_at": "2024-01-16T09:00:00Z"
}
```

---

### GET /api/submissions/{id}/pdf/
**Download generated PDF report**

**Authorization:** Supervisor only

**Response:** PDF file download

---

## Common Response Formats

### Error Response
```json
{
  "error": "Detailed error message",
  "code": "ERROR_CODE",
  "field_errors": {
    "username": ["This field is required"],
    "password": ["Password too weak"]
  }
}
```

### Pagination Response
```json
{
  "count": 100,
  "next": "http://api.example.com/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful deletion
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (duplicate submission)
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error

---

## Rate Limiting

- Authentication endpoints: 5 requests per minute per IP
- File upload endpoints: 10 requests per hour per user
- General API endpoints: 100 requests per minute per user

---

## Content Types

- **Request**: `application/json` for data, `multipart/form-data` for file uploads
- **Response**: `application/json` for all responses except PDF downloads

---

## Authentication Headers

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

This API provides comprehensive functionality for the ATM Maintenance Management System with proper authentication, validation, and error handling.