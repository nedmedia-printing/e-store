from flask import Flask
import asyncio
from sqlalchemy.orm import joinedload
from src.controller import Controllers, error_handler
from src.database.models.profile import Profile
from src.database.sql.profile import ProfileORM


class ProfileController(Controllers):
    def __init__(self):
        super().__init__()
        self.__profiles = []
        self.__profiles_dict = {}

    def init_app(self, app: Flask):
        asyncio.run(self.preload_profiles())
        super().init_app(app=app)

    @error_handler
    async def preload_profiles(self):
        self.__profiles = await self.get_all_profiles()
        self.__profiles_dict = {profile.uid: profile for profile in self.__profiles}

    async def get_all_profiles(self) -> list[Profile]:
        """

        :return:
        """
        with self.get_session() as session:
            profiles_list_orm = (
                session.query(ProfileORM)
                .options(
                    joinedload(ProfileORM.user)
                )
                .all()
            )
            return [Profile(**profile_orm.to_dict(include_relationships=True)) for profile_orm in profiles_list_orm]

    @error_handler
    async def get_profiles(self) -> list[Profile]:
        """ Retrieves all profiles from the database with joined records. """
        return self.__profiles

    @error_handler
    async def get_profile(self, uid: str) -> Profile | None:
        """ Retrieves a profile by ID from the preloaded profiles. """
        return self.__profiles_dict.get(uid)

    @error_handler
    async def add_profile(self, profile: Profile) -> Profile:
        """ Adds a new profile to the database. """
        with self.get_session() as session:
            session.add(ProfileORM(
                uid=profile.uid,
                profile_name=profile.profile_name,
                first_name=profile.first_name,
                surname=profile.surname,
                cell=profile.cell,
                email=profile.email,
                notes=profile.notes
            ))

        await self.preload_profiles()  # Update preloaded profiles after adding a new one
        return profile

    @error_handler
    async def update_profile(self, profile_id: str, updated_data: dict) -> bool:
        """ Updates an existing profile's details. """
        with self.get_session() as session:
            profile_orm: ProfileORM = session.query(ProfileORM).filter_by(uid=profile_id).first()
            if not profile_orm:
                return False
            for key, value in updated_data.items():
                setattr(profile_orm, key, value)

        await self.preload_profiles()  # Update preloaded profiles after updating
        return True

    @error_handler
    async def delete_profile(self, profile_id: str) -> bool:
        """ Deletes a profile by ID along with all linked records. """
        with self.get_session() as session:
            profile_orm = session.query(ProfileORM).filter_by(uid=profile_id).first()
            if not profile_orm:
                return False
            session.delete(profile_orm)

        await self.preload_profiles()  # Update preloaded profiles after deletion
        return True
