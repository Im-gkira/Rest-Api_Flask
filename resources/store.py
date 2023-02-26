from flask_smorest import Blueprint, abort
from flask.views import MethodView
from schemas import StoreSchema
from models import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db

bp = Blueprint("stores", __name__, description="Operations on Store")


@bp.route("/store/<string:store_id>")
class Store(MethodView):

    @bp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @bp.response(200)
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return "Store Deleted", 200


@bp.route("/store")
class StoreList(MethodView):
    @bp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @bp.arguments(StoreSchema)
    @bp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A store with that name already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the store.")

        return store
