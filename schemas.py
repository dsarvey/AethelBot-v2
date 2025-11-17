# schemas.py
#
# Contains all Pydantic models (schemas) for validating
# API request and response bodies.

from pydantic import BaseModel, Field
from typing import Dict, Any

class DeployBody(BaseModel):
    initialFunding: float
    additionalCapital: float
    configuration: Dict[str, Any]

class CapitalInjectBody(BaseModel):
    amount: float

class TsoQuery(BaseModel):
    ticker: str