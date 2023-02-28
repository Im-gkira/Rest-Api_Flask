from flask_smorest import Blueprint, abort
from flask.views import MethodView
from http import HTTPStatus
from schemas import *
from db import db
from models import TagModel, StoreModel, ItemModel
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

    @bp.response(
        202,
        description="Deletes a tag if no item is tagged with it.",
        example={"message": "Tag deleted."},
    )
    @bp.alt_response(404, description="Tag not found.")
    @bp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.",
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any items, then try again.",
        )


@bp.route("/item/<string:item_id>/tags/<string:tag_id>")
class LinksTagsToItem(MethodView):

    @bp.response(HTTPStatus.ACCEPTED, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.apppend(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(HTTPStatus.BAD_REQUEST, message="An error has occurred")

    @bp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return {"message": "Item removed from tag", "item": item, "tag": tag}
