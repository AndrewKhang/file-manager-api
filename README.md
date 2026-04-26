# File Manager API

A RESTful file management API built with FastAPI and PostgreSQL, featuring JWT authentication, role-based access control, email verification, and file upload/download/preview.

## Live Demo

[https://file-manager-api-production.up.railway.app](https://file-manager-api-production.up.railway.app)

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy ORM
- **Database:** PostgreSQL
- **Auth:** JWT (python-jose), bcrypt
- **Email:** Resend API
- **Frontend:** HTML / CSS / Vanilla JS
- **Deploy:** Railway

## Features

- User registration with email verification
- JWT-based authentication
- Role-based access control (admin / user)
- File upload, download, and preview
- Search and pagination for file list
- Admin dashboard: manage all users and files
- Drag & drop file upload
- Custom confirm modal (no browser dialog)

## Project Structure

```
file_manager_api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── email.py
│   └── routers/
│       ├── users.py
│       └── files.py
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── auth.css
│   └── dashboard.css
├── tests/
│   └── test_files.py
├── uploads/
├── .env
└── requirements.txt
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/file-manager-api.git
cd file-manager-api
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=file_manager
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
RESEND_API_KEY=your_resend_api_key
```

> Get a free Resend API key at [resend.com](https://resend.com)

### 5. Create uploads folder

```bash
mkdir uploads
```

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/docs`

## Running Tests

```bash
pytest tests/
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/users/register` | Register new user | — |
| POST | `/users/login` | Login | — |
| GET | `/users/me` | Get current user | ✅ |
| GET | `/users/verify-email` | Verify email via token | — |
| GET | `/users/admin/users` | Get all users | Admin |
| DELETE | `/users/admin/users/{id}` | Delete user | Admin |
| GET | `/files/` | List files | ✅ |
| POST | `/files/upload` | Upload file | ✅ |
| GET | `/files/{id}/download` | Download file | ✅ |
| GET | `/files/{id}/preview` | Preview file | ✅ |
| DELETE | `/files/{id}` | Delete file | ✅ |
