from pydantic import BaseModel, Field, Extra


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

    # class Config:
    #     extra = Extra.ignore

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return self.main_game_id == other.main_game_id


class ProfileUpdate(BaseModel):
    uid: str
    profile_name: str | None
    notes: str | None

    class Config:
        extra = Extra.ignore
