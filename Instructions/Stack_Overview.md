# Stack Overview - ATM Maintenance Management System

## Technology Stack

### Backend: Django 4.2+ with Django REST Framework
**Why Django?**
- **Mature ORM**: Robust PostgreSQL integration with built-in migration system
- **Security**: Built-in protection against SQL injection, XSS, CSRF
- **Admin Interface**: Quick data management and debugging
- **REST Framework**: Powerful serialization and API view classes
- **Community Support**: Extensive documentation and third-party packages
- **Authentication**: Native support for JWT tokens via `djangorestframework-simplejwt`

**Key Packages**:
- `djangorestframework` - RESTful API development
- `djangorestframework-simplejwt` - JWT authentication
- `psycopg2-binary` - PostgreSQL adapter
- `openpyxl` - Excel file parsing
- `reportlab` or `xhtml2pdf` - PDF generation
- `python-decouple` - Environment variable management
- `django-cors-headers` - CORS configuration

---

### Frontend: React 18+ with Tailwind CSS
**Why React?**
- **Component-Based**: Modular, reusable UI components
- **Virtual DOM**: Efficient rendering and performance
- **Rich Ecosystem**: Extensive libraries for routing, state management, HTTP requests
- **Developer Experience**: Hot reload, debugging tools, large community
- **Modern JavaScript**: Hooks, Context API for state management

**Why Tailwind CSS?**
- **Utility-First**: Rapid UI development with predefined classes
- **Responsive Design**: Mobile-first breakpoints built-in
- **Consistency**: Design system enforced through utility classes
- **No CSS Conflicts**: Scoped styling without additional tooling
- **Small Bundle Size**: PurgeCSS removes unused styles

**Key Libraries**:
- `react-router-dom` - Client-side routing
- `axios` - HTTP client for API calls
- `lucide-react` - Modern icon library
- `tailwindcss` - Utility-first CSS framework

---

### Database: PostgreSQL 14+
**Why PostgreSQL?**
- **ACID Compliance**: Data integrity and transaction safety
- **Advanced Features**: JSON fields, full-text search, array types
- **Scalability**: Handles large datasets efficiently
- **Reliability**: Proven track record in production environments
- **Django Integration**: First-class support with native adapters

**Schema Design Principles**:
- Normalized structure (3NF)
- Foreign keys with appropriate cascade rules
- Indexed fields for query performance (interaction_id, user email)
- Timestamp tracking (created_at, updated_at)

---

### File Storage: Local /media/ (Development)
**Current Approach**:
- Photos stored in `/media/photos/{submission_id}/`
- PDFs stored in `/media/pdfs/{submission_id}/`
- Served via Django's MEDIA_URL in development

**Future Migration Path**:
- AWS S3 for production
- CloudFront CDN for global delivery
- Presigned URLs for secure access

---

### Email Delivery: Django EmailBackend (SMTP)
**Current Approach**:
- Django's built-in email system
- SMTP configuration via environment variables
- Synchronous sending (blocking)

**Future Optimization**:
- Celery + Redis for async email sending
- Email queue for retry logic
- SendGrid/AWS SES for production

---

### Authentication: JWT (JSON Web Tokens)
**Why JWT?**
- **Stateless**: No server-side session storage
- **Scalable**: Works across multiple servers
- **Mobile-Friendly**: Token stored in memory (React state)
- **Standard**: Industry-standard authentication method

**Token Strategy**:
- Access Token: 1 hour expiry (short-lived)
- Refresh Token: 7 days expiry (long-lived)
- Role embedded in token payload
- Tokens stored in React state (NOT localStorage)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ Host       │  │ Technician │  │ Supervisor           │  │
│  │ Dashboard  │  │ Dashboard  │  │ Dashboard            │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
│         │                │                    │              │
│         └────────────────┴────────────────────┘              │
│                          │                                   │
│                    JWT Auth + API Calls                      │
└──────────────────────────┼───────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   NGINX     │ (Future: Reverse Proxy)
                    └──────┬──────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                    Backend (Django REST API)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Auth Views  │  │ Host Views   │  │ Technician Views │   │
│  │ (JWT)       │  │ (Excel,      │  │ (Devices,        │   │
│  │             │  │  Users)      │  │  Submissions)    │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Supervisor Views                          │   │
│  │  (Submissions, Approval, PDF Gen, Email)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│         ┌────────────────┼────────────────┐                 │
│         │                │                │                 │
│    ┌────▼────┐    ┌──────▼──────┐  ┌─────▼──────┐         │
│    │ Models  │    │ Utils       │  │ Middleware │         │
│    │ (ORM)   │    │ (PDF, Email)│  │ (Auth,Log) │         │
│    └────┬────┘    └─────────────┘  └────────────┘         │
└─────────┼──────────────────────────────────────────────────┘
          │
    ┌─────▼──────┐
    │ PostgreSQL │
    │ Database   │
    └────────────┘
```

---

## Development Environment

**Prerequisites**:
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- npm or yarn

**Project Structure**:
```
atm-maintenance-system/
├── backend/
│   ├── atm_backend/         # Django project
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── core/                # Main app
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   └── urls.py
│   ├── utils/               # Helper functions
│   │   ├── excel_parser.py
│   │   ├── pdf_generator.py
│   │   ├── email_sender.py
│   │   └── file_handler.py
│   ├── media/               # Uploaded files
│   ├── static/              # Static assets
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   │   ├── Host/
│   │   │   ├── Technician/
│   │   │   └── Supervisor/
│   │   ├── context/         # React Context (Auth)
│   │   ├── api/             # API service layer
│   │   ├── utils/           # Helper functions
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   └── tailwind.config.js
│
├── instructions/            # VIBE documentation
│   ├── stack-overview.md
│   ├── best-practices.md
│   ├── security-guidelines.md
│   ├── database-schema.md
│   └── api-endpoints.md
│
└── README.md
```

---

## Deployment Strategy (Localhost Development)

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Frontend**:
```bash
cd frontend
npm install
npm start
```

**Database**:
```bash
psql -U postgres
CREATE DATABASE atm_maintenance;
CREATE USER atm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE atm_maintenance TO atm_user;
```

---

## Future Scalability Considerations

**When moving to production**:
1. **Containerization**: Docker + Docker Compose
2. **Reverse Proxy**: NGINX for static files and load balancing
3. **Cloud Storage**: AWS S3 for media files
4. **CDN**: CloudFront for global file delivery
5. **Async Tasks**: Celery + Redis for email sending and PDF generation
6. **Monitoring**: Sentry for error tracking, Prometheus for metrics
7. **Database**: RDS or managed PostgreSQL with automated backups
8. **CI/CD**: GitHub Actions or GitLab CI for automated testing and deployment

---

## Performance Optimization

**Backend**:
- Database query optimization (select_related, prefetch_related)
- API response caching (Redis)
- Pagination for large datasets
- Database connection pooling

**Frontend**:
- Code splitting (React.lazy)
- Image optimization (WebP format, lazy loading)
- Bundle size optimization (tree shaking)
- Service workers for offline capability

---

## Version Control Strategy

**Git Workflow**:
- `main` branch: Production-ready code
- `develop` branch: Integration branch
- `feature/*` branches: Individual features
- Pull requests required for merging
- Semantic versioning (v1.0.0)

---

This stack provides a solid foundation for building a secure, scalable, and maintainable ATM maintenance management system while allowing for future growth and optimization.