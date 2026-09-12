# College Student Data Collection & Admin System

A professional college student data collection web application built with FastAPI, MongoDB, and vanilla JavaScript.

## Features

### Public Student Submission
- Clean, responsive student registration form
- No login required for students
- Form validation on frontend and backend
- Success/error notifications

### Secure Admin/Staff Management Panel
- JWT-based authentication with bcrypt password hashing
- Role-based access control (Admin/Staff)
- Admin dashboard with statistics
- Student management (view, edit, delete, search, filter, pagination)
- PDF export (all students or individual)
- User management (admin only)

## Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **MongoDB** - NoSQL database with Motor (async driver)
- **Pydantic** - Data validation and serialization
- **JWT** - Token-based authentication
- **bcrypt** - Password hashing
- **ReportLab** - PDF generation
- **Uvicorn** - ASGI server

### Frontend
- **HTML5/CSS3** - Modern, responsive design
- **Vanilla JavaScript** - No frameworks
- **Fetch API** - HTTP requests
- **CSS Grid/Flexbox** - Responsive layouts

## Project Structure

```
college-student-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # MongoDB connection and indexes
│   ├── dependencies.py         # Auth dependencies
│   ├── create_admin.py         # Admin creation script
│   ├── models/
│   │   ├── __init__.py
│   │   ├── student.py          # Student models
│   │   └── user.py             # User models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py             # Auth schemas
│   │   └── response.py         # API response schemas
│   ├── auth/
│   │   ├── __init__.py
│   │   └── security.py         # JWT and password utilities
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── public.py           # Public student submission
│   │   ├── auth.py             # Authentication & user management
│   │   ├── admin_students.py   # Admin student CRUD
│   │   └── admin_pdf.py        # PDF export endpoints
│   └── services/
│       ├── __init__.py
│       └── pdf_service.py      # PDF generation
├── static/
│   ├── css/
│   │   └── style.css           # All styles
│   └── js/
│       ├── auth.js             # Auth utilities
│       ├── index.js            # Student form
│       ├── login.js            # Login page
│       ├── dashboard.js        # Admin dashboard
│       └── student-details.js  # Student details page
├── templates/
│   ├── base.html               # Base template
│   ├── index.html              # Student submission form
│   ├── login.html              # Admin login
│   ├── dashboard.html          # Admin dashboard
│   └── student_details.html    # Student details
├── tests/
├── .env.example                # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- pip

## Installation

### 1. Clone and Navigate
```bash
cd college-student-system
```

### 2. Create Virtual Environment
```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Required: MONGODB_URI, JWT_SECRET_KEY
```

### 5. Setup MongoDB

#### Local MongoDB
```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod
```

#### MongoDB Atlas (Cloud)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster
3. Get connection string
4. Add to `.env` as `MONGODB_URI`

### 6. Create First Admin
```bash
python -m app.create_admin
```
Enter username and password when prompted.

### 7. Run the Application
```bash
uvicorn app.main:app --reload
```

The application will be available at:
- **Public Form**: http://localhost:8000/
- **Admin Login**: http://localhost:8000/login
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `college_student_system` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | **Required** |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | `60` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:8000` |

## API Endpoints

### Public
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/students` | Submit student details |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/users` | Create user (admin) |
| GET | `/api/auth/users` | List users (admin) |
| PUT | `/api/auth/users/{id}` | Update user (admin) |
| DELETE | `/api/auth/users/{id}` | Delete user (admin) |

### Admin - Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/students` | List students (paginated, search, filter) |
| GET | `/api/admin/students/stats` | Get statistics |
| GET | `/api/admin/students/{id}` | Get student by ID |
| PUT | `/api/admin/students/{id}` | Update student |
| DELETE | `/api/admin/students/{id}` | Delete student |
| GET | `/api/admin/students/pdf` | Export all students PDF |
| GET | `/api/admin/students/{id}/pdf` | Export student PDF |

### Admin - Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/users` | Create user |
| GET | `/api/auth/users` | List users |
| PUT | `/api/auth/users/{id}` | Update user |
| DELETE | `/api/auth/users/{id}` | Delete user |

## Authentication

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Token
```bash
curl -X GET http://localhost:8000/api/admin/students \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Student Data Model

```json
{
  "name": "John Doe",
  "course": "BCA",
  "college": "Example College",
  "admission_through": "KCET"
}
```

**Admission Methods**: KCET, NEET, NUCAT, MANAGEMENT

## User Roles

| Role | Permissions |
|------|-------------|
| **admin** | Full access: students CRUD, user management, PDF export |
| **staff** | View students, search/filter, PDF export, edit students |

## PDF Export

### All Students
```
GET /api/admin/students/pdf?search=query&admission_through=KCET
```

### Individual Student
```
GET /api/admin/students/{student_id}/pdf
```

## Production Deployment

### Security Checklist
- [ ] Use strong `JWT_SECRET_KEY` (32+ random characters)
- [ ] Set `CORS_ORIGINS` to specific domains
- [ ] Use HTTPS (reverse proxy with SSL)
- [ ] Secure MongoDB (authentication, network restrictions)
- [ ] Use MongoDB Atlas or VPC
- [ ] Set appropriate token expiration
- [ ] Configure firewall
- [ ] Enable MongoDB backups
- [ ] Monitor logs
- [ ] Never commit `.env` to version control

### Reverse Proxy (Nginx Example)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service
```ini
[Unit]
Description=College Student Management System
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/.venv/bin"
ExecStart=/path/to/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Testing

Run backend tests:
```bash
pytest tests/ -v
```

## Development

### Code Style
- Python: Black formatter
- JavaScript: ES6+ with consistent formatting
- CSS: BEM-like naming convention

### Adding Features
1. Create models in `app/models/`
2. Create schemas in `app/schemas/`
3. Add routes in `app/routers/`
4. Update frontend templates and JS
5. Test thoroughly

## License

MIT License - feel free to use for your college/institution.

## Support

For issues or questions, please create an issue in the repository.