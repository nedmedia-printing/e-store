from pydantic import BaseModel, Field


class CreateProject(BaseModel):
    project_name: str
    introduction: str
    description: str
    filename: str
