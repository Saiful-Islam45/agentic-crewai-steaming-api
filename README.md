# Website Builder AI Platform

A Django-based web application that leverages CrewAI agents to perform real-time market research for website niches and locations. The platform streams AI-generated insights to users via a modern web UI.

---

## Features

- **CrewAI Integration:** Multi-agent AI system for market research, including demographic analysis, niche demand forecasting, and market viability scoring.
- **Streaming Output:** Real-time, Markdown-formatted results streamed to the frontend using Server-Sent Events (SSE).
- **Modern UI:** Responsive web interface for user input and live output display.
- **Configurable Agents & Tasks:** Easily extendable agent/task definitions in [`website_builder_api/services/crew_agents.py`](website_builder_api/services/crew_agents.py) and [`website_builder_api/services/crew_tasks.py`](website_builder_api/services/crew_tasks.py).
- **Environment-Based Configuration:** API keys and settings managed via `.env` and [`my_website_builder/config.py`](my_website_builder/config.py).

---

## Project Structure

```
my_website_builder/        # Django project settings and config
website_builder_api/       # Django app with API, agents, tasks, and streaming logic
UI/                        # Frontend HTML/CSS/JS client
manage.py                  # Django management script
requirements.txt           # Python dependencies
.env                       # Environment variables (API keys, etc.)
```

---

## Quickstart

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `my_website_builder/config.py.sample` to `my_website_builder/config.py` and set your API keys.
   - Set up `.env` with required keys (see sample).

3. **Run Django server:**
   ```sh
   python manage.py migrate
   python manage.py runserver
   ```

4. **Access the UI:**
   - Open [`UI/index.html`](UI/index.html) in your browser.
   - Enter a location and niche, then start market research.

---

## API Overview

- **Endpoint:** `POST /api/market-research/`
- **Payload:** `{ "location": "London", "niche": "coffee shops" }`
- **Response:** Streams Markdown-formatted output via SSE.

Backend streaming logic is implemented in [`website_builder_api/services/crew_runner.py`](website_builder_api/services/crew_runner.py) using [`run_market_research_crew`](website_builder_api/services/crew_runner.py).

---

## Customization

- **Agents:** Define or modify agents in [`website_builder_api/services/crew_agents.py`](website_builder_api/services/crew_agents.py).
- **Tasks:** Define or modify tasks in [`website_builder_api/services/crew_tasks.py`](website_builder_api/services/crew_tasks.py).
- **Frontend:** Customize UI in [`UI/index.html`](UI/index.html).

---

## Technologies Used

- Django & Django REST Framework
- CrewAI
- Python threading & queue for streaming
- Tailwind CSS (frontend)
- Server-Sent Events (SSE) for real-time output

---

## License

This project is for educational and demonstration purposes. Please review third-party library licenses before production use.

---

## Authors

- AI agent orchestration and backend: [`website_builder_api/services/crew_runner.py`](website_builder_api/services/crew_runner.py)
- Frontend UI: [`UI/index.html`](UI/index.html)