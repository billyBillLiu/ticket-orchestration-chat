# AI Ticket Orchestration Chat
This is a AI Chat that orchestrates ticket creation based on the user's needs. It is built upon the open-source LibreChat frontend.
Work in progress. Currently migrating backend from Node to FastAPI

### TODO:
- Dropdown selection fields are never prefilled
- Fix Date Issue: when the LLM fills date ranges, it fills wrong dates

@ticket_agent.py @ticket_plan.py @endpoints.py @agent_io.py @llm_service.py @planner_service.py @validator_service.py @catalog_service.py @catalog.py . These are the files currently involved in the agentic flow of my chatbot. It is not quite working how I want it to work. Firstly, the LLM takes in any input as a valid value for the ticket fields, even if the type does not match what is set in the catalog. Currently it takes the user's raw input and sets it as the field's value. I want to make it so the llm and chatbot takes the user's input, processes it, and creates a value that fits the type specified in th catalog. For example, if the the field needs to be an int, and the user says "the code is 42", the chatbot will extract the number 42 and set it as the field (this can be done either programatically or through an llm prompt, programatically will probably be more efficient). Another example is many of the fields have pre set options that the user can choose from. The chatbot currently does not display those options when questioning the user for the field. Make it so the options are shown first and then whatever the user inputs, the LLM takes it, uses it to find the best match within the available options list, and uses that option as the field value. Do the same with date fields and time fields. Another issue is that the final message does not show the entire json of the ticket created. I want it to show the entire json for now for clarity sake.


### Cursor Rule Ideas:  
- Reminder to use venv  
- Reminder of which folder is frontend and which is backend  
- Reminder of what shell you are using
- Reminder to put tests in test folder

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

## Temporary Notes:

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