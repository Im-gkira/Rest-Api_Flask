from flask_smorest import Blueprint, abort
from flask.views import MethodView
from http import HTTPStatus
from schemas import *
from db import db
from models import TagModel, StoreModel
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint("tags", __name__, description="Operations on tags")


@bp.route("/tags/<string:store_id>/tag")
class TagsInStore(MethodView):

    @bp.response(HTTPStatus.ACCEPTED, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id).first()
        return store.tags.all()

    @bp.arguments(TagSchema)
    @bp.response(HTTPStatus.CREATED, TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(HTTPStatus.BAD_REQUEST, message="tag already exists")

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(HTTPStatus.BAD_GATEWAY, message=f"{e}")

        return tag


@bp.route("/tag/<string:tag_id>")
class Tag(MethodView):

    @bp.response(HTTPStatus.ACCEPTED, TagSchema)
    def get(self, tag_id):
        return TagModel.query.get_or_404(tag_id)


