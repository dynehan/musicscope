# MusicScope

MusicScope is a full-stack web service that collects, analyzes, and visualizes music trend data by country.  
The system integrates multiple public music APIs and provides analytics results through REST APIs and an interactive web dashboard.

## Overview

MusicScope demonstrates how external web services can be integrated into a modern web application using an ETL pipeline and analytics APIs.  
Users can trigger data ingestion jobs, explore music trends by country, and compare genre distributions across different regions.

The project was developed as part of a Web Services course and focuses on API integration, backend–frontend separation, and cloud deployment.

## System Architecture

The system follows a client–server architecture consisting of:  
	•	Frontend: React-based dashboard for visualization and ETL control  
	•	Backend: FastAPI REST server handling ETL and analytics  
	•	Database: PostgreSQL for persistent storage  
	•	External APIs: Last.fm and MusicBrainz  
	•	Deployment: Railway (frontend, backend, database)

The frontend communicates exclusively with the backend through REST APIs.  
The backend manages data ingestion, processing, and aggregation.

## Tech Stack
	•	Frontend: React, Vite, Recharts  
	•	Backend: FastAPI, Python  
	•	Database: PostgreSQL  
	•	External APIs: Last.fm API, MusicBrainz API  
	•	Deployment: Railway

## Setup Instructions

### Backend (Local)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:  
```
http://127.0.0.1:8000
```

Swagger UI:  
```
http://127.0.0.1:8000/docs
```

### Frontend (Local)
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:  
```
http://localhost:5173
```

## Environment Variables

Create environment variable files based on the templates below.

Backend (.env.example)  
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
LASTFM_API_KEY=your_lastfm_api_key
ALLOWED_ORIGINS=*
```

Frontend (.env.example)  
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Endpoints (Examples)

ETL Endpoints  
```http
POST /etl/lastfm/run?country=spain&limit=20
POST /etl/musicbrainz/run
```

Analytics Endpoints  
```http
GET /analytics/genre-distribution?country=spain&top_n=10
GET /analytics/top-artists-by-country?country=spain&top_n=10
GET /analytics/country-genre-comparison?c1=spain&c2=united states&top_n=10
```

System  
```http
GET /health
```

## ETL Usage
	1.	Select a country from the frontend dashboard  
	2.	Click “Run Last.fm ETL” to collect popularity-based data  
	3.	Optionally click “Run MusicBrainz ETL” to enrich metadata  
	4.	Analytics charts update automatically after ETL completion

If the Last.fm API key is not set, the system reports the configuration issue gracefully.

## Deployment

The system is deployed on Railway with separate services for the frontend, backend, and database.  
	•	Backend URL:  
```
https://musicscope-production.up.railway.app
```
	•	Frontend URL:  
```
https://musicscope-frontend-production.up.railway.app
```

The backend includes CORS configuration to allow secure communication with the deployed frontend.

## Screenshots

Screenshots of the dashboard, charts, and ETL execution can be found in the final project report.

## AI Usage

AI tools such as ChatGPT were used to assist with system design, API planning, debugging, and deployment troubleshooting.  
All final implementation decisions, code integration, and testing were performed by the developer.

## Author

Dyne Han  
Web Services Project 2