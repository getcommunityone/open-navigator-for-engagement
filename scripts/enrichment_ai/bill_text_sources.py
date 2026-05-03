"""
Bill Text Data Sources Configuration - FREE/PUBLIC DOMAIN ONLY
"""
from typing import Dict, List
from enum import Enum

class BillTextSource(Enum):
    OPENSTATES_BULK = "openstates_bulk"
    OPENSTATES_API = "openstates_api"
    GEORGIA_SOAP = "georgia_soap"
    UNAVAILABLE = "unavailable"

STATE_BILL_TEXT_APIS: Dict[str, BillTextSource] = {
    "GA": BillTextSource.GEORGIA_SOAP,
}

def get_bill_text_source(state: str) -> BillTextSource:
    return STATE_BILL_TEXT_APIS.get(state.upper(), BillTextSource.UNAVAILABLE)

def can_fetch_bill_text(state: str) -> bool:
    return get_bill_text_source(state) != BillTextSource.UNAVAILABLE

def get_supported_states() -> List[str]:
    return [s for s, src in STATE_BILL_TEXT_APIS.items() if src != BillTextSource.UNAVAILABLE]
