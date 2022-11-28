from importlib import resources
from flask import Flask, jsonify, render_template, Blueprint
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from resources.user import ACCESS_EXPIRES, UserRegister, UserLogin, User, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from datadb import conn
from blacklist import BLACKLIST
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)
conn.init_app(app)
api = Api(app)


@app.before_first_request
def create_tables():
    conn.create_all()


jwt = JWTManager(app)

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST

# API
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")

# SITE
main_bp = Blueprint('main_bp', __name__)
app.register_blueprint(main_bp)
@app.route("/")
def home():
    param1 = "Victor"
    param2 = datetime.now()
    return render_template("home.html", param1=param1, param2=param2)

if __name__ == "__main__":
    conn.init_app(app)
    app.run(debug=True, host='0.0.0.0')
