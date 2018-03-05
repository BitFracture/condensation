#! /usr/bin/env python3
"""Regenerates the database from our seed scripts and schema"""
from data.admin import dropSchema, declareSchema, populate
from data.session import SessionManager
from configLoader import ConfigLoader

config = ConfigLoader("config.local.json")
sessionMgr = SessionManager(
        config.get("dbUser"),
        config.get("dbPassword"),
        config.get("dbEndpoint"))

with sessionMgr.session_scope() as session:
    dropSchema(sessionMgr.engine)
    declareSchema(sessionMgr.engine)
    populate(session)



