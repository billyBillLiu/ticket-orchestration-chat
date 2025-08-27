from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Literal, Dict, Any

Department = Literal["Dialer&WFMServices", "EnterpriseRiskManagement", "FacilitiesServices", "HR", "Intranet&Communications", "IntakeRequests", "InfoSec", "IT", "ProdSupport", "TechnologyChange"]

class TicketItem(BaseModel):
    system: Literal["service"] = "service"
    department: Department
    category: str
    ticketType: str

class PlanMeta(BaseModel):
    requestText: str
    requester: Optional[str] = None
    targetEmployee: Optional[str] = None

class TicketPlan(BaseModel):
    items: List[TicketItem]
    meta: PlanMeta