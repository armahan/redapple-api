from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.eduModel import SubjectModel

class SubjectRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('subject_name',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    parser.add_argument('parent_id',
                        type=int,
                        required=False,
                        help="This field must be parent id.")
    def post(self):
        data = SubjectRegister.parser.parse_args()
        subject = SubjectModel.find_by_subject_name(data['subject_name'])

        if subject:
            return {"message": "subject already exits."}, 400
        subject = SubjectModel(data['subject_name'], data['parent_id'])
        subject.save_to_db()
        return {"subject_id":subject.id, "subject": subject.name}, 201

class SubjectList(Resource):
    def get(self):
        return {'subjects': list(map(lambda x: x.json(), SubjectModel.query.all()))}

class Subject(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('subject_id',
                        type=int,
                        required=False,
                        help="This field must be subject id.")
    parser.add_argument('subject_name',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    parser.add_argument('parent_id',
                        type=int,
                        required=False,
                        help="This field must be parent id.")
    def get(self, id):
        subject = SubjectModel.find_by_subject_id(id)
        if subject:
            return subject.json()
        return {'message': 'subject not found'}, 404

    def put(self, id):
        data = Subject.parser.parse_args()
        subject = SubjectModel.find_by_subject_id(id)
        if subject:
            try:
                subject.name = data['subject_name']
                subject.parent_id = data['parent_id']
                subject.save_to_db()
                return subject.json(), 201
            except:
                return {"message": "An error occurred inserting the subject."}, 500
        return {'message': 'Subject not found.'}, 404

    def delete(self, id):
        subject = SubjectModel.find_by_subject_id(id)
        if subject:
            check_child = SubjectModel.find_by_child_id(subject.parent_id)
            if check_child.parent_id is not None:
                subject.delete_from_db()
                return {'message': 'Subject deleted.'}, 201
            else:
                return {'message': 'This subject is a main category.'}
        return {'message': 'Subject not found.'}, 404

