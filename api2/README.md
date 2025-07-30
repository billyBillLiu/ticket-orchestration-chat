# Need to replicate:  
| Component              | Directory Path                         |
|------------------------|----------------------------------------|
| Routes/Endpoints       | `api/server/routes/`                   |
| Controllers            | `api/server/controllers/`              |
| Services               | `api/server/services/`                 |
| Models                 | `api/models/`                          |
| Middleware             | `api/server/middleware/`               |
| Config/Env             | `api/config/`                          |

##  Endpoints

Look at the endpoint routes in `api/server/routes/` and note the:
- HTTP method (GET, POST, etc.)
- Path
- Request/Response shape  

Then create the equivalent route in `api2/routes`:
```
from fastapi import APIRouter

router = APIRouter()

@router.get("/agents")
def get_agents():
    # TODO: Implement logic
    return [{"id": 1, "name": "Agent Smith"}]
```
Include the new router in main.py:
```
from fastapi import FastAPI
from routes import agents

app = FastAPI()
app.include_router(agents.router, prefix="/api")
```

## Models
Use Pydantic for request/response models  
USe SQLAlchemy or other ORM for database models  
Example Pydantic Model:
```
from pydantic import BaseModel

class Agent(BaseModel):
    id: int
    name: str
```

## Business Logic:
Move logic from Node.js controllers/services to Python modules in `api2/services/`

## Middleware
FastAPI suppoerts middleware for CORS, authentication, logging, etc.
Example:
```
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
## Connect to React Frontend
- Update the API URLs to point to the FastAPI server
- Make sure CORS is enabled for frontend's origin in FastAPI
- The request/response shapes should match the frontend expectations

### API2 Structure:
```
api2/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection setup
│   │
│   ├── models/                 # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── agent.py
│   │   ├── assistant.py
│   │   ├── role.py
│   │   ├── preset.py
│   │   ├── file.py
│   │   ├── action.py
│   │   ├── transaction.py
│   │   └── ...
│   │
│   ├── schemas/                # Pydantic models (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── agent.py
│   │   ├── assistant.py
│   │   ├── auth.py
│   │   └── ...
│   │
│   ├── routes/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── conversations.py
│   │   ├── messages.py
│   │   ├── agents.py
│   │   ├── assistants.py
│   │   ├── files.py
│   │   ├── actions.py
│   │   ├── balance.py
│   │   ├── config.py
│   │   ├── prompts.py
│   │   ├── roles.py
│   │   ├── presets.py
│   │   ├── memories.py
│   │   ├── plugins.py
│   │   ├── oauth.py
│   │   └── ...
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── conversation_service.py
│   │   ├── message_service.py
│   │   ├── agent_service.py
│   │   ├── assistant_service.py
│   │   ├── file_service.py
│   │   ├── action_service.py
│   │   ├── balance_service.py
│   │   ├── model_service.py
│   │   ├── tool_service.py
│   │   ├── mcp_service.py
│   │   └── ...
│   │
│   ├── middleware/             # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── cors.py
│   │   ├── rate_limiting.py
│   │   └── ...
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── files.py
│   │   ├── tokens.py
│   │   └── ...
│   │
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── config.py
│   │   └── ...
│   │
│   └── dependencies/           # FastAPI dependencies
│       ├── __init__.py
│       ├── auth.py
│       ├── database.py
│       └── ...
│
├── tests/                      # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_conversations.py
│   └── ...
│
├── alembic/                    # Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── .env.example               # Environment variables example
├── .env                       # Environment variables (gitignored)
├── Dockerfile                 # Docker configuration
└── README.md                  # Documentation
```

# Notes:
Frontend: http://localhost:8000 (React app)  
Backend API: http://localhost:8000/api/*  
API Docs: http://localhost:8000/docs  
Health Check: http://localhost:8000/health  

### Completed:
- Database Models: User model with all necessary fields
- Pydantic Schemas: Request/response validation
- Authentication Routes: /api/auth/register, /api/auth/login, /api/auth/me
- Database Integration: SQLAlchemy with automatic table creation
- JWT Token System: Secure authentication

### In Progress:


### Migration To Do List: 
#### Phase 1: 
- Database Models: User model with all necessary fields
- Pydantic Schemas: Request/response validation
- Authentication Routes: /api/auth/register, /api/auth/login, /api/auth/me
- Database Integration: SQLAlchemy with automatic table creation
- JWT Token System: Secure authentication
#### Phase 2:
- Conversations (api/server/routes/convos.js → api2/app/routes/conversations.py)
- Messages (api/server/routes/messages.js → api2/app/routes/messages.py)
- Config (api/server/routes/config.js → api2/app/routes/config.py)
#### Phase 3:
- Agents (api/server/routes/agents/ → api2/app/routes/agents/)
- Assistants (api/server/routes/assistants/ → api2/app/routes/assistants/)
- Files (api/server/routes/files/ → api2/app/routes/files/)
#### Phase 4:
- Presets (api/server/routes/presets.js → api2/app/routes/presets.py)
- Prompts (api/server/routes/prompts.js → api2/app/routes/prompts.py)
- Roles (api/server/routes/roles.js → api2/app/routes/roles.py)

---

## Missing API Routes (to implement)

Based on recent 404 errors, the following routes are missing and need to be implemented:

- `GET /api/convos`
- `GET /api/files/speech/config/get`
- `GET /api/models`
- `GET /api/files`
- `GET /api/search/enable`
- `GET /api/roles/user`
- `GET /api/balance`