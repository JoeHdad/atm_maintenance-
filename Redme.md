# ATM Maintenance System

## Project Overview
The ATM Maintenance System streamlines collaboration between hosts, technicians, and supervisors. A Django REST API powers the backend workflows (device onboarding, submissions, approvals), while a React dashboard orchestrates role-based experiences, PDF generation, and notifications.

## Features
- **Role-specific dashboards** with JWT authentication for hosts, technicians, and supervisors.
- **Submission lifecycle** covering technician visit logs, supervisor approvals/rejections, and comment trails.
- **Automated PDF generation + email dispatch** with standardized filenames per device type.
- **Device intelligence**: type filters, location metadata, and status summaries.
- **Notification center** informing technicians when supervisors approve or reject reports.
- **Bulk data utilities** for Excel imports, data validation, and QA scripts.
- **Production-ready configs** (CORS, CSRF exemptions, media serving, deploy scripts) targeting Render/Hostinger.

## Installation
> Requirements: Python 3.10+, Node.js 18+, PostgreSQL 14+, Git.

### Backend
```bash
git clone <repo-url>
cd atm-maintenance-system/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd ../frontend
npm install
npm start
```

### Editable install (package-style)
```bash
cd backend
pip install -e .
```

## Usage Examples
### Backend utilities
```python
from core.utils.pdf_generator import generate_submission_pdf
from core.models import Submission

submission = Submission.objects.get(pk=1)
pdf_path = generate_submission_pdf(submission)
print(pdf_path)
```

```python
from core.views_admin import SubmissionApprovalService

service = SubmissionApprovalService(user=request.user)
approved_submission = service.approve(submission_id=42, notes="All checks passed")
```

### Frontend API client
```javascript
import supervisorClient from '@/api/supervisor';

export async function fetchApprovedElectrical() {
  const { data } = await supervisorClient.getSubmissions({
    status: 'Approved',
    device_type: 'Electrical',
  });
  return data.results;
}
```

## Project Structure
```
atm-maintenance-system/
├── backend/
│   ├── atm_backend/        # Django project config
│   ├── core/               # Models, views, serializers, utils
│   ├── media/              # Uploaded assets (dev)
│   ├── staticfiles/
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── utils/
│   └── package.json
├── Instructions/           # Stack overview, security, schema docs
├── AI_report/              # Deployment + QA artifacts
├── requirements.txt        # Root requirements (if applicable)
└── Redme.md                # This README
```

## Documentation
- Functions and classes include docstrings describing behavior and parameters.
- Extended references live under `Instructions/` (stack overview, API endpoints, DB schema, best practices, security guidelines).
- Link additional external docs or knowledge bases here when available.

## Testing
Run backend tests with pytest:
```bash
cd backend
pytest
```
Frontend tests (if configured) can be executed via `npm test` inside `frontend/`.

## Contribution Guidelines
1. **Branching**: Use `feature/<short-desc>` for enhancements, `fix/<issue>` for bug fixes.
2. **Code quality**: Follow PEP8, add/maintain type hints, and align with existing React + Tailwind conventions. Include docstrings for new helpers.
3. **Process**: Keep commits focused, open draft PRs early, and request review before merge. Attach screenshots/logs for UI or API changes.
4. **Testing**: Extend pytest/React coverage for your changes and ensure `pytest` + `npm test` (if applicable) pass locally.

## License
_Placeholder — insert MIT/Apache/custom license text or link once finalized._
