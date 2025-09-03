# AI Ticket Orchestration Chat
This is a AI Chat that orchestrates ticket creation based on the user's needs. It is built upon the open-source LibreChat frontend.
Work in progress. Currently migrating backend from Node to FastAPI

### TODO:
- Issues: Some fields are still being prefilled when they should not be
- Still needs conversation title generation
- Does not automatically log out when auth token expires

## Temporary Notes:

## Local Dev:
- cp .env.example .env && cp librechat.example.yaml librechat.yaml
- npm install
- cd api2 && cd env.example .env &&python -m venv .venv && pip install -r requirements.txt

### Windows Commands:  
- .venv/Scripts/Activate  
- python -m uvicorn main:app --host 127.0.0.1 --port 3080  
- cd ../client ; npm run build ; cd ../api2 ; python -m   uvicorn main:app --host 127.0.0.1 --port 3080  

### Mac Commands:   
- source .venv/bin/activate  
- python -m uvicorn main:app --host 0.0.0.0 --port 3080  
- cd ../client && npm run build && cd ../api2 && python -m uvicorn main:app --host 0.0.0.0 --port 3080  

### Model and Provider Selection:
- api2/.env: Contains API Keys & Addresses
- api2/app/constants.py: Provider and Model Selection
- api2/app/config.py: Where all the (models, keys, providers, and addresses) pass through to be exported to the rest of the app



