from flask_smorest import Blueprint, abort
from flask.views import MethodView
from schemas import *
from models import ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt
from http import HTTPStatus

bp = Blueprint("Items", __name__, description="Operations on Items")


@bp.route("/item/<string:item_id>")
class Item(MethodView):
    @jwt_required()
    @bp.response(200, ItemSchema)
    def get(self, item_id):
        return ItemModel.query.get_or_404(item_id)

    @jwt_required()
    @bp.response(200)
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(HTTPStatus.UNAUTHORIZED, message="Admin Privileges Required")

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return "Item Deleted", 200

    @bp.arguments(UpdateItemSchema)
    @bp.response(201, UpdateItemSchema)
    def put(self, data_item, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.name = data_item["name"]
            item.price = data_item["price"]
        else:
            item = {id: item_id, **data_item}

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "Something went wrong!")
        raise NotImplementedError


@bp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @bp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required()
    @bp.arguments(ItemSchema)
    @bp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            return abort(500, "something went wrong!")

        return item_data
