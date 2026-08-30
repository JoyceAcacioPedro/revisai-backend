# RevisAI — Backend

**AI-powered study platform backend**  
Built with Django · Django REST Framework · LangChain · PostgreSQL


## What It Does

RevisAI is a productivity platform that uses AI to help 
students organise and optimise their study schedules.

This repository contains the full backend — REST API, 
authentication system, AI integration, and database layer.


## Architecture

Client (React) → Django REST API → PostgreSQL
↓
LangChain + LLM
↓
Brevo (Email via HTTP API)



## Tech Stack

Framework: Django · Django REST Framework
Authentication: JWT (SimpleJWT) — email-based login
Database: PostgreSQL (Render)
AI Layer: LangChain · AI Integration
Email: Brevo HTTP API (not SMTP)
Deployment: Render


## Key Features

- JWT authentication with email (not username)
- Custom token serializer for email-based login
- AI-integrated study scheduling
- Brevo HTTP API for transactional emails
- CORS configured for Vercel frontend
- REST API consumed by React frontend


## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Login — returns JWT tokens |
| POST | `/api/register/` | Register new user |
| GET | `/api/activity/` | Get user activity |
| GET/POST | `/api/subjects/` | Manage subjects |
| GET/POST | `/api/topics/` | Manage topics |
| GET/POST | `/api/revisions/` | Manage revisions |


## Environment Variables

```env
SECRET_KEY=
DEBUG=
DATABASE_URL=
BREVO_API_KEY=
ALLOWED_HOSTS=
CORS_ALLOWED_ORIGINS=
```


## Local Setup

```bash
# Clone the repository
git clone https://github.com/JoycePedro/revisai-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```


## Deployment

Backend deployed on **Render** (free tier).

> Note: Render's free tier blocks outbound SMTP ports.
> Email sending uses Brevo's HTTP API over HTTPS (port 443)
> instead of traditional SMTP — this was a key architectural
> decision made during deployment.

Frontend repository: [revisai-frontend](#)  
Live demo: [revisai.vercel.app](#)


## Engineering Notes

This project was built solo — from requirements to production.

Key challenges solved:

- JWT field mismatch: frontend sent `email`, 
  SimpleJWT expected `username` — 
  solved with CustomTokenObtainPairSerializer
- SMTP blocked by Render free tier — 
  solved by switching to Brevo HTTP API
- Non-breaking space characters (`\xa0`) 
  breaking Python indentation after copy-paste
- Frontend calling `localhost` in production — 
  solved with `VITE_API_URL` environment variable


*Software Engineer — Applied AI & Full Stack*  
[LinkedIn](https://www.linkedin.com/in/joyceacaciopedro) · 
[Twitter/X](https://x.com/Joyceap2005)