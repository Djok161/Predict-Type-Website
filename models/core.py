from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Website(Base):
	__tablename__ = "websites"
	id = Column(Integer, primary_key=True, index=True)
	url = Column(String, index=True)
	class_website = Column(String, index=True)
