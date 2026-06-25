# 🚀 GitHub Time Machine

An AI-powered GitHub Repository Analytics Platform that helps developers understand repository health, contributor ownership, code hotspots, historical trends, and project risks through interactive dashboards and natural language insights.

---

## 📌 Features

### 📊 Repository Analytics
- Analyze any public GitHub repository
- Commit activity over time
- Repository health score
- Bus Factor calculation
- Contributor statistics
- Ownership analysis
- Timeline visualization
- High-risk hotspot detection

### 🤖 AI-Powered Insights
- AI-generated repository summaries
- Repository risk analysis
- Strengths & recommendations
- Natural language Q&A about the repository
- Supports multiple AI providers:
  - Groq
  - Gemini
  - OpenAI

### 📈 Interactive Dashboard
- Overview Dashboard
- Contributors Dashboard
- Hotspots Dashboard
- Ownership Dashboard
- Timeline Dashboard

### 🐳 Dockerized
- One-command setup using Docker Compose
- PostgreSQL database
- FastAPI backend
- React frontend

---

# 🛠 Tech Stack

## Backend
- FastAPI
- Python
- SQLAlchemy
- PostgreSQL
- GitPython
- Pydantic

## Frontend
- React
- TypeScript
- Tailwind CSS
- Recharts
- Shadcn UI

## AI
- Groq API
- OpenAI API
- Google Gemini API

## DevOps
- Docker
- Docker Compose

---

# 📂 Project Structure

```
github-time-machine
│
├── backend
│   ├── api
│   ├── core
│   ├── models
│   ├── services
│   ├── repositories
│   └── utils
│
├── frontend
│   ├── components
│   ├── pages
│   ├── hooks
│   ├── api
│   └── types
│
├── docker-compose.yml
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/aditysinhania/github-time-machine.git

cd github-time-machine
```

---

## Configure Environment

Create a `.env` file.

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/github_time_machine

GITHUB_TOKEN=

AI_PROVIDER=groq

GROQ_API_KEY=YOUR_GROQ_KEY

OPENAI_API_KEY=

GEMINI_API_KEY=

SECRET_KEY=changeme

ENVIRONMENT=development
```

---

## Run with Docker

```bash
docker compose up --build
```

---

## Access Application

Frontend

```
http://localhost:5173
```

Backend API

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

---

# 📊 Dashboard Features

### Overview
- Repository Health Score
- Commit Activity
- High Risk Files
- Top Contributors

### Contributors
- Contribution Distribution
- Bus Factor
- Individual Contributor Analytics

### Hotspots
- Frequently Modified Files
- Security Sensitive Files
- Risk Classification

### Ownership
- Module Ownership
- Ownership Percentage
- Orphan Modules

### Timeline
- Repository Evolution
- Commit History
- Milestones

### AI Insights
- Repository Summary
- Risk Detection
- Recommendations
- Repository Chat Assistant

---

# 🤖 AI Example Questions

Ask questions like:

- Summarize this repository.
- What are the biggest risks?
- Who owns the auth module?
- Which files should be reviewed first?
- Explain the contributor distribution.
- Which files are the most volatile?
- What is the bus factor?
- Recommend improvements.

---

---

# 🚀 Future Improvements

- GitHub OAuth Login
- Repository Comparison
- Private Repository Support
- Code Churn Analysis
- Pull Request Analytics
- Issue Analytics
- Email Reports
- CI/CD Integration
- Deployment Support

---

# 👨‍💻 Author

**Adity Sinha**

LinkedIn:
https://www.linkedin.com/in/adity-sinha-/

GitHub:
https://github.com/aditysinhania

---

# ⭐ If you found this project useful, consider giving it a star!
