from sqlalchemy import Column, String, inspect, Integer, Boolean, Text

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class SMSInboxORM(Base):
    __tablename__ = "sms_inbox"

    message_id: str = Column(String(ID_LEN), primary_key=True, index=True)
    to_branch: str = Column(String(ID_LEN), index=True)
    parent_reference: str = Column(String(ID_LEN), nullable=True)
    from_cell: str = Column(String(17))
    is_response: bool = Column(Boolean)
    previous_history: str = Column(Text)
    message: str = Column(Text)
    date_time_received: str = Column(String(36))
    is_read: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        """
        Convert the object to a dictionary representation.
        """
        return {
            "from_cell": self.from_cell,

            "to_branch": self.to_branch,
            "message_id": self.message_id,
            "is_response": self.is_response,
            "parent_reference": self.parent_reference,
            "message": self.message,
            "date_time_received": self.date_time_received,
            "is_read": self.is_read
        }


class SMSComposeORM(Base):
    __tablename__ = "sms_compose"

    message_id: str = Column(String(ID_LEN), primary_key=True, index=True)
    reference: str = Column(String(ID_LEN))
    message: str = Column(Text)
    from_cell: str = Column(String(17))
    to_cell: str = Column(String(17))
    to_branch: str = Column(String(ID_LEN))
    recipient_type: str = Column(String(36))
    date_time_composed: str = Column(String(36))
    date_time_sent: str = Column(String(36))
    is_delivered: bool = Column(Boolean)
    client_responded: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        """
        Convert the object to a dictionary representation.
        """
        return {
            "message_id": self.message_id,
            "message": self.message,
            "reference": self.reference,
            "from_cell": self.from_cell,
            "to_cell": self.to_cell,
            "to_branch": self.to_branch,
            "recipient_type": self.recipient_type,
            "date_time_composed": self.date_time_composed,
            "date_time_sent": self.date_time_sent,
            "is_delivered": self.is_delivered,
            "client_responded": self.client_responded
        }


class EmailComposeORM(Base):
    __tablename__ = "email_compose"
    message_id = Column(String(ID_LEN), primary_key=True, index=True)
    to_branch = Column(String(NAME_LEN), index=True)
    reference = Column(String(ID_LEN))
    from_email = Column(String(255))
    to_email = Column(String(255))
    subject = Column(String(NAME_LEN))
    message = Column(Text)
    recipient_type = Column(String(NAME_LEN))
    is_sent = Column(Boolean)
    date_time_sent = Column(String(36))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        """
        Convert the object to a dictionary representation.
        """
        return {
            'message_id': self.message_id,
            'reference': self.reference,
            'from_email': self.from_email,
            'to_email': self.to_email,
            'subject': self.subject,
            'message': self.message,
            'to_branch': self.to_branch,
            'recipient_type': self.recipient_type,
            'is_sent': self.is_sent,
            'date_time_sent': self.date_time_sent,
        }


class SMSSettingsORM(Base):
    __tablename__ = "sms_settings"
    company_id: str = Column(String(ID_LEN), primary_key=True, index=True)
    enable_sms_notifications: bool = Column(Boolean)
    enable_sms_campaigns: bool = Column(Boolean)
    sms_signature: str = Column(String(255))
    policy_lapsed_notifications: bool = Column(Boolean)
    upcoming_payments_notifications: bool = Column(Boolean)
    policy_paid_notifications: bool = Column(Boolean)
    claims_notifications: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            cls.__table__.create(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        """
        Convert the object to a dictionary representation.
        """
        return {
            "company_id": self.company_id,
            "enable_sms_notifications": self.enable_sms_notifications,
            "enable_sms_campaigns": self.enable_sms_campaigns,
            "sms_signature": self.sms_signature,
            "policy_lapsed_notifications": self.policy_lapsed_notifications,
            "upcoming_payments_notifications": self.upcoming_payments_notifications,
            "policy_paid_notifications": self.policy_paid_notifications,
            "claims_notifications": self.claims_notifications,
        }
