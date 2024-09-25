from os import path
from src.database.models import CreateProject
from src.database.projects import ProjectsORM
from src.controllers import Controllers
from src.utils import upload_folder


class ProjectController(Controllers):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_projects(self) -> list[dict[str, str]]:
        with self.get_session() as session:
            projects: list[ProjectsORM] = session.query(ProjectsORM).all()
            return [project.to_dict() for project in projects]

    @staticmethod
    async def create_image_src(filename: str) -> str:
        """
        :return:
        """
        filename: str = path.join(upload_folder(), filename)
        return filename

    async def add_project(self, project_data: CreateProject) -> str:
        with self.get_session() as session:
            # Create an instance of ProjectsORM using the project_data dictionary
            image_src: str = await self.create_image_src(filename=project_data.filename)
            new_project: ProjectsORM = ProjectsORM(**project_data.dict())
            session.add(new_project)
            session.commit()
            return image_src

    async def delete_project(self, _id: int):
        with self.get_session() as session:
            # Query the project by its ID
            project_to_delete = session.query(ProjectsORM).filter_by(id=_id).first()

            if project_to_delete:
                # If the project exists, delete it
                session.delete(project_to_delete)
                session.commit()
                return True  # Return True to indicate successful deletion
            else:
                # If the project doesn't exist, return False to indicate failure
                return False
