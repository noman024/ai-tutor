# AI Tutor

An innovative educational platform that combines AI-powered teaching with interactive visualizations and lab simulations.

---

## 🚀 Project Overview & Architecture

**AI Tutor** is a full-stack educational platform built with:
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Backend:** FastAPI, PostgreSQL, Redis
- **Containerization:** Docker Compose

### Key Features
- AI-powered teaching (OpenAI/Gemini)
- File upload and automatic conversion to slides (PDF, DOCX, TXT, images → PPTX)
- Modern dashboard and navigation
- File list with conversion status and download/preview links
- Slide deck selection from converted files
- AI Q&A with slide deck context awareness
- **Virtual teacher avatar in Q&A area**
- Persistent database and admin tools (pgAdmin, Redis Commander)
- Automated database migrations
- RESTful API with JWT authentication
- Redis caching for AI answers

### Dashboard Features
- Upload files (PDF, DOCX, TXT, images)
- View a list of uploaded files with conversion status
- Download original and converted PPTX files
- Select a slide deck from converted files for AI Q&A
- Ask questions to the AI tutor with slide deck context
- View AI responses with source attribution (slides vs. general knowledge)
- **See a friendly virtual teacher avatar that reacts to your questions**
- **Start an interactive teaching session: step through slides, and get AI explanations for each slide**
- **See slide content highlighted when the AI teacher is explaining (pointing effect)**

---

## 🛠️ Getting Started

### 1. Clone the Repository
   ```bash
   git clone https://github.com/noman024/ai-tutor.git
   cd ai-tutor
   ```

### 2. Environment Setup
- Copy and edit environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Build and Start All Services
```bash
docker-compose up --build
# Or in detached mode
docker-compose up -d --build
```

This will start:
- Backend API at http://localhost:8000
- Frontend at http://localhost:3000
- PostgreSQL at http://localhost:5432
- Redis at http://localhost:6379
- pgAdmin at http://localhost:5050
- Redis Commander at http://localhost:8081

### 4. Useful Development Commands

#### Docker & Containers
- Start all services:
  ```bash
  docker-compose up -d
  ```
- Stop all services:
  ```bash
  docker-compose stop
  ```
- View running containers:
  ```bash
  docker ps
  ```
- View logs for a service:
  ```bash
  docker-compose logs backend
  docker-compose logs frontend
  docker-compose logs db
  docker-compose logs redis
  docker-compose logs pgadmin
  docker-compose logs redis-commander
  ```
- Restart a service:
  ```bash
  docker-compose restart backend
  ```
- Remove all containers (keep data):
  ```bash
  docker-compose down
  ```
- Remove all containers and volumes (delete all data!):
  ```bash
  docker-compose down -v
  ```

#### Database & Migrations
- Create a new migration:
  ```bash
  cd backend
  PYTHONPATH=.. alembic revision --autogenerate -m "migration message"
  ```
- Apply migrations:
  ```bash
  cd backend
  PYTHONPATH=.. alembic upgrade head
  ```

#### Backend
- Run backend locally (if not using Docker):
  ```bash
  cd backend
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
- Run backend tests:
   ```bash
  docker-compose exec backend pytest
   ```

#### Frontend
- Run frontend locally (if not using Docker):
   ```bash
   cd frontend
   npm install
  npm run dev
  ```
- Run frontend tests:
  ```bash
  docker-compose exec frontend npm test
  ```

#### Redis & pgAdmin
- Access Redis Commander: http://localhost:8081
- Access pgAdmin: http://localhost:5050

---

## 🧩 Architecture Overview
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Backend:** FastAPI, PostgreSQL, Redis
- **Containerization:** Docker Compose

---

## 🛡️ API Reference & Example Requests

### Authentication
- **Register:**
  - `POST /api/v1/auth/register`
  - Request: `{ "email": "user@example.com", "password": "yourpassword" }`
  - Response: `{ "id": 1, "email": "user@example.com" }`
- **Login:**
  - `POST /api/v1/auth/login`
  - Request: `{ "email": "user@example.com", "password": "yourpassword" }`
  - Response: `{ "access_token": "...", "token_type": "bearer" }`

### File Upload & Conversion
- **Upload File(s):**
  - `POST /api/v1/files/upload`
  - Headers: `Authorization: Bearer <token>`
  - Body: `form-data` with one or more files (`uploads`)
  - Supported: PPTX, PDF, DOCX, TXT, images (jpg, png, gif, bmp)
  - Non-PPTX files are auto-converted to PPTX. Multiple images are combined into one PPTX.
- **List Uploaded Files:**
  - `GET /api/v1/files/list`
  - Headers: `Authorization: Bearer <token>`
  - Response: List of files with conversion status and PPTX path

### AI Q&A
- **Ask the AI Teacher:**
  - `POST /api/v1/ai/ask`
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ "question": "What is the Pythagorean theorem?", "slide_deck_id": 1 }`
  - Response: `{ "answer": "...", "cached": false, "provider": "openai" }`
  - When `slide_deck_id` is provided, the AI uses the slide deck content as primary reference
  - The AI clearly indicates which parts of the answer come from the slides vs. general knowledge
- **List Slides in a Deck:**
  - `GET /api/v1/ai/slides/{slide_deck_id}`
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ "slides": [ { "slide_number": 1, "content": "...", "image_available": true }, ... ] }`
  - Only returns slides if the user owns the deck and it is converted
  - **If `image_available` is true, the slide image can be viewed using the endpoint below**
- **Get Slide Image:**
  - `GET /api/v1/ai/slide-image/{slide_deck_id}/{slide_number}`
  - Headers: `Authorization: Bearer <token>`
  - Response: Raw image file (PNG)
- **Explain a Slide:**
  - `POST /api/v1/ai/explain-slide`
  - Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
  - Body: `{ "slide_deck_id": 1, "slide_number": 2 }`
  - Response: `{ "explanation": "...", "provider": "openai" }`
  - Only uses the content of the specified slide for the explanation
  - **Now supports both text and image-based slides using OpenAI Vision (primary) and Gemini Vision (fallback)**

### Health Check
- `GET /health`

---

## 📝 Example API Requests (Postman)

**Register:**
```json
POST http://localhost:8000/api/v1/auth/register
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Login:**
```json
POST http://localhost:8000/api/v1/auth/login
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Upload File(s):**
- POST http://localhost:8000/api/v1/files/upload
- Headers: `Authorization: Bearer <token>`
- Body: form-data, key: `uploads`, type: file

**List Files:**
- GET http://localhost:8000/api/v1/files/list
- Headers: `Authorization: Bearer <token>`

**Ask AI Teacher:**
```json
POST http://localhost:8000/api/v1/ai/ask
Headers: Authorization: Bearer <token>
{
  "question": "What is the Pythagorean theorem?",
  "slide_deck_id": 1  // Optional: Use slide deck content as reference
}
```

**List Slides in a Deck:**
```json
GET http://localhost:8000/api/v1/ai/slides/1
Headers: Authorization: Bearer <token>
Response:
{
  "slides": [
    { "slide_number": 1, "content": "Introduction to AI", "image_available": true },
    { "slide_number": 2, "content": "What is Machine Learning?", "image_available": true }
  ]
}
```

**Get Slide Image:**
```json
GET http://localhost:8000/api/v1/ai/slide-image/1/1
Headers: Authorization: Bearer <token>
Response: Raw image file (PNG)
```

**Explain a Slide:**
```json
POST http://localhost:8000/api/v1/ai/explain-slide
Headers: Authorization: Bearer <token>
{
  "slide_deck_id": 1,
  "slide_number": 2
}
Response:
{
  "explanation": "This slide introduces the concept of ...",
  "provider": "openai"
}
```

---

## 🛠️ Troubleshooting
- If you lose your database or pgAdmin setup, make sure you are not using `docker-compose down -v` unless you want to delete all data.
- For persistent pgAdmin setup, a volume is now configured in `docker-compose.yml`.
- If migrations do not run, check the backend logs and ensure the entrypoint script is present and executable.

---

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
├── docs/                 # Documentation (legacy, now merged here)
├── scripts/              # Utility scripts
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore file
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

---

## 🚦 Roadmap & Tasklist (Prioritized)

#### **MVP (Phase 1)**
- [x] User registration/login (backend & frontend)
- [x] File upload (PPT/PPTX, PDF, DOC, TXT, images)
- [x] File conversion pipeline (PDF/DOC/TXT/Image → PPTX)
- [x] Store and manage slide decks (original and converted PPTX)
- [x] Dashboard: List and select slide decks
- [x] AI teacher Q&A (text, GPT-4/Gemini, with Redis caching)
- [x] Slide deck-aware AI Q&A (context from selected slides)
- [x] Persistent database and admin tools (pgAdmin, Redis Commander)

#### **Phase 2: Core Teaching Experience**
- [x] Avatar/virtual teacher (realistic human-like AI teacher)
- [x] Interactive teaching session (AI steps through slides, explains, points, draws)
    - [x] Backend: Endpoint to list slides for a given deck (with slide numbers and content)
    - [x] Backend: Endpoint for "explain this slide" (AI uses only the current slide's content)
    - [x] Frontend: Teaching session UI (slide viewer, avatar, navigation controls)
    - [x] Frontend: "Teach me this slide" button (calls backend, shows AI explanation)
    - [x] Frontend: Highlight/pointing effect for slide content (MVP: text highlight)
    - [ ] Frontend: User can ask questions about the current slide (optional for MVP)
    - [ ] Frontend: Simple annotation/drawing overlay (optional for MVP)
- [ ] Real-time slide navigation (AI and user can go back/forth)
- [ ] Contextual Q&A (AI references current slide and previous context)
- [ ] UI: Show current slide, avatar, and Q&A area
- [ ] Slide content extraction and formatting improvements

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

#### **Phase 5: Vision Model Integration**
- [x] Vision model integration for image-based slides (OpenAI primary, Gemini fallback)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔐 Security

- All API keys are stored in environment variables
- Regular security audits
- Dependencies are regularly updated
- Security issues should be reported privately

## 🖥️ Frontend Authentication Flow

- `/register` — Register a new user
- `/login` — Login and get JWT token (stored in localStorage)
- `/dashboard` — Protected page, only accessible if logged in

**How it works:**
- Register a new user via the form
- Login with your credentials
- On success, you are redirected to `/dashboard`
- Logout removes the token and redirects to `/login` 