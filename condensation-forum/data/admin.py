#! /usr/bin/env python3
from data.session import Session


def open():
    session = Session("postgres","password","localhost", debug=True)
