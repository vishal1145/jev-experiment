# SmartDesk AI

An intelligent support ticket management application.

## Stack
- React + Vite
- Flask (MVC architecture)
- SQLite
- Jev TypeSafe AI

## Jev decisions
- Choice: Ticket department
- Score: Urgency from 0 to 5
- Noul: Human escalation probability

## Start backend
cd backend
source .venv/bin/activate
python run.py

## Start frontend (separate terminal)
cd frontend
npm run dev

Backend: http://127.0.0.1:5000
Frontend: http://localhost:5173

