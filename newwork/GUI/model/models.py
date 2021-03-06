from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from setting.orderset import SQLALCHEMY_DIR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float,Table
from sqlalchemy.orm import relationship, backref
from datetime import datetime

from sqlalchemy.orm import sessionmaker

Base = declarative_base()
import logging
logger = logging.getLogger(__name__)

class Account(Base):
    __tablename__ = 'account'
    account_id = Column(Integer,nullable=False, autoincrement=True)
    name = Column(String(50),  primary_key=True)
    password = Column(String(200), nullable=False)
    datetime = Column(DateTime, default=datetime.now())
    parameter_id = relationship("Result", backref = "account", cascade="all")



class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True, autoincrement=True)
    corediameter = Column(Float, nullable=False)
    claddiameter = Column(Float, nullable=False)
    coreroundness = Column(Float, nullable=False)
    cladroundness = Column(Float, nullable=False)
    concentricity = Column(Float, nullable=False)

    sharpindex = Column(Float, nullable=False)
    fibertype = Column(String(50), nullable=False)
    fiberLength = Column(String(50), nullable=False)
    producer = Column(String(50), nullable=False)
    fiberNo = Column(String(50), nullable=False)
    # worker = Column(String(50), nullable=False)

    worker = Column(String(50), ForeignKey('account.name'))

    datetime = Column(DateTime, default=datetime.now())
    EXIT_KEYS = ('corediameter', 'claddiameter', 'coreroundness', 'cladroundness', 'concentricity',
            'sharpindex', 'fibertype', 'fiberLength', 'producer', 'fiberNo', 'worker',)

engine = create_engine(SQLALCHEMY_DIR)
DBSession = sessionmaker(bind=engine)
logger.warning("creat db by "+SQLALCHEMY_DIR)

def session_add_by_account(result):
    session = DBSession()
    is_exit = session.query(Account).filter(Account.name == result['worker']).count()
    if 0 == is_exit:
        logger.warning('user not exit '+ result['worker'] +' '+str(is_exit))
        return
    logger.warning('add data to db by user '+result['worker'])
    results = {k:v for k,v in result.items() if k in Result.EXIT_KEYS}
    session.add(Result(**results))
    session.commit()
    session.close()