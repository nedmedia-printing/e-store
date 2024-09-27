from datetime import date, datetime
from pydantic import BaseModel


def create_date_paid() -> date:
    return datetime.now().date()



