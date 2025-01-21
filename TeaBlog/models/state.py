from backend.db import Base
from sqlalchemy import Column, String, Integer, Text


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(200), nullable=True)

    def __repr__(self):
        return f'<State {self.title}>'
