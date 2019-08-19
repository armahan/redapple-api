from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.eduModel import StudentClassModel, ClassNameModel

class StudentClassRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('class_name_id',
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('student_id',
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = StudentClassRegister.parser.parse_args()

        student_add = StudentClassModel(data['class_name_id'], data['student_id'])
        class_name = ClassNameModel.find_by_id(data['class_name_id'])
        try:
            student_add.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        return class_name.json(), 201

class StudentInClass(Resource):
    def get(self, student_id):
        student = StudentClassModel.find_by_student_id(student_id)
        if student:
            return {'class_name': list(map(lambda x: x.json(), student))}

        return {'message': 'Student not found'}, 404
