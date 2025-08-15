# AI Ticket Orchestration Chat
This is a AI Chat that orchestrates ticket creation based on the user's needs. It is built upon the open-source LibreChat frontend.
Work in progress. Currently migrating backend from Node to FastAPI

### TODO:
- Implement Archive Comvos
- Implement Delete Convos
- Agents
- E2E Testing

### Cursor Rule Ideas:  
- Reminder to use venv  
- Reminder of which folder is frontend and which is backend  

### When Starting:
- cp .env.example .env && cp librechat.example.yaml librechat.yaml
- npm install
- cd api2 && python -m venv .venv && pip install -r requirements.txt

### Windows Commands:  
- .venv/Scripts/Activate  
- python -m uvicorn main:app --host 127.0.0.1 --port 3080  
- cd ../client ; npm run build ; cd ../api2 ; python -m   uvicorn main:app --host 127.0.0.1 --port 3080  

### Mac Commands:   
- source .venv/bin/activate  
- python -m uvicorn main:app --host 0.0.0.0 --port 3080  
- cd ../client && npm run build && cd ../api2 && python -m uvicorn main:app --host 0.0.0.0 --port 3080  



