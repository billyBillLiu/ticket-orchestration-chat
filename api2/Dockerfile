FROM python:3.11-slim

WORKDIR /app

COPY api2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI app code
COPY api2/ .

# Copy built frontend from root client/dist to /app/client/dist
COPY client/dist ./client/dist

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]