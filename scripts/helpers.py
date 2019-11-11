# -*- coding: utf-8 -*-

from scripts import create_table
from flask import session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import bcrypt


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    s = get_session()
    s.expire_on_commit = False
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()


def get_session():
    return sessionmaker(bind=create_table.engine)()

def add_user(username, password, email, paymentflag):
    with session_scope() as s:
        u = create_table.User(username=username, password=password, email=email, paymentflag=paymentflag)
        s.add(u)
        s.commit()

def credentials_valid(username, password, paymentflag):
    with session_scope() as s:
        user = s.query(create_table.User).filter(create_table.User.username.in_([username])).first()
        passkey = user.password
        paymentflag = paymentflag
        if user and paymentflag=='Y' and passkey==password:
            #return bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8'))
            return True
        else:
            return False