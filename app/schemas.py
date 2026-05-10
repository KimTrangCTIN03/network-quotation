from typing import Any, Dict, List

from pydantic import BaseModel


class SurveyPayload(BaseModel):
    hq: Dict[str, Any]
    buildings: List[Dict[str, Any]]
    server_farm: Dict[str, Any]
    wan_sites: List[Dict[str, Any]]
    dc_sdn: Dict[str, Any] = {}


class BomPayload(BaseModel):
    quote_data: Dict[str, Any]
    option_key: str | None = None
    group_filter: str | None = None


class DeviceRecommendPayload(BaseModel):
    group: str = "De xuat thiet bi"
    item_type: str
    quantity: int = 1
    requirement: Dict[str, Any] = {}


class ManualDeviceListPayload(BaseModel):
    text: str


class DeviceSpecsRecommendPayload(BaseModel):
    sheet: str
    quantity: int = 1
    requirement: Dict[str, Any] = {}


class AmPricePayload(BaseModel):
    model: str
    vendor: str = "Cisco"
    price: float = 0
    list_price: float | None = None


class QuoteRecordPayload(BaseModel):
    title: str = ""
    status: str = "draft"
    quote_data: Dict[str, Any]


def payload_to_dict(payload: SurveyPayload) -> Dict[str, Any]:
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    return payload.dict()
