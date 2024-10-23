from pydantic import BaseModel

from src.database.models.users import User


class Profile(BaseModel):
    """
        **Profile**
            allows users to create personalized settings
            such us - deposit multiplier
    """
    uid: str
    profile_name: str | None
    first_name: str | None
    surname: str | None
    cell: str | None
    email: str | None
    notes: str | None
    user: User | None

