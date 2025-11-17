# Classroom Optimizer

An AI-powered seating optimization tool for teachers, part of the ULP (Ultimate Learning Platform).

## 🎯 Overview

Classroom Optimizer helps teachers create optimal seating arrangements based on student needs and constraints. It combines constraint satisfaction algorithms (OR-Tools) with AI-powered natural language interaction (Google ADK).

## ✨ Features

### Constraint Management
- **Social Constraints**: Students who cannot sit together
- **Accessibility Needs**: Front row, near door, near window requirements
- **Environmental Preferences**: Quiet areas, avoiding distractions
- **Behavioral Management**: Separating disruptive pairs

### Constraint Types

**Hard Constraints** (must be satisfied):
- ❌ Cannot sit next to [specific student]
- ✅ Must sit in front row
- 🚪 Must be close to door
- 🪟 Must be close to window
- ❌ Cannot sit by window
- ❌ Cannot sit by door
- ❌ Cannot sit in back row

**Soft Constraints** (preferences, weighted):
- 🤫 Needs quiet environment
- 👥 Works well with [specific students]
- 📚 Needs teacher proximity

### AI-Powered Interface
- Natural language input: "Alex cannot sit next to Jordan"
- Intelligent suggestions for optimal arrangements
- Explain why certain arrangements work better
- Learn from teacher feedback

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  Teacher (User)                         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  AI Agent (Google ADK)                  │
│  - Natural language understanding       │
│  - Constraint extraction                │
│  - Result explanation                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Optimization Engine (OR-Tools)         │
│  - Constraint satisfaction              │
│  - Seating layout generation            │
│  - Multiple solution generation         │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- UV package manager
- Google ADK API key

### Installation

```bash
# Clone and install
cd classroom-optimizer
uv venv
uv sync
```

### Set up environment

```bash
# Create .env file
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

### Run the optimizer

```bash
# Start the web interface
uv run adk web . --host 0.0.0.0 --port 7070
```

## 📊 Example Usage

### Via AI Chat Interface

```
Teacher: "I have a classroom with 30 students. Alex cannot sit next to Jordan. 
         Emma needs to sit in the front row. Sam needs to be near the door."

Optimizer: "I'll create an optimal seating arrangement with those constraints. 
           Let me analyze the classroom layout..."

[Generates seating chart with explanations]
```

### Via API

```bash
POST /api/optimize
{
  "classroom": {
    "rows": 5,
    "columns": 6,
    "total_students": 30
  },
  "students": [
    {"name": "Alex", "id": 1},
    {"name": "Jordan", "id": 2},
    {"name": "Emma", "id": 3}
  ],
  "constraints": [
    {"type": "cannot_sit_together", "students": [1, 2]},
    {"type": "must_front_row", "student": 3}
  ]
}
```

## 🔧 Tech Stack

- **Backend**: Python + FastAPI
- **Optimization**: Google OR-Tools (constraint satisfaction)
- **AI Agent**: Google ADK + Gemini 2.5 Flash
- **Containerization**: Docker
- **Deployment**: Kubernetes + ArgoCD
- **CI/CD**: GitHub Actions

## 📝 API Endpoints

- `POST /api/optimize` - Generate optimal seating arrangement
- `GET /api/constraints` - List available constraint types
- `POST /api/validate` - Validate constraint configuration
- `GET /api/solutions/{id}` - Retrieve generated solution
- `POST /api/feedback` - Submit teacher feedback on solution

## 🎓 Educational Principles

The optimizer considers:
- **Pedagogical best practices** - Student engagement and learning
- **Behavioral management** - Reducing disruptions
- **Accessibility** - Ensuring all students can participate
- **Social-emotional learning** - Promoting positive interactions

## 🔒 Security

- API keys stored in Kubernetes Sealed Secrets
- No sensitive student data stored permanently
- GDPR-compliant data handling

## 📦 Deployment

### Kubernetes

```bash
# Deploy via ArgoCD
kubectl apply -f argocd-ULP/template/classroom-optimizer.yaml

# Or manually
kubectl apply -f k8s/
```

### Configuration

- **Port**: 7070
- **Language**: Configurable (en/sv)
- **Max Students**: Configurable per classroom

## 🤝 Integration with ULP

- **Backstage**: Registered as service in catalog
- **Clara**: Future integration for study group formation
- **Shared Authentication**: Uses ULP platform credentials

## 📚 Documentation

See `/docs` folder for:
- Architecture diagrams
- Constraint definitions
- API documentation
- Teacher guides

## 🛠️ Development

```bash
# Run tests
uv run pytest

# Lint code
uv run black .
uv run isort .

# Type checking
uv run mypy .
```

## 📄 License

Part of the ULP Platform

