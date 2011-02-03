"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy import orm

from bookie.model import meta

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    ## Reflected tables must be defined and mapped here
    #global reflected_table
    #reflected_table = sa.Table("Reflected", meta.metadata, autoload=True,
    #                           autoload_with=engine)
    #orm.mapper(Reflected, reflected_table)
    #

    # Setup the SQLAlchemy database engine
    meta.engine = engine
    meta.Base = sa.ext.declarative.declarative_base(bind=meta.engine)
    meta.metadata = meta.Base.metadata

    sm = orm.sessionmaker(bind=meta.engine,
        autoflush=True,
        autocommit=False,
        expire_on_commit=True)

    meta.Session = orm.scoped_session(sm)
    meta.Base.query = meta.Session.query_property(orm.Query)
    meta.Base.__todict__ = meta.todict
    meta.Base.__iter__ = meta.iterfunc
    meta.Base.fromdict = meta.fromdict
