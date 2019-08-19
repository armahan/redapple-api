from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.eduModel import ClassNameModel

class ClassNameRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('teacher_id',
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('name',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    def post(self):
        data = ClassNameRegister.parser.parse_args()

        if ClassNameModel.find_by_name(data['name']):
            return {"message": "A class with that class name already exits."}, 400

        class_name = ClassNameModel(data['teacher_id'], data['name'])
        class_name.save_to_db()

        return {"message": "Class name created successfully."}, 201

class ClassNameList(Resource):
    def get(self):
        return {'Class': list(map(lambda x: x.json(), ClassNameModel.query.all()))}

class ClassName(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('teacher_id',
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('name',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    def get(self, name):
        class_name = ClassNameModel.find_by_name(name)
        if class_name:
            return class_name.json()
        return {'message': 'Class not found'}, 404

    def put(self, name):
        data = ClassName.parser.parse_args()
        class_name = ClassNameModel.find_by_name(name)

        if class_name:
            class_name.name = data['name']

        class_name.save_to_db()
        return class_name.json()

class ClassListByTeacher(Resource):

    def get(self, teacher_id):
        teacher = ClassNameModel.find_by_teacher_id(teacher_id)
        if teacher:
            return {'Class_name': list(map(lambda x: x.json(), teacher))}
        return {'message': 'Class not found'}, 404
