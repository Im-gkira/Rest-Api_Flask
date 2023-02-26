from db import db
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from schemas import UserSchema
from passlib.hash import pbkdf2_sha256
from models import UserModel, BlockedJwt
from http import HTTPStatus
from flask_jwt_extended import create_access_token, get_jwt, jwt_required

bp = Blueprint("users", __name__, description="Operations on user database")


@bp.route("/register")
class UserRegister(MethodView):

    @bp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(HTTPStatus.CONFLICT, message="user already exists")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )

        db.session.add(user)
        db.session.commit()

        return {"message": "user created successfully"}, HTTPStatus.CREATED


@bp.route("/user/<int:user_id>")
class User(MethodView):

    @bp.response(HTTPStatus.ACCEPTED, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @staticmethod
    def delete(user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "user deleted"}, HTTPStatus.ACCEPTED


@bp.route("/login")
class UserLogin(MethodView):

    @bp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user.password, user_data["password"]):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, HTTPStatus.ACCEPTED

        abort(HTTPStatus.UNAUTHORIZED, message="Invalid Credentials")


@bp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        blockJWT = BlockedJwt(jti)

        db.session.add(blockJWT)
        db.session.commit()

        return {"message": "Successfully logged out"}, HTTPStatus.ACCEPTED
