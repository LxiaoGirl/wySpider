#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: xiaoL-pkav l@pker.in
@version: 2015/10/10 18:08
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR

Base = declarative_base()


class LBugs(Base):
    __tablename__ = 'L_bugs'

    Id = Column(INTEGER(11), primary_key=True)
    BugUrl = Column(VARCHAR(255))
    BugName = Column(VARCHAR(255))
    IsGet = Column(TINYINT(5))
