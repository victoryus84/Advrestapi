from typing import Dict, Union
from json import *
from flask_sqlalchemy import SQLAlchemy
from datadb import conn

UserJSON = Dict[str, Union[int, str]]

class UserModel(conn.Model):
    __tablename__ = "users"

    id = conn.Column(conn.Integer, primary_key=True)
    username = conn.Column(conn.String(80), unique=True)
    password = conn.Column(conn.String(80))

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


    def json(self) -> UserJSON:
        return {
            "id": self.id,
            "username": self.username
        }
        # return json.dumps({
        #     "id": id,
        #     "username": username
        # })

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        userfound = cls.query.filter_by(username=username).first()
        return userfound

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()


    def save_to_db(self) -> None:
        conn.session.add(self)
        conn.session.commit()


    def delete_from_db(self) -> None:
        conn.session.delete(self)
        conn.session.commit()
