from enum import Enum

from pydantic import BaseModel, Field
from datetime import datetime
from src.utils import create_id


def date_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class RecipientTypes(Enum):
    EMPLOYEES = "Employees"
    CLIENTS = "Policy Holders"
    LAPSED_POLICY = "Lapsed Policy - Policy Holders"

    @classmethod
    def get_fields(cls):
        """Return a list of field names."""
        return [field.value for field in cls]


class SMSCompose(BaseModel):

    message_id: str = Field(default_factory=create_id)
    reference: str | None
    message: str
    from_cell: str | None
    to_cell: str | None
    
    recipient_type: str
    date_time_composed: str = Field(default_factory=date_time)
    date_time_sent: str | None
    is_delivered: bool = Field(default=False)
    client_responded: bool = Field(default=False)


class SMSInbox(BaseModel):

    message_id: str = Field(default_factory=create_id)
    
    parent_reference: str | None
    from_cell: str | None
    is_response: bool = Field(default=True)
    previous_history: str | None
    message: str
    date_time_received: str = Field(default_factory=date_time)
    is_read: bool = Field(default=False)


class EmailCompose(BaseModel):
    """
        email compose
    """
    message_id: str = Field(default_factory=create_id)
    reference: str | None
    from_email: str | None
    to_email: str | None
    subject: str
    message: str
    
    recipient_type: str
    is_sent: bool = Field(default=False)
    date_time_sent: str | None


class SMSSettings(BaseModel):
    company_id: str
    enable_sms_notifications: bool = Field(default=False)
    enable_sms_campaigns: bool = Field(default=False)
    sms_signature: str
    policy_lapsed_notifications: bool = Field(default=False)
    upcoming_payments_notifications: bool = Field(default=False)
    policy_paid_notifications: bool = Field(default=False)
    claims_notifications: bool = Field(default=False)
