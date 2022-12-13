from datetime import timedelta
import redis
from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt

from sqlalchemy import true

from models.user import UserModel
from blacklist import BLACKLIST
import hmac
def str_to_bytes(s): return s.encode("utf-8") if isinstance(s, str) else s


def safe_str_cmp(a, b): return hmac.compare_digest(
    str_to_bytes(a), str_to_bytes(b))


BLANK_ERROR = "{} cannot be blank."
USER_ALREADY_EXISTS = "A user with that username already exists."
USER_CREATED_SUCCESSFULLY = "User created successfully."
USER_NOT_FOUND = "User not found."
USER_DELETED = "User deleted."
USER_LOGGED_OUT = "User <id={user_id}> successfully logged out."
INVALID_CREDENTIALS = "Invalid credentials!"
ACCESS_EXPIRES = timedelta(hours=1)
PARSER = reqparse.RequestParser()
PARSER.add_argument(
    "username", type=str, required=True, help=BLANK_ERROR.format("username"), nullable=False
)
PARSER.add_argument(
    "password", type=str, required=True, help=BLANK_ERROR.format("password"), nullable=False
)

# Setup our redis connection for storing the blocklisted tokens. You will probably
# want your redis instance configured to persist data to disk, so that a restart
# does not cause your application to forget that a JWT was revoked.
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

class UserRegister(Resource):

    def post(self):
        data = PARSER.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": USER_ALREADY_EXISTS}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": USER_CREATED_SUCCESSFULLY}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """
    @classmethod
    def get(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user.json(), 200

    @classmethod
    def delete(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):

    def post(self):
        data = PARSER.parse_args()
        user = UserModel.find_by_username(data["username"])

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, data["password"]):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):

    @jwt_required(verify_type=False)
    def post(self):
        # jti is "JWT ID", a unique identifier for a JWT.
        token = get_jwt()
        jti = token["jti"]
        user_id = get_jwt_identity()
        jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
        return {"message": USER_LOGGED_OUT.format(user_id=user_id)}, 200


class TokenRefresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
