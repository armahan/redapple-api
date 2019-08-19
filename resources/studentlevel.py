from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.eduModel import StudentLevelModel

class StudentLevel(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('student_id',
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('level_id',
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('is_done',
                        type=bool,
                        required=True,
                        help="This field cannot be blank."
                        )
    def post(self):
        data = StudentLevel.parser.parse_args()

        level_add = StudentLevelModel(data['student_id'], data['level_id'], data['is_done'])
        try:
            level_add.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        return level_add.json(), 201


class StudentLevelList(Resource):

    def get(self, student_id):
        student = StudentLevelModel.find_by_student_id_all(student_id)
        if student:
            return {'Level': list(map(lambda x: x.json(), student))}
        return {'message': 'Student does not have any level.'}

class StudentLevelUpdate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('level_id',
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('is_done',
                        type=bool,
                        required=True,
                        help="This field cannot be blank."
                        )
    def put(self, student_id, level_id):
        data = StudentLevelUpdate.parser.parse_args()
        student = StudentLevelModel.find_by_student_id(student_id)

        if student:
            try:
                student.level_id = data['level_id']
                student.is_done = data['is_done']
                student.save_to_db()
                return {"id": student.student_id, "level": student.level_id, "Is done": student.is_done}
            except:
                return {"message": "An error occurred inserting the item."}, 500
        return {'message': 'Student {} does not in level {} .'.format(student_id, level_id)}
