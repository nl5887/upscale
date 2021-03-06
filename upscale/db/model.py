from upscale import config
config = config.config

import sqlalchemy as SA
dburl = SA.engine.url.URL(**config['db'])

from sqlalchemy import create_engine
engine = create_engine(dburl, echo=False, pool_recycle=3600)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class Namespace(Base):
	__tablename__ = 'namespaces'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	#projects = relationship("Project", lazy="dynamic")
	
class Project(Base):
	__tablename__ = 'projects'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	template = Column(String)
	namespaceid = Column(Integer, ForeignKey('namespaces.id'))
	namespace = relationship("Namespace", uselist=False, backref=backref('projects', order_by=id, lazy='dynamic'))

class Repository(Base):
	__tablename__ = 'repositories'

	id = Column(Integer, primary_key=True)
	#name = Column(String)
	#public = Column(String)
	#active = Column(Boolean)
	#private_key = Column(String)
	#public_key = Column(String)
	url = Column(String)
	projectid = Column('projectid', Integer, ForeignKey('projects.id'))
	project = relationship("Project", uselist=False, backref=backref('repository', order_by=id, uselist=False))

class Key(Base):
	__tablename__ = 'keys'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	#public = Column(String)
	active = Column(Boolean)
	private_key = Column(String)
	public_key = Column(String)
	projectid = Column('projectid', Integer, ForeignKey('projects.id'))
	project = relationship("Project", uselist=False, backref=backref('key', order_by=id, uselist=False))

	#namespaceid = Column(Integer, ForeignKey('namespaces.id'))
	#namespace = relationship("Namespace", uselist=False, backref=backref('key', order_by=id, uselist=False))

class Domain(Base):
	__tablename__ = 'domains'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	active = Column(Boolean)
	projectid = Column(Integer, ForeignKey('projects.id'))
	project = relationship("Project", uselist=False, backref=backref('domains', order_by=id, lazy='dynamic'))

class Hook(Base):
	__tablename__ = 'hooks'

	id = Column(Integer, primary_key=True)
	projectid = Column(Integer, ForeignKey('projects.id'))
	project = relationship("Project", backref=backref('hooks', order_by=id))

class Template(Base):
	__tablename__ = 'templates'

	id = Column(Integer, primary_key=True)
	path = Column(String)
	template = Column(String)
	projectid = Column(Integer, ForeignKey('projects.id'))
	project = relationship("Project", backref=backref('templates', order_by=id))

class Parameter(Base):
	__tablename__ = 'parameters'

	id = Column(Integer, primary_key=True)
	key = Column(String)
	value = Column(String)
	projectid = Column(Integer, ForeignKey('projects.id'))
	project = relationship("Project", backref=backref('parameters', order_by=id))

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
Session = scoped_session(sessionmaker(bind=engine))
#Session = sessionmaker(bind=engine)
#session = Session()

