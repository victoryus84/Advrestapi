from typing import Dict, List, Union
from datadb import conn
from models.item import ItemJSON

StoreJSON = Dict[str, Union[int, str, List[ItemJSON]]]


class StoreModel(conn.Model):
    __tablename__ = "stores"

    id = conn.Column(conn.Integer, primary_key=True)
    name = conn.Column(conn.String(80), unique=True)

    items = conn.relationship("ItemModel", lazy="dynamic", overlaps="store")

    def __init__(self, name: str):
        self.name = name


    def json(self) -> StoreJSON:
        return {
            "id": self.id,
            "name": self.name,
            "items": [item.json() for item in self.items.all()],
        }

    @classmethod
    def find_by_name(cls, name: str) -> "StoreModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls) -> List["StoreModel"]:
        return cls.query.all()


    def save_to_db(self) -> None:
        conn.session.add(self)
        conn.session.commit()


    def delete_from_db(self) -> None:
        conn.session.delete(self)
        conn.session.commit()
