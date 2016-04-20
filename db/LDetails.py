#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: xiaoL-pkav l@pker.in
@version: 2015/10/11 22:36
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, CHAR, DATETIME, TEXT

Base = declarative_base()


class LDetails(Base):
    __tablename__ = 'L_details'

    Id = Column(INTEGER(11), primary_key=True)
    Url = Column(VARCHAR(255))
    BugNumber = Column(CHAR(30))
    BugTitle = Column(VARCHAR(255))
    BugCompany = Column(VARCHAR(255))
    BugAuthor = Column(VARCHAR(255))
    SubmitTime = Column(DATETIME())
    OpenTime = Column(DATETIME())
    BugType = Column(VARCHAR(255))
    BugLevel = Column(VARCHAR(255))
    BugDescribe = Column(TEXT())
    BugState = Column(TEXT())
    BugProve = Column(TEXT())
    BugPatch = Column(TEXT())
    Attention = Column(INTEGER(11))
    Collect = Column(INTEGER(11))
    ReplyType = Column(VARCHAR(255))
    ReplyRank = Column(INTEGER(11))
    ReplyTime = Column(DATETIME(255))
    ReplyDetails = Column(TEXT())
    ReplyNew = Column(TEXT())


