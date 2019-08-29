from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.eduModel import ContentModel, SubjectModel, UserModel


class ContentPost(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('content_name',
                        type=str,
                        required=True,
                        help="Content name field cannot be blank.")
    parser.add_argument('content',
                        type=str,
                        required=True,
                        help="Content body field cannot be blank.")
    parser.add_argument('subject_id',
                        type=int,
                        required=True,
                        help="Subject field cannot be blank."
                        )

    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        data = ContentPost.parser.parse_args()
        content = ContentModel.find_by_name(data['content_name'])
        subject = SubjectModel.find_by_subject_id(data['subject_id'])
        user = UserModel.find_by_id(claims['user_id'])
        if content:
            return {'message': 'Content is already exists.'}, 400
        else:
            content = ContentModel(data['content_name'], data['content'])
            content.subject.append(subject)
            content.owner.append(user)
            content.save_to_db()
            return {'content_id': content.id, 'content_name': content.name}, 201


class ContentList(Resource):
    def get(self):
        return {'Contents': list(map(lambda x: x.json(), ContentModel.query.all()))}


class Content(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('content_id',
                        type=int,
                        required=False,
                        help="Subject field cannot be blank."
                        )
    parser.add_argument('content_name',
                        type=str,
                        required=False,
                        help="Content name field cannot be blank.")
    parser.add_argument('content',
                        type=str,
                        required=True,
                        help="Content body field cannot be blank.")
    parser.add_argument('subject_id',
                        type=int,
                        required=True,
                        help="Subject field cannot be blank."
                        )

    def get(self, id):
        content = ContentModel.find_by_id(id)
        subjects = content.subject
        if content:
            return {'subject_id': list(map(lambda x: x.json(), subjects)),
                    'content_id': content.id,
                    'content_name': content.name,
                    'content': content.text }, 200
            # Below loop is content in subjects 
            # 'subjects': list(map(lambda x: x.json(), content.query.filter_by(id=content.id).first().subject))}, 200
        return {'message': 'Content not found'}, 404

    def put(self, id):
        data = Content.parser.parse_args()
        subject = SubjectModel.find_by_subject_id(data['subject_id'])
        content = ContentModel.find_by_id(id)
        if content:
            try:
                content.text = data['content']
                content.name = data['content_name']
                content.subject.append(subject)
                content.save_to_db()
                return content.json(), 201
            except:
                return {"message": "An error occurred inserting the content."}, 500
        return {'message': 'Content not found.'}, 404

    def delete(self, id):
        content_name = ContentModel.find_by_id(id)
        subjects_id = content_name.query.filter_by(
            id=content_name.id).first().subject
        if content_name:
            if subjects_id:
                for subject in subjects_id:
                    rm = SubjectModel.find_by_subject_id(subject.id)
                    content_name.subject.remove(rm)
                    content_name.save_to_db()
            content_name.delete_from_db()
            return {'message': 'Content is deleted'}, 201
        return {'message': 'Content not found.'}, 404

class ContentBySubject(Resource):
    def get(self, id):
        subject = SubjectModel.find_by_subject_id(id)
        if subject:
            return{
                'subject': subject.name,
                'contents': list(map(lambda x: x.json(), subject.query.filter_by(id=subject.id).first().content))}, 200
        return {'message': 'Subject not found.'}, 404
