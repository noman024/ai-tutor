# AI Tutor

An innovative educational platform that combines AI-powered teaching with interactive visualizations and lab simulations.

## 🚀 Project Status

### Current Phase: Development Setup
- [x] Project planning
- [x] Technical architecture design
- [x] Development environment setup
- [ ] Core feature implementation (in progress)

### Feature Implementation Status
1. **Foundation** (Complete)
   - [x] Project structure setup
   - [x] Development environment configuration
   - [x] Basic frontend setup (Next.js + TypeScript + Tailwind CSS)
   - [x] Basic backend setup (FastAPI)
   - [x] Database setup (PostgreSQL)
   - [x] Alembic migrations working
   - [x] User model and users table created
   - [x] Verified DB setup
   - [x] Authentication endpoints (register, login)

2. **Core Features** (In Progress)
   - [x] User registration and login (backend)
   - [x] User registration and login (frontend)
   - [x] File upload and processing
   - [ ] AI teacher integration (GPT-4/Gemini Q&A, subject-specific logic)
   - [ ] Whiteboard and slide conversion (from uploaded files)
   - [ ] Lab simulation triggers and visualization (basic MVP)
   - [ ] Voice interaction (Q&A via Whisper, TTS)
   - [ ] User session management and saving (video, notes)
   - [ ] Interruptible lessons (future phase)
   - [ ] Progressive whiteboarding (future phase)
   - [ ] Subject-specific teaching styles (future phase)

3. **AI Integration** (Pending)
   - [ ] GPT-4 Turbo integration
   - [ ] Gemini 2.0 Flash integration
   - [ ] Model fallback system
   - [ ] Basic lab simulation

4. **Polish & Testing** (Pending)
   - [ ] UI/UX improvements
   - [ ] Performance optimization
   - [ ] Testing
   - [ ] Documentation

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- Git

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/noman024/ai-tutor.git
   cd ai-tutor
   ```

2. **Configure environment variables**
   ```bash
   # Copy the example env file
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start development environment with Docker**
   ```bash
   # Build and start all services
   docker-compose up --build
   
   # Or start in detached mode
   docker-compose up -d --build
   ```

   This will start:
   - Backend API at http://localhost:8000
   - Frontend at http://localhost:3000
   - PostgreSQL at  http://localhost:5432
   - Redis at  http://localhost:6379

4. **Verify the setup**
   ```bash
   # Check backend health
   curl http://localhost:8000/health
   
   # Check frontend
   # Open http://localhost:3000 in your browser
   ```

### Frontend Development

The frontend is built with:
- Next.js 14
- TypeScript
- Tailwind CSS
- React Query for data fetching
- Zustand for state management

Key features:
- Modern, responsive design
- Type-safe development
- Component-based architecture
- Built-in API routes
- Server-side rendering

### Backend Development

The backend is built with:
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic for migrations

Key features:
- RESTful API
- WebSocket support
- JWT authentication
- Database migrations
- Redis caching (with best-practice utility and AI answer cache service)

### Development Workflow

1. **Feature Development Process**
   - Each feature is developed in its own branch
   - Feature branches are named: `feature/feature-name`
   - Each feature must include tests
   - Features are only merged after passing all tests
   - README is updated after each feature completion

2. **Testing Requirements**
   - Unit tests for all new code
   - Integration tests for API endpoints
   - End-to-end tests for critical user flows
   - Performance testing for AI interactions

3. **Code Quality**
   - Follow PEP 8 for Python code
   - Follow ESLint rules for JavaScript/TypeScript
   - All code must be documented
   - All PRs require code review

4. **Feature Implementation Checklist**
   - [ ] Create feature branch
   - [ ] Implement feature
   - [ ] Write tests
   - [ ] Run all tests
   - [ ] Update documentation
   - [ ] Create pull request
   - [ ] Code review
   - [ ] Merge to main

## 📁 Project Structure
```
ai-tutor/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utility functions
│   ├── tests/            # Backend tests
│   └── main.py           # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js app directory
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   └── utils/        # Utility functions
│   ├── public/           # Static files
│   └── tests/            # Frontend tests
├── docker/
│   ├── backend/          # Backend Dockerfile
│   └── frontend/         # Frontend Dockerfile
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore file
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## 🧪 Testing

### Running Tests
```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test

# End-to-end tests
docker-compose exec frontend npm run test:e2e
```

### Test Coverage
- Backend: Aim for >80% coverage
- Frontend: Aim for >70% coverage
- Critical paths: 100% coverage

## 📝 Documentation

- API documentation is available at http://localhost:8000/docs when running the backend
- Component documentation will be available in the frontend storybook
- Architecture decisions are documented in `docs/architecture/`
- API specifications are in `docs/api/`
- See [docs/getting_started.md](docs/getting_started.md) for setup and all development commands used so far.

## 🔄 CI/CD

- GitHub Actions for automated testing
- Automated deployment to staging
- Manual deployment to production
- Automated documentation updates

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔐 Security

- All API keys are stored in environment variables
- Regular security audits
- Dependencies are regularly updated
- Security issues should be reported privately

## 🛡️ API Endpoints (Authentication)

- `POST /api/v1/auth/register` — Register a new user
  - Request: `{ "email": "user@example.com", "password": "yourpassword" }`
  - Response: `{ "id": 1, "email": "user@example.com" }`

- `POST /api/v1/auth/login` — Login and get JWT token
  - Request: `{ "email": "user@example.com", "password": "yourpassword" }`
  - Response: `{ "access_token": "...", "token_type": "bearer" }`

## 🖥️ Frontend Authentication Flow

- `/register` — Register a new user
- `/login` — Login and get JWT token (stored in localStorage)
- `/dashboard` — Protected page, only accessible if logged in

**How it works:**
- Register a new user via the form
- Login with your credentials
- On success, you are redirected to `/dashboard`
- Logout removes the token and redirects to `/login`

### Roadmap & Tasklist (Prioritized)

#### **MVP (Phase 1)**
- [x] User registration/login (backend & frontend)
- [x] File upload (PPT/PPTX, PDF, DOC, TXT, images)
- [ ] File conversion pipeline (PDF/DOC/TXT/Image → PPTX)
- [ ] Store and manage slide decks (original and converted PPTX)
- [ ] Dashboard: List and select slide decks
- [ ] AI teacher Q&A (text, GPT-4/Gemini, with Redis caching)
- [ ] Persistent database and admin tools (pgAdmin, Redis Commander)

#### **Phase 2: Core Teaching Experience**
- [ ] Avatar/virtual teacher (realistic human-like AI teacher)
- [ ] Teaching session: AI steps through slides, explains line-by-line
- [ ] Real-time slide navigation (AI and user can go back/forth)
- [ ] User can ask questions (text) about current slide/content
- [ ] AI answers contextually, referencing current slide
- [ ] UI: Show current slide, avatar, and Q&A area

#### **Phase 3: Advanced Interaction**
- [ ] Voice Q&A (Whisper integration, TTS for AI responses)
- [ ] Whiteboard/board drawing (AI can annotate slides)
- [ ] Lab simulation triggers and basic visualization
- [ ] User session management (track/save sessions, notes)

#### **Phase 4: Full "Live Class" Experience**
- [ ] Advanced avatar animation (gestures, pointing, lip sync)
- [ ] Progressive whiteboarding (stepwise teaching, drawing)
- [ ] Interruptible lessons (user can pause/interject at any time)
- [ ] Advanced lab simulation (animation, scripting)
- [ ] Session saving (video, notes)
- [ ] Subject-specific teaching styles and behaviors
- [ ] Real-time Q&A (voice and text)
- [ ] Guardian/teacher alerts, progress tracking

---

This README will be updated as the project progresses. Each feature implementation will be documented here with its status and any relevant notes. 