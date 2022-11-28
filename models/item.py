from typing import Dict, List, Union
from datadb import conn

ItemJSON = Dict[str, Union[int, str, float]]

class ItemModel(conn.Model):
    __tablename__ = "items"

    id = conn.Column(conn.Integer, primary_key=True)
    name = conn.Column(conn.String(80), unique=True)
    price = conn.Column(conn.Float(precision=2))

    store_id = conn.Column(conn.Integer, conn.ForeignKey("stores.id"))
    store = conn.relationship("StoreModel")

    def __init__(self, name: str, price: float, store_id: int):
        self.name = name
        self.price = price
        self.store_id = store_id


    def json(self) -> ItemJSON:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "store_id": self.store_id,
        }

    @classmethod
    def find_by_name(cls, name: str) -> "ItemModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls) -> List["ItemModel"]:
        return cls.query.all()


    def save_to_db(self) -> None:
        conn.session.add(self)
        conn.session.commit()


    def delete_from_db(self) -> None:
        conn.session.delete(self)
        conn.session.commit()
