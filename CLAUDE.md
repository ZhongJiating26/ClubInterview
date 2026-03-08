# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ClubInterview is a full-stack club interview management system with three user roles:
- **Admin** (desktop web): Club management, recruitment, interviews, statistics
- **Interviewer** (desktop web): Interview scoring, reviews
- **Student** (mobile H5): Browse clubs, apply, view interview status

## Project Structure

```
ClubInterview/
├── frontend/          # Vue 3 + TypeScript + Vite (web app)
└── backend/           # FastAPI + SQLModel + MySQL (API server)
```

---

## Frontend (Vue 3)

### Tech Stack
- Vue 3 (Composition API + Script Setup)
- TypeScript
- Vite 7
- Vue Router 4 (nested routes with role-based guards)
- Pinia 3 (state management)
- shadcn-vue + reka-ui (component library)
- Tailwind CSS 4
- Axios (HTTP client)

### Common Commands

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (http://localhost:5173, supports LAN access)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Directory Structure

```
frontend/src/
├── api/
│   ├── modules/           # API modules (auth, clubs, interview, score, etc.)
│   ├── request.ts        # Axios instance with interceptors
│   └── index.ts
├── components/
│   ├── ui/               # shadcn-vue base components
│   └── AppSidebar.vue
├── layouts/
│   ├── AdminLayout.vue   # Desktop layout with sidebar
│   ├── InterviewerLayout.vue
│   └── StudentLayout.vue # Mobile-friendly layout
├── router/index.ts       # Routes with auth guards
├── stores/user.ts        # Pinia store for auth state
└── views/               # Page components by role
```

### Authentication Flow
1. User logs in via `/login` → gets JWT token stored in localStorage
2. Token is attached to requests via Axios interceptor
3. Router guards check roles (`meta.roles`) before allowing access
4. 401 responses trigger automatic logout and redirect to login

### API Response Handling
The project uses two response formats:
- **Wrapped**: `{ code: 200, data: ..., message: "" }` → extracted to return `data`
- **Direct**: Returns raw data (some endpoints like dashboard, clubs)

See `frontend/src/api/request.ts` for the response interceptor logic.

### Role-Based Routing
Routes are grouped by role under `/admin`, `/interviewer`, `/student` paths. Each route has `meta.roles` for permission checking. The router guard handles redirects based on user roles.

### Key Patterns

**Adding New API Module** - Create file in `frontend/src/api/modules/`:
```typescript
import request from '../request'
export function getExample() {
  return request.get('/example')
}
```

**Adding New Page**:
1. Create Vue component in `frontend/src/views/{role}/`
2. Add route in `frontend/src/router/index.ts` with `meta.roles`
3. Add navigation item in `frontend/src/components/AppSidebar.vue`

**Using shadcn-vue Components**:
```vue
<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
</script>
```

Add new components via: `npx shadcn-vue add [component-name]`

---

## Backend (FastAPI)

### Tech Stack
- FastAPI 0.104+ (async web framework)
- SQLModel 0.0.14+ (ORM + Pydantic)
- MySQL 8.0+ (database)
- Passlib/bcrypt (password hashing)
- python-jose (JWT tokens)
- boto3 (S3-compatible storage)

### Common Commands

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Directory Structure

```
backend/
├── app/
│   ├── api/v1/           # API endpoints (auth, club, interview, signup, etc.)
│   ├── core/             # Config, security, storage
│   ├── db/               # Database session
│   ├── models/           # SQLModel entities
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # FastAPI app entry
├── scripts/             # Utility scripts
└── tests/               # Test files
```

### Database Models
Key models in `backend/app/models/`:
- `user_account.py` - User accounts (phone, password)
- `role.py` - User roles (CLUB_ADMIN, INTERVIEWER, STUDENT)
- `school.py` - Schools
- `club.py` - Clubs
- `department.py` / `club_position.py` - Departments and positions
- `signup_session.py` / `recruitment_session.py` - Signup/recruitment sessions
- `interview_session.py` / `interview_candidate.py` / `interview_record.py` - Interview entities
- `score_template.py` / `score_item.py` - Scoring system
- `ticket.py` / `notification.py` - Support tickets and notifications

### API Endpoints
Main API routes in `backend/app/api/v1/`:
- `auth.py` - Authentication (login, register, password reset)
- `club.py` - Club management
- `signup.py` - Signup/applications
- `interview.py` - Interview management
- `recruitment_session.py` - Recruitment sessions
- `school.py` - School data
- `department.py` / `position.py` - Organization management
- `system.py` - System settings

### Environment Variables
Configure in `backend/.env`:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - MySQL config
- `JWT_SECRET_KEY`, `JWT_ALGORITHM` - JWT config
- `STORAGE_*` - S3-compatible storage config

---

## Running the Full Stack

1. **Start MySQL** (ensure MySQL 8.0+ is running)
2. **Start Backend**:
   ```bash
   cd backend
   alembic upgrade head
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

Frontend proxies `/api/*` to backend at `http://localhost:8000`.
