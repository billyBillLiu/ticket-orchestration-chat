# AI Ticket Orchestration Chat
This is a AI Chat that orchestrates ticket creation based on the user's needs. It is built upon the open-source LibreChat frontend.
Work in progress. Currently migrating backend from Node to FastAPI

### TODO:
- Connect LLM
- Agents
- Use agents to create tickets
- Implement Archive Comvos
- Remove Other Useless Features (forking, right-side bar etc.)
- E2E Testing

### Cursor Rule Ideas:  
- Reminder to use venv  
- Reminder of which folder is frontend and which is backend  

## Local Dev:
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

## Temporary Notes:
### LLM Integration:
Add to api2/requirements.txt:
- ollama - For running local models via Ollama
- openai - For OpenAI API compatibility layer
- transformers - For Hugging Face models
- torch - For PyTorch backend
- accelerate - For optimized inference

Create api2/app/services/llm_service.py:
- This is an abstract LLM interface
- Use Ollama integration for local models
- Model management
- Response streaming

Replace api2/app/routes/endopoints.py placeholders:
- the ask endpoint. replace the hardcoded messages.
- implement proper streaming responses

Add to api2/app/config.py:
- LLM provider settings
- Model configs
- Local model path

### Agent Integration:
Create api2/app/models/agent.py:
- Agent definition model
- Tool Definitions
- Agent state management

Create api2/app/services/agent_services.py
- Agent orchestration logic
- Tool execution framework
- Agent state management

Create api2/app/routes/agents.py
- Agent CRUD operations
- Agent execution endpoints
- Tool management

### Ticket Creation:
Create api2/app/models/ticket.py:
- Ticket data model
- Ticket status tracking
- Priority and categorization

Create api2/app/services/ticket_tools.py:
- create_ticket() - Creates support tickets
- categorize_issue() - Determines ticket category
- assign_priority() - Sets ticket priority
- extract_user_info() - Parses user details

Specialized Agents:
- Intake Agent: Initial user interaction and issue classification
- Information Gathering Agent: Collects missing details
- Ticket Creation Agent: Creates and submits tickets
- Follow-up Agent: Handles post-creation communication