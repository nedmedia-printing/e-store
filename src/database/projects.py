from sqlalchemy import Column, Integer, inspect, Text, String

from src.database import Base, engine


class ProjectsORM(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    project_name = Column(Text)
    introduction = Column(Text)
    description = Column(Text)
    filename = Column(Text)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'introduction': self.introduction,
            'description': self.description,
            'filename': self.filename,
            # You may want to exclude the image attribute from the dictionary
            # 'image': self.image
        }