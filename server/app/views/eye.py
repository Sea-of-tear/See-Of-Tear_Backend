from flask import request, Response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import UserModel
from app.models.eye import EyeModel, Comment


class PostEye(Resource):
    @jwt_required
    def post(self):
        user = UserModel.objects(id=get_jwt_identity()).first()

        if not user:
            return Response('user not found', 401)

        title = request.form['title']
        description = request.form['description']
        background_image = request.form['background']
        category = request.form['category']

        EyeModel(
            title=title,
            description=description,
            author=user,
            background_image=background_image,
            category=category
        ).save()

        return Response('', 201)


class EyesList(Resource):
    @jwt_required
    def get(self):
        """
        카테고리별 eye 목록 조회
        """
        user = UserModel.objects(id=get_jwt_identity()).first()

        if not user:
            return Response('user not found', 401)

        category = request.args['category']

        return [{
            'title': eye.title,
            'category': eye.category,
            'author': eye.author.nickname,
            'posting_time': eye.posting_time,
            'comment_count': eye.comment_count,
            'tear_count': eye.tear_count
        } for eye in EyeModel.objects(category=category)], 200


class ViewEye(Resource):
    @jwt_required
    def get(self, eye_id):
        """
        특정 eye 조회
        """
        user = UserModel.objects(id=get_jwt_identity()).first()

        if not user:
            return Response('user not found', 401)

        eye = EyeModel.objects(id=eye_id).first()

        if not eye:
            Response('', 204)

        return {
            'title': eye.title,
            'description': eye.description,
            'author': eye.user.nickname,
            'category': eye.category,
            'comments': [{
                'author': comment.author.nickname,
                'description': comment.description,
                'tissue': comment.tissue
            } for comment in eye.comments],
            # 'posting_time': eye.posting_time,
            'comment_count': eye.comment_count,
            'tear_count': eye.tear_count
        }, 200


class PostComment(Resource):
    @jwt_required
    def post(self, eye_id):
        """
        특정 eye 에 위로글 달기
        """
        user = UserModel.objects(id=get_jwt_identity()).first()

        if not user:
            return Response('user not found', 401)

        eye = EyeModel.objects(id=eye_id).first()

        if not eye:
            Response('', 204)

        description = request.form['description']

        eye.comments.append(Comment(author=user, description=description))
        eye.save()

        cnt = int(eye.comment_count) + 1
        eye.update(comment_count=cnt)

        return Response('', 201)


class PostTear(Resource):
    @jwt_required
    def post(self, eye_id):
        """
        특정 eye 에 눈물 표시
        """
        user = UserModel.objects(id=get_jwt_identity()).first()

        if not user:
            return Response('user not found', 401)

        eye = EyeModel.objects(id=eye_id).first()

        if not eye:
            Response('', 204)

        tear_cnt = int(eye.tear_count) + 1
        eye.update(tear_count=tear_cnt)

        owner = eye.author

        get_tears_count = int(owner.get_tears_count) + 1
        owner.update(get_tears_count=get_tears_count)

        return Response('', 201)


class AdoptTissue(Resource):
    @jwt_required
    def post(self, eye_id, comment_id):
        eye = EyeModel.objects(id=eye_id).first()

        cnt = 0

        if get_jwt_identity() == eye.author.id:
            for comment in eye.comments:
                if comment.id == comment_id:
                    eye.comments[cnt].tissue = True
                    eye.save()
                    cnt = int(eye.author.tissue_count) + 1
                    eye.author.update(tissue_count=cnt)
                    break
                cnt += 1

        return Response('', 201)
