# FleetIQ Python Backend

FastAPI replacement for the original Spring Boot fleet analytics backend.

## Run locally

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

Open: http://localhost:8080/docs

## Environment

Create `.env`:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB=fleet-analytics-tracking-backend
```

If MongoDB is not configured, the backend runs with demo in-memory data.
